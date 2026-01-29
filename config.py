# -*- coding: utf-8 -*-
"""Centralized configuration for Network Anomaly Detector.

Configuration can be set via:
1. Environment variables (highest priority)
2. Config file (config.yaml)
3. Default values (lowest priority)
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _env_bool(key: str, default: bool = False) -> bool:
    """Get boolean from environment variable."""
    val = os.environ.get(key, "").lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    return default


def _env_int(key: str, default: int) -> int:
    """Get integer from environment variable."""
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def _env_float(key: str, default: float) -> float:
    """Get float from environment variable."""
    try:
        return float(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


@dataclass
class DataConfig:
    """Data storage and processing configuration."""

    raw_dir: str = os.path.join(BASE_DIR, "data", "raw")
    processed_dir: str = os.path.join(BASE_DIR, "data", "processed")
    plots_dir: str = os.path.join(BASE_DIR, "data", "processed", "plots")
    models_dir: str = os.path.join(BASE_DIR, "models")

    # PCAP parsing
    max_packets: int = _env_int("MAX_PACKETS", 100000)
    cache_pcap: bool = _env_bool("CACHE_PCAP", True)

    # Parquet settings
    compression: str = os.environ.get("PARQUET_COMPRESSION", "snappy")

    def ensure_dirs(self):
        """Create all data directories if they don't exist."""
        for d in [self.raw_dir, self.processed_dir, self.plots_dir, self.models_dir]:
            os.makedirs(d, exist_ok=True)


@dataclass
class MAWIConfig:
    """MAWI data source configuration."""

    # Default PCAP URLs (2019 samples - smaller files)
    sample_urls: List[str] = field(default_factory=lambda: [
        "http://mawi.wide.ad.jp/mawi/samplepoint-F/2019/201901011400.pcap.gz",
        "http://mawi.wide.ad.jp/mawi/samplepoint-F/2019/201901021400.pcap.gz",
        "http://mawi.wide.ad.jp/mawi/samplepoint-F/2019/201901031400.pcap.gz",
    ])

    # Custom PCAP URL (overrides samples if set)
    custom_url: Optional[str] = os.environ.get("MAWI_PCAP_URL")

    # Download settings
    download_timeout: int = _env_int("DOWNLOAD_TIMEOUT", 300)
    chunk_size: int = 1024 * 1024  # 1 MB

    @property
    def pcap_url(self) -> str:
        """Get the PCAP URL to use."""
        return self.custom_url or self.sample_urls[0]


@dataclass
class ModelConfig:
    """Machine learning model configuration."""

    # Isolation Forest parameters
    contamination: float = _env_float("CONTAMINATION", 0.05)
    random_state: int = _env_int("RANDOM_STATE", 42)
    n_estimators: int = _env_int("N_ESTIMATORS", 100)

    # Feature columns
    features: List[str] = field(default_factory=lambda: [
        "latency_ms",
        "packet_loss_pct",
        "signal_quality",
    ])

    # Model persistence
    model_filename: str = "isolation_forest.pkl"
    scaler_filename: str = "scaler.pkl"


@dataclass
class MetricsConfig:
    """Prometheus metrics configuration."""

    enabled: bool = _env_bool("PROMETHEUS_ENABLED", False)
    port: int = _env_int("PROMETHEUS_PORT", 8000)
    host: str = os.environ.get("PROMETHEUS_HOST", "0.0.0.0")


@dataclass
class LogConfig:
    """Logging configuration."""

    level: str = os.environ.get("LOG_LEVEL", "INFO")
    format: str = "[%(levelname)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class StreamingConfig:
    """Real-time streaming mode configuration."""

    enabled: bool = _env_bool("STREAMING_ENABLED", False)
    interval_seconds: int = _env_int("STREAMING_INTERVAL", 300)  # 5 minutes
    batch_size: int = _env_int("STREAMING_BATCH_SIZE", 10000)


@dataclass
class Config:
    """Main configuration class."""

    data: DataConfig = field(default_factory=DataConfig)
    mawi: MAWIConfig = field(default_factory=MAWIConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    log: LogConfig = field(default_factory=LogConfig)
    streaming: StreamingConfig = field(default_factory=StreamingConfig)

    def __post_init__(self):
        """Initialize configuration."""
        self.data.ensure_dirs()


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global _config
    _config = Config()
    return _config


# Convenience exports
def get_data_config() -> DataConfig:
    return get_config().data


def get_mawi_config() -> MAWIConfig:
    return get_config().mawi


def get_model_config() -> ModelConfig:
    return get_config().model


def get_metrics_config() -> MetricsConfig:
    return get_config().metrics


if __name__ == "__main__":
    # Print current configuration
    cfg = get_config()
    print("Network Anomaly Detector Configuration")
    print("=" * 50)
    print(f"\nData Config:")
    print(f"  Raw directory:       {cfg.data.raw_dir}")
    print(f"  Processed directory: {cfg.data.processed_dir}")
    print(f"  Models directory:    {cfg.data.models_dir}")
    print(f"  Max packets:         {cfg.data.max_packets}")

    print(f"\nMAWI Config:")
    print(f"  PCAP URL:            {cfg.mawi.pcap_url}")
    print(f"  Download timeout:    {cfg.mawi.download_timeout}s")

    print(f"\nModel Config:")
    print(f"  Contamination:       {cfg.model.contamination}")
    print(f"  Features:            {cfg.model.features}")
    print(f"  N estimators:        {cfg.model.n_estimators}")

    print(f"\nMetrics Config:")
    print(f"  Enabled:             {cfg.metrics.enabled}")
    print(f"  Port:                {cfg.metrics.port}")

    print(f"\nStreaming Config:")
    print(f"  Enabled:             {cfg.streaming.enabled}")
    print(f"  Interval:            {cfg.streaming.interval_seconds}s")
