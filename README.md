# Network Performance Anomaly Detector

A production-ready data engineering pipeline designed to monitor high-throughput network performance and detect chronic application-level issues using Machine Learning and real-world telemetry.

## Overview

This system demonstrates a ground-based software solution for processing and analyzing large-scale network metrics. It is specifically architected to handle the types of data challenges found in satellite-to-cell constellations (like Starlink Direct-to-Cell), where latency, packet loss, and signal integrity are paramount.

The pipeline processes **real-world network traces from the MAWI Working Group** to identify anomalies that could indicate widespread application issues, making it suitable for monitoring critical infrastructure and ensuring high service reliability.

## Features

- **Real PCAP Data Ingestion** - Downloads and parses actual network traces from MAWI repository
- **Isolation Forest Anomaly Detection** - Unsupervised ML for detecting network anomalies
- **Prometheus Metrics Export** - Real-time metrics for Grafana dashboards
- **Streaming Mode** - Continuous monitoring with configurable intervals
- **Comprehensive Visualizations** - 7 different plot types for analysis
- **Docker Support** - Containerized deployment with docker-compose
- **Configurable Pipeline** - Environment variables and CLI arguments

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Data Processing | Pandas, NumPy, PyArrow |
| Storage | Apache Parquet (Snappy compression) |
| Machine Learning | Scikit-learn (Isolation Forest) |
| PCAP Parsing | dpkt |
| Visualization | Matplotlib, Seaborn |
| Metrics | Prometheus-compatible HTTP exporter |
| Containerization | Docker, docker-compose |
| Data Source | MAWI Working Group network traces |

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Abi5678/Network-Performance-Anomaly-Detector.git
cd Network-Performance-Anomaly-Detector
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run with default settings (downloads ~1.2GB PCAP, processes 100k packets)
python network_anomaly_detector.py

# Use a pre-trained model (faster, skips training)
python network_anomaly_detector.py --load-model

# Process more packets for better accuracy
python network_anomaly_detector.py --max-packets 200000

# Skip plot generation for faster execution
python network_anomaly_detector.py --no-plots
```

### Streaming Mode (Continuous Monitoring)

```bash
# Run in continuous streaming mode
python network_anomaly_detector.py --streaming --interval 60

# Full production setup with metrics
python network_anomaly_detector.py --streaming --metrics --interval 300
```

### Prometheus Metrics

```bash
# Enable metrics server on port 8000
python network_anomaly_detector.py --metrics

# Custom port
python network_anomaly_detector.py --metrics --metrics-port 9090
```

Access metrics at: `http://localhost:8000/metrics`

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t network-anomaly-detector .

# Run with default settings
docker run -p 8000:8000 network-anomaly-detector

# Run with custom arguments
docker run -p 8000:8000 network-anomaly-detector --max-packets 50000 --metrics
```

### Docker Compose (Full Stack)

Launch the complete monitoring stack with Prometheus and Grafana:

```bash
docker-compose up -d
```

Access:
- **Anomaly Detector Metrics**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Project Structure

```
Network-Performance-Anomaly-Detector/
│
├── network_anomaly_detector.py   # Main pipeline orchestration
├── visualize.py                  # Visualization module (7 plot types)
├── metrics_exporter.py           # Prometheus metrics exporter
├── config.py                     # Centralized configuration
│
├── tests/                        # Unit tests
│   ├── __init__.py
│   └── test_pipeline.py
│
├── data/                         # Data storage
│   ├── raw/                      # Downloaded PCAP files, raw CSV
│   └── processed/                # Parquet files, reports
│       └── plots/                # Generated visualizations
│
├── models/                       # Trained ML models
│   ├── isolation_forest.pkl
│   └── scaler.pkl
│
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Full stack deployment
├── prometheus.yml                # Prometheus configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## CLI Reference

