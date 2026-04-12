"""
Visualisation module for generating SIGINT-ready plots and charts.
Uses seaborn and matplotlib for high-fidelity output.
"""

import logging
import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from antigravity.config import PLOT_STYLE, PLOTS_DIR
from antigravity.models import Packet, StreamStats

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize plot style
sns.set_theme(style=PLOT_STYLE["style"])


def plot_raw_bytes(raw: np.ndarray, packets: List[Packet]):
    """
    Scatter plot of raw byte values over time with packet boundaries.
    """
    plt.figure(figsize=PLOT_STYLE["figsize_ts"])
    
    # Sample data if too large for performance
    indices = np.arange(len(raw))
    if len(raw) > 10000:
        step = len(raw) // 10000
        indices = indices[::step]
        raw_sampled = raw[::step]
    else:
        raw_sampled = raw

    plt.scatter(indices, raw_sampled, s=1, alpha=0.3, color='blue', label='Byte Value')
    
    # Add vertical lines at packet starts (first 50 for visibility)
    for p in packets[:50]:
        # We index by byte offset here for the x-axis
        # Finding start byte of packet p
        start_idx = p.index * 38 # Heuristic boundary
        plt.axvline(x=start_idx, color='red', linestyle='--', linewidth=0.5, alpha=0.5)
        
    plt.title("Raw Byte Values & Packet Boundaries")
    plt.xlabel("Byte Offset")
    plt.ylabel("Byte Value (0-255)")
    plt.ylim(-5, 260)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "raw_byte_values.png"), dpi=PLOT_STYLE["dpi"])
    plt.close()


def plot_sequence_counters(packets: List[Packet]):
    """
    Sawtooth plot showing sequence counter rollover per stream ID.
    """
    plt.figure(figsize=PLOT_STYLE["figsize_ts"])
    
    data = []
    for p in packets:
        data.append({
            "index": p.index,
            "stream_id": p.stream_id,
            "sequence": p.flags
        })
    df = pd.DataFrame(data)
    
    sns.lineplot(data=df, x="index", y="sequence", hue="stream_id", palette="bright", marker='o', markersize=2)
    
    plt.title("Sequence Counter Rollover Patterns")
    plt.xlabel("Packet Index")
    plt.ylabel("Sequence (Flags Byte Value)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "sequence_counter.png"), dpi=PLOT_STYLE["dpi"])
    plt.close()


def plot_ipg(ipg_ms: np.ndarray):
    """
    Stem plot of inter-packet gaps.
    """
    plt.figure(figsize=PLOT_STYLE["figsize_ts"])
    
    # Only plot first 200 gaps for clarity
    plot_data = ipg_ms[:200]
    indices = np.arange(len(plot_data))
    
    plt.stem(indices, plot_data)
    plt.axhline(y=1.0, color='red', linestyle='--', label='1ms Threshold')
    
    plt.title("Inter-Packet Gaps (IPG)")
    plt.xlabel("Gap Index")
    plt.ylabel("Gap (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "inter_packet_gap.png"), dpi=PLOT_STYLE["dpi"])
    plt.close()


def plot_sync_freq(packets: List[Packet]):
    """
    Bar chart of Start-Of-Frame (SOF) byte frequencies.
    """
    plt.figure(figsize=PLOT_STYLE["figsize_std"])
    
    sofs = [p.stream_id for p in packets]
    df = pd.Series(sofs).value_counts().reset_index()
    df.columns = ["SOF", "Count"]
    
    sns.barplot(data=df, x="SOF", y="Count", palette="viridis")
    
    plt.title("Sync Byte Frequency (SOF)")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "sync_byte_frequency.png"), dpi=PLOT_STYLE["dpi"])
    plt.close()


def plot_packet_structure(stats: StreamStats):
    """
    Pie chart showing the ratio of Header vs Avg Payload.
    """
    plt.figure(figsize=PLOT_STYLE["figsize_std"])
    
    # 4 bytes fixed header
    header = 4
    payload = max(0, stats.dominant_size - header)
    
    labels = ["Header (Plaintext)", "Payload (Encrypted)"]
    sizes = [header, payload]
    colors = ['#ff9999','#66b3ff']
    
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title("Average Packet Structure")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "avg_packet_structure.png"), dpi=PLOT_STYLE["dpi"])
    plt.close()


def generate_all_plots(raw: np.ndarray, packets: List[Packet], ipg_ms: np.ndarray, stats: StreamStats):
    """
    Utility to run all plotting functions.
    """
    plot_raw_bytes(raw, packets)
    plot_sequence_counters(packets)
    plot_ipg(ipg_ms)
    plot_sync_freq(packets)
    plot_packet_structure(stats)
    logger.info(f"All plots generated and saved to {PLOTS_DIR}")
