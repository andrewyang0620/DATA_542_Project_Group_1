import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from math import pi

# --- Setup Academic Style ---
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 12,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# Color Palette (Colorblind friendly / Academic)
COLORS = {
    "Copilot": "#0072B2",       # Blue
    "GitHub Copilot": "#0072B2",# Blue
    "Codex": "#D55E00",         # Vermilion
    "OpenAI Codex": "#D55E00",  # Vermilion
    "OpenAI_Codex": "#D55E00",  # Vermilion (Dataset key)
    "Devin": "#009E73",         # Bluish Green
    "Cursor": "#785EF0",        # Purple
    "Claude": "#CC79A7",        # Reddish Purple
    "Claude Code": "#CC79A7",   # Reddish Purple
    "Claude_Code": "#CC79A7"    # Reddish Purple (Dataset key)
}

OUTPUT_DIR = "analysis_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    print("Loading data...")
    # URLs
    all_pr_url = "hf://datasets/hao-li/AIDev/all_pull_request.parquet"
    pr_details_url = "hf://datasets/hao-li/AIDev/pr_commit_details.parquet"
    
    # Load Agent info (using only necessary columns)
    try:
        all_pr_df = pd.read_parquet(all_pr_url, columns=['id', 'agent', 'merged_at'])
        print(f"Loaded all_pr_df: {len(all_pr_df)} rows")
    except Exception as e:
        print(f"Error loading all_pr_df: {e}")
        return None, None

    # Load Commit Details (this is large, so be careful)
    try:
        # We only need columns relevant to the analysis
        pr_details_df = pd.read_parquet(pr_details_url, columns=['pr_id', 'filename', 'additions', 'deletions', 'patch'])
        print(f"Loaded pr_details_df: {len(pr_details_df)} rows")
    except Exception as e:
        print(f"Error loading pr_details_df: {e}")
        return None, None
        
    # Load enriched PR subset to get titles and bodies for RQ2
    # We can join this with all_pr_df to get the agent
    pr_subset_url = "hf://datasets/hao-li/AIDev/pull_request.parquet"
    try:
        pr_subset_df = pd.read_parquet(pr_subset_url, columns=['id', 'title', 'body', 'state'])
        print(f"Loaded pr_subset_df: {len(pr_subset_df)} rows")
    except Exception as e:
        print(f"Error loading pr_subset_df: {e}")
        return None, None

    # Merge Agent info into pr_subset
    # Note: pr_subset_df 'id' matches all_pr_df 'id'
    merged_pr_df = pd.merge(pr_subset_df, all_pr_df[['id', 'agent', 'merged_at']], on='id', how='inner')
    
    # Filter for specific agents if needed (Codex, Devin, Copilot, Cursor, Claude Code)
    print(f"Agents found: {merged_pr_df['agent'].unique()}")
    print(f"Columns in merged_pr_df: {merged_pr_df.columns}")
    
    return merged_pr_df, pr_details_df

def analyze_rq1(pr_df, details_df):
    print("\n--- Analyzing RQ1: Patch Characteristics ---")
    
    # Filter details for PRs in our subset
    subset_details = details_df[details_df['pr_id'].isin(pr_df['id'])]
    
    # Aggregations
    pr_stats = subset_details.groupby('pr_id').agg({
        'additions': 'sum',
        'deletions': 'sum',
        'filename': 'nunique'
    }).rename(columns={'filename': 'unique_files_touched'}).reset_index()
    
    # Merge back with agent info
    analysis_df = pd.merge(pr_stats, pr_df[['id', 'agent']], left_on='pr_id', right_on='id')
    
    # Metrics to analyze
    metrics = ['additions', 'deletions', 'unique_files_touched']
    
    # Visualization
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, metric in enumerate(metrics):
        # Log scale might be better for additions/deletions, but boxplot handles it okay
        # Fix FutureWarning: assign x to hue and set legend=False
        sns.boxplot(x='agent', y=metric, hue='agent', data=analysis_df, ax=axes[i], showfliers=False, palette=COLORS, legend=False) 
        axes[i].set_title(f'Distribution of {metric}')
        # axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=45) # Removed as redundant with hue/legend=False
        axes[i].tick_params(axis='x', rotation=45)
        
        # Stats Test (Kruskal-Wallis)
        groups = [group[metric].values for name, group in analysis_df.groupby('agent')]
        if len(groups) > 1:
            stat, p = stats.kruskal(*groups)
            print(f"{metric} - Kruskal-Wallis p-value: {p}")

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/rq1_patch_characteristics.png")
    print("RQ1 Analysis complete. Plot saved.")
    return analysis_df

