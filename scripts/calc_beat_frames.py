#!/usr/bin/env python3
"""独立节拍计算工具（不依赖主包）"""
import sys
import math

def calculate_beat_frames(fps, bpm, beat_num):
    T = 60.0 / bpm
    start = math.floor((beat_num - 1) * T * fps)
    end = math.floor(beat_num * T * fps) - 1
    if end < start:
        end = start
    return start, end

def main():
    print("=== 节拍帧范围计算器 ===")
    try:
        fps = float(input("帧率 (fps): "))
        bpm = float(input("BPM: "))
        beat_a = int(input("第一拍序号 (1-4): "))
        beat_b = int(input("第二拍序号 (1-4): "))
        if not (1 <= beat_a <= 4 and 1 <= beat_b <= 4):
            print("拍序号范围1-4")
            return
        
        for i in range(1, 5):
            s, e = calculate_beat_frames(fps, bpm, i)
            print(f"第{i}拍: {s}~{e} (共{e-s+1}帧)")
        sa, ea = calculate_beat_frames(fps, bpm, beat_a)
        sb, eb = calculate_beat_frames(fps, bpm, beat_b)
        print(f"\n交换第{beat_a}拍({sa}~{ea})和第{beat_b}拍({sb}~{eb})")
        if (ea-sa+1) != (eb-sb+1):
            print("[WARN] 两拍帧数不同，需手动调整")
    except ValueError:
        print("输入无效")

if __name__ == "__main__":
    main()