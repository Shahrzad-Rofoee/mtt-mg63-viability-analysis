import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# ------------------------------------------------------------------
# This module performs the statistical analysis pipeline on the tidy
# MTT assay dataset produced by build_dataset.py. The data come from
# an M.Sc. thesis project evaluating MG-63 osteoblast-like cell
# viability on 316L stainless steel coated with electrospun TiO2 and
# TiO2/Sr nanofibers (single-nozzle and dual-nozzle configurations),
# compared against a control of cells cultured on tissue-culture
# polystyrene.
# ------------------------------------------------------------------


def load_data(path="data/mtt_tidy.csv"):
    """Load the tidy MTT assay dataset."""
    return pd.read_csv(path)


def descriptive_stats(df):
    """Compute mean, standard deviation, sample count, and viability
    percent (relative to same-day control) for each group and day."""
    summary = df.groupby(["day", "group"])["absorbance"].agg(
        mean="mean",
        std="std",
        n="count"
    ).reset_index()

    viability_list = []
    for day_value in summary["day"].unique():
        control_mean = summary.loc[
            (summary["day"] == day_value) & (summary["group"] == "control"),
            "mean"
        ].values[0]

        day_rows = summary[summary["day"] == day_value]
        for _, row in day_rows.iterrows():
            viability_percent = 100 * row["mean"] / control_mean
            viability_list.append(viability_percent)

    summary["viability_percent"] = viability_list
    return summary


def normality_tests(df):
    """Shapiro-Wilk normality test for each group/day combination."""
    results = []
    for (day_value, group_value), group_data in df.groupby(["day", "group"]):
        stat, p_value = stats.shapiro(group_data["absorbance"])
        results.append({
            "day": day_value,
            "group": group_value,
            "shapiro_stat": stat,
            "shapiro_p": p_value,
            "normal_at_0.05": p_value > 0.05,
        })
    return pd.DataFrame(results)


def levene_tests(df):
    """Levene's test for homogeneity of variance across groups, per day."""
    results = []
    for day_value, day_data in df.groupby("day"):
        group_arrays = [
            group_data["absorbance"].values
            for _, group_data in day_data.groupby("group")
        ]
        stat, p_value = stats.levene(*group_arrays)
        results.append({
            "day": day_value,
            "levene_stat": stat,
            "levene_p": p_value,
            "equal_variance_at_0.05": p_value > 0.05,
        })
    return pd.DataFrame(results)


def one_way_anova(df):
    """One-way ANOVA per day, with eta-squared effect size."""
    results = []
    for day_value, day_data in df.groupby("day"):
        group_arrays = [
            group_data["absorbance"].values
            for _, group_data in day_data.groupby("group")
        ]
        f_stat, p_value = stats.f_oneway(*group_arrays)

        grand_mean = day_data["absorbance"].mean()
        ss_between = sum(
            len(arr) * (arr.mean() - grand_mean) ** 2 for arr in group_arrays
        )
        ss_total = sum((day_data["absorbance"] - grand_mean) ** 2)
        eta_squared = ss_between / ss_total

        results.append({
            "day": day_value,
            "F_statistic": f_stat,
            "p_value": p_value,
            "eta_squared": eta_squared,
            "significant_at_0.05": p_value < 0.05,
        })
    return pd.DataFrame(results)


def tukey_posthoc(df):
    """Tukey HSD post-hoc pairwise comparisons per day.
    Returns a dict: {day: DataFrame of pairwise results}."""
    results = {}
    for day_value, day_data in df.groupby("day"):
        tukey_result = pairwise_tukeyhsd(
            endog=day_data["absorbance"],
            groups=day_data["group"],
            alpha=0.05
        )
        tukey_table = pd.DataFrame(
            data=tukey_result._results_table.data[1:],
            columns=tukey_result._results_table.data[0]
        )
        tukey_table.insert(0, "day", day_value)
        results[day_value] = tukey_table
    return results


def proliferation_ttest(df):
    """Independent-samples Welch's t-test comparing Day 1 vs Day 3
    absorbance within each group, plus fold-change. Independent (not
    paired) because the MTT assay is destructive: Day 1 and Day 3
    wells are physically different samples."""
    results = []
    for group_value, group_data in df.groupby("group"):
        day1_values = group_data.loc[group_data["day"] == 1, "absorbance"]
        day3_values = group_data.loc[group_data["day"] == 3, "absorbance"]

        t_stat, p_value = stats.ttest_ind(day1_values, day3_values, equal_var=False)
        fold_change = day3_values.mean() / day1_values.mean()

        results.append({
            "group": group_value,
            "day1_mean": day1_values.mean(),
            "day3_mean": day3_values.mean(),
            "fold_change": fold_change,
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant_at_0.05": p_value < 0.05,
        })
    return pd.DataFrame(results)


def run_full_pipeline(data_path="data/mtt_tidy.csv", out_dir="report"):
    """Run the full statistical pipeline and save all results to CSV."""
    df = load_data(data_path)

    summary = descriptive_stats(df)
    normality_df = normality_tests(df)
    levene_df = levene_tests(df)
    anova_df = one_way_anova(df)
    tukey_dict = tukey_posthoc(df)
    proliferation_df = proliferation_ttest(df)

    summary.to_csv(f"{out_dir}/descriptive_statistics.csv", index=False)
    normality_df.to_csv(f"{out_dir}/shapiro_normality.csv", index=False)
    levene_df.to_csv(f"{out_dir}/levene_variance.csv", index=False)
    anova_df.to_csv(f"{out_dir}/anova_results.csv", index=False)
    pd.concat(tukey_dict.values()).to_csv(f"{out_dir}/tukey_posthoc.csv", index=False)
    proliferation_df.to_csv(f"{out_dir}/day1_vs_day3_ttest.csv", index=False)

    return {
        "data": df,
        "descriptive": summary,
        "normality": normality_df,
        "levene": levene_df,
        "anova": anova_df,
        "tukey": tukey_dict,
        "proliferation": proliferation_df,
    }


if __name__ == "__main__":
    results = run_full_pipeline()
    print("Descriptive statistics:")
    print(results["descriptive"])
    print("\nShapiro-Wilk normality:")
    print(results["normality"])
    print("\nLevene's test:")
    print(results["levene"])
    print("\nOne-way ANOVA:")
    print(results["anova"])
    print("\nTukey HSD:")
    for day, table in results["tukey"].items():
        print(f"Day {day}:")
        print(table)
    print("\nProliferation t-test:")
    print(results["proliferation"])