def analyze_rq2(pr_df, details_df):
    print("\n--- Analyzing RQ2: Description Consistency ---")
    print(f"Columns in pr_df for RQ2: {pr_df.columns}")
    
    # Handle missing patches/NaNs
    details_df['patch'] = details_df['patch'].fillna('')
    
    patch_agg = details_df.groupby('pr_id')['patch'].apply(lambda x: ' '.join(x)).reset_index()
    
    # Merge with PR info
    analysis_df = pd.merge(pr_df, patch_agg, left_on='id', right_on='pr_id')
    print(f"Columns in analysis_df after merge: {analysis_df.columns}")
    
    # Prepare text
    analysis_df['text_desc'] = analysis_df['title'].fillna('') + " " + analysis_df['body'].fillna('')
    
    # Calculate Similarity
    tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
    
    print("Computing TF-IDF similarities...")
    
    # Concatenate all text to fit vectorizer
    all_text = pd.concat([analysis_df['text_desc'], analysis_df['patch']])
    tfidf.fit(all_text)
    
    desc_matrix = tfidf.transform(analysis_df['text_desc'])
    patch_matrix = tfidf.transform(analysis_df['patch'])
    
    # Element-wise dot product (Cosine Similarity for normalized vectors)
    sim_scores = np.array(desc_matrix.multiply(patch_matrix).sum(axis=1)).flatten()
    analysis_df['similarity'] = sim_scores
    
    # Define Merged vs Unmerged
    # Check if merged_at exists, if not check for _x/_y
    if 'merged_at' in analysis_df.columns:
        analysis_df['is_merged'] = analysis_df['merged_at'].notna()
    elif 'merged_at_x' in analysis_df.columns:
        analysis_df['is_merged'] = analysis_df['merged_at_x'].notna()
    else:
         print("Error: 'merged_at' column not found in analysis_df")
         return analysis_df

    
    # Visualization
    plt.figure(figsize=(10, 6))
    sns.violinplot(x='agent', y='similarity', hue='is_merged', data=analysis_df, split=True, palette="muted")
    plt.title('Semantic Similarity (Description vs Code) by Agent and Merge Status')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/rq2_similarity_consistency.png")
    
    # Stats
    print("Statistical Tests for RQ2:")
    for agent in analysis_df['agent'].unique():
        merged = analysis_df[(analysis_df['agent'] == agent) & (analysis_df['is_merged'])]['similarity']
        unmerged = analysis_df[(analysis_df['agent'] == agent) & (~analysis_df['is_merged'])]['similarity']
        if len(merged) > 0 and len(unmerged) > 0:
            stat, p = stats.mannwhitneyu(merged, unmerged)
            print(f"Agent: {agent} - Mann-Whitney U p-value (Merged vs Unmerged): {p}")
            
    return analysis_df

