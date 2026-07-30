#!/usr/bin/env python3
"""命令行界面（参数解析、流程调度）"""
import sys
import argparse
import time
import os
import shutil
from pathlib import Path

from .config import Config
from .exceptions import MihoyoError, SwapParameterError, BPMDetectionError
from .core import VideoProcessor, AudioProcessor, BeatCalculator
from .utils import (
    get_video_info,
    has_audio_stream,
    detect_bpm,
    resolve_input_path,
    confirm_overwrite,
    cleanup_temp_files,
    estimate_performance,
    estimate_memory_feasible
)


def show_info_only(input_path: str):
    w, h, fps, total, fourcc = get_video_info(input_path)
    print("\n=== 视频基本信息 ===")
    print(f"分辨率：{w} x {h}")
    print(f"帧率：{fps:.2f} fps")
    print(f"总帧数：{total}")
    print(f"编码格式：{fourcc}")
    bytes_per_frame = w * h * 3
    total_memory = bytes_per_frame * total
    from .utils.performance import format_bytes
    print(f"每帧内存: {format_bytes(bytes_per_frame)}")
    print(f"全部帧内存: {format_bytes(total_memory)}")
    if total_memory > 1024**3:
        print("[WARN] 内存占用超过1GB，建议使用流式模式")
    estimate_performance(total, fps, fourcc)
    print("\n仅显示信息，未处理视频。")


def auto_calc_beat_params(input_path: str, beat_pair: str, bpm: float):
    """自动计算节拍交换参数，bpm 必须提供"""
    _, _, fps, _, _ = get_video_info(input_path)
    beat_a, beat_b = (1, 3) if beat_pair == "1-3" else (2, 4)
    all_beats = BeatCalculator.get_all_beats(fps, bpm)
    start_a, end_a = all_beats[beat_a]
    start_b, end_b = all_beats[beat_b]
    len_a = end_a - start_a + 1
    len_b = end_b - start_b + 1
    
    if len_a != len_b:
        print("\n[WARN] 四拍帧数不一致：")
        for i in range(1, 5):
            s, e = all_beats[i]
            print(f"  第{i}拍: {e-s+1} 帧 ({s}~{e})")
        print("请手动输入交换参数（建议基于以上范围）:")
        while True:
            try:
                gs = int(input("分组大小 (group_size): "))
                s1 = int(input(f"第{beat_a}拍起始 (建议 {start_a}): "))
                s2 = int(input(f"第{beat_b}拍起始 (建议 {start_b}): "))
                l = int(input(f"交换长度 (不超过 {min(len_a, len_b)}): "))
                if s1 + l > gs or s2 + l > gs:
                    print("错误：交换区域超出分组大小")
                    continue
                if l <= 0:
                    print("长度必须为正")
                    continue
                break
            except ValueError:
                print("请输入整数")
        return {
            "group_size": gs,
            "swap1_start": s1,
            "swap2_start": s2,
            "swap_len": l
        }
    else:
        swap_len = len_a
        group_size = max(end_a, end_b) + 1
        print(f"\n根据节拍 {beat_pair} 自动计算：")
        print(f"  第{beat_a}拍: 帧 {start_a}~{end_a} (共{swap_len}帧)")
        print(f"  第{beat_b}拍: 帧 {start_b}~{end_b} (共{swap_len}帧)")
        print(f"  分组大小: {group_size}")
        return {
            "group_size": group_size,
            "swap1_start": start_a,
            "swap2_start": start_b,
            "swap_len": swap_len
        }


