import os
import cv2
import numpy as np
from typing import Callable, Optional, Tuple

def save_image_utf8(filepath: str, image: np.ndarray, quality: int = 95) -> bool:
    """
    Saves an image to a path that may contain non-ASCII (Turkish) characters.
    """
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
    """
    Returns metadata about the video file.
    """
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

def apply_zoom_crop(
    frame: np.ndarray,
    zoom_factor: float = 1.0,
    zoom_position: str = "center", # 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    crop_box: Optional[Tuple[int, int, int, int]] = None # (x, y, w, h)
) -> np.ndarray:
    """
    Applies zoom / crop to a video frame.
    """
    h, w = frame.shape[:2]

    # Custom crop box
    if crop_box is not None:
        cx, cy, cw, ch = crop_box
        cx = max(0, min(cx, w - 1))
        cy = max(0, min(cy, h - 1))
        cw = max(1, min(cw, w - cx))
        ch = max(1, min(ch, h - cy))
        return frame[cy:cy+ch, cx:cx+cw]

    # Zoom factor crop
    if zoom_factor > 1.001:
        new_w = int(w / zoom_factor)
        new_h = int(h / zoom_factor)
        
        if zoom_position == "top-left":
            x1, y1 = 0, 0
        elif zoom_position == "top-right":
            x1, y1 = w - new_w, 0
        elif zoom_position == "bottom-left":
            x1, y1 = 0, h - new_h
        elif zoom_position == "bottom-right":
            x1, y1 = w - new_w, h - new_h
        else: # center
            x1 = (w - new_w) // 2
            y1 = (h - new_h) // 2

        x2 = min(w, x1 + new_w)
        y2 = min(h, y1 + new_h)
        cropped = frame[y1:y2, x1:x2]
        # Resize back to original dimensions for high quality zoom preview/export
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)

    return frame

def extract_frames(
    video_path: str,
    output_dir: str,
    mode: str = "seconds",  # 'seconds', 'every_frame', 'interval_frames', 'total_count'
    interval_value: float = 1.0,
    start_sec: float = 0.0,
    end_sec: Optional[float] = None,
    image_format: str = "jpg",
    quality: int = 95,
    zoom_factor: float = 1.0,
    zoom_position: str = "center",
    crop_box: Optional[Tuple[int, int, int, int]] = None,
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
    if start_sec >= end_sec:
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
    
    padding = max(5, len(str(total_to_extract)))
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
            millis = int((timestamp_sec - int(timestamp_sec)) * 1000)
            
            # Apply Zoom / Crop if requested
            processed_frame = apply_zoom_crop(frame, zoom_factor, zoom_position, crop_box)
            
            saved_count += 1
            filename = f"kare_{saved_count:0{padding}d}_{mins:02d}m{secs:02d}s_{millis:03d}ms.{image_format.lower()}"
            out_path = os.path.join(output_dir, filename)
            
            save_image_utf8(out_path, processed_frame, quality=quality)
            
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
