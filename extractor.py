import os
import cv2
import numpy as np
from typing import Callable, Optional

def save_image_utf8(filepath: str, image: np.ndarray, quality: int = 95) -> bool:
    ext = os.path.splitext(filepath)[1].lower()
    if not ext:
        ext = '.jpg'
        filepath += ext
        
    if ext in ['.jpg', '.jpeg']:
        params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    elif ext == '.png':
        params = [int(cv2.IMWRITE_PNG_COMPRESSION), 3]
    else:
        params = []
        
    success, encoded_img = cv2.imencode(ext, image, params)
    if success:
        with open(filepath, 'wb') as f:
            encoded_img.tofile(f)
        return True
    return False

def get_video_info(video_path: str):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video dosyası bulunamadı: {video_path}")
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Video dosyası açılamadı: {video_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = 30.0
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames / fps if fps > 0 else 0
    cap.release()
    
    return {
        "fps": fps,
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_sec": duration_sec
    }

def extract_frames(
    video_path: str,
    output_dir: str,
    mode: str = "seconds",  # 'seconds', 'every_frame', 'interval_frames', 'total_count'
    interval_value: float = 1.0,
    start_sec: float = 0.0,
    end_sec: Optional[float] = None,
    image_format: str = "jpg",
    quality: int = 95,
    progress_callback: Optional[Callable[[int, int, str], bool]] = None
) -> int:
    info = get_video_info(video_path)
    fps = info["fps"]
    total_frames = info["total_frames"]
    duration = info["duration_sec"]
    
    if end_sec is None or end_sec <= 0 or end_sec > duration:
        end_sec = duration
    if start_sec < 0:
        start_sec = 0.0
        
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)
    if end_frame > total_frames:
        end_frame = total_frames
        
    target_frame_indices = []
    
    if mode == "every_frame":
        target_frame_indices = list(range(start_frame, end_frame))
    elif mode == "seconds":
        step_frames = max(1, int(interval_value * fps))
        target_frame_indices = list(range(start_frame, end_frame, step_frames))
    elif mode == "interval_frames":
        step_frames = max(1, int(interval_value))
        target_frame_indices = list(range(start_frame, end_frame, step_frames))
    elif mode == "total_count":
        count = max(1, int(interval_value))
        if count == 1:
            target_frame_indices = [start_frame]
        else:
            target_frame_indices = [int(x) for x in np.linspace(start_frame, end_frame - 1, count)]
            target_frame_indices = sorted(list(set(target_frame_indices)))
    else:
        raise ValueError(f"Bilinmeyen mod: {mode}")

    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Video açılamadı: {video_path}")
        
    total_to_extract = len(target_frame_indices)
    saved_count = 0
    
    video_stem = os.path.splitext(os.path.basename(video_path))[0]
    padding = max(4, len(str(total_to_extract)))
    target_set = set(target_frame_indices)
    max_target = max(target_frame_indices) if target_frame_indices else 0
    
    current_frame = 0
    if start_frame > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        
    while cap.isOpened() and current_frame <= max_target:
        ret, frame = cap.read()
        if not ret:
            break
            
        if current_frame in target_set:
            timestamp_sec = current_frame / fps
            mins = int(timestamp_sec // 60)
            secs = int(timestamp_sec % 60)
            
            saved_count += 1
            filename = f"{video_stem}_kare_{saved_count:0{padding}d}_{mins:02d}m{secs:02d}s.{image_format.lower()}"
            out_path = os.path.join(output_dir, filename)
            
            save_image_utf8(out_path, frame, quality=quality)
            
            if progress_callback:
                should_continue = progress_callback(saved_count, total_to_extract, filename)
                if should_continue is False:
                    break
                    
        current_frame += 1
        
        if target_frame_indices:
            remaining = [t for t in target_frame_indices if t > current_frame]
            if remaining:
                next_target = remaining[0]
                if next_target - current_frame > 45:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, next_target)
                    current_frame = next_target
                    
    cap.release()
    return saved_count
