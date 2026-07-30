"""集成测试：完整运行 CLI 并验证输出"""
import subprocess
from pathlib import Path

def test_cli_basic_swap(test_video_path, output_dir):
    output = output_dir / "basic_swap.mp4"
    cmd = ["mihoyo-video-tr", "-i", test_video_path, "-o", str(output), "--force"]
    subprocess.run(cmd, check=True)
    assert output.exists()
    assert output.stat().st_size > 0

def test_cli_beat_pair_auto(test_video_path, output_dir):
    output = output_dir / "beat_auto.mp4"
    cmd = ["mihoyo-video-tr", "-i", test_video_path, "-o", str(output),
           "--beat-pair", "1-3", "--bpm", "120", "--force"]
    subprocess.run(cmd, check=True)
    assert output.exists()

def test_cli_no_audio(test_video_no_audio_path, output_dir):
    output = output_dir / "no_audio_out.mp4"
    cmd = ["mihoyo-video-tr", "-i", test_video_no_audio_path, "-o", str(output), "--force"]
    subprocess.run(cmd, check=True)
    assert output.exists()

def test_cli_info(test_video_path):
    result = subprocess.run(
        ["mihoyo-video-tr", "-i", test_video_path, "--info"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "分辨率" in result.stdout

def test_cli_custom_params(test_video_path, output_dir):
    output = output_dir / "custom.mp4"
    cmd = [
        "mihoyo-video-tr", "-i", test_video_path, "-o", str(output),
        "--group-size", "20", "--swap1-start", "5", "--swap2-start", "12",
        "--swap-len", "4", "--force"
    ]
    subprocess.run(cmd, check=True)
    assert output.exists()