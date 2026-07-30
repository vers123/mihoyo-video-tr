"""全局配置常量"""
from pathlib import Path

class Config:
    DEFAULT_OUTPUT = "output_swapped.mp4"
    DEFAULT_GROUP_SIZE = 12
    DEFAULT_SWAP1_START = 0
    DEFAULT_SWAP2_START = 6
    DEFAULT_SWAP_LEN = 3
    
    # 目录名称
    VIDEO_INPUT_DIR = "Video"
    TEST_VIDEO_DIR = "Video/Test"
    OUTPUT_DIRS = {
        "1-3": "Output_1to3",
        "2-4": "Output_2to4"
    }
    OUTPUT_TEST_DIR = "Output_test"
    
    # 性能阈值 (字节)
    MEMORY_LIMIT_BYTES = 1024 * 1024 * 1024  # 1GB
    
    @classmethod
    def get_video_dir(cls) -> Path:
        return Path.cwd() / cls.VIDEO_INPUT_DIR
    
    @classmethod
    def get_test_video_dir(cls) -> Path:
        return Path.cwd() / cls.TEST_VIDEO_DIR
    
    @classmethod
    def get_output_dir(cls, beat_pair: str) -> Path:
        return Path.cwd() / cls.OUTPUT_DIRS.get(beat_pair, ".")
    
    @classmethod
    def get_test_output_dir(cls) -> Path:
        return Path.cwd() / cls.OUTPUT_TEST_DIR