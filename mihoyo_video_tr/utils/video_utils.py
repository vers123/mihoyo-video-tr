"""视频信息获取"""
import cv2

def get_video_info(video_path: str):
    """返回 (width, height, fps, total_frames, fourcc_str)"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件: {video_path}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    codec = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc_str = "".join(chr((codec >> 8 * i) & 0xFF) for i in range(4)) if codec else "未知"
    cap.release()
    return width, height, fps, total_frames, fourcc_str