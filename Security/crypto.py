"""
Crypto module for statistical analysis of the encrypted stream.
Includes entropy calculations, frequency analysis, and pattern detection.
"""

import logging
import math
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

from antigravity.models import Packet

logger = logging.getLogger(__name__)


def shannon_entropy(data: bytes) -> float:
    """
    Calculate the Shannon entropy of a byte sequence.

    Args:
        data: Byte sequence to analyze.

    Returns:
        float: Entropy in bits per byte (0.0 to 8.0).
    """
    if not data:
        return 0.0
    
    counts = Counter(data)
    total = len(data)
    entropy = 0.0
    
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
        
    return entropy


def per_region_entropy(packets: List[Packet]) -> Dict[str, float]:
    """
    Calculate average entropy for different packet regions.

    Args:
        packets: List of packets.

    Returns:
        Dict: Average entropy for "header", "payload", and "full".
    """
    if not packets:
        return {"header": 0.0, "payload": 0.0, "full": 0.0}
    
    headers = b"".join([p.raw[:4] for p in packets])
    payloads = b"".join([p.payload for p in packets if p.payload])
    full = b"".join([p.raw for p in packets])
    
    return {
        "header": shannon_entropy(headers),
        "payload": shannon_entropy(payloads),
        "full": shannon_entropy(full)
    }


def byte_frequency(data: bytes) -> np.ndarray:
    """
    Calculate the frequency of each byte value (0-255).

    Args:
        data: Byte sequence.

    Returns:
        np.ndarray: Frequency counts (shape 256).
    """
    freq = np.zeros(256, dtype=np.int64)
    if not data:
        return freq
    
    counts = Counter(data)
    for b, count in counts.items():
        freq[b] = count
    return freq


def chi_square_uniformity(freq: np.ndarray) -> Tuple[float, float]:
    """
    Perform a Chi-Square goodness-of-fit test against a uniform distribution.

    Args:
        freq: Frequency counts of bytes.

    Returns:
        Tuple[float, float]: (Chi-square statistic, p-value).
    """
    # Expected frequency for each byte if uniform
    total = np.sum(freq)
    if total == 0:
        return 0.0, 1.0
        
    expected = np.full(256, total / 256.0)
    statistic, p_value = stats.chisquare(freq, f_expected=expected)
    return float(statistic), float(p_value)


def xor_analysis(packets: List[Packet], stream_id: str) -> np.ndarray:
    """
    XOR same-length payloads of the same stream type pairwise.
    Reveals if a fixed key or repeating keystream is used.

    Args:
        packets: List of packets.
        stream_id: The SOF identifier to filter by.

    Returns:
        np.ndarray: Matrix of XOR differences.
    """
    filtered = [p for p in packets if p.stream_id == stream_id]
    if len(filtered) < 2:
        return np.array([])
    
    # Use the first packet as a baseline for same-length comparison
    baseline = filtered[0]
    results = []
    
    for p in filtered[1:]:
        if len(p.payload) == len(baseline.payload):
            # XOR pairwise
            xor_diff = np.bitwise_xor(
                np.frombuffer(p.payload, dtype=np.uint8),
                np.frombuffer(baseline.payload, dtype=np.uint8)
            )
            results.append(xor_diff)
            
    return np.array(results) if results else np.array([])


def detect_ecb(packets: List[Packet]) -> bool:
    """
    Detect if any identical payloads exist for the same length, 
    suggesting lack of salt/IV (Electronic Codebook mode).

    Args:
        packets: List of packets.

    Returns:
        bool: True if duplicate payloads are found.
    """
    seen = set()
    for p in packets:
        if not p.payload:
            continue
        payload_hash = (len(p.payload), p.payload)
        if payload_hash in seen:
            logger.warning(f"Duplicate payload detected at packet {p.index}!")
            return True
        seen.add(payload_hash)
    return False


def autocorrelation(data: bytes, max_lag: int = 256) -> np.ndarray:
    """
    Compute the autocorrelation of the byte stream to find repeating patterns.

    Args:
        data: Byte sequence.
        max_lag: Maximum lag to calculate.

    Returns:
        np.ndarray: Autocorrelation values.
    """
    if len(data) < max_lag:
        max_lag = len(data)
        
    arr = np.frombuffer(data, dtype=np.uint8).astype(np.float64)
    arr -= np.mean(arr)
    
    result = np.correlate(arr, arr, mode='full')
    mid = len(result) // 2
    return result[mid : mid + max_lag] / result[mid]


def detect_keystream_reuse(
    packets: List[Packet], 
    threshold: float = 0.8
) -> List[Tuple[int, int, float]]:
    """
    Identifies pairs of packets with suspiciously high payload similarity.

    Args:
        packets: List of packets.
        threshold: Similarity threshold (0.0 to 1.0).

    Returns:
        List[Tuple[int, int, float]]: (idx1, idx2, similarity).
    """
    suspicious = []
    # Simplified: Only compare first 50 packets to avoid O(N^2) explosion
    subset = packets[:100]
    
    for i in range(len(subset)):
        for j in range(i + 1, len(subset)):
            p1, p2 = subset[i], subset[j]
            if len(p1.payload) == len(p2.payload) and len(p1.payload) > 8:
                # Count matching bytes
                matches = sum(1 for a, b in zip(p1.payload, p2.payload) if a == b)
                similarity = matches / len(p1.payload)
                if similarity > threshold:
                    suspicious.append((p1.index, p2.index, similarity))
                    
    return suspicious
