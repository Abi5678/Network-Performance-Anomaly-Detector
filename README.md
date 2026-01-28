# Network Performance Anomaly Detector

A mission-critical data engineering pipeline designed to monitor high-throughput network performance and detect chronic application-level issues using Machine Learning and real-world telemetry.

## 🛰️ Project Overview

This system demonstrates a ground-based software solution for processing and analyzing large-scale network metrics. It is specifically architected to handle the types of data challenges found in satellite-to-cell constellations (like Starlink Direct-to-Cell), where latency, packet loss, and signal integrity are paramount.

The pipeline processes real-world network traces to identify anomalies that could indicate widespread application issues, making it suitable for monitoring critical infrastructure and ensuring high service reliability.

## 🛠️ Tech Stack

- **Languages**: Python 3.9+ (Pandas, NumPy)
- **Data Engineering**: Apache Parquet, PyArrow (Columnar Storage & Snappy Compression)
- **Machine Learning**: Scikit-learn (Isolation Forest for Unsupervised Anomaly Detection)
- **Real-World Data**: Integrated with MAWI Working Group network traces for high-fidelity transit link modeling

## 🚀 Key Features

- **Scalable Data Ingest**: ETL logic designed to ingest raw network traces and transform them into optimized Parquet stores, simulating TB-scale historical analysis
- **Predictive Analytics**: Uses an Isolation Forest model (contamination=5%) to identify "widespread application issues" without the need for pre-labeled datasets
- **High-Throughput Partitioning**: Demonstrates advanced partitioning logic by `node_id` to optimize query performance in large-scale environments
- **Real-World Validation**: Leverages actual network telemetry from MAWI repository for production-grade testing

## 📊 Analytics Methodology

1. **Extraction**: Fetches real-world transit characteristics (latency log-normal distributions) from the MAWI repository
2. **Transformation**: Normalizes features using `StandardScaler` to prepare for multi-variate analysis
3. **Storage**: Implements highly efficient I/O using the Parquet columnar format, optimized for analytical queries
4. **Detection**: Triggers alerts when metrics deviate significantly from the baseline operating window

## 💻 Getting Started

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
pip install pandas numpy scikit-learn pyarrow requests
```

### Running the Pipeline

To run the full monitoring simulation, ingestion, and anomaly detection:

```bash
python anomaly_detector.py
```

## 📁 Project Structure

```
Network-Performance-Anomaly-Detector/
│
├── anomaly_detector.py          # Main pipeline orchestration
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
│
├── data/                         # Raw and processed data
│   ├── raw/                      # Ingested network traces
│   └── processed/                # Parquet-optimized datasets
│
└── models/                       # Trained ML models
    └── isolation_forest.pkl      # Serialized anomaly detector
```

## 🔍 How It Works

The system employs an **Isolation Forest** algorithm, which excels at detecting anomalies in high-dimensional data without requiring labeled training examples. The model:

- Analyzes network metrics including latency, packet loss, and throughput
- Identifies data points that are significantly different from normal patterns
- Flags potential application-level issues for investigation

**Contamination Rate**: Set at 5%, meaning the model expects approximately 5% of observations to be anomalous under normal operating conditions.

## 📈 Future Scope

- **Grafana Integration**: Exporting detection results to Prometheus for real-time visualization
- **Cloud Orchestration**: Deploying as a containerized service on Kubernetes to handle auto-scaling of ingestion workers
- **CI/CD**: Implementing GitLab CI/CD pipelines for automated testing of the ML model performance
- **Advanced Modeling**: Exploring time-series models (LSTM, Prophet) for temporal anomaly detection
- **Multi-Source Integration**: Expanding to ingest telemetry from multiple network monitoring sources

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Abishek**

- GitHub: [@Abi5678](https://github.com/Abi5678)
- LinkedIn: [Abishek's LinkedIn](https://www.linkedin.com/in/abishek-b-m)

## 🙏 Acknowledgments

- MAWI Working Group for providing real-world network trace datasets
- Scikit-learn community for robust ML implementations
- Apache Arrow project for high-performance columnar data processing

---
