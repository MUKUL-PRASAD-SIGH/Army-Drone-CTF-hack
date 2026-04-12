"""Test suite for the protocol module."""

import pandas as pd
from antigravity import protocol
from antigravity.models import Packet

def test_decode_header():
    pkt = Packet(
        index=0, timestamp=0.0, raw=b'\xAA\x01\x02\x0Atest',
        sof=0xAA, msg_class=0x01, flags=0x02, length=10,
        payload=b'test', direction="D", stream_id="0xAA"
    )
    header = protocol.decode_header(pkt)
    assert header['sof'] == 0xAA
    assert header['length'] == 10

def test_classify_direction():
    assert protocol.classify_direction(0xAA) == "DRONE->GCS"
    assert protocol.classify_direction(0xEE) == "GCS->DRONE"
    assert protocol.classify_direction(0xFF) == "UNKNOWN"

def test_analyze_transitions():
    packets = [
        Packet(0, 0, b'', 0xAA, 0, 0, 0, b'', "", "0xAA"),
        Packet(1, 0, b'', 0xEE, 0, 0, 0, b'', "", "0xEE"),
        Packet(2, 0, b'', 0xAA, 0, 0, 0, b'', "", "0xAA")
    ]
    df = protocol.analyze_transitions(packets)
    assert isinstance(df, pd.DataFrame)
    assert "0xEE" in df.columns
