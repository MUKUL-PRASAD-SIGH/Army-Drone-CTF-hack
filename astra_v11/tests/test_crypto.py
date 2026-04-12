"""Test suite for the crypto module."""

import numpy as np
import pytest
from astra_v11 import crypto
from astra_v11.models import Packet

def test_shannon_entropy():
    data = b'\x00' * 100
    assert crypto.shannon_entropy(data) == 0.0
    data = bytes(range(256))
    assert crypto.shannon_entropy(data) == 8.0

def test_byte_frequency():
    data = np.array([0, 1, 1, 2, 2, 2], dtype=np.uint8)
    freq = crypto.byte_frequency(data)
    assert freq[0] == 1
    assert freq[1] == 2
    assert freq[2] == 3

def test_chi_square_uniformity():
    freq = np.full(256, 100, dtype=np.int64)
    stat, p = crypto.chi_square_uniformity(freq)
    assert p > 0.9

def test_detect_ecb():
    packets = [
        Packet(0, 0, b'', 0, 0, 0, 0, b'secret', "", ""),
        Packet(1, 0, b'', 0, 0, 0, 0, b'secret', "", "")
    ]
    assert crypto.detect_ecb(packets) is True

def test_autocorrelation():
    data = b'\x01\x02\x01\x02' * 10
    corr = crypto.autocorrelation(data, max_lag=10)
    assert len(corr) == 10
    assert corr[0] == 1.0

def test_xor_analysis():
    p1 = Packet(0, 0, b'', 0, 0, 0, 5, b'AAAAA', "", "S1")
    p2 = Packet(1, 0, b'', 0, 0, 0, 5, b'AAAAA', "", "S1")
    res = crypto.xor_analysis([p1, p2], "S1")
    assert np.all(res[0] == 0)