def analyze_rq3(pr_df, details_df):
    print("\n--- Analyzing RQ3: File Type Distribution ---")
    
    # Define regex for file types
    def classify_file(filename):
        if pd.isna(filename): return 'Other'
        filename = filename.lower()
        if any(x in filename for x in ['test', 'spec', 'testing']):
            return 'Test'
        elif any(filename.endswith(x) for x in ['.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.xml', '.gradle', 'package.json']):
            return 'Config/Docs'
        elif any(filename.endswith(x) for x in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rb', '.php']):
            return 'Production'
        else:
            return 'Other'
            
    details_df['file_type'] = details_df['filename'].apply(classify_file)
    
    # Filter details for PRs in subset
    subset_details = details_df[details_df['pr_id'].isin(pr_df['id'])]
    
    # Merge with agent to group
    merged_details = pd.merge(subset_details, pr_df[['id', 'agent']], left_on='pr_id', right_on='id')
    
    # Count file types per PR
    pr_type_counts = merged_details.pivot_table(index='id', columns='file_type', values='filename', aggfunc='count', fill_value=0)
    pr_type_counts = pd.merge(pr_type_counts, pr_df[['id', 'agent']], on='id')
    
    # Classify Patch Type
    def get_patch_type(row):
        # Handle missing columns if they don't exist (e.g. no 'Production' files found at all)
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
    
    # Contingency table for Stats
    contingency = pd.crosstab(pr_type_counts['agent'], pr_type_counts['patch_type'])
    print("\nPatch Type Contingency Table:")
    print(contingency)
    
    stat, p, dof, expected = stats.chi2_contingency(contingency)
    print(f"Chi-square test for independence: p-value = {p}")
    
    # Visualization: Operational Profile (Stacked Bar Chart)
    # Calculate percentages from contingency table
    df_pct = contingency.div(contingency.sum(axis=1), axis=0) * 100
    
    # Ensure columns are in logical order if they exist
    desired_order = ['Mixed (Code+Test)', 'Production Only', 'Test Only', 'Other']
    existing_cols = [c for c in desired_order if c in df_pct.columns]
    df_pct = df_pct[existing_cols]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Custom colors for categories
    # Map categories to specific colors if possible, else use default list
    cat_colors = ["#E69F00", "#56B4E9", "#009E73", "#999999"] # Orange, Blue, Green, Gray
    # Adjust color list length to match columns
    current_colors = cat_colors[:len(existing_cols)]
    
    df_pct.plot(kind='barh', stacked=True, color=current_colors, ax=ax, width=0.7, edgecolor='white')

    ax.set_xlabel('Percentage of Pull Requests (%)', fontsize=12)
    ax.set_title('Operational Profile: File Type Distribution by Agent', fontsize=14, weight='bold')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4, frameon=False)
    
    # Add percentage labels
    for c in ax.containers:
        ax.bar_label(c, fmt='%.0f%%', label_type='center', color='white', fontsize=9, weight='bold')

    ax.set_xlim(0, 100)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/fig_operational_profile.png", bbox_inches='tight')
    print(f"Saved {OUTPUT_DIR}/fig_operational_profile.png")
    
    return pr_type_counts

def plot_agent_fingerprint():
    """
    Generates the Agent Fingerprint Radar Chart.
    Note: This uses summarized/normalized data derived from the statistical results
    of RQ1, RQ2, and RQ3.
    """
    print("\n--- Generating Agent Fingerprint ---")
    categories = ['Production Focus', 'Test Focus', 'Patch Size', 'Desc. Consistency\nImportance']
    N = len(categories)

    # Data (Normalized 0-1 based on report findings)
    data = {
        "GitHub Copilot": [0.3, 0.9, 0.2, 0.95], 
        "Devin":          [0.85, 0.4, 0.9, 0.2],
        "OpenAI Codex":   [0.8, 0.6, 0.8, 0.8],
        "Cursor":         [0.8, 0.3, 0.7, 0.3],
        "Claude Code":    [0.6, 0.5, 0.4, 0.4]
    }

    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # Close the loop

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    
    plt.xticks(angles[:-1], categories, color='black', size=11)
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["", "", "", ""], color="grey", size=7)
    plt.ylim(0, 1)

    for agent, values in data.items():
        values += values[:1] # Close the loop
        # Match agent name to color key
        color_key = agent.split()[-1] # Copilot, Codex, Devin
        if "GitHub" in agent: color_key = "Copilot"
        if "OpenAI" in agent: color_key = "Codex"
        if "Claude" in agent: color_key = "Claude"
        
        color = COLORS.get(color_key, "#333")
        
        # Use slightly different line styles to distinguish overlapping lines
        linestyle = 'solid'
        if agent == "Cursor": linestyle = 'dashed'
        if agent == "Claude Code": linestyle = 'dashdot'

        ax.plot(angles, values, linewidth=2, linestyle=linestyle, label=agent, color=color)
        ax.fill(angles, values, alpha=0.05, color=color)

    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.title("The 'Agent Fingerprint':\nOperational Characteristics Comparison", y=1.08, fontsize=16, weight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/fig_agent_fingerprint.png", bbox_inches='tight')
    print(f"Saved {OUTPUT_DIR}/fig_agent_fingerprint.png")

if __name__ == "__main__":
    pr_df, details_df = load_data()
    
    if pr_df is not None and details_df is not None:
        analyze_rq1(pr_df, details_df)
        analyze_rq2(pr_df, details_df)
        analyze_rq3(pr_df, details_df)
        plot_agent_fingerprint()
