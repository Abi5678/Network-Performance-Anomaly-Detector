# -*- coding: utf-8 -*-
"""Prometheus metrics exporter for Network Anomaly Detector.

Exposes pipeline metrics for Grafana dashboards:
- Total flows processed
- Anomalies detected
- Latency statistics
- Packet loss statistics
- Signal quality statistics
- Processing time
"""

import os
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# Metrics storage (thread-safe)
_metrics = {
    "flows_processed_total": 0,
    "anomalies_detected_total": 0,
    "latency_ms_avg": 0.0,
    "latency_ms_max": 0.0,
    "latency_ms_min": 0.0,
    "packet_loss_pct_avg": 0.0,
    "packet_loss_pct_max": 0.0,
    "signal_quality_avg": 0.0,
    "signal_quality_min": 0.0,
    "processing_time_seconds": 0.0,
    "last_run_timestamp": 0,
    "model_trained": 0,
}
_metrics_lock = threading.Lock()


def update_metrics(
    flows_processed: int = 0,
    anomalies_detected: int = 0,
    latency_avg: float = 0.0,
    latency_max: float = 0.0,
    latency_min: float = 0.0,
    packet_loss_avg: float = 0.0,
    packet_loss_max: float = 0.0,
    signal_quality_avg: float = 0.0,
    signal_quality_min: float = 0.0,
    processing_time: float = 0.0,
    model_trained: bool = False,
):
    """Update metrics with latest pipeline run results."""
    with _metrics_lock:
        _metrics["flows_processed_total"] += flows_processed
        _metrics["anomalies_detected_total"] += anomalies_detected
        _metrics["latency_ms_avg"] = latency_avg
        _metrics["latency_ms_max"] = latency_max
        _metrics["latency_ms_min"] = latency_min
        _metrics["packet_loss_pct_avg"] = packet_loss_avg
        _metrics["packet_loss_pct_max"] = packet_loss_max
        _metrics["signal_quality_avg"] = signal_quality_avg
        _metrics["signal_quality_min"] = signal_quality_min
        _metrics["processing_time_seconds"] = processing_time
        _metrics["last_run_timestamp"] = time.time()
        _metrics["model_trained"] = 1 if model_trained else 0


def update_from_dataframe(df, processing_time: float = 0.0, model_trained: bool = False):
    """Update metrics from a pandas DataFrame with detection results."""
    if df is None or df.empty:
        return

    anomalies = df[df.get("is_anomaly", False) == True] if "is_anomaly" in df.columns else df.head(0)

    update_metrics(
        flows_processed=len(df),
        anomalies_detected=len(anomalies),
        latency_avg=df["latency_ms"].mean() if "latency_ms" in df.columns else 0,
        latency_max=df["latency_ms"].max() if "latency_ms" in df.columns else 0,
        latency_min=df["latency_ms"].min() if "latency_ms" in df.columns else 0,
        packet_loss_avg=df["packet_loss_pct"].mean() if "packet_loss_pct" in df.columns else 0,
        packet_loss_max=df["packet_loss_pct"].max() if "packet_loss_pct" in df.columns else 0,
        signal_quality_avg=df["signal_quality"].mean() if "signal_quality" in df.columns else 0,
        signal_quality_min=df["signal_quality"].min() if "signal_quality" in df.columns else 0,
        processing_time=processing_time,
        model_trained=model_trained,
    )


