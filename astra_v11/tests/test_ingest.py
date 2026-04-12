"""Test suite for the ingest module."""

import numpy as np
import pytest
from astra_v11 import ingest

def test_extract_timestamps():
    raw = np.zeros(100, dtype=np.uint8)
    baud = 1000 
    ts = ingest.extract_timestamps(raw, baud)
    
    assert len(ts) == 100
    assert ts[0] == 0.0
    assert pytest.approx(ts[1], 0.01) == 0.01

def test_validate_stream():
    raw = np.array([0, 10, 255, 128], dtype=np.uint8)
    stats = ingest.validate_stream(raw)
    
    assert stats['byte_count'] == 4
    assert stats['min_value'] == 0
    assert stats['max_value'] == 255
    assert stats['is_non_null'] is True
    assert stats['null_byte_percentage'] == 25.0
