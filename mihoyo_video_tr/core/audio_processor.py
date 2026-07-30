"""音频处理（提取、交换、合并）"""
import subprocess
import tempfile
import os
from pathlib import Path

from ..exceptions import FFmpegError
from ..utils.audio_utils import has_audio_stream
from ..utils.video_utils import get_video_info


class AudioProcessor:
    @staticmethod
    def extract_audio(video_path: str, output_wav: str):
        """提取音频为 WAV"""
        cmd = ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', output_wav, '-y']
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise FFmpegError(f"音频提取失败: {e.stderr.decode()}")
    
    @staticmethod
    def swap_audio_segments(video_path: str, group_size: int,
                           swap1_start: int, swap2_start: int, swap_len: int,
                           output_audio: str):
        """
        交换音频片段（基于帧的切割和重组）
        使用 pydub 进行精确切割
        """
        from pydub import AudioSegment
        
        # 获取帧率
        _, _, fps, _, _ = get_video_info(video_path)
        frame_duration_ms = 1000.0 / fps
        
        # 提取原音频
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            original_wav = tmp.name
        AudioProcessor.extract_audio(video_path, original_wav)
        
        audio = AudioSegment.from_wav(original_wav)
        group_duration_ms = group_size * frame_duration_ms
        
        _, _, _, total_frames, _ = get_video_info(video_path)
        full_groups = total_frames // group_size
        new_audio = AudioSegment.empty()
        
        for g in range(full_groups):
            start_ms = g * group_duration_ms
            group_audio = audio[start_ms:start_ms + group_duration_ms]
            # 切割成单帧块
            blocks = []
            for i in range(group_size):
                block_start = i * frame_duration_ms
                block = group_audio[block_start:block_start + frame_duration_ms]
                # 补足长度
                if len(block) < frame_duration_ms - 1:
                    block = block + AudioSegment.silent(duration=frame_duration_ms - len(block))
                blocks.append(block)
            # 交换
            a = slice(swap1_start, swap1_start + swap_len)
            b = slice(swap2_start, swap2_start + swap_len)
            blocks[a], blocks[b] = blocks[b], blocks[a]
            for block in blocks:
                new_audio += block
        
        # 剩余不足一组的音频直接追加
        remaining_frames = total_frames % group_size
        if remaining_frames > 0:
            remaining_start_ms = full_groups * group_duration_ms
            remaining_audio = audio[remaining_start_ms:]
            new_audio += remaining_audio
        
        new_audio.export(output_audio, format="wav")
        os.remove(original_wav)
    
    @staticmethod
    def merge_audio_video(video_file: str, audio_file: str, output_file: str):
        """合并音视频（复制视频流，转码音频为AAC）"""
        cmd = [
            'ffmpeg', '-i', video_file, '-i', audio_file,
            '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', '-y', output_file
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise FFmpegError(f"合并失败: {e.stderr.decode()}")