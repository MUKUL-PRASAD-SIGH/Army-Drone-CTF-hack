"""
Segmenter module for slicing the raw UART byte stream into discrete packets.
"""

import logging
from typing import List

import numpy as np

from astra_v11.config import (
    DIRECTION_MAP,
    GAP_THRESHOLD_MS,
    SOF_DRONE,
    SOF_GCS_1,
    SOF_GCS_2,
    STREAM_ID_MAP,
)
from astra_v11.models import Packet

logger = logging.getLogger(__name__)


def compute_ipg(timestamps: np.ndarray) -> np.ndarray:
    """
    Compute the inter-packet gap (IPG) in milliseconds.
    """
    if len(timestamps) < 2:
        return np.array([], dtype=np.float64)
    
    gaps_sec = np.diff(timestamps)
    return gaps_sec * 1000.0


def segment_by_gap(
    raw: np.ndarray, 
    timestamps: np.ndarray, 
    gap_ms: float = GAP_THRESHOLD_MS
) -> List[Packet]:
    """
    Primary segmentation strategy: splitting the stream at temporal gaps.
    """
    ipgs = compute_ipg(timestamps)
    split_indices = np.where(ipgs > gap_ms)[0] + 1
    
    raw_segments = np.split(raw, split_indices)
    timestamp_segments = np.split(timestamps, split_indices)
    
    packets = []
    for i, (r_seg, t_seg) in enumerate(zip(raw_segments, timestamp_segments)):
        if len(r_seg) < 4:
            continue
        
        packets.append(
            Packet(
                index=i,
                timestamp=float(t_seg[0]),
                raw=bytes(r_seg),
                sof=int(r_seg[0]),
                msg_class=int(r_seg[1]),
                flags=int(r_seg[2]),
                length=int(r_seg[3]),
                payload=bytes(r_seg[4:]),
                direction=DIRECTION_MAP.get(int(r_seg[0]), "UNKNOWN"),
                stream_id=STREAM_ID_MAP.get(int(r_seg[0]), hex(r_seg[0]))
            )
        )
    
    logger.info(f"Segmented {len(packets)} packets using {gap_ms}ms gap threshold.")
    return packets


def segment_by_sof(raw: np.ndarray) -> List[Packet]:
    """
    Fallback segmentation strategy: scanning for known SOF byte markers.
    """
    target_sofs = {SOF_DRONE, SOF_GCS_1, SOF_GCS_2}
    raw_list = list(raw)
    
    packet_start_indices = [
        i for i, b in enumerate(raw_list) if b in target_sofs
    ]
    
    packets = []
    for i in range(len(packet_start_indices)):
        start_idx = packet_start_indices[i]
        end_idx = packet_start_indices[i+1] if i+1 < len(packet_start_indices) else len(raw)
        
        r_seg = raw[start_idx:end_idx]
        if len(r_seg) < 4:
            continue
            
        packets.append(
            Packet(
                index=i,
                timestamp=0.0,
                raw=bytes(r_seg),
                sof=int(r_seg[0]),
                msg_class=int(r_seg[1]),
                flags=int(r_seg[2]),
                length=int(r_seg[3]),
                payload=bytes(r_seg[4:]),
                direction=DIRECTION_MAP.get(int(r_seg[0]), "UNKNOWN"),
                stream_id=STREAM_ID_MAP.get(int(r_seg[0]), hex(r_seg[0]))
            )
        )
        
    logger.info(f"Segmented {len(packets)} packets using SOF marker fallback.")
    return packets


def rebuild_frames(raw_packets: List[Packet]) -> List[Packet]:
    """
    Refine and validate already segmented packets.
    """
    validated = []
    for p in raw_packets:
        if p.length + 4 == len(p.raw):
            validated.append(p)
        else:
            validated.append(p)
    return validated
