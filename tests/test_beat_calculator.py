import pytest
from mihoyo_video_tr.core.beat_calculator import BeatCalculator

def test_calculate_beat_frames():
    fps = 30.0
    bpm = 120.0
    s, e = BeatCalculator.calculate_beat_frames(fps, bpm, 1)
    assert s == 0
    assert e == 14
    s, e = BeatCalculator.calculate_beat_frames(fps, bpm, 2)
    assert s == 15
    assert e == 29

def test_are_all_beats_equal_length():
    fps = 30.0
    bpm = 120.0
    assert BeatCalculator.are_all_beats_equal_length(fps, bpm) is True
    fps = 30.0
    bpm = 125.0
    assert BeatCalculator.are_all_beats_equal_length(fps, bpm) is False