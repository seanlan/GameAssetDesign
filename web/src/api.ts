const BASE_URL = 'http://localhost:8080';

export interface Asset {
  file: string;
  filename: string;
  name: string;
  type: string;
  width: number;
  height: number;
  size_bytes: number;
  is_shared: boolean;
  prompt: string;
  model: string;
  style: string;
  generated_at: string;
  relationships: Record<string, any>;
  image_url: string;
}

export const api = {
  async getAssets(type?: string, search?: string, sort?: string) {
    const params = new URLSearchParams();
    if (type) params.set('type', type);
    if (search) params.set('search', search);
    if (sort) params.set('sort', sort);
    const res = await fetch(`${BASE_URL}/api/assets?${params}`);
    return res.json();
  },

  async deleteAsset(name: string) {
    const res = await fetch(`${BASE_URL}/api/assets/${name}`, { method: 'DELETE' });
    return res.json();
  },

  async updateAsset(name: string, updates: { name?: string; type?: string }) {
    const res = await fetch(`${BASE_URL}/api/assets/${name}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return res.json();
  },

  async getVersions(name: string) {
    const res = await fetch(`${BASE_URL}/api/assets/${name}/versions`);
    return res.json();
  },

  async rollback(name: string, version: number) {
    const res = await fetch(`${BASE_URL}/api/assets/${name}/versions/rollback?version=${version}`, { method: 'POST' });
    return res.json();
  },

  async generate(description: string, type: string, style?: string) {
    const res = await fetch(`${BASE_URL}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description, type, style }),
    });
    return res.json();
  },

  async refine(assetName: string, refineType: string, note: string) {
    const res = await fetch(`${BASE_URL}/api/refine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ asset_name: assetName, refine_type: refineType, note }),
    });
    return res.json();
  },

  async exportAssets(engine: string) {
    const res = await fetch(`${BASE_URL}/api/export`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ engine }),
    });
    return res.json();
  },

  async packAtlas(inputType: string) {
    const res = await fetch(`${BASE_URL}/api/atlas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_type: inputType }),
    });
    return res.json();
  },

  async getProgress() {
    const res = await fetch(`${BASE_URL}/api/progress`);
    return res.json();
  },

  async analyzeDesign(file: File) {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${BASE_URL}/api/analyze`, { method: 'POST', body: form });
    return res.json();
  },

  async extractAssets(designId?: string) {
    const res = await fetch(`${BASE_URL}/api/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(designId ? { design_id: designId } : {}),
    });
    return res.json();
  },

  getImageUrl(asset: Asset) {
    return `${BASE_URL}${asset.image_url}`;
  },
};
