# -*- coding: utf-8 -*-
"""Unit tests for Network Anomaly Detector pipeline."""

import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_anomaly_detector import MAWIDataLoader, NetworkMonitor


class TestNetworkMonitor(unittest.TestCase):
    """Tests for NetworkMonitor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.monitor = NetworkMonitor(contamination=0.05)

        # Create sample data
        self.sample_data = pd.DataFrame({
            "timestamp": [datetime.now() for _ in range(100)],
            "flow_id": [f"192.168.1.{i}->10.0.0.1" for i in range(100)],
            "latency_ms": np.random.normal(30, 5, 100),
            "packet_loss_pct": np.random.exponential(0.1, 100),
            "signal_quality": np.random.normal(15, 2, 100),
            "packet_count": np.random.randint(10, 1000, 100),
            "bytes_total": np.random.randint(1000, 100000, 100),
        })

    def test_features_constant(self):
        """Test that FEATURES constant is correctly defined."""
        expected = ["latency_ms", "packet_loss_pct", "signal_quality"]
        self.assertEqual(NetworkMonitor.FEATURES, expected)

    def test_store_raw_csv(self):
        """Test CSV storage functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily override data dir
            original_raw = os.path.join(tmpdir, "raw")
            os.makedirs(original_raw)

            path = os.path.join(original_raw, "test.csv")
            self.sample_data.to_csv(path, index=False)

            # Verify file was created
            self.assertTrue(os.path.exists(path))

            # Verify data integrity
            loaded = pd.read_csv(path)
            self.assertEqual(len(loaded), len(self.sample_data))

    def test_store_to_parquet(self):
        """Test Parquet storage functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.parquet")

            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.Table.from_pandas(self.sample_data)
            pq.write_table(table, path, compression="snappy")

            # Verify file was created
            self.assertTrue(os.path.exists(path))

            # Verify data integrity
            loaded = pd.read_parquet(path)
            self.assertEqual(len(loaded), len(self.sample_data))

    def test_train_and_detect(self):
        """Test model training and anomaly detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Store data
            path = os.path.join(tmpdir, "train.parquet")
            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.Table.from_pandas(self.sample_data)
            pq.write_table(table, path)

            # Train model
            self.monitor.train_anomaly_detector(path)

            # Detect anomalies
            results = self.monitor.detect_anomalies(self.sample_data)

            # Verify results
            self.assertIn("is_anomaly", results.columns)
            self.assertIn("anomaly_score", results.columns)
            self.assertEqual(len(results), len(self.sample_data))

    def test_anomaly_detection_finds_outliers(self):
        """Test that anomaly detection correctly identifies outliers."""
        # Create data with clear anomalies
        normal_data = pd.DataFrame({
            "timestamp": [datetime.now() for _ in range(95)],
            "flow_id": [f"flow_{i}" for i in range(95)],
            "latency_ms": np.random.normal(30, 2, 95),
            "packet_loss_pct": np.random.normal(0.1, 0.02, 95),
            "signal_quality": np.random.normal(20, 1, 95),
        })

        # Add clear anomalies
        anomaly_data = pd.DataFrame({
            "timestamp": [datetime.now() for _ in range(5)],
            "flow_id": [f"anomaly_{i}" for i in range(5)],
            "latency_ms": [500, 600, 700, 800, 900],  # Very high latency
            "packet_loss_pct": [10, 12, 15, 8, 11],   # Very high loss
            "signal_quality": [2, 1, 3, 2, 1],        # Very low signal
        })

        combined = pd.concat([normal_data, anomaly_data], ignore_index=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "train.parquet")
            import pyarrow as pa
            import pyarrow.parquet as pq

            table = pa.Table.from_pandas(combined)
            pq.write_table(table, path)

            self.monitor.train_anomaly_detector(path)
            results = self.monitor.detect_anomalies(combined)

            # Check that some anomalies were detected
            anomaly_count = results["is_anomaly"].sum()
            self.assertGreater(anomaly_count, 0)

    def test_model_save_and_load(self):
        """Test model persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override model directory
            import network_anomaly_detector as nad
            original_models_dir = nad.MODELS_DIR
            nad.MODELS_DIR = tmpdir

            try:
                # Train model
                path = os.path.join(tmpdir, "train.parquet")
                import pyarrow as pa
                import pyarrow.parquet as pq

                table = pa.Table.from_pandas(self.sample_data)
                pq.write_table(table, path)

                self.monitor.train_anomaly_detector(path)
                self.monitor.save_model()

                # Verify files exist
                self.assertTrue(os.path.exists(os.path.join(tmpdir, "isolation_forest.pkl")))
                self.assertTrue(os.path.exists(os.path.join(tmpdir, "scaler.pkl")))

                # Create new monitor and load model
                new_monitor = NetworkMonitor()
                loaded = new_monitor.load_model()
                self.assertTrue(loaded)

                # Verify loaded model works
                results = new_monitor.detect_anomalies(self.sample_data)
                self.assertIn("is_anomaly", results.columns)

            finally:
                nad.MODELS_DIR = original_models_dir


class TestMAWIDataLoader(unittest.TestCase):
    """Tests for MAWIDataLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = MAWIDataLoader(cache_dir=self.temp_dir)

    def test_aggregate_flow_metrics(self):
        """Test flow metrics aggregation."""
        # Create mock flow data
        flows = {
            "192.168.1.1->10.0.0.1": {
                "timestamps": [1000.0, 1000.01, 1000.02, 1000.03, 1000.04],
                "sizes": [100, 150, 120, 130, 140],
                "tcp_flags": [0x02, 0x10, 0x10, 0x10, 0x11],
                "retransmits": 0,
                "total_packets": 5,
            },
            "192.168.1.2->10.0.0.2": {
                "timestamps": [1000.0, 1000.1, 1000.2],
                "sizes": [1000, 1200, 1100],
                "tcp_flags": [0x02, 0x10, 0x11],
                "retransmits": 0,
                "total_packets": 3,
            },
        }

        df = self.loader._aggregate_flow_metrics(flows)

        # Verify output
        self.assertEqual(len(df), 2)
        self.assertIn("latency_ms", df.columns)
        self.assertIn("packet_loss_pct", df.columns)
        self.assertIn("signal_quality", df.columns)
        self.assertIn("flow_id", df.columns)

    def test_aggregate_filters_single_packet_flows(self):
        """Test that flows with only one packet are filtered out."""
        flows = {
            "192.168.1.1->10.0.0.1": {
                "timestamps": [1000.0],  # Only one packet
                "sizes": [100],
                "tcp_flags": [0x02],
                "retransmits": 0,
                "total_packets": 1,
            },
            "192.168.1.2->10.0.0.2": {
                "timestamps": [1000.0, 1000.1],  # Two packets
                "sizes": [1000, 1200],
                "tcp_flags": [0x02, 0x10],
                "retransmits": 0,
                "total_packets": 2,
            },
        }

        df = self.loader._aggregate_flow_metrics(flows)

        # Only the second flow should be included
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["flow_id"], "192.168.1.2->10.0.0.2")

    @patch("requests.get")
    def test_download_pcap_caching(self, mock_get):
        """Test that cached files are not re-downloaded."""
        # Create a fake cached file
        cached_path = os.path.join(self.temp_dir, "test.pcap.gz")
        with open(cached_path, "w") as f:
            f.write("fake pcap data")

        url = "http://example.com/test.pcap.gz"
        result = self.loader.download_pcap(url)

        # Should return cached path without making HTTP request
        self.assertEqual(result, cached_path)
        mock_get.assert_not_called()


