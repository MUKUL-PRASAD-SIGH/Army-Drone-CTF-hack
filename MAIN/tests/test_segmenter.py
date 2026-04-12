"""Test suite for the segmenter module."""

import numpy as np
import pytest
from antigravity import segmenter
from antigravity.models import Packet

def test_compute_ipg():
    ts = np.array([0.0, 0.01, 0.05], dtype=np.float64)
    gaps = segmenter.compute_ipg(ts)
    assert len(gaps) == 2
    assert gaps[0] == 10.0 # 10ms
    assert gaps[1] == 40.0 # 40ms

def test_segment_by_gap():
    # 10 bytes, gap after 5th byte
    raw = np.array([0xAA, 1, 2, 3, 4, 0xAA, 5, 6, 7, 8], dtype=np.uint8)
    # Timestamps: 0, 1, 2, 3, 4, 100, 101, 102, 103, 104
    ts = np.array([0, 1, 2, 3, 4, 10, 11, 12, 13, 14], dtype=np.float64)
    
    packets = segmenter.segment_by_gap(raw, ts, gap_ms=5000.0)
    assert len(packets) == 2
    assert packets[0].sof == 0xAA
    assert packets[1].sof == 0xAA
    assert len(packets[0].raw) == 5

def test_segment_by_sof():
    raw = np.array([0xAA, 1, 2, 0xEE, 3, 4, 0xEA, 5], dtype=np.uint8)
    packets = segmenter.segment_by_sof(raw)
    assert len(packets) == 3
    assert packets[0].sof == 0xAA
    assert packets[1].sof == 0xEE
    assert packets[2].sof == 0xEA
