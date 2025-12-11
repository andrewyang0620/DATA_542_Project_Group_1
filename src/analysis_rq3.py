import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import os

from data_loading import load_data
from data_preprocessing import preprocess_data

OUTPUT_DIR = "analysis_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'figure.dpi': 300,
    'axes.spines.top': False,
    'axes.spines.right': False,
})


def classify_file(filename):
    """
    Classify file based on extension
    Production, Test, Config/Docs, or Other.
    """
    if pd.isna(filename):
        return 'Other'
    filename = filename.lower()

    if any(x in filename for x in ['test', 'spec', 'testing']):
        return 'Test'
    elif filename.endswith(('.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.xml', '.gradle', 'package.json')):
        return 'Config/Docs'
    elif filename.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rb', '.php')):
        return 'Production'
    else:
        return 'Other'


def analyze_rq3(pr_df, details_df):
    '''main analysis function for RQ3'''
    print("\n--- Running RQ3: File-Type Distribution ---")

    # Classify each file in the commit details
    details_df['file_type'] = details_df['filename'].apply(classify_file)
    subset_details = details_df[details_df['pr_id'].isin(pr_df['id'])]
    merged_details = pd.merge(subset_details, pr_df[['id', 'agent']], left_on='pr_id', right_on='id')

    # Count file types per pr
    pr_type_counts = merged_details.pivot_table(
        index='id',
        columns='file_type',
        values='filename',
        aggfunc='count',
        fill_value=0
    ).reset_index()

    # Add agent
    pr_type_counts = pd.merge(pr_type_counts, pr_df[['id', 'agent']], on='id')

    # Determine patch
    def get_patch_type(row):
        """
        determine patch type based on file type counts
        """
        prod = row.get('Production', 0)
        test = row.get('Test', 0)

        if prod > 0 and test > 0:
            return 'Mixed (Code+Test)'
        elif prod > 0:
            return 'Production Only'
        elif test > 0:
            return 'Test Only'
        else:
            return 'Other'

    pr_type_counts['patch_type'] = pr_type_counts.apply(get_patch_type, axis=1)

    contingency = pd.crosstab(pr_type_counts['agent'], pr_type_counts['patch_type'])
    print("\nContingency Table:\n")
    print(contingency)

    # Chi-square
    stat, p, dof, expected = stats.chi2_contingency(contingency)
    print(f"\nChi-square test p-value: {p:.4e}")

    # plotting
    df_pct = contingency.div(contingency.sum(axis=1), axis=0) * 100

    ordered_cols = ['Mixed (Code+Test)', 'Production Only', 'Test Only', 'Other']
    df_pct = df_pct[[c for c in ordered_cols if c in df_pct.columns]]

    fig, ax = plt.subplots(figsize=(10, 6))
    df_pct.plot(kind='barh', stacked=True, ax=ax, width=0.7,
                color=["#E69F00", "#56B4E9", "#009E73", "#999999"])

    ax.set_title("File-Type Distribution Across AI Agents", fontsize=14)
    ax.set_xlabel("Percentage of Pull Requests (%)")
    ax.set_xlim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False)

    # Percentage labels
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f%%', label_type='center', color='white', fontsize=8)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/rq3_fig_operational_profile.png")
    print(f"Saved plot → {OUTPUT_DIR}/rq3_fig_operational_profile.png")

    return pr_type_counts


if __name__ == "__main__":
    pr_df_raw, pr_details_df_raw = load_data()
    pr_df, details_df = preprocess_data(pr_df_raw, pr_details_df_raw)

    print(f"\nData ready → {len(pr_df)} PRs, {len(details_df)} file changes")
    analyze_rq3(pr_df, details_df)