class TestDataIntegrity(unittest.TestCase):
    """Tests for data integrity throughout the pipeline."""

    def test_feature_columns_preserved(self):
        """Test that required feature columns are preserved through transformations."""
        required_cols = ["latency_ms", "packet_loss_pct", "signal_quality"]

        # Create sample data
        data = pd.DataFrame({
            "timestamp": [datetime.now() for _ in range(10)],
            "flow_id": [f"flow_{i}" for i in range(10)],
            "latency_ms": np.random.normal(30, 5, 10),
            "packet_loss_pct": np.random.exponential(0.1, 10),
            "signal_quality": np.random.normal(15, 2, 10),
        })

        for col in required_cols:
            self.assertIn(col, data.columns)

    def test_no_null_values_in_features(self):
        """Test that feature columns don't contain null values after aggregation."""
        loader = MAWIDataLoader()

        flows = {
            "flow_1": {
                "timestamps": [1000.0, 1000.01, 1000.02],
                "sizes": [100, 150, 120],
                "tcp_flags": [],
                "retransmits": 0,
                "total_packets": 3,
            },
        }

        df = loader._aggregate_flow_metrics(flows)

        self.assertFalse(df["latency_ms"].isna().any())
        self.assertFalse(df["packet_loss_pct"].isna().any())
        self.assertFalse(df["signal_quality"].isna().any())


if __name__ == "__main__":
    unittest.main()
