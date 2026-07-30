#!/usr/bin/env python3
"""一键运行所有测试（单元测试 + 集成测试），并生成覆盖率报告"""
import subprocess
import sys
import os

# 修复 Windows 控制台编码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_test_deps():
    try:
        import pytest
    except ImportError:
        print("pytest 未安装，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements-dev.txt'], check=True)

def main():
    print("=== mihoyo-video-tr 一键本地测试 ===")
    print("\n1. 检查环境...")
    if not check_ffmpeg():
        print("[ERROR] FFmpeg 未找到，请先安装 FFmpeg 并添加到 PATH")
        sys.exit(1)
    print("[OK] FFmpeg 可用")
    
    install_test_deps()
    
    try:
        import mihoyo_video_tr
        print(f"[OK] 项目已安装 (版本 {mihoyo_video_tr.__version__})")
    except ImportError:
        print("[WARN] 项目未以开发模式安装，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
    
    print("\n2. 运行测试 (包含单元测试和集成测试)...")
    result = subprocess.run([
        'pytest', 'tests/',
        '-v', '--cov=mihoyo_video_tr', '--cov-report=term', '--cov-report=html'
    ])
    
    if result.returncode == 0:
        print("\n[OK] 所有测试通过！")
        print("详细覆盖率报告已生成: htmlcov/index.html")
    else:
        print("\n[ERROR] 部分测试失败，请检查日志。")
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()