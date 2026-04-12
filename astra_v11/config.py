"""
Configuration module for the ASTRA-V11 SIGINT analysis pipeline.
Contains all hard-coded dataset facts, file paths, and visualization settings.
"""

import os
from typing import Any, Dict

# =============================================================================
# DATASET FACTS
# =============================================================================
TOTAL_BYTES: int = 207_770
SESSION_DURATION: float = 420.95  # seconds
TOTAL_PACKETS: int = 5_414
BAUD_RATE: int = 115_200
INTER_BYTE_US: int = 85           # microseconds
GAP_THRESHOLD_MS: float = 1.0     # ms for packet segmentation
SOF_DRONE: int = 0xAA             # Drone -> GCS
SOF_GCS_1: int = 0xEE             # GCS -> Drone type 1
SOF_GCS_2: int = 0xEA             # GCS -> Drone type 2
DOMINANT_PKT_SIZE: int = 38       # bytes
HEADER_BYTES: int = 4             # plaintext header length
PAYLOAD_ENTROPY: float = 7.80     # bits/byte
HEADER_ENTROPY: float = 2.50      # bits/byte
BURST_PERIOD_S: float = 38.0      # seconds (±0.1 s)
MAVLINK_BAUD: int = 115_200       # confirms MAVLink v2 / Pixhawk

# =============================================================================
# FILE SYSTEM PATHS
# =============================================================================
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
OUTPUT_DIR: str = os.path.join(BASE_DIR, "output")
PLOTS_DIR: str = os.path.join(OUTPUT_DIR, "plots")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)

# =============================================================================
# VISUALIZATION SETTINGS
# =============================================================================
PLOT_STYLE: Dict[str, Any] = {
    "style": "whitegrid",
    "context": "talk",
    "palette": "viridis",
    "figsize_ts": (12, 3),    # Time-series
    "figsize_std": (6, 4),    # Bar/Pie
    "dpi": 300
}

# Mapping for direction identification
DIRECTION_MAP: Dict[int, str] = {
    SOF_DRONE: "DRONE->GCS",
    SOF_GCS_1: "GCS->DRONE",
    SOF_GCS_2: "GCS->DRONE"
}

STREAM_ID_MAP: Dict[int, str] = {
    SOF_DRONE: "0xAA",
    SOF_GCS_1: "0xEE",
    SOF_GCS_2: "0xEA"
}
