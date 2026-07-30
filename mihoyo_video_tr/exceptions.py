"""自定义异常"""

class MihoyoError(Exception):
    """基础异常"""
    pass

class VideoOpenError(MihoyoError):
    """无法打开视频文件"""
    pass

class BPMDetectionError(MihoyoError):
    """BPM检测失败"""
    pass

class SwapParameterError(MihoyoError):
    """交换参数无效"""
    pass

class FFmpegError(MihoyoError):
    """FFmpeg执行错误"""
    pass