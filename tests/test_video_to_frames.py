import os
import pytest
from game_asset_tools.video_to_frames import extract_frames, is_opencv_available


def test_is_opencv_available():
    result = is_opencv_available()
    assert isinstance(result, bool)


@pytest.fixture
def sample_video(tmp_dir):
    if not is_opencv_available():
        pytest.skip("opencv not installed")
    import cv2
    import numpy as np
    path = os.path.join(tmp_dir, "test.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, 10, (64, 64))
    for i in range(30):
        frame = np.full((64, 64, 3), fill_value=(i * 8) % 256, dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return path


def test_extract_frames_basic(sample_video, tmp_dir):
    out_dir = os.path.join(tmp_dir, "frames")
    count = extract_frames(sample_video, out_dir, fps=5)
    assert count > 0
    files = os.listdir(out_dir)
    assert len(files) == count
    assert all(f.endswith(".png") for f in files)


def test_extract_frames_with_dedup(sample_video, tmp_dir):
    out_dir = os.path.join(tmp_dir, "frames")
    count = extract_frames(sample_video, out_dir, fps=10, dedup=True, dedup_threshold=0.99)
    assert count > 0


def test_extract_frames_missing_file(tmp_dir):
    with pytest.raises(FileNotFoundError):
        extract_frames("/nonexistent/video.mp4", tmp_dir)
