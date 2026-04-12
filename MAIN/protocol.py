"""
Protocol module for decoding packet headers and analyzing 
stream-level behaviors such as transitions and sequence tracking.
"""

import logging
from typing import Dict, List

import pandas as pd

from antigravity.config import DIRECTION_MAP
from antigravity.models import Packet

logger = logging.getLogger(__name__)


def decode_header(pkt: Packet) -> Dict[str, int]:
    """
    Parse the 4-byte plaintext header.

    Args:
        pkt: The Packet object.

    Returns:
        Dict: Mapped header fields.
    """
    return {
        "sof": pkt.sof,
        "msg_class": pkt.msg_class,
        "flags": pkt.flags,
        "length": pkt.length
    }


def classify_direction(sof_byte: int) -> str:
    """
    Map the SOF byte to a direction string.

    Args:
        sof_byte: The first byte of the packet.

    Returns:
        str: "DRONE->GCS", "GCS->DRONE", or "UNKNOWN".
    """
    return DIRECTION_MAP.get(sof_byte, "UNKNOWN")


def validate_length_field(pkt: Packet) -> bool:
    """
    Check if the declared length in B[3] matches the actual payload size.

    Args:
        pkt: The Packet object.

    Returns:
        bool: True if length + 4 == len(raw).
    """
    return pkt.length + 4 == len(pkt.raw)


def analyze_transitions(packets: List[Packet]) -> pd.DataFrame:
    """
    Build an N×N transition matrix of SOF byte sequences.
    Shows the probability or frequency of one SOF following another.

    Args:
        packets: List of analyzed packets.

    Returns:
        pd.DataFrame: Transition matrix.
    """
    if len(packets) < 2:
        logger.warning("Insufficient packets to analyze transitions.")
        return pd.DataFrame()

    sofs = [p.stream_id for p in packets]
    pairs = list(zip(sofs[:-1], sofs[1:]))
    df_pairs = pd.DataFrame(pairs, columns=["From", "To"])
    
    # Use pivot_table instead of series.unstack for robustness
    transitions = df_pairs.groupby(["From", "To"]).size().unstack(fill_value=0)
    
    logger.info("Generated SOF transition matrix.")
    return transitions


def compute_sequence_counters(packets: List[Packet]) -> pd.DataFrame:
    """
    Extract and track sequence numbers per stream_id.
    Heuristic: Assuming 'flags' (B[2]) or first payload byte (B[4]) 
    contains a sequence counter. We will track B[2] for this challenge.

    Args:
        packets: List of packets.

    Returns:
        pd.DataFrame: DataFrame with [index, stream_id, sequence].
    """
    data = []
    for p in packets:
        data.append({
            "index": p.index,
            "timestamp": p.timestamp,
            "stream_id": p.stream_id,
            "sequence": p.flags  # Using flags byte as proxy for sequence
        })
    
    df = pd.DataFrame(data)
    logger.info("Extracted sequence counters from packet flags.")
    return df
