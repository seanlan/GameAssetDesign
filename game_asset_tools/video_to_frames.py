"""Video frame extraction with optional deduplication."""

import os


def is_opencv_available() -> bool:
    try:
        import cv2
        return True
    except ImportError:
        return False


def extract_frames(video_path, output_dir, fps=8, dedup=False, dedup_threshold=0.95):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    if not is_opencv_available():
        raise RuntimeError("opencv-python-headless is not installed.")

    import cv2
    import numpy as np

    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 30

    frame_interval = max(1, int(video_fps / fps))
    frame_idx = 0
    saved_count = 0
    prev_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0:
            save = True
            if dedup and prev_frame is not None:
                similarity = _frame_similarity(prev_frame, frame)
                if similarity >= dedup_threshold:
                    save = False
            if save:
                out_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
                cv2.imwrite(out_path, frame)
                prev_frame = frame.copy()
                saved_count += 1
        frame_idx += 1

    cap.release()
    return saved_count


def _frame_similarity(frame1, frame2):
    import cv2
    import numpy as np
    g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY).astype(np.float32)
    result = cv2.matchTemplate(g1, g2, cv2.TM_CCORR_NORMED)
    return float(result[0][0])
