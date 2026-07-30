"""节拍帧范围计算"""
import math
from typing import Tuple, Dict

class BeatCalculator:
    @staticmethod
    def calculate_beat_frames(fps: float, bpm: float, beat_num: int) -> Tuple[int, int]:
        """
        返回第 beat_num 拍（1-indexed）的 (start_frame, end_frame)
        """
        T = 60.0 / bpm
        start_time = (beat_num - 1) * T
        end_time = beat_num * T
        start_frame = math.floor(start_time * fps)
        end_frame = math.floor(end_time * fps) - 1
        if end_frame < start_frame:
            end_frame = start_frame
        return start_frame, end_frame
    
    @classmethod
    def get_all_beats(cls, fps: float, bpm: float) -> Dict[int, Tuple[int, int]]:
        """返回 {1: (s,e), 2: (s,e), ...}"""
        return {i: cls.calculate_beat_frames(fps, bpm, i) for i in range(1, 5)}
    
    @classmethod
    def get_beat_lengths(cls, fps: float, bpm: float) -> Dict[int, int]:
        """返回 {1: length, 2: length, ...}"""
        beats = cls.get_all_beats(fps, bpm)
        return {i: end - start + 1 for i, (start, end) in beats.items()}
    
    @classmethod
    def are_all_beats_equal_length(cls, fps: float, bpm: float) -> bool:
        lengths = list(cls.get_beat_lengths(fps, bpm).values())
        return len(set(lengths)) == 1