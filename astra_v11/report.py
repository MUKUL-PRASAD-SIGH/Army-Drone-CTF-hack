"""
Report module for exporting analysis results in various formats.
"""

import base64
import csv
import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from astra_v11.models import InferenceResult, Packet, StreamStats

logger = logging.getLogger(__name__)


def build_json_summary(stats: StreamStats, result: InferenceResult) -> Dict:
    """
    Build a comprehensive machine-readable dictionary of the analysis.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "statistics": stats.__dict__,
        "inference": result.__dict__
    }


def export_csv(packets: List[Packet], path: str):
    """
    Export the packet list to a CSV file.
    """
    fieldnames = [
        'index', 'timestamp', 'sof', 'msg_class', 
        'flags', 'length', 'direction', 'stream_id', 'raw_hex'
    ]
    
    try:
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in packets:
                row = {
                    'index': p.index,
                    'timestamp': p.timestamp,
                    'sof': hex(p.sof),
                    'msg_class': hex(p.msg_class),
                    'flags': hex(p.flags),
                    'length': p.length,
                    'direction': p.direction,
                    'stream_id': p.stream_id,
                    'raw_hex': p.raw.hex()
                }
                writer.writerow(row)
        logger.info(f"Packets exported to CSV: {path}")
    except Exception as e:
        logger.error(f"Failed to export CSV: {e}")


def _get_image_base64(path: str) -> str:
    """Helper to read image and return base64 string."""
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate_html_report(
    stats: StreamStats, 
    result: InferenceResult, 
    plot_paths: Dict[str, str]
) -> str:
    """
    Generate a high-quality, self-contained HTML report.
    """
    img_tags = {}
    for name, path in plot_paths.items():
        b64 = _get_image_base64(path)
        img_tags[name] = f"data:image/png;base64,{b64}" if b64 else ""

    severity = "HIGH" if result.confidence > 0.8 else "MEDIUM" if result.confidence > 0.4 else "LOW"
    severity_class = "text-danger" if severity == "HIGH" else "text-warning" if severity == "MEDIUM" else "text-success"

    evidence_html = "".join([f"<li>{e}</li>" for e in result.evidence_list])
    commands_html = "".join([f"<span class='badge bg-primary m-1'>{c}</span>" for c in result.command_types])

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASTRA-V11 SIGINT Intel Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .header-section {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 2rem 0; margin-bottom: 2rem; }}
        .card {{ margin-bottom: 1.5rem; border: None; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .plot-container {{ text-align: center; padding: 1rem; }}
        .plot-img {{ max-width: 100%; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header-section text-center">
        <h1>ASTRA-V11 SIGINT Intel Report</h1>
        <p>Session ID: 868MHz_QNu_Qore_Encrypted</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="container">
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title">Target Inference</h4>
                        <table class="table">
                            <tr><th>Platform</th><td>{result.platform}</td></tr>
                            <tr><th>Protocol</th><td>{result.protocol}</td></tr>
                            <tr><th>Confidence</th><td><strong class="{severity_class}">{result.confidence*100:.1f}%</strong></td></tr>
                            <tr><th>Severity</th><td><span class="badge {'bg-danger' if severity=='HIGH' else 'bg-warning'}">{severity}</span></td></tr>
                        </table>
                        <h5>Evidence</h5>
                        <ul>{evidence_html}</ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title">Stream Statistics</h4>
                        <table class="table">
                            <tr><th>Total Packets</th><td>{stats.n_packets}</td></tr>
                            <tr><th>Baud Rate</th><td>{stats.baud_inferred}</td></tr>
                            <tr><th>Dominant Size</th><td>{stats.dominant_size} bytes</td></tr>
                            <tr><th>Payload Entropy</th><td>{stats.entropy_payload:.2f} bits/byte</td></tr>
                        </table>
                        <h5>Probable Commands</h5>
                        <div>{commands_html}</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h4>Visual Analysis</h4>
                        <div class="row">
                            <div class="col-md-6 plot-container">
                                <h6>Raw Byte Distribution</h6>
                                <img src="{img_tags.get('raw', '')}" class="plot-img">
                            </div>
                            <div class="col-md-6 plot-container">
                                <h6>Sequence Rollover</h6>
                                <img src="{img_tags.get('sequence', '')}" class="plot-img">
                            </div>
                            <div class="col-md-4 plot-container">
                                <h6>Sync Frequencies</h6>
                                <img src="{img_tags.get('sync', '')}" class="plot-img">
                            </div>
                            <div class="col-md-4 plot-container">
                                <h6>Inter-Packet Gaps</h6>
                                <img src="{img_tags.get('ipg', '')}" class="plot-img">
                            </div>
                            <div class="col-md-4 plot-container">
                                <h6>Structure Ratio</h6>
                                <img src="{img_tags.get('structure', '')}" class="plot-img">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="text-center mt-4 text-muted">
            <p>&copy; 2026 ASTRA-V11 SIGINT Systems Engineering</p>
        </footer>
    </div>
</body>
</html>
"""
    return html
