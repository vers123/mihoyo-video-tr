# Video Frame & Audio Swapper

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-V1.0.0-green)

| Language / 语言 | [English](README.md) | [中文](README_zh.md) |

> **Disclaimer**: This project is for learning and technical research only. It does not contain or distribute any game assets or data, and is not affiliated with miHoYo / HoYoverse or its affiliates.

A video/audio frame swapping tool based on OpenCV and FFmpeg.  
It can group video frames into fixed-size groups, swap **two specified ranges** of frames within each group, and **swap the corresponding audio segments** synchronously, creating creative effects like "glitch art" or rhythm displacement.

## ✨ Features

- **Flexible frame swapping rules**  
  Customizable group size (`--group-size`), starting positions of two swap regions (`--swap1-start`, `--swap2-start`), and swap length (`--swap-len`). Supports arbitrary frame swaps.

- **Beat‑aware automatic swapping**  
  Use `--beat-pair 1-3` or `--beat-pair 2-4` together with `--bpm`. The program automatically calculates the frame ranges of the corresponding beats, sets the group size and swap parameters. If the four beats have different lengths, it prompts the user to manually enter the parameters.  
  **Note: When using `--beat-pair`, you must manually specify `--bpm`; the program does not auto‑detect BPM.**

- **Audio‑video synchronization**  
  Audio is sliced into per‑frame segments (duration = `1/fps` seconds), swapped according to the same rules, and re‑combined, ensuring final audio‑video sync.

- **Two processing modes**  
  - **Memory mode**: loads all frames into memory at once, suitable for short videos.  
  - **Streaming mode**: processes group by group, low memory usage, suitable for long or high‑resolution videos.  
  The program automatically selects the appropriate mode based on video size, or you can manually specify it.

- **Automatic BPM detection (non‑beat‑pair scenario)**  
  Use `--auto-bpm` to automatically detect the audio BPM and adjust the group size (for custom swap rules, not used with `--beat-pair`).

- **Performance estimation**  
  Before processing, it shows video information, memory usage estimation, and estimated processing time to help you decide whether to use streaming mode.

- **FFmpeg dependency**  
  Heavy lifting (encoding/decoding, format conversion) is delegated to FFmpeg for speed and quality.

## 📦 Installation

### 1. System dependency: FFmpeg