```
usage: network_anomaly_detector.py [-h] [--pcap-url PCAP_URL]
                                   [--max-packets MAX_PACKETS]
                                   [--contamination CONTAMINATION]
                                   [--load-model] [--no-plots]
                                   [--metrics] [--metrics-port METRICS_PORT]
                                   [--streaming] [--interval INTERVAL]

Options:
  --pcap-url URL        MAWI PCAP URL to download (default: 2019 sample)
  --max-packets N       Maximum packets to parse (default: 100000)
  --contamination F     Expected anomaly fraction (default: 0.05)
  --load-model          Load saved model instead of retraining
  --no-plots            Skip generating visualization plots
  --metrics             Enable Prometheus metrics server
  --metrics-port PORT   Prometheus metrics port (default: 8000)
  --streaming           Enable continuous streaming mode
  --interval SECONDS    Streaming interval (default: 300)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MAX_PACKETS` | Maximum packets to process | 100000 |
| `CONTAMINATION` | Anomaly fraction | 0.05 |
| `PROMETHEUS_ENABLED` | Enable metrics server | false |
| `PROMETHEUS_PORT` | Metrics server port | 8000 |
| `STREAMING_ENABLED` | Enable streaming mode | false |
| `STREAMING_INTERVAL` | Interval in seconds | 300 |
| `LOG_LEVEL` | Logging level | INFO |

## Visualizations

The pipeline generates 7 comprehensive plots:

1. **Time Series** - Metrics over time with anomaly highlights
2. **Distributions** - Histograms and box plots (normal vs anomalous)
3. **Correlation Heatmap** - Feature correlation matrix
4. **2D Scatter Plots** - Feature pairs colored by anomaly status
5. **3D Scatter Plot** - All features in 3D space
6. **Anomaly Score Distribution** - Isolation Forest score histogram
7. **Summary Dashboard** - Combined overview with statistics

## How It Works

### Data Flow

```
MAWI PCAP Repository
        │
        ▼
┌───────────────────┐
│  Download PCAP    │  (~1.2 GB compressed)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Parse Packets    │  Extract flows with dpkt
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Derive Metrics   │  latency, packet_loss, signal_quality
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Store Parquet    │  Columnar storage with Snappy
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Train Model      │  Isolation Forest (contamination=5%)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Detect Anomalies │  Score and flag outliers
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Export Reports   │  CSV + Visualizations + Metrics
└───────────────────┘
```

### Feature Derivation

From raw packet data, the pipeline derives:

| Feature | Description | Derivation |
|---------|-------------|------------|
| `latency_ms` | Inter-packet delay | Mean of timestamp differences within flows |
| `packet_loss_pct` | Packet loss proxy | Derived from packet size variance |
| `signal_quality` | Signal quality proxy | Inverse of jitter (delay variance) |

### Anomaly Detection

The system uses **Isolation Forest**, which excels at detecting anomalies in high-dimensional data without requiring labeled training examples:

- **Contamination**: Set at 5%, meaning ~5% of traffic is expected to be anomalous
- **Features**: latency_ms, packet_loss_pct, signal_quality
- **Scaling**: StandardScaler normalization before training

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Prometheus Metrics

Available metrics at `/metrics`:

| Metric | Type | Description |
|--------|------|-------------|
| `network_anomaly_flows_processed_total` | Counter | Total flows processed |
| `network_anomaly_anomalies_detected_total` | Counter | Total anomalies detected |
| `network_anomaly_latency_ms_avg` | Gauge | Average latency |
| `network_anomaly_latency_ms_max` | Gauge | Maximum latency |
| `network_anomaly_packet_loss_pct_avg` | Gauge | Average packet loss |
| `network_anomaly_signal_quality_avg` | Gauge | Average signal quality |
| `network_anomaly_processing_time_seconds` | Gauge | Last batch processing time |
| `network_anomaly_model_trained` | Gauge | Model training status |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Abishek**

- GitHub: [@Abi5678](https://github.com/Abi5678)
- LinkedIn: [Abishek's LinkedIn](https://www.linkedin.com/in/abishek-b-m)

## Acknowledgments

- MAWI Working Group for providing real-world network trace datasets
- Scikit-learn community for robust ML implementations
- Apache Arrow project for high-performance columnar data processing

---

Built with data engineering best practices for production-grade network monitoring.
