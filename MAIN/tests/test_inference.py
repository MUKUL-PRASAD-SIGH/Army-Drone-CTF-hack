"""Test suite for the inference module."""

import numpy as np
import pytest
from antigravity import inference
from antigravity.models import Packet, StreamStats

def test_infer_baud_rate():
    # 115200 baud -> 10 bits / 115200 = ~86us gap
    gap = 10 / 115200
    ts = np.array([0, gap, gap*2, gap*3], dtype=np.float64)
    raw = np.zeros(4)
    baud = inference.infer_baud_rate(ts, raw)
    assert baud == 115200

def test_fingerprint_protocol():
    stats = StreamStats(
        total_bytes=1000,
        n_packets=50,
        duration=100.0,
        dominant_size=38,
        baud_inferred=115200,
        entropy_header=2.5,
        entropy_payload=7.8
    )
    result = inference.fingerprint_protocol(stats)
    assert "MAVLink" in result.protocol
    assert result.confidence > 0.8

def test_detect_bursts():
    packets = [
        Packet(0, 1.0, b'x'*200, 0, 0, 0, 196, b'', "", ""),
        Packet(1, 2.0, b'x'*10, 0, 0, 0, 6, b'', "", ""),
        Packet(2, 40.0, b'x'*200, 0, 0, 0, 196, b'', "", "")
    ]
    bursts = inference.detect_bursts(packets, min_size=100)
    assert len(bursts) == 1
    assert pytest.approx(bursts[0]['period_to_next'], 0.1) == 39.0
