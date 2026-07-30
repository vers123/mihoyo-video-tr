"""视频帧处理（交换核心）"""
import os
import cv2
import numpy as np
from typing import List, Iterator
from pathlib import Path

from ..exceptions import VideoOpenError
from ..utils.performance import estimate_memory_feasible


class VideoProcessor:
    def __init__(self, input_path: str, output_path: str, group_size: int,
                 swap1_start: int, swap2_start: int, swap_len: int,
                 mode: str = "auto"):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.group_size = group_size
        self.swap1_start = swap1_start
        self.swap2_start = swap2_start
        self.swap_len = swap_len
        self.mode = mode
        
        # 延迟加载，初始化时不打开视频
        self.fps = None
        self.width = None
        self.height = None
        self.total_frames = None
        
        self._validate_swap_params()
    
    def _load_video_info(self):
        """实际打开视频读取信息（延迟调用）"""
        cap = cv2.VideoCapture(str(self.input_path))
        if not cap.isOpened():
            raise VideoOpenError(f"无法打开视频: {self.input_path}")
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
    
    def _validate_swap_params(self):
        if self.swap1_start + self.swap_len > self.group_size:
            raise ValueError(f"swap1_start+swap_len 超出 group_size")
        if self.swap2_start + self.swap_len > self.group_size:
            raise ValueError(f"swap2_start+swap_len 超出 group_size")
        if self.swap1_start == self.swap2_start and self.swap_len > 0:
            raise ValueError("两个交换区域起始相同，无效果")
    
    def _swap_group(self, group: List[np.ndarray]) -> List[np.ndarray]:
        a = slice(self.swap1_start, self.swap1_start + self.swap_len)
        b = slice(self.swap2_start, self.swap2_start + self.swap_len)
        group[a], group[b] = group[b], group[a]
        return group
    
    def _frame_iterator(self) -> Iterator[np.ndarray]:
        cap = cv2.VideoCapture(str(self.input_path))
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            yield frame
        cap.release()
    
    def _create_writer(self):
        os.makedirs(self.output_path.parent, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(str(self.output_path), fourcc, self.fps,
                               (self.width, self.height))
    
    def _memory_feasible(self) -> bool:
        return estimate_memory_feasible(self.width, self.height, self.total_frames)
    
    def process(self):
        """处理入口：先加载信息，再选择模式"""
        self._load_video_info()
        
        if self.mode == "memory" or (self.mode == "auto" and self._memory_feasible()):
            self._process_memory()
        else:
            self._process_streaming()
    
    def _process_memory(self):
        print("使用内存模式处理视频...")
        frames = list(self._frame_iterator())
        total = len(frames)
        full_groups = total // self.group_size
        for i in range(0, full_groups * self.group_size, self.group_size):
            frames[i:i+self.group_size] = self._swap_group(frames[i:i+self.group_size])
        writer = self._create_writer()
        for f in frames:
            writer.write(f)
        writer.release()
    
    def _process_streaming(self):
        print("使用流式模式处理视频...")
        writer = self._create_writer()
        buffer = []
        for frame in self._frame_iterator():
            buffer.append(frame)
            if len(buffer) == self.group_size:
                buffer = self._swap_group(buffer)
                for f in buffer:
                    writer.write(f)
                buffer = []
        for f in buffer:
            writer.write(f)
        writer.release()