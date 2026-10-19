# Video Frame & Audio Swapper

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-V1.0.0-green)

| Language / 语言 | [English](README.md) | [中文](README_zh.md) |

> **免责声明**：本项目仅用于学习与技术研究，不包含、不分发任何游戏资源或数据；与米哈游（miHoYo / HoYoverse）及其关联公司无任何关系。

基于 OpenCV 和 FFmpeg 的视频/音频同步帧交换工具。  
它能够将视频按照固定帧数分组，在每组内交换**两个指定范围**的视频帧，并**同步交换对应的音频片段**，从而产生类似“故障艺术”或节奏错位的创意效果。

## ✨ 功能特点

- **灵活的帧交换规则**  
  可自定义分组大小（`--group-size`）、两个交换区域的起始位置（`--swap1-start`、`--swap2-start`）和交换长度（`--swap-len`），支持任意帧数的交换。

- **节拍感知自动交换**  
  使用 `--beat-pair 1-3` 或 `--beat-pair 2-4` 并配合 `--bpm`，程序会根据 BPM 自动计算对应拍的帧范围，并设置分组大小和交换参数。如果四拍不等长，会提示用户交互式输入精确参数。  
  **注意：使用 `--beat-pair` 时必须手动指定 `--bpm`，程序不会自动检测 BPM。**

- **音视频同步处理**  
  音频会按照帧时长（`1/fps` 秒）被切割成与每帧对应的片段，并跟随视频帧一起交换，保证最终的音画同步。

- **两种处理模式**  
  - **内存模式**：将所有帧一次性加载到内存中处理，适合短时长视频。  
  - **流式模式**：逐组处理，内存占用低，适合长视频或分辨率较高的素材。  
  程序会根据视频大小自动选择合适的模式，也可手动指定。

- **自动 BPM 检测（非节拍交换场景）**  
  通过 `--auto-bpm` 参数可自动检测音频 BPM 并调整分组大小（用于自定义交换规则，不与 `--beat-pair` 同时使用）。

- **性能预估**  
  运行前会显示视频信息、内存占用估算、预计处理时间，帮助你决定是否采用流式模式。

- **依赖 FFmpeg**  
  视频/音频编解码、格式转换等重量级工作交给 FFmpeg，处理速度快，编码质量高。

## 📦 依赖安装

### 1. 系统依赖：FFmpeg

