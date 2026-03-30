"""AI service — Gemini API integration for image generation and editing."""

import os
import base64
from datetime import datetime

from server.services.asset_service import AssetService

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AIService:
    """Wraps Gemini API for image operations."""

    def __init__(self):
        self.asset_service = AssetService()
        self._client = None

    def _get_client(self):
        """Lazy-init Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                api_key = os.environ.get("GEMINI_API_KEY", "")
                if not api_key:
                    raise RuntimeError(
                        "GEMINI_API_KEY not set. "
                        "Set it in environment or .env file."
                    )
                genai.configure(api_key=api_key)
                self._client = genai
            except ImportError:
                raise RuntimeError(
                    "google-generativeai not installed. "
                    "Run: pip install google-generativeai"
                )
        return self._client

    async def generate_image(
        self,
        description: str,
        asset_type: str = "character",
        style: str | None = None,
    ) -> dict:
        """Generate an image with Gemini."""
        genai = self._get_client()

        # Build prompt with style
        config = self.asset_service.get_project_config()
        style_keywords = ""
        if config:
            from game_asset_tools.config import get_style_keywords
            style_keywords = get_style_keywords(config)

        prompt = f"{description}, {style_keywords}" if style_keywords else description

        # Use Gemini's image generation
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_modalities=["image", "text"],
            ),
        )

        # Extract image from response
        output_dir = os.path.join(PROJECT_ROOT, "output", self._type_to_dir(asset_type))
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{asset_type}_{timestamp}.png"
        output_path = os.path.join(output_dir, filename)

        for part in response.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image_data = part.inline_data.data
                with open(output_path, "wb") as f:
                    f.write(image_data)
                break
        else:
            raise RuntimeError("Gemini did not return an image")

        # Update manifest
        from game_asset_tools.manifest import Manifest
        rel_path = os.path.relpath(output_path, self.asset_service.output_dir)
        m = Manifest(self.asset_service.output_dir, config.get("project", {}).get("name", "default") if config else "default")
        m.add_entry(file=rel_path, asset_type=asset_type, prompt=description, model="gemini", style=style or "")
        m.save()

        return {
            "file": rel_path,
            "path": output_path,
            "type": asset_type,
            "prompt": description,
            "image_url": f"/output/{rel_path}",
        }

    async def analyze_design(self, image_path: str) -> dict:
        """Analyze a design image and identify elements."""
        genai = self._get_client()

        # Upload image for Gemini to analyze
        import PIL.Image
        img = PIL.Image.open(image_path)
        w, h = img.size

        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content([
            "Analyze this game UI design image. Identify all visual elements (characters, icons, buttons, health bars, backgrounds). "
            "For each element, provide: name, type (character/icon/ui/background), approximate bounding box [left, top, right, bottom] in pixels, "
            "and which layer it belongs to (bottom/middle/top). "
            "Also identify shared components (borders/frames used by multiple elements). "
            f"Image size is {w}x{h} pixels. "
            "Return ONLY valid JSON in this format: "
            '{"source": "path", "source_size": [w,h], "layers": {"bottom": [...], "middle": [...], "top": [...]}, "shared_assets": [...]}',
            img,
        ])

        # Parse response as JSON
        import json
        text = response.text.strip()
        # Remove markdown code block if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[:-3]

        try:
            elements = json.loads(text)
        except json.JSONDecodeError:
            elements = {
                "source": image_path,
                "source_size": [w, h],
                "layers": {},
                "shared_assets": [],
                "_raw_response": text,
            }

        elements["source"] = image_path
        elements["source_size"] = [w, h]

        # Save elements.json
        elements_path = os.path.join(self.asset_service.tmp_dir, "elements.json")
        os.makedirs(self.asset_service.tmp_dir, exist_ok=True)
        with open(elements_path, "w") as f:
            json.dump(elements, f, indent=2, ensure_ascii=False)

        # Generate annotated preview
        from game_asset_tools.annotate import annotate_image
        annotated_path = os.path.join(self.asset_service.tmp_dir, "annotated.png")
        annotate_image(image_path, elements, annotated_path)

        return {
            "elements": elements,
            "elements_path": elements_path,
            "annotated_image": f"/output/.tmp/annotated.png",
        }

    async def refine_asset(
        self,
        asset_name: str,
        refine_type: str,
        note: str = "",
    ) -> dict:
        """Refine an asset using AI."""
        asset = self.asset_service.get_asset(asset_name)
        if not asset:
            raise ValueError(f"Asset '{asset_name}' not found")

        path = asset["path"]

        # Save version before refining
        from game_asset_tools.version import VersionManager
        vm = VersionManager(path)
        vm.save_version(action=f"before_{refine_type}", note="Auto-saved before refinement")

        if refine_type == "edge_fix":
            from game_asset_tools.remove_bg import remove_background, is_rembg_available
            from game_asset_tools.trim import trim_transparent
            if is_rembg_available():
                tmp = path + ".tmp.png"
                remove_background(path, tmp)
                trim_transparent(tmp, path, padding=2)
                os.remove(tmp)

        elif refine_type in ("ai_edit", "ai_inpaint"):
            genai = self._get_client()
            import PIL.Image
            img = PIL.Image.open(path)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")

            prompt = note if refine_type == "ai_edit" else f"Complete the missing part: {note}"
            response = model.generate_content([prompt, img],
                generation_config=genai.GenerationConfig(response_modalities=["image", "text"]))

            for part in response.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    with open(path, "wb") as f:
                        f.write(part.inline_data.data)
                    break

        elif refine_type == "style_unify":
            # Style transfer would need a reference image
            pass

        # Save version after refining
        vm.save_version(action=refine_type, note=note)

        return {
            "asset": asset_name,
            "refine_type": refine_type,
            "note": note,
            "image_url": asset.get("image_url", ""),
        }

    @staticmethod
    def _type_to_dir(asset_type: str) -> str:
        mapping = {
            "character": "characters", "icon": "icons", "ui": "ui",
            "background": "backgrounds", "card": "cards",
            "sprite": "sprites", "tileset": "tilesets",
        }
        return mapping.get(asset_type, asset_type)
