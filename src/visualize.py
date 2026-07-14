import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------------
# This module generates publication-style figures from the MTT assay
# statistical results. The data come from an M.Sc. thesis project
# evaluating MG-63 osteoblast-like cell viability on 316L stainless
# steel coated with electrospun TiO2 and TiO2/Sr nanofibers
# (single-nozzle and dual-nozzle configurations), compared against a
# control of cells cultured on tissue-culture polystyrene.
# ------------------------------------------------------------------

GROUP_ORDER = ["control", "DN", "SN", "TiO2"]
GROUP_COLORS = {
    "control": "#0072B2",
    "DN": "#009E73",
    "SN": "#D55E00",
    "TiO2": "#CC79A7",
}


def fig_absorbance_bar(df, summary, out="figures/01_absorbance_bar.png"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    for ax, day_value in zip(axes, [1, 3]):
        day_summary = summary[summary["day"] == day_value].set_index("group").loc[GROUP_ORDER]
        x_positions = np.arange(len(GROUP_ORDER))
        ax.bar(
            x_positions, day_summary["mean"], yerr=day_summary["std"], capsize=6,
            color=[GROUP_COLORS[g] for g in GROUP_ORDER], edgecolor="black",
        )
        ax.set_xticks(x_positions)
        ax.set_xticklabels(GROUP_ORDER)
        ax.set_title(f"Day {day_value}")
        ax.set_ylabel("Absorbance (OD 570 nm)")
    fig.suptitle("MTT Assay: MG-63 Viability by Coating Group", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure to {out}")


def fig_viability_bar(summary, out="figures/02_viability_percent.png"):
    fig, ax = plt.subplots(figsize=(9, 6))
    bar_width = 0.35
    x_positions = np.arange(len(GROUP_ORDER))
    day1_summary = summary[summary["day"] == 1].set_index("group").loc[GROUP_ORDER]
    day3_summary = summary[summary["day"] == 3].set_index("group").loc[GROUP_ORDER]

    ax.bar(x_positions - bar_width / 2, day1_summary["viability_percent"], width=bar_width,
           label="Day 1", color=[GROUP_COLORS[g] for g in GROUP_ORDER], edgecolor="black", alpha=1.0)
    ax.bar(x_positions + bar_width / 2, day3_summary["viability_percent"], width=bar_width,
           label="Day 3", color=[GROUP_COLORS[g] for g in GROUP_ORDER], edgecolor="black", alpha=0.55)

    ax.axhline(100, color="gray", linestyle="--", linewidth=1, label="Control (100%)")
    ax.axhline(70, color="firebrick", linestyle=":", linewidth=1.2, label="ISO 10993-5 threshold (70%)")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(GROUP_ORDER)
    ax.set_ylabel("Cell viability (% of control)")
    ax.set_title("MG-63 Relative Viability by Coating Group", fontsize=14, fontweight="bold")
    ax.legend(fontsize=9, loc="lower right")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure to {out}")


def fig_boxplot(df, out="figures/03_boxplot_distribution.png"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    for ax, day_value in zip(axes, [1, 3]):
        day_data = df[df["day"] == day_value]
        box_data = [day_data.loc[day_data["group"] == g, "absorbance"].values for g in GROUP_ORDER]
        box = ax.boxplot(box_data, tick_labels=GROUP_ORDER, patch_artist=True, widths=0.5)
        for patch, g in zip(box["boxes"], GROUP_ORDER):
            patch.set_facecolor(GROUP_COLORS[g])
            patch.set_edgecolor("black")
        for i, g in enumerate(GROUP_ORDER, start=1):
            values = day_data.loc[day_data["group"] == g, "absorbance"]
            ax.scatter(np.full(len(values), i), values, color="black", zorder=3, s=25)
        ax.set_title(f"Day {day_value}")
        ax.set_ylabel("Absorbance (OD 570 nm)")
    fig.suptitle("Replicate-Level Absorbance Distribution (n = 4 per group)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure to {out}")


def fig_proliferation_trend(summary, out="figures/04_proliferation_trend.png"):
    fig, ax = plt.subplots(figsize=(8, 6))
    for g in GROUP_ORDER:
        group_summary = summary[summary["group"] == g].sort_values("day")
        ax.errorbar(group_summary["day"], group_summary["mean"], yerr=group_summary["std"],
                    marker="o", markersize=8, linewidth=2, capsize=5, color=GROUP_COLORS[g], label=g)
    ax.set_xticks([1, 3])
    ax.set_xlabel("Culture time (days)")
    ax.set_ylabel("Absorbance (OD 570 nm, mean +/- SD)")
    ax.set_title("MG-63 Proliferation Trend (Day 1 to Day 3)", fontsize=14, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure to {out}")


def fig_viability_heatmap(summary, out="figures/05_viability_heatmap.png"):
    fig, ax = plt.subplots(figsize=(6, 5))
    heatmap_matrix = np.zeros((len(GROUP_ORDER), 2))
    for row_index, g in enumerate(GROUP_ORDER):
        for col_index, day_value in enumerate([1, 3]):
            value = summary.loc[
                (summary["group"] == g) & (summary["day"] == day_value), "viability_percent"
            ].values[0]
            heatmap_matrix[row_index, col_index] = value

    im = ax.imshow(heatmap_matrix, cmap="viridis", vmin=60, vmax=105, aspect="auto")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Day 1", "Day 3"])
    ax.set_yticks(np.arange(len(GROUP_ORDER)))
    ax.set_yticklabels(GROUP_ORDER)
    ax.set_title("Viability (%) Summary Heatmap", fontsize=14, fontweight="bold")

    for row_index in range(len(GROUP_ORDER)):
        for col_index in range(2):
            value = heatmap_matrix[row_index, col_index]
            ax.text(col_index, row_index, f"{value:.1f}", ha="center", va="center",
                    color="white" if value < 85 else "black", fontsize=12, fontweight="bold")

    fig.colorbar(im, ax=ax, label="Viability (%)")
    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure to {out}")


def generate_all_figures(df, summary, tukey=None):
    """Generate all five figures and save them to the figures/ folder."""
    fig_absorbance_bar(df, summary)
    fig_viability_bar(summary)
    fig_boxplot(df)
    fig_proliferation_trend(summary)
    fig_viability_heatmap(summary)


if __name__ == "__main__":
    from analysis import load_data, descriptive_stats
    df = load_data()
    summary = descriptive_stats(df)
    generate_all_figures(df, summary)