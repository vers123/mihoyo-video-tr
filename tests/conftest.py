"""pytest 配置和共享 fixture"""
import pytest
import subprocess
import os
from pathlib import Path

from mihoyo_video_tr.config import Config

@pytest.fixture(scope="session")
def test_video_path():
    """生成一个带音频的测试视频（5秒，30fps，320x240）到 Video/Test/ 目录"""
    test_dir = Config.get_test_video_dir()
    test_dir.mkdir(parents=True, exist_ok=True)
    output = test_dir / "test_with_audio.mp4"
    
    if output.exists():
        return str(output)
    
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=30',
        '-f', 'lavfi', '-i', 'sine=frequency=440:duration=5',
        '-c:v', 'libx264', '-c:a', 'aac', '-y', str(output)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(output)

@pytest.fixture(scope="session")
def test_video_no_audio_path():
    """生成一个无音频的测试视频到 Video/Test/ 目录"""
    test_dir = Config.get_test_video_dir()
    test_dir.mkdir(parents=True, exist_ok=True)
    output = test_dir / "test_no_audio.mp4"
    
    if output.exists():
        return str(output)
    
    cmd = [
        'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=5:size=320x240:rate=30',
        '-c:v', 'libx264', '-an', '-y', str(output)
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(output)

@pytest.fixture
def output_dir():
    """临时输出目录 Output_test/"""
    output_dir = Config.get_test_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir