<div align="center">

# ASTRA-V11
### Advanced SIGINT Telemetry Reconnaissance & Analysis

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge)
![Security Audit](https://img.shields.io/badge/security-audited-orange?style=for-the-badge)
![Coverage](https://img.shields.io/badge/coverage-100%25-success?style=for-the-badge)

---

</div>

ASTRA-V11 is a production-grade SIGINT analysis framework engineered to deconstruct and fingerprint post-quantum encrypted UART telemetry. Developed for the "Crack the Uncrackable" drone-GCS challenge, this pipeline provides deep-packet inspection, statistical cryptographic analysis, and automated intelligence reporting for QNu Qore encrypted links.

## Core Capabilities

The system implements a modular 7-layer architecture designed for maximum reliability and analytical depth:

### Layer 1: Data Ingestion
Hybrid loader supporting Binary, Intel HEX, and CSV formats. Implements synthetic jitter-aware timing derivation based on standard UART 8N1 framing.

### Layer 2: Temporal Segmentation
Packet slicing using high-precision Inter-Packet Gap (IPG) analysis (~1ms threshold) and Start-Of-Frame (SOF) marker fallback for fragmented streams.

### Layer 3: Protocol Semantic Decoding
Header extraction and direction classification (Drone vs. GCS). Handles multi-stream identification for complex mesh-relay scenarios.

### Layer 4: Cryptographic Statistical Analysis
Verification of encryption quality via Shannon Entropy (Target: 7.8+ bits/byte), Chi-Square uniformity testing, and ECB/Keystream-reuse detection.

### Layer 5: Heuristic Inference Engine
Automated platform identification (Pixhawk/Qore) and protocol fingerprinting (MAVLink v2). Inferred results include baud rate, flight duration, and burst periodicity.

### Layer 6: Signal Visualization
Generation of high-fidelity analytics including sequence counter rollover trajectories, IPG stem plots, and raw byte distribution maps.

### Layer 7: Intelligence Reporting
Export of self-contained HTML Intelligence Reports with embedded visual evidence, machine-readable JSON summaries, and full packet-level CSV exports.

## Technical Stack

The ASTRA-V11 pipeline leverages high-performance Python libraries for specialized analysis:

*   **Analysis Core**: NumPy, SciPy (Signal Processing), pandas (Data Analytics)
*   **Visual Intelligence**: Matplotlib (Fine-grain Plotting), Seaborn (High-level Statistical Viz)
*   **Terminal Interface**: Rich (CLI Rendering & Real-time Logging)
*   **Validation Suite**: Pytest (100% Logic Coverage)

## Execution Flow

The pipeline follows a strict unidirectional data flow to maintain state integrity:

1.  **Ingest**: Raw stream validation and timestamp generation.
2.  **Segment**: Data packetization and boundary detection.
3.  **Decode**: Header parsing and sequence tracking.
4.  **Analyze**: Entropy calculation and pattern discovery.
5.  **Infer**: Platform matching and confidence scoring.
6.  **Report**: Visual and data export for final delivery.

## Installation & Deployment

```bash
# Clone the secured repository
git clone https://github.com/rohan-chand-m-01/ASTRA-V11.git
cd astra_v11

# Resolve dependencies
pip install -r requirements.txt
```

## Usage

### standard Pipeline Execution
```bash
python -m astra_v11.main --input data/capture.bin --plots --report all
```

### Advanced Debug Mode
```bash
python -m astra_v11.main --input data/capture.csv --verbose --report json
```

## Analysis Team

Development and maintenance of the ASTRA-V11 framework is led by the following core SIGINT engineering team:

*   **Rohan** (Lead Architect)
*   **Abhisek Reddy** (Crypto-Analyst)
*   **Mukul Prasad** (Systems Engineer)
*   **Kishan J** (Visualization Expert)
*   **Sandeesh** (Protocol Specialist)

---

<div align="center">

**NOT FOR UNAUTHORIZED DISCLOSURE**
ASTRA-V11 Proprietary Framework

</div>
