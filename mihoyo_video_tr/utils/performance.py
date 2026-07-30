"""性能估算工具"""
from .video_utils import get_video_info

def format_bytes(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def estimate_memory_feasible(width: int, height: int, total_frames: int,
                            limit_bytes: int = 1024**3) -> bool:
    """估算内存占用是否小于限制（默认1GB）"""
    bytes_per_frame = width * height * 3
    total_memory = bytes_per_frame * total_frames
    print(f"全部帧内存占用: {format_bytes(total_memory)}")
    return total_memory <= limit_bytes

def estimate_performance(total_frames: int, fps: float, fourcc: str):
    """显示性能估算信息"""
    duration_sec = total_frames / fps
    if fourcc.upper() == "AV01":
        speed_factor = 4.0
    elif fourcc.upper() in ["HEVC", "H265"]:
        speed_factor = 2.5
    else:
        speed_factor = 1.5
    estimated_sec = duration_sec * speed_factor
    print(f"视频时长: {duration_sec:.1f} 秒 ({duration_sec/60:.1f} 分钟)")
    print(f"预计处理耗时（流式模式）: {estimated_sec:.1f} 秒 ({estimated_sec/60:.1f} 分钟)")
    return estimated_sec, duration_sec