def main():
    parser = argparse.ArgumentParser(description="视频帧与音频同步交换工具")
    parser.add_argument("-i", "--input", required=True, help="输入视频文件")
    parser.add_argument("-o", "--output", default=Config.DEFAULT_OUTPUT, help="输出文件")
    parser.add_argument("--info", action="store_true", help="仅显示信息")
    parser.add_argument("--mode", choices=["auto", "memory", "streaming"], default="auto")
    parser.add_argument("--no-swap", action="store_true", help="不交换，仅复制")
    parser.add_argument("--force", action="store_true", help="强制覆盖")
    parser.add_argument("--group-size", type=int, default=Config.DEFAULT_GROUP_SIZE)
    parser.add_argument("--swap1-start", type=int, default=Config.DEFAULT_SWAP1_START)
    parser.add_argument("--swap2-start", type=int, default=Config.DEFAULT_SWAP2_START)
    parser.add_argument("--swap-len", type=int, default=Config.DEFAULT_SWAP_LEN)
    parser.add_argument("--beat-pair", choices=["1-3", "2-4"], help="节拍对交换（必须同时指定 --bpm）")
    parser.add_argument("--bpm", type=float, help="手动指定 BPM（与 --beat-pair 配合使用，必填）")
    
    args = parser.parse_args()
    
    try:
        input_path = resolve_input_path(args.input)
        if args.info:
            show_info_only(input_path)
            return
        
        if args.beat_pair:
            # 必须提供 --bpm
            if args.bpm is None:
                print("[ERROR] 使用 --beat-pair 时必须同时指定 --bpm")
                sys.exit(1)
            beat_params = auto_calc_beat_params(input_path, args.beat_pair, args.bpm)
            args.group_size = beat_params["group_size"]
            args.swap1_start = beat_params["swap1_start"]
            args.swap2_start = beat_params["swap2_start"]
            args.swap_len = beat_params["swap_len"]
            
            if args.output == Config.DEFAULT_OUTPUT:
                out_dir = Config.get_output_dir(args.beat_pair)
                out_dir.mkdir(exist_ok=True)
                base = Path(input_path).stem
                args.output = str(out_dir / f"{base}_swapped.mp4")
                print(f"输出文件: {args.output}")
        
        # 参数合法性校验
        if args.swap1_start + args.swap_len > args.group_size or \
           args.swap2_start + args.swap_len > args.group_size:
            raise SwapParameterError("交换区域超出分组大小")
        if args.swap1_start == args.swap2_start and args.swap_len > 0:
            raise SwapParameterError("两个交换区域重叠且起始相同，无效交换")
        if args.swap_len <= 0:
            raise SwapParameterError("交换长度必须为正")
        
        if not confirm_overwrite(args.output, args.force):
            return
        
        w, h, fps, total, fourcc = get_video_info(input_path)
        print(f"\n=== 处理参数 ===")
        print(f"输入: {input_path}")
        print(f"输出: {args.output}")
        print(f"分辨率: {w}x{h}, 帧率: {fps:.2f}, 总帧数: {total}")
        print(f"分组大小: {args.group_size}")
        print(f"交换区域: [{args.swap1_start}:{args.swap1_start+args.swap_len-1}] <-> [{args.swap2_start}:{args.swap2_start+args.swap_len-1}]")
        
        if args.mode == "auto":
            mode = "memory" if estimate_memory_feasible(w, h, total) else "streaming"
        else:
            mode = args.mode
        print(f"处理模式: {mode}")
        
        temp_video = args.output + ".temp_video.mp4"
        temp_audio = args.output + ".temp_audio.wav"
        
        start_time = time.time()
        if args.no_swap:
            shutil.copy2(input_path, temp_video)
        else:
            vp = VideoProcessor(input_path, temp_video, args.group_size,
                               args.swap1_start, args.swap2_start, args.swap_len,
                               mode=mode)
            vp.process()
        
        if not args.no_swap and has_audio_stream(input_path):
            print("正在处理音频...")
            AudioProcessor.swap_audio_segments(input_path, args.group_size,
                                              args.swap1_start, args.swap2_start,
                                              args.swap_len, temp_audio)
            print("合并音视频...")
            AudioProcessor.merge_audio_video(temp_video, temp_audio, args.output)
            cleanup_temp_files(args.output)
        else:
            if not args.no_swap and not has_audio_stream(input_path):
                print("输入视频无音频轨道，输出无音频")
            os.replace(temp_video, args.output)
        
        elapsed = time.time() - start_time
        print(f"[OK] 完成！耗时 {elapsed:.1f} 秒")
        
    except MihoyoError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 未预期错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()