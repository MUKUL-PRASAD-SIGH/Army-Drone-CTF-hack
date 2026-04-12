<div align="center">

# ASTRA-V11
## ADVANCED SIGINT TELEMETRY RECONNAISSANCE & ANALYSIS

![System Profile](https://img.shields.io/badge/System-SIGINT_PIPELINE-1e3c72?style=for-the-badge)
![Security](https://img.shields.io/badge/Link-POST_QUANTUM_ENCRYPTED-2a5298?style=for-the-badge)
![Compliance](https://img.shields.io/badge/Protocol-MAVLINK_V2-blue?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)
![Testing](https://img.shields.io/badge/Tests-100%25_Passing-brightgreen?style=flat-square)
![Analysis](https://img.shields.io/badge/Analysis-Multilayer-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

</div>

ASTRA-V11 is an elite signals intelligence (SIGINT) framework specifically engineered for the deconstruction of high-security drone-to-GCS telemetry links. Designed for 868 MHz post-quantum encrypted streams, the pipeline provides a deterministic approach to recovering intelligence from uncrackable UART data.

---

### ARCHITECTURAL FRAMEWORK

The system utilizes a specialized **Seven-Layer Inversion Stack** to process raw radio-frequency captures into actionable intelligence:

| Layer | Component | Functionality |
| :--- | :--- | :--- |
| **L1** | **Ingestion** | Multi-source loading for BIN, HEX, and CSV formats with microsecond-precision timing normalization. |
| **L2** | **Segmentation** | Algorithmic frame extraction using temporal gap analysis and SOF marker isolation. |
| **L3** | **Decryption Prep** | Packet header parsing, directionality mapping, and multi-stream identification. |
| **L4** | **Cryptometrics** | High-fidelity statistical analysis including Shannon Entropy and Chi-Square uniformity testing. |
| **L5** | **Inference** | Automated platform fingerprinting and protocol class identification (MAVLink v2). |
| **L6** | **Signal Viz** | Generation of complex analytical plots: Sequence Rollover, IPG Stem, and Byte Value Heatmaps. |
| **L7** | **Intelligence** | Automated HTML/JSON/CSV reporting with embedded visual evidence and metadata. |

---

### TECHNICAL SPECIFICATIONS

| Metric | Specification |
| :--- | :--- |
| **Baud Rate Support** | 115,200 bps (Standard) / Variable |
| **Packet Structure** | 4-Byte Plaintext Header / Variable Payload |
| **Entropy Target** | 7.80 bits/byte (Encrypted Region) |
| **Timing Accuracy** | ±10 microseconds |
| **Analysis Period** | 420.95 Seconds (Capture Duration) |

---

### SYSTEM DEPLOYMENT

```bash
# Initialize Environment
git clone https://github.com/rohan-chand-m-01/ASTRA-V11.git
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install Analysis Dependencies
pip install -r requirements.txt
```

### PIPELINE EXECUTION

Execute the full suite with visualization and telemetry reporting:

```bash
python -m astra_v11.main --input data/capture.bin --plots --report all --verbose
```

---

### ANALYSIS TEAM

*   **Rohan**
*   **Abhisek Reddy**
*   **Mukul Prasad**
*   **Kishan J**
*   **Sandeesh**

---

<div align="center">

**CLASSIFICATION: UNRESTRICTED CORE**
PRODUCED BY ASTRA-V11 SYSTEMS ENGINEERING

</div>
