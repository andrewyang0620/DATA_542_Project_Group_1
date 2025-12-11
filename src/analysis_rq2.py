import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer

from plot_style import set_academic_style
from data_loading import load_data

OUTPUT_DIR = "analysis_results"


def analyze_rq2(pr_df: pd.DataFrame, details_df: pd.DataFrame) -> pd.DataFrame:
    """
    main analysis function for RQ2
    Analyze description consistency with code changes
    """
    print("\n--- Analyzing RQ2: Description Consistency ---")
    print(f"Columns in pr_df for RQ2: {pr_df.columns}")
 
    details_df = details_df.copy()
    details_df['patch'] = details_df['patch'].fillna('')
    patch_agg = (details_df.groupby('pr_id')['patch'].apply(lambda x: ' '.join(x)).reset_index())

    analysis_df = pd.merge(pr_df, patch_agg, left_on='id', right_on='pr_id')
    print(f"Columns in analysis_df after merge: {analysis_df.columns}")
    print(f"After merging with patches: {len(analysis_df)} PRs")

    analysis_df['text_desc'] = (analysis_df['title'].fillna('') + " " + analysis_df['body'].fillna(''))
    
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    print("Computing TF-IDF similarities, may take some time...")
    all_text = pd.concat([analysis_df['text_desc'], analysis_df['patch']])
    tfidf.fit(all_text)
    
    desc_matrix = tfidf.transform(analysis_df['text_desc'])
    patch_matrix = tfidf.transform(analysis_df['patch'])

    sim_scores = np.array(desc_matrix.multiply(patch_matrix).sum(axis=1)).flatten()
    analysis_df['similarity'] = sim_scores
    # Determine merge status
    if 'merged_at' in analysis_df.columns:
        analysis_df['is_merged'] = analysis_df['merged_at'].notna()
    elif 'merged_at_x' in analysis_df.columns:
        analysis_df['is_merged'] = analysis_df['merged_at_x'].notna()
    else:
        print("Col not found")
        return analysis_df

    plt.figure(figsize=(10, 6))
    sns.violinplot(
        x='agent',
        y='similarity',
        hue='is_merged',
        data=analysis_df,
        split=True,
        palette="muted"
    )
    plt.title('Semantic Similarity (Description vs Code) by Agent and Merge Status')
    plt.xticks(rotation=45)
    plt.tight_layout()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.savefig(f"{OUTPUT_DIR}/rq2_similarity_consistency.png")

    print("Statistical Tests for RQ2:")
    # perform statistical tests
    for agent in analysis_df['agent'].unique():
        merged = analysis_df[
            (analysis_df['agent'] == agent) &
            (analysis_df['is_merged'])
        ]['similarity']
        unmerged = analysis_df[
            (analysis_df['agent'] == agent) &
            (~analysis_df['is_merged'])
        ]['similarity']
        
        if len(merged) > 0 and len(unmerged) > 0:
            stat, p = stats.mannwhitneyu(merged, unmerged)
            print(f"Agent: {agent} - Mann-Whitney U p-value (Merged vs Unmerged): {p}")
            
    return analysis_df

if __name__ == "__main__":
    set_academic_style()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # timer for running time, rq2 can take a while
    timer = __import__('time').time
    start_time = timer()
    pr_df_raw, pr_details_df_raw = load_data()
    if pr_df_raw is None or pr_details_df_raw is None:
        end_time = timer()
        print("Error loading data, aborting RQ2 analysis.")
    else:
        result_df = analyze_rq2(pr_df_raw, pr_details_df_raw)
        end_time = timer()
        total_time = end_time - start_time
        print(f"\nResults saved to {OUTPUT_DIR}/rq2_similarity_consistency.png")
        print(f"Analyzed {len(result_df)} PRs")
        print(f"{total_time:.2f} seconds used for RQ2 analysis")