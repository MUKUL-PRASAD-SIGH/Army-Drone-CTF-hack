"""
Models module providing dataclasses for packet representation, 
stream statistics, and inference results.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Packet:
    """
    Represents a single decoded UART packet.

    Attributes:
        index: Sequential index of the packet in the stream.
        timestamp: Derived or parsed timestamp in seconds.
        raw: The complete raw byte sequence of the packet.
        sof: Start of Frame byte (B[0]).
        msg_class: Message class byte (B[1]).
        flags: Protocol flags byte (B[2]).
        length: Declared payload length (B[3]).
        payload: The encrypted payload bytes (B[4:]).
        direction: Human-readable direction (DRONE->GCS or GCS->DRONE).
        stream_id: Hex string representation of the SOF byte.
    """
    index: int
    timestamp: float
    raw: bytes
    sof: int
    msg_class: int
    flags: int
    length: int
    payload: bytes
    direction: str
    stream_id: str


@dataclass
class StreamStats:
    """
    Aggregated statistics for the entire analyzed stream.

    Attributes:
        total_bytes: Sum of all bytes processed.
        n_packets: Total number of successfully segmented packets.
        duration: Total capture duration in seconds.
        pkt_rate: Packets per second.
        dominant_size: The most frequently occurring packet size.
        baud_inferred: The calculated baud rate based on timing.
        entropy_header: Shannon entropy of the header region.
        entropy_payload: Shannon entropy of the payload region.
        burst_period: Detected periodicity of large data bursts.
    """
    total_bytes: int = 0
    n_packets: int = 0
    duration: float = 0.0
    pkt_rate: float = 0.0
    dominant_size: int = 0
    baud_inferred: int = 0
    entropy_header: float = 0.0
    entropy_payload: float = 0.0
    burst_period: float = 0.0


@dataclass
class InferenceResult:
    """
    High-level conclusions drawn from the SIGINT analysis.

    Attributes:
        platform: Identified hardware/software platform (e.g., Pixhawk).
        protocol: Identified communication protocol (e.g., MAVLink v2).
        confidence: Statistical confidence in the identification (0.0-1.0).
        flight_duration: Total inferred duration of the drone operation.
        command_types: List of identified potential command categories.
        sync_period: Calculated synchronization interval.
        evidence_list: List of specific findings supporting the inference.
    """
    platform: str
    protocol: str
    confidence: float
    flight_duration: float
    command_types: List[str] = field(default_factory=list)
    sync_period: float = 0.0
    evidence_list: List[str] = field(default_factory=list)
