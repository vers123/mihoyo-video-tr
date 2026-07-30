"""音频检测与BPM检测（注意：--beat-pair 要求手动提供 --bpm，此函数仅用于 --auto-bpm）"""
import subprocess
import tempfile
import os

def has_audio_stream(video_path: str) -> bool:
    """检查视频是否包含音频流"""
    cmd = ['ffmpeg', '-i', video_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                encoding='utf-8', errors='ignore')
        return 'Audio:' in result.stderr
    except:
        return False

def detect_bpm(video_path: str):
    """提取音频并返回BPM，失败返回None；确保返回Python原生int"""
    try:
        import librosa
    except ImportError:
        print("[WARN] 未安装 librosa，无法自动检测 BPM。请运行: pip install librosa")
        return None

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_file = tmp.name
    try:
        cmd = ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', audio_file, '-y']
        subprocess.run(cmd, check=True, capture_output=True)
        y, sr = librosa.load(audio_file, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        if hasattr(tempo, 'item'):
            return int(tempo.item())
        return int(tempo)
    except Exception as e:
        print(f"BPM检测失败: {e}")
        return None
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)