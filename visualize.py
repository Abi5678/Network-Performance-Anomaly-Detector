# -*- coding: utf-8 -*-
"""Visualization module for Network Anomaly Detector.

Generates comprehensive plots for anomaly analysis:
- Time-series plots with anomaly highlights
- Distribution plots (histograms, box plots)
- Correlation heatmap
- Anomaly scatter plots (2D and 3D)
"""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configure plot style
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")

FEATURES = ["latency_ms", "packet_loss_pct", "signal_quality"]
FEATURE_LABELS = {
    "latency_ms": "Latency (ms)",
    "packet_loss_pct": "Packet Loss (%)",
    "signal_quality": "Signal Quality",
}


def plot_time_series(df, output_dir):
    """Plot each metric over time with anomalies highlighted."""
    print("[PLOT] Generating time-series plots...")

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Sort by timestamp
    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    normal = df_sorted[~df_sorted["is_anomaly"]]
    anomalies = df_sorted[df_sorted["is_anomaly"]]

    for idx, feature in enumerate(FEATURES):
        ax = axes[idx]

        # Plot normal points
        ax.scatter(
            normal.index,
            normal[feature],
            c="steelblue",
            alpha=0.5,
            s=10,
            label="Normal",
        )

        # Highlight anomalies
        ax.scatter(
            anomalies.index,
            anomalies[feature],
            c="crimson",
            alpha=0.8,
            s=30,
            marker="x",
            label="Anomaly",
        )

        ax.set_ylabel(FEATURE_LABELS[feature], fontsize=11)
        ax.legend(loc="upper right")

        # Add mean line
        mean_val = df_sorted[feature].mean()
        ax.axhline(y=mean_val, color="gray", linestyle="--", alpha=0.5)

    axes[0].set_title("Network Metrics Over Time (MAWI Real Data)", fontsize=14)
    axes[-1].set_xlabel("Flow Index (sorted by time)", fontsize=11)

    plt.tight_layout()
    path = os.path.join(output_dir, "time_series.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_distributions(df, output_dir):
    """Plot distribution histograms and box plots for each metric."""
    print("[PLOT] Generating distribution plots...")

    fig, axes = plt.subplots(2, 3, figsize=(15, 8))

    for idx, feature in enumerate(FEATURES):
        # Histogram with KDE
        ax_hist = axes[0, idx]
        normal_data = df[~df["is_anomaly"]][feature]
        anomaly_data = df[df["is_anomaly"]][feature]

        ax_hist.hist(
            normal_data,
            bins=50,
            alpha=0.6,
            color="steelblue",
            label="Normal",
            density=True,
        )
        ax_hist.hist(
            anomaly_data,
            bins=30,
            alpha=0.7,
            color="crimson",
            label="Anomaly",
            density=True,
        )

        ax_hist.set_xlabel(FEATURE_LABELS[feature])
        ax_hist.set_ylabel("Density")
        ax_hist.legend()
        ax_hist.set_title(f"{FEATURE_LABELS[feature]} Distribution")

        # Box plot
        ax_box = axes[1, idx]
        box_data = [normal_data, anomaly_data]
        bp = ax_box.boxplot(
            box_data,
            labels=["Normal", "Anomaly"],
            patch_artist=True,
        )
        bp["boxes"][0].set_facecolor("steelblue")
        bp["boxes"][0].set_alpha(0.6)
        bp["boxes"][1].set_facecolor("crimson")
        bp["boxes"][1].set_alpha(0.6)

        ax_box.set_ylabel(FEATURE_LABELS[feature])
        ax_box.set_title(f"{FEATURE_LABELS[feature]} Box Plot")

    plt.suptitle("Distribution Analysis: Normal vs Anomalous Flows", fontsize=14, y=1.02)
    plt.tight_layout()
    path = os.path.join(output_dir, "distributions.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_correlation_heatmap(df, output_dir):
    """Plot correlation heatmap of features."""
    print("[PLOT] Generating correlation heatmap...")

    fig, ax = plt.subplots(figsize=(8, 6))

    # Include anomaly score in correlation
    corr_cols = FEATURES + ["anomaly_score"]
    corr_matrix = df[corr_cols].corr()

    # Create labels
    labels = [FEATURE_LABELS.get(c, c.replace("_", " ").title()) for c in corr_cols]

    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="RdBu_r",
        center=0,
        fmt=".2f",
        square=True,
        ax=ax,
        xticklabels=labels,
        yticklabels=labels,
        vmin=-1,
        vmax=1,
    )

    ax.set_title("Feature Correlation Matrix", fontsize=14)
    plt.tight_layout()
    path = os.path.join(output_dir, "correlation_heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_anomaly_scatter_2d(df, output_dir):
    """2D scatter plots of feature pairs colored by anomaly status."""
    print("[PLOT] Generating 2D scatter plots...")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    feature_pairs = [
        ("latency_ms", "packet_loss_pct"),
        ("latency_ms", "signal_quality"),
        ("packet_loss_pct", "signal_quality"),
    ]

    for idx, (f1, f2) in enumerate(feature_pairs):
        ax = axes[idx]

        # Normal points
        normal = df[~df["is_anomaly"]]
        ax.scatter(
            normal[f1],
            normal[f2],
            c="steelblue",
            alpha=0.4,
            s=20,
            label="Normal",
        )

        # Anomaly points
        anomalies = df[df["is_anomaly"]]
        ax.scatter(
            anomalies[f1],
            anomalies[f2],
            c="crimson",
            alpha=0.8,
            s=50,
            marker="x",
            label="Anomaly",
        )

        ax.set_xlabel(FEATURE_LABELS[f1])
        ax.set_ylabel(FEATURE_LABELS[f2])
        ax.legend()

    plt.suptitle("Anomaly Detection: Feature Space Analysis", fontsize=14, y=1.02)
    plt.tight_layout()
    path = os.path.join(output_dir, "anomaly_scatter_2d.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_anomaly_scatter_3d(df, output_dir):
    """3D scatter plot of all three features."""
    print("[PLOT] Generating 3D scatter plot...")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    normal = df[~df["is_anomaly"]]
    anomalies = df[df["is_anomaly"]]

    ax.scatter(
        normal["latency_ms"],
        normal["packet_loss_pct"],
        normal["signal_quality"],
        c="steelblue",
        alpha=0.4,
        s=15,
        label="Normal",
    )

    ax.scatter(
        anomalies["latency_ms"],
        anomalies["packet_loss_pct"],
        anomalies["signal_quality"],
        c="crimson",
        alpha=0.9,
        s=60,
        marker="^",
        label="Anomaly",
    )

    ax.set_xlabel(FEATURE_LABELS["latency_ms"])
    ax.set_ylabel(FEATURE_LABELS["packet_loss_pct"])
    ax.set_zlabel(FEATURE_LABELS["signal_quality"])
    ax.legend()
    ax.set_title("3D Feature Space: Anomaly Detection", fontsize=14)

    path = os.path.join(output_dir, "anomaly_scatter_3d.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_anomaly_score_distribution(df, output_dir):
    """Plot the distribution of anomaly scores."""
    print("[PLOT] Generating anomaly score distribution...")

    fig, ax = plt.subplots(figsize=(10, 5))

    normal = df[~df["is_anomaly"]]["anomaly_score"]
    anomalies = df[df["is_anomaly"]]["anomaly_score"]

    ax.hist(
        normal,
        bins=50,
        alpha=0.6,
        color="steelblue",
        label=f"Normal (n={len(normal)})",
        density=True,
    )
    ax.hist(
        anomalies,
        bins=30,
        alpha=0.7,
        color="crimson",
        label=f"Anomaly (n={len(anomalies)})",
        density=True,
    )

    # Add threshold line (anomaly score < 0 typically indicates anomaly)
    ax.axvline(x=0, color="black", linestyle="--", linewidth=2, label="Decision boundary")

    ax.set_xlabel("Anomaly Score (Isolation Forest)", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.set_title("Anomaly Score Distribution", fontsize=14)
    ax.legend()

    plt.tight_layout()
    path = os.path.join(output_dir, "anomaly_score_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def plot_summary_dashboard(df, output_dir):
    """Create a summary dashboard with key metrics."""
    print("[PLOT] Generating summary dashboard...")

    fig = plt.figure(figsize=(16, 10))

    # Layout: 2x3 grid
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # 1. Pie chart of normal vs anomaly
    ax1 = fig.add_subplot(gs[0, 0])
    anomaly_counts = df["is_anomaly"].value_counts()
    labels = ["Normal", "Anomaly"]
    colors = ["steelblue", "crimson"]
    sizes = [anomaly_counts.get(False, 0), anomaly_counts.get(True, 0)]
    ax1.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax1.set_title("Anomaly Distribution")

    # 2. Bar chart of mean metrics
    ax2 = fig.add_subplot(gs[0, 1])
    normal_means = df[~df["is_anomaly"]][FEATURES].mean()
    anomaly_means = df[df["is_anomaly"]][FEATURES].mean()

    x = np.arange(len(FEATURES))
    width = 0.35
    ax2.bar(x - width / 2, normal_means, width, label="Normal", color="steelblue", alpha=0.7)
    ax2.bar(x + width / 2, anomaly_means, width, label="Anomaly", color="crimson", alpha=0.7)
    ax2.set_xticks(x)
    ax2.set_xticklabels([FEATURE_LABELS[f].split()[0] for f in FEATURES], rotation=15)
    ax2.set_ylabel("Mean Value")
    ax2.set_title("Mean Metrics: Normal vs Anomaly")
    ax2.legend()

    # 3. Stats text box
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis("off")
    stats_text = f"""
    Dataset Summary
    ───────────────────
    Total Flows:     {len(df):,}
    Normal:          {len(df[~df['is_anomaly']]):,}
    Anomalies:       {len(df[df['is_anomaly']]):,}
    Anomaly Rate:    {len(df[df['is_anomaly']]) / len(df) * 100:.1f}%

    Anomaly Characteristics
    ───────────────────
    Avg Latency:     {df[df['is_anomaly']]['latency_ms'].mean():.1f} ms
    Avg Pkt Loss:    {df[df['is_anomaly']]['packet_loss_pct'].mean():.2f}%
    Avg Signal:      {df[df['is_anomaly']]['signal_quality'].mean():.1f}
    """
    ax3.text(0.1, 0.5, stats_text, fontsize=11, family="monospace", va="center")

    # 4-6. Feature scatter plots (bottom row)
    for idx, (f1, f2) in enumerate([
        ("latency_ms", "packet_loss_pct"),
        ("latency_ms", "signal_quality"),
        ("packet_loss_pct", "signal_quality"),
    ]):
        ax = fig.add_subplot(gs[1, idx])
        normal = df[~df["is_anomaly"]]
        anomalies = df[df["is_anomaly"]]

        ax.scatter(normal[f1], normal[f2], c="steelblue", alpha=0.3, s=10)
        ax.scatter(anomalies[f1], anomalies[f2], c="crimson", alpha=0.7, s=30, marker="x")
        ax.set_xlabel(FEATURE_LABELS[f1])
        ax.set_ylabel(FEATURE_LABELS[f2])

    plt.suptitle("Network Anomaly Detection Dashboard (MAWI Real Data)", fontsize=16, y=0.98)
    path = os.path.join(output_dir, "summary_dashboard.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[PLOT] Saved: {path}")


def generate_all_plots(df, output_dir):
    """Generate all visualization plots."""
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("  GENERATING VISUALIZATION PLOTS")
    print("=" * 60 + "\n")

    # Validate required columns
    required_cols = FEATURES + ["is_anomaly", "anomaly_score"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f"[ERROR] Missing columns: {missing}")
        return

    # Generate each plot type
    plot_time_series(df, output_dir)
    plot_distributions(df, output_dir)
    plot_correlation_heatmap(df, output_dir)
    plot_anomaly_scatter_2d(df, output_dir)
    plot_anomaly_scatter_3d(df, output_dir)
    plot_anomaly_score_distribution(df, output_dir)
    plot_summary_dashboard(df, output_dir)

    print(f"\n[PLOT] All plots saved to: {output_dir}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test with sample data
    import sys

    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        df = pd.read_csv(csv_path)
        output_dir = os.path.dirname(csv_path) + "/plots"
        generate_all_plots(df, output_dir)
    else:
        print("Usage: python visualize.py <path_to_anomaly_report.csv>")
