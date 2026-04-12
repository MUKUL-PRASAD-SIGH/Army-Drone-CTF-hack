"""Test suite for the segmenter module."""

import numpy as np
import pytest
from astra_v11 import segmenter
from astra_v11.models import Packet

def test_compute_ipg():
    ts = np.array([0.0, 0.01, 0.05], dtype=np.float64)
    gaps = segmenter.compute_ipg(ts)
    assert len(gaps) == 2
    assert gaps[0] == 10.0
    assert gaps[1] == 40.0

def test_segment_by_gap():
    # Segments need to be >= 4 bytes by default in our implementation
    raw = np.array([0xAA, 1, 2, 3, 4, 0xAA, 5, 6, 7, 8], dtype=np.uint8)
    ts = np.array([0, 1, 2, 3, 4, 10, 11, 12, 13, 14], dtype=np.float64)
    
    packets = segmenter.segment_by_gap(raw, ts, gap_ms=5000.0)
    assert len(packets) == 2
    assert packets[0].sof == 0xAA
    assert packets[1].sof == 0xAA
    assert len(packets[0].raw) == 5

def test_segment_by_sof():
    # Segments need to be >= 4 bytes
    raw = np.array([0xAA, 1, 2, 3, 0xEE, 4, 5, 6, 0xEA, 7, 8, 9, 10], dtype=np.uint8)
    packets = segmenter.segment_by_sof(raw)
    assert len(packets) == 3
    assert packets[0].sof == 0xAA
    assert packets[1].sof == 0xEE
    assert packets[2].sof == 0xEA