- **Windows**: Download the [FFmpeg executable](https://ffmpeg.org/download.html) and add it to `PATH`.
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` (Debian/Ubuntu)

### 2. Python dependencies

```bash
git clone https://github.com/vers123/mihoyo-video-tr.git

cd mihoyo-video-tr
```

```bash
python -m venv .venv
```

```bash
# macOS / Linux
source .venv/bin/activate

# Windows（CMD / PowerShell）
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

Or install the project directly:

```bash
pip install -e .
```

## 🚀 Quick Start

### Basic usage (default rules)

Default: groups of 12 frames, swap frames 0‑2 with frames 6‑8 within each group:

```bash
mihoyo-video-tr -i input.mp4 -o output.mp4
```

### Custom swap rules

Example: groups of 32 frames, swap frames 0‑7 (8 frames) with frames 16‑23 (8 frames):

```bash
mihoyo-video-tr -i input.mp4 -o output.mp4 \
    --group-size 32 --swap1-start 0 --swap2-start 16 --swap-len 8
```

### Beat‑based auto swap

**Note: When using `--beat-pair`, you must also specify `--bpm`.**

Swap beats 1 and 3 (BPM=120), output to `Output_1to3/original_filename_swapped.mp4`:

```bash
mihoyo-video-tr -i music_video.mp4 --beat-pair 1-3 --bpm 120
```

Swap beats 2 and 4 (BPM=128):

```bash
mihoyo-video-tr -i music_video.mp4 --beat-pair 2-4 --bpm 128
```

**Interactive manual parameters**: If the program detects inconsistent lengths among the four beats (common with non‑integer frame‑rate/BPM combinations), it displays the frame ranges for each beat and prompts you to manually enter `group-size`, `swap1-start`, `swap2-start`, and `swap-len`. You can adjust based on the suggested values and the program will continue.

### Auto‑detect BPM and adjust group size (non‑beat‑pair)

```bash
mihoyo-video-tr -i music_video.mp4 --auto-bpm
```

This command detects the audio BPM, automatically computes a reasonable `group-size`, and then processes using the default or custom swap rules. `--auto-bpm` cannot be used together with `--beat-pair`.

### Show video information only (no processing)

```bash
mihoyo-video-tr -i input.mp4 --info
```

### Force overwrite output file

```bash
mihoyo-video-tr -i input.mp4 -o output.mp4 --force
```

### Standalone beat frame calculator

```bash
python scripts/calc_beat_frames.py
```

## 📋 Command Line Arguments

| Argument | Type | Default | Description |
| ----- | ----- | ----- | ----- |
| `-i`, `--input` | str | **required** | Input video file (automatically looks in `Video/` folder) |
| `-o`, `--output` | str | `output_swapped.mp4` | Output video file path |
| `--info` | flag | - | Show video information only, do not process |
| `--mode` | str | `auto` | Processing mode: `auto` / `memory` / `streaming` |
| `--no-swap` | flag | - | No swapping (just copy video, no audio processing) |
| `--force` | flag | - | Force overwrite output file |
| `--group-size` | int | `12` | Number of frames per group (must be ≥ end of swap regions) |
| `--swap1-start` | int | `0` | Start frame index of first swap region (0‑based) |
| `--swap2-start` | int | `6` | Start frame index of second swap region (0‑based) |
| `--swap-len` | int | `3` | Length of swap region (number of frames) |
| `--auto-bpm` | flag | - | Auto‑detect BPM and override `--group-size` (not for use with `--beat-pair`) |
| `--beat-pair` | {1-3,2-4} | - | Beat pair to swap (must also specify `--bpm`) |
| `--bpm` | float | - | Manually specify BPM (required with `--beat-pair`) |

## ⚙️ How It Works

1. **Get video information** (resolution, frame rate, total frames, codec)
2. **Process video frames in groups**:  
   - Streaming mode: buffer `group_size` frames → swap specified regions → write output  
   - Memory mode: load all frames at once → swap within each group → write output
3. **Process audio synchronously**:  
   - Extract full audio (WAV) using FFmpeg  
   - Slice into per‑frame segments (duration = `1000/fps` milliseconds)  
   - Reorder segments according to the same swap rules  
   - Merge new audio with the processed video using FFmpeg
4. **Output final MP4 file** (H.264 video + AAC audio)

## 📝 Notes

- **Swap regions must not exceed group size**, otherwise the program errors.  
- **Swap regions may overlap**, but a warning will be given; results may be unexpected.  
- **Audio slicing accuracy**: FFmpeg slicing may have tiny deviations (<1ms), imperceptible.  
- **Long videos**: Use streaming mode (`--mode streaming`) to avoid memory issues.  
- **Temporary files**: `.temp_video.mp4` and `.temp_audio.wav` are generated in the same directory as the output file and deleted after processing.  
- **Encoding quality**: Output video uses `libx264` with FFmpeg’s default `crf` (≈23). For higher quality, modify the script’s encoding parameters.  
- **Auto output directory for beat‑pair**: When `--beat-pair` is used and `-o` is not specified, the output file is automatically placed in `Output_1to3/` or `Output_2to4/` with the name `original_filename_swapped.mp4`.  
- **BPM must be manually provided**: When using `--beat-pair`, you must also specify `--bpm` (e.g., `--bpm 120`). The program does not auto‑detect BPM for beat‑pair swapping.

## 🛠️ FAQ

### 1. “FFmpeg not found”

Make sure FFmpeg is installed and added to `PATH`. You can test by running `ffmpeg -version` in your terminal.

### 2. Memory explosion when processing long videos

Use `--mode streaming` to force streaming mode, or let the program automatically choose (default `auto` selects based on memory estimation).

### 3. Audio out of sync

Check if the input video has a constant frame rate (variable frame rate may cause inaccurate slicing). Use FFmpeg to convert to constant frame rate:

```bash
ffmpeg -i input.mp4 -vsync cfr -r 30 output_cfr.mp4
```

### 4. Corrupted frames after swapping

This may happen if you swapped regions that contain dependent frames (e.g., B/P frames). Try `--no-swap` to test if copying works. If it does, the swap logic itself is fine; adjust the swap regions to avoid dense key‑frame areas.

### 5. “Inconsistent beat lengths” when using `--beat-pair`

This occurs when the given BPM and video frame rate do not produce integer frame counts per beat. The program will display the actual frame ranges for each beat and guide you to manually input swap parameters. You can adjust the group size and swap length accordingly.

### 6. Why can’t `--beat-pair` auto‑detect BPM?

Beat‑based swapping requires an exact BPM value. Auto‑detection may introduce errors due to audio quality or ambiguous rhythm, leading to incorrect frame range calculations. Therefore, you must manually provide BPM via `--bpm`. If you need auto‑detection for adjusting group size (non‑beat‑pair scenario), you can use `--auto-bpm`.

## 📄 License

This project is open‑sourced under the MIT License.  
Third‑party libraries used (OpenCV, FFmpeg, pydub) are subject to their own licenses.

## 🙏 Acknowledgements

- [FFmpeg](https://ffmpeg.org/) – core audio/video processing
- [OpenCV](https://opencv.org/) – video frame reading/writing
- [pydub](https://github.com/jiaaro/pydub) – audio slicing and concatenation
