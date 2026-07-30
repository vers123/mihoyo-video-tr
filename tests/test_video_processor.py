import pytest
import numpy as np
from mihoyo_video_tr.core.video_processor import VideoProcessor

def test_swap_group():
    group = [np.zeros((2,2,3), dtype=np.uint8) for _ in range(10)]
    for i, f in enumerate(group):
        f[0,0,0] = i
    vp = VideoProcessor.__new__(VideoProcessor)
    vp.group_size = 10
    vp.swap1_start = 1
    vp.swap2_start = 5
    vp.swap_len = 3
    swapped = vp._swap_group(group)
    assert swapped[1][0,0,0] == 5
    assert swapped[2][0,0,0] == 6
    assert swapped[3][0,0,0] == 7
    assert swapped[5][0,0,0] == 1
    assert swapped[6][0,0,0] == 2
    assert swapped[7][0,0,0] == 3

def test_validate_swap_params():
    with pytest.raises(ValueError):
        VideoProcessor("dummy", "dummy", 10, 8, 1, 3, mode="memory")