"""
Protocol module for decoding packet headers and analyzing stream transitions.
"""

import logging
from typing import Dict, List

import pandas as pd

from astra_v11.config import DIRECTION_MAP
from astra_v11.models import Packet

logger = logging.getLogger(__name__)


def decode_header(pkt: Packet) -> Dict[str, int]:
    """
    Parse the 4-byte plaintext header.
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
    """
    return DIRECTION_MAP.get(sof_byte, "UNKNOWN")


def validate_length_field(pkt: Packet) -> bool:
    """
    Check if the declared length matches the actual payload size.
    """
    return pkt.length + 4 == len(pkt.raw)


def analyze_transitions(packets: List[Packet]) -> pd.DataFrame:
    """
    Build an N×N transition matrix of SOF byte sequences.
    """
    if len(packets) < 2:
        logger.warning("Insufficient packets to analyze transitions.")
        return pd.DataFrame()

    sofs = [p.stream_id for p in packets]
    pairs = list(zip(sofs[:-1], sofs[1:]))
    df_pairs = pd.DataFrame(pairs, columns=["From", "To"])
    
    transitions = df_pairs.groupby(["From", "To"]).size().unstack(fill_value=0)
    
    logger.info("Generated SOF transition matrix.")
    return transitions


def compute_sequence_counters(packets: List[Packet]) -> pd.DataFrame:
    """
    Extract and track sequence numbers per stream_id.
    """
    data = []
    for p in packets:
        data.append({
            "index": p.index,
            "timestamp": p.timestamp,
            "stream_id": p.stream_id,
            "sequence": p.flags
        })
    
    df = pd.DataFrame(data)
    logger.info("Extracted sequence counters from packet flags.")
    return df