- **Windows**：下载 [FFmpeg 可执行文件](https://ffmpeg.org/download.html) 并添加到 `PATH`。
- **macOS**：`brew install ffmpeg`
- **Linux**：`sudo apt install ffmpeg` （Debian/Ubuntu）

### 2. Python 依赖

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

或者直接安装项目：

```bash
pip install -e .
```

## 🚀 快速开始

### 基本用法（默认规则）

默认每 12 帧一组，交换组内第 0-2 帧与第 6-8 帧：

```bash
mihoyo-video-tr -i input.mp4 -o output.mp4
```

### 自定义交换规则

例如：每 32 帧一组，交换第 0-7 帧（8帧）与第 16-23 帧（8帧）：

```bash
mihoyo-video-tr -i input.mp4 -o output.mp4 \
    --group-size 32 --swap1-start 0 --swap2-start 16 --swap-len 8
```

### 根据节拍自动交换

**注意：使用 `--beat-pair` 时必须同时指定 `--bpm`。**

交换第 1 拍和第 3 拍（BPM=120），输出到 `Output_1to3/原文件名_swapped.mp4`：

```bash
mihoyo-video-tr -i music_video.mp4 --beat-pair 1-3 --bpm 120
```

交换第 2 拍和第 4 拍（BPM=128）：

```bash
mihoyo-video-tr -i music_video.mp4 --beat-pair 2-4 --bpm 128
```

**交互式手动参数**：如果程序检测到四拍帧数不一致（常见于非整数帧率/BPM组合），会显示每拍的帧范围，并提示你手动输入 `group-size`、`swap1-start`、`swap2-start`、`swap-len`。你可以根据建议值调整，程序将继续处理。

### 自动检测 BPM 调整分组大小（非节拍交换）

```bash
mihoyo-video-tr -i music_video.mp4 --auto-bpm
```

此命令会检测音频 BPM，自动计算合理的 `group-size`，然后使用默认或自定义的交换规则进行处理。`--auto-bpm` 不能与 `--beat-pair` 同时使用。

### 仅查看视频信息，不处理

```bash
mihoyo-video-tr -i input.mp4 --info
```

### 强制覆盖输出文件

```bash
mihoyo-video-tr -i input.mp4 -o output.mp4 --force
```

### 计算节拍帧范围（独立工具）

```bash
python scripts/calc_beat_frames.py
```

## 📋 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
| ----- | ----- | ----- | ----- |
| `-i`, `--input` | str | **必填** | 输入视频文件（自动在 `Video/` 目录查找） |
| `-o`, `--output` | str | `output_swapped.mp4` | 输出视频文件路径 |
| `--info` | flag | - | 仅显示视频信息，不处理 |
| `--mode` | str | `auto` | 处理模式：`auto` / `memory` / `streaming` |
| `--no-swap` | flag | - | 不执行交换（仅复制视频且不处理音频） |
| `--force` | flag | - | 强制覆盖输出文件 |
| `--group-size` | int | `12` | 每组帧数（必须 ≥ 交换区域终点） |
| `--swap1-start` | int | `0` | 第一组交换区域的起始帧索引（0‑based） |
| `--swap2-start` | int | `6` | 第二组交换区域的起始帧索引 |
| `--swap-len` | int | `3` | 交换区域的长度（帧数） |
| `--auto-bpm` | flag | - | 自动检测 BPM 并覆盖 `--group-size`（不与 `--beat-pair` 共用） |
| `--beat-pair` | {1-3,2-4} | - | 节拍对交换（必须同时指定 `--bpm`） |
| `--bpm` | float | - | 手动指定 BPM（与 `--beat-pair` 配合使用，必填） |

## ⚙️ 工作原理

1. **获取视频信息**（分辨率、帧率、总帧数、编码格式）
2. **按组处理视频帧**：  
   - 流式模式：缓存 `group_size` 帧 → 交换指定区域 → 写入输出  
   - 内存模式：一次性加载所有帧 → 在每组内交换 → 写入输出
3. **同步处理音频**：  
   - 用 FFmpeg 提取完整音频（WAV）  
   - 按每帧时长（`1000/fps` 毫秒）切割音频片段  
   - 按相同的交换规则重组音频片段  
   - 用 FFmpeg 将新音频与处理后的视频合并
4. **输出最终 MP4 文件**（H.264 视频 + AAC 音频）

## 📝 注意事项

- **交换区域不能超出组大小**，否则程序会报错。  
- **两个交换区域可以重叠**，但会给出警告，结果可能不符合预期。  
- **音频切割精度**：由于使用 FFmpeg 按时间切割，可能存在微小偏差（<1ms），人耳无法察觉。  
- **长视频处理**：建议使用流式模式（`--mode streaming`），避免内存不足。  
- **临时文件**：处理过程中会在输出文件同目录下生成 `.temp_video.mp4` 和 `.temp_audio.wav`，处理完成后会自动删除。  
- **编码质量**：输出视频使用 `libx264` 编码，`crf` 采用 FFmpeg 默认值（约 23），如需更高画质可自行修改脚本中的编码参数。
- **节拍交换的自动输出目录**：使用 `--beat-pair` 且未指定 `-o` 时，输出文件会自动放入 `Output_1to3/` 或 `Output_2to4/` 目录，文件名为 `原文件名_swapped.mp4`。
- **BPM 必须手动提供**：使用 `--beat-pair` 时，必须同时用 `--bpm` 指定 BPM 数值（如 `--bpm 120`）。程序不会自动检测 BPM。

## 🛠️ 常见问题

### 1. 提示“FFmpeg 未找到”

请确保 FFmpeg 已安装并加入系统 PATH，或者在命令行中可以直接执行 `ffmpeg -version`。

### 2. 处理长视频时内存爆炸

使用 `--mode streaming` 强制启用流式模式，或者让程序自动选择（默认 `auto` 会根据内存估算自动选择）。

### 3. 音频与视频不同步

检查输入视频的帧率是否恒定（可变帧率可能导致音频切割不精确）。建议先用 FFmpeg 将视频转为恒定帧率：

```bash
ffmpeg -i input.mp4 -vsync cfr -r 30 output_cfr.mp4
```

### 4. 交换后画面花屏

可能是交换区域设置不当导致参考帧丢失（例如交换了 B/P 帧依赖的区域）。可以尝试使用 `--no-swap` 先测试能否正常复制，如果正常，则说明交换逻辑本身没问题，可以调整交换区域避开关键帧密集区。

### 5. 使用 `--beat-pair` 时提示“四拍帧数不一致”

这是因为你指定的 BPM 和视频帧率组合导致每拍帧数不是整数。程序会显示每拍的实际帧范围，并引导你手动输入交换参数。你可以根据建议值调整分组大小和交换长度。

### 6. 为什么使用 `--beat-pair` 时不能自动检测 BPM？

节拍交换要求精确的 BPM 值，自动检测可能因音频质量、节奏模糊等产生误差，导致帧范围计算错误。因此强制要求用户通过 `--bpm` 手动指定。若你需要自动检测 BPM 来调整分组大小（非节拍交换场景），可以使用 `--auto-bpm` 参数。

## 📄 许可证

本项目基于 MIT 许可证开源。  
使用的第三方库（OpenCV、FFmpeg、pydub）均遵循其各自的许可证。

## 🙏 致谢

- [FFmpeg](https://ffmpeg.org/) – 音视频处理核心
- [OpenCV](https://opencv.org/) – 视频帧读写
- [pydub](https://github.com/jiaaro/pydub) – 音频切割与拼接