def get_metrics_text():
    """Generate Prometheus-formatted metrics text."""
    with _metrics_lock:
        lines = [
            "# HELP network_anomaly_flows_processed_total Total number of network flows processed",
            "# TYPE network_anomaly_flows_processed_total counter",
            f"network_anomaly_flows_processed_total {_metrics['flows_processed_total']}",
            "",
            "# HELP network_anomaly_anomalies_detected_total Total number of anomalies detected",
            "# TYPE network_anomaly_anomalies_detected_total counter",
            f"network_anomaly_anomalies_detected_total {_metrics['anomalies_detected_total']}",
            "",
            "# HELP network_anomaly_latency_ms_avg Average latency in milliseconds",
            "# TYPE network_anomaly_latency_ms_avg gauge",
            f"network_anomaly_latency_ms_avg {_metrics['latency_ms_avg']:.2f}",
            "",
            "# HELP network_anomaly_latency_ms_max Maximum latency in milliseconds",
            "# TYPE network_anomaly_latency_ms_max gauge",
            f"network_anomaly_latency_ms_max {_metrics['latency_ms_max']:.2f}",
            "",
            "# HELP network_anomaly_latency_ms_min Minimum latency in milliseconds",
            "# TYPE network_anomaly_latency_ms_min gauge",
            f"network_anomaly_latency_ms_min {_metrics['latency_ms_min']:.2f}",
            "",
            "# HELP network_anomaly_packet_loss_pct_avg Average packet loss percentage",
            "# TYPE network_anomaly_packet_loss_pct_avg gauge",
            f"network_anomaly_packet_loss_pct_avg {_metrics['packet_loss_pct_avg']:.4f}",
            "",
            "# HELP network_anomaly_packet_loss_pct_max Maximum packet loss percentage",
            "# TYPE network_anomaly_packet_loss_pct_max gauge",
            f"network_anomaly_packet_loss_pct_max {_metrics['packet_loss_pct_max']:.4f}",
            "",
            "# HELP network_anomaly_signal_quality_avg Average signal quality",
            "# TYPE network_anomaly_signal_quality_avg gauge",
            f"network_anomaly_signal_quality_avg {_metrics['signal_quality_avg']:.2f}",
            "",
            "# HELP network_anomaly_signal_quality_min Minimum signal quality",
            "# TYPE network_anomaly_signal_quality_min gauge",
            f"network_anomaly_signal_quality_min {_metrics['signal_quality_min']:.2f}",
            "",
            "# HELP network_anomaly_processing_time_seconds Time taken to process last batch",
            "# TYPE network_anomaly_processing_time_seconds gauge",
            f"network_anomaly_processing_time_seconds {_metrics['processing_time_seconds']:.3f}",
            "",
            "# HELP network_anomaly_last_run_timestamp Unix timestamp of last pipeline run",
            "# TYPE network_anomaly_last_run_timestamp gauge",
            f"network_anomaly_last_run_timestamp {_metrics['last_run_timestamp']:.0f}",
            "",
            "# HELP network_anomaly_model_trained Whether the model has been trained (1) or not (0)",
            "# TYPE network_anomaly_model_trained gauge",
            f"network_anomaly_model_trained {_metrics['model_trained']}",
        ]
        return "\n".join(lines) + "\n"


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for Prometheus metrics endpoint."""

    def do_GET(self):
        if self.path == "/metrics":
            content = get_metrics_text()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


class MetricsServer:
    """Background HTTP server for Prometheus metrics."""

    def __init__(self, port: int = 8000):
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """Start the metrics server in a background thread."""
        self.server = HTTPServer(("0.0.0.0", self.port), MetricsHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[METRICS] Prometheus metrics server started on port {self.port}")

    def stop(self):
        """Stop the metrics server."""
        if self.server:
            self.server.shutdown()
            print("[METRICS] Prometheus metrics server stopped")


# Global server instance
_server = None


def start_metrics_server(port: int = 8000):
    """Start the global metrics server."""
    global _server
    if _server is None:
        _server = MetricsServer(port)
        _server.start()


def stop_metrics_server():
    """Stop the global metrics server."""
    global _server
    if _server:
        _server.stop()
        _server = None


if __name__ == "__main__":
    # Test the metrics server
    print("Starting metrics server on port 8000...")
    start_metrics_server(8000)

    # Simulate some metrics
    import pandas as pd
    import numpy as np

    test_df = pd.DataFrame({
        "latency_ms": np.random.normal(30, 5, 100),
        "packet_loss_pct": np.random.exponential(0.1, 100),
        "signal_quality": np.random.normal(15, 2, 100),
        "is_anomaly": [False] * 95 + [True] * 5,
    })

    update_from_dataframe(test_df, processing_time=1.23, model_trained=True)

    print("Metrics available at http://localhost:8000/metrics")
    print("Press Ctrl+C to stop...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_metrics_server()
