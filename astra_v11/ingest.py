"""
Ingest module for loading raw UART streams from various file formats
and pre-processing them for segmentation.
"""

import logging
import os
from typing import Dict, Union

import numpy as np

from astra_v11.config import BAUD_RATE

# Configure logging for this module
logger = logging.getLogger(__name__)


def load_raw(path: str) -> np.ndarray:
    """
    Loads raw byte data from a file. 
    Supports .csv (hex column), .bin (binary), and .hex formats.

    Args:
        path: Path to the input file.

    Returns:
        np.ndarray: A numpy array of uint8 bytes.

    Raises:
        FileNotFoundError: If the path does not exist.
        ValueError: If the file format is unsupported or data is invalid.
    """
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    try:
        if ext == '.bin':
            with open(path, 'rb') as f:
                data = np.frombuffer(f.read(), dtype=np.uint8)
        
        elif ext == '.csv':
            import pandas as pd
            df = pd.read_csv(path, header=None)
            first_val = df.iloc[0, 0]
            if isinstance(first_val, str) and (first_val.startswith('0x') or len(first_val) <= 2):
                data = df[0].apply(lambda x: int(str(x), 16)).astype(np.uint8).values
            else:
                data = df[0].astype(np.uint8).values
        
        elif ext == '.hex':
            with open(path, 'r') as f:
                content = f.read().strip()
                if ' ' in content or len(content) > 100:
                    hex_values = content.replace('\n', ' ').split()
                    data = np.array([int(h, 16) for h in hex_values], dtype=np.uint8)
                else:
                    data = np.array([int(content[i:i+2], 16) for i in range(0, len(content), 2)], dtype=np.uint8)
        
        else:
            logger.info(f"Unknown extension {ext}, attempting binary read.")
            with open(path, 'rb') as f:
                data = np.frombuffer(f.read(), dtype=np.uint8)

        logger.info(f"Successfully loaded {len(data)} bytes from {path}")
        return data

    except Exception as e:
        logger.error(f"Failed to load raw data from {path}: {e}")
        raise ValueError(f"Error parsing {ext} file: {e}")


def extract_timestamps(raw: np.ndarray, baud: int = BAUD_RATE) -> np.ndarray:
    """
    Derive synthetic timestamps from the baud rate for each byte.
    """
    bits_per_byte = 10 
    seconds_per_byte = bits_per_byte / baud
    
    indices = np.arange(len(raw), dtype=np.float64)
    timestamps = indices * seconds_per_byte
    
    logger.debug(f"Generated {len(timestamps)} timestamps based on {baud} baud.")
    return timestamps


def validate_stream(raw: np.ndarray) -> Dict[str, Union[int, float, bool]]:
    """
    Perform basic sanity checks on the raw stream.
    """
    stats = {
        "byte_count": len(raw),
        "min_value": int(np.min(raw)) if len(raw) > 0 else 0,
        "max_value": int(np.max(raw)) if len(raw) > 0 else 0,
        "is_non_null": bool(np.any(raw != 0)),
        "null_byte_percentage": float((raw == 0).sum() / len(raw) * 100) if len(raw) > 0 else 0.0
    }
    
    logger.info(f"Stream validation: {stats}")
    return stats
