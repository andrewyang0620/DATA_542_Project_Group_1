import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
import os
from plot_style import COLORS, set_academic_style
from data_loading import load_data
from data_preprocessing import preprocess_data

OUTPUT_DIR = "analysis_results"

def analyze_rq1(pr_df, details_df):
    print("\n--- RQ1: Patch Characteristics ---")
    print("\n")

    pr_details = details_df[details_df['pr_id'].isin(pr_df['id'])]

    pr_stats = pr_details.groupby('pr_id').agg({
        'additions': 'sum',
        'deletions': 'sum',
        'filename': 'nunique'
    }).rename(columns={'filename': 'unique_files_touched'}).reset_index()

    analysis_df = pd.merge(pr_stats, pr_df[['id','agent']], left_on='pr_id', right_on='id')

    metrics = ['additions', 'deletions', 'unique_files_touched']

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))

    for i, metric in enumerate(metrics):
        sns.boxplot(x='agent', y=metric, data=analysis_df, hue='agent', palette=COLORS, ax=axes[i], showfliers=False, legend=False)
        axes[i].set_title(metric)
        axes[i].tick_params(axis='x', rotation=45)

        groups = [group[metric].values for name, group in analysis_df.groupby('agent')]
        stat, p = stats.kruskal(*groups) 
        print(f"{metric} Kruskal-Wallis H={stat:.2f}, p={p:.2e}")

    fig.tight_layout()
    fig.savefig(f"{OUTPUT_DIR}/rq1_patch_characteristics.png")
    return analysis_df

if __name__ == "__main__":
    set_academic_style()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pr_df_raw, pr_details_df_raw = load_data()
    pr_df, pr_details_df = preprocess_data(pr_df_raw, pr_details_df_raw)
    result_df = analyze_rq1(pr_df, pr_details_df)
    print(f"\nAnalysis complete! Results saved to {OUTPUT_DIR}/rq1_patch_characteristics.png")
    print(f"Analyzed {len(result_df)} PRs")