"""文件路径处理、用户确认、临时文件清理"""
import os
import sys
from pathlib import Path

from ..config import Config

def resolve_input_path(input_arg: str) -> str:
    """
    解析输入路径：如果不存在，尝试 Video/ 目录下查找；
    若仍找不到且是交互式终端，则提示用户输入；
    若是非交互环境（如测试），直接抛出 FileNotFoundError。
    """
    input_path = Path(input_arg)
    if input_path.exists():
        return str(input_path)
    
    # 尝试 Video 目录
    video_dir = Config.get_video_dir()
    alt_path = video_dir / input_path.name
    if alt_path.exists():
        print(f"[OK] 自动在 Video 文件夹找到: {alt_path}")
        return str(alt_path)
    
    # 尝试 Video/Test 目录（仅用于测试视频）
    test_video_dir = Config.get_test_video_dir()
    test_alt_path = test_video_dir / input_path.name
    if test_alt_path.exists():
        print(f"[OK] 自动在 Video/Test 文件夹找到: {test_alt_path}")
        return str(test_alt_path)
    
    # 非交互环境（pytest 等）直接报错
    if not sys.stdin.isatty():
        raise FileNotFoundError(f"找不到文件: {input_arg} (尝试过: {input_path}, {alt_path}, {test_alt_path})")
    
    # 交互式终端，提示用户输入
    print(f"[ERROR] 找不到文件: {input_arg}")
    print(f"   尝试路径: {input_arg} 和 {alt_path}")
    while True:
        user_input = input("请手动输入正确的视频文件路径（输入 q 退出）: ").strip()
        if user_input.lower() in ('q', 'exit', 'quit'):
            print("用户取消操作。")
            sys.exit(0)
        if Path(user_input).exists():
            return user_input
        print(f"文件不存在: {user_input}")

def confirm_overwrite(output_path: str, force: bool) -> bool:
    if force:
        return True
    if os.path.exists(output_path):
        while True:
            choice = input(f"输出文件 '{output_path}' 已存在。覆盖？(y/n): ").strip().lower()
            if choice in ('y', 'yes'):
                return True
            elif choice in ('n', 'no'):
                return False
    return True

def cleanup_temp_files(base_output: str):
    temp_video = base_output + ".temp_video.mp4"
    temp_audio = base_output + ".temp_audio.wav"
    for f in [temp_video, temp_audio]:
        if os.path.exists(f):
            os.remove(f)