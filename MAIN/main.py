"""
Main entry point for the Antigravity SIGINT analysis pipeline.
Orchestrates the data flow from ingestion to reporting.
"""

import argparse
import json
import logging
import os
import sys
from typing import List

from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from antigravity import (
    config,
    crypto,
    inference,
    ingest,
    protocol,
    report,
    segmenter,
    visualise,
)
from antigravity.models import Packet

# Initialize Rich console
console = Console()


def setup_logging(verbose: bool):
    """Configure logging with Rich support."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )


def run_pipeline(args):
    """Execute the SIGINT processing pipeline."""
    setup_logging(args.verbose)
    
    logger = logging.getLogger("pipeline")
    logger.info("[bold blue]Starting Antigravity SIGINT Pipeline...[/]", extra={"markup": True})

    # 1. Ingestion
    logger.info("Phase 1: Ingesting raw stream...")
    if not args.input or not os.path.exists(args.input):
        logger.warning(f"Input file '{args.input}' not found. Using internal mock data for demonstration.")
        # Generate 207k bytes of mock data with SOF markers
        import numpy as np
        # 5400 packets of 38 bytes
        packet_template = [0xAA, 0x01, 0x00, 0x22] + [0]*34
        raw = np.tile(np.array(packet_template, dtype=np.uint8), 5400)
        # Add some variation to simulate encrypted payload
        raw[4::38] = np.random.randint(0, 256, 5400, dtype=np.uint8)
    else:
        raw = ingest.load_raw(args.input)
    
    # Generate timestamps with synthetic gaps to ensure segmentation works
    if not args.input or not os.path.exists(args.input):
        # Every 38 bytes, add 2ms gap
        indices = np.arange(len(raw))
        base_ts = indices * (10 / config.BAUD_RATE)
        gaps = (indices // 38) * 0.002 # 2ms gap every 38 bytes
        timestamps = base_ts + gaps
    else:
        timestamps = ingest.extract_timestamps(raw, config.BAUD_RATE)
        
    ingest_stats = ingest.validate_stream(raw)

    # 2. Segmentation
    logger.info("Phase 2: Segmenting packets...")
    packets = segmenter.segment_by_gap(raw, timestamps, config.GAP_THRESHOLD_MS)
    if len(packets) < 10: # If mock didn't gap properly
        logger.warning("Few packets found via gap segmentation. Falling back to SOF markers.")
        packets = segmenter.segment_by_sof(raw)

    # 3. Protocol Decode
    logger.info(f"Phase 3: Decoding protocol headers for {len(packets)} packets...")
    transitions = protocol.analyze_transitions(packets)
    seq_counters = protocol.compute_sequence_counters(packets)

    # 4. Crypto Analysis
    logger.info("Phase 4: Statistical crypto analysis...")
    entropy_map = crypto.per_region_entropy(packets)
    ecb_detected = crypto.detect_ecb(packets)
    freq = crypto.byte_frequency(raw)
    chi_stat, p_val = crypto.chi_square_uniformity(freq)

    # 5. Inference
    logger.info("Phase 5: Inferring protocol and platform...")
    stats = inference.infer_session_params(packets, timestamps)
    stats.entropy_header = entropy_map["header"]
    stats.entropy_payload = entropy_map["payload"]
    
    result = inference.fingerprint_protocol(stats)
    intel_table = inference.generate_intel_table(result)

    # 6. Visualisation
    if args.plots:
        logger.info("Phase 6: Generating visualisation plots...")
        ipg_ms = segmenter.compute_ipg(timestamps)
        visualise.generate_all_plots(raw, packets, ipg_ms, stats)

    # 7. Reporting
    logger.info("Phase 7: Exporting reports...")
    output_dir = args.output or config.OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    if args.report in ['json', 'all']:
        sum_json = report.build_json_summary(stats, result)
        with open(os.path.join(output_dir, "summary.json"), 'w') as f:
            json.dump(sum_json, f, indent=4)
        logger.info(f"JSON report saved to {output_dir}")

    if args.report in ['csv', 'all']:
        report.export_csv(packets, os.path.join(output_dir, "packets.csv"))
        logger.info(f"CSV report saved to {output_dir}")

    if args.report in ['html', 'all']:
        plot_paths = {
            'raw': os.path.join(config.PLOTS_DIR, "raw_byte_values.png"),
            'sequence': os.path.join(config.PLOTS_DIR, "sequence_counter.png"),
            'ipg': os.path.join(config.PLOTS_DIR, "inter_packet_gap.png"),
            'sync': os.path.join(config.PLOTS_DIR, "sync_byte_frequency.png"),
            'structure': os.path.join(config.PLOTS_DIR, "avg_packet_structure.png")
        }
        html_content = report.generate_html_report(stats, result, plot_paths)
        with open(os.path.join(output_dir, "report.html"), 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"HTML report saved to {output_dir}")

    # Final Summary CLI Table
    print_summary_table(stats, result)


def print_summary_table(stats, result):
    """Print a beautiful summary table using Rich."""
    table = Table(title="[bold cyan]Antigravity Pipeline Execution Summary[/]", title_justify="left")

    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Total Packets", str(stats.n_packets))
    table.add_row("Detected Platform", result.platform)
    table.add_row("Identified Protocol", result.protocol)
    table.add_row("Confidence", f"{result.confidence*100:.1f}%")
    table.add_row("Payload Entropy", f"{stats.entropy_payload:.2f} bits/byte")
    table.add_row("Baud Rate Inferred", f"{stats.baud_inferred} bps")
    
    console.print("\n")
    console.print(table)
    console.print("\n[bold green]Pipeline completed successfully![/]")


def main():
    parser = argparse.ArgumentParser(description="Antigravity Drone-GCS UART SIGINT Pipeline")
    parser.add_argument("--input", help="Path to encrypted dataset")
    parser.add_argument("--format", choices=['csv', 'bin', 'hex'], help="Input format")
    parser.add_argument("--output", help="Output directory for reports")
    parser.add_argument("--plots", action="store_true", help="Generate visualisation plots")
    parser.add_argument("--report", default="all", choices=['json', 'csv', 'html', 'all'], help="Export format")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    
    try:
        run_pipeline(args)
    except Exception as e:
        console.print(f"[bold red]Pipeline Error:[/] {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
