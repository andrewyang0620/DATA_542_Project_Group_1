import pandas as pd
import numpy as np

def find_representative_cases():
    print("Loading data for case finding...")
    # URLs
    all_pr_url = "hf://datasets/hao-li/AIDev/all_pull_request.parquet"
    pr_details_url = "hf://datasets/hao-li/AIDev/pr_commit_details.parquet"
    pr_subset_url = "hf://datasets/hao-li/AIDev/pull_request.parquet"

    # Load Data
    pr_subset_df = pd.read_parquet(pr_subset_url, columns=['id', 'title', 'body', 'state', 'repo_url'])
    all_pr_df = pd.read_parquet(all_pr_url, columns=['id', 'agent', 'merged_at'])
    pr_details_df = pd.read_parquet(pr_details_url, columns=['pr_id', 'filename', 'additions', 'deletions', 'patch'])

    # Merge
    merged_pr_df = pd.merge(pr_subset_df, all_pr_df[['id', 'agent', 'merged_at']], on='id', how='inner')
    
    print(f"Total PRs loaded: {len(merged_pr_df)}")

    # Helper to get file type
    def classify_file(filename):
        if pd.isna(filename): return 'Other'
        filename = filename.lower()
        if any(x in filename for x in ['test', 'spec', 'testing']):
            return 'Test'
        elif any(filename.endswith(x) for x in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rb', '.php']):
            return 'Production'
        return 'Other'

    pr_details_df['file_type'] = pr_details_df['filename'].apply(classify_file)

    # --- Case 1: Copilot Test-Only PR ---
    # Criteria: Agent=Copilot, Merged=True, Files=Test Only, Additions < 100
    print("\nSearching for Copilot Test-Only Case...")
    copilot_prs = merged_pr_df[
        (merged_pr_df['agent'] == 'Copilot') & 
        (merged_pr_df['merged_at'].notna())
    ]
    
    for idx, pr in copilot_prs.head(1000).iterrows():
        pr_id = pr['id']
        details = pr_details_df[pr_details_df['pr_id'] == pr_id]
        
        file_types = set(details['file_type'])
        # Allow Test only, or Test + Other (config)
        if 'Production' not in file_types and 'Test' in file_types:
            print(f"\n[FOUND] Copilot Case ID: {pr_id}")
            print(f"Repo: {pr['repo_url']}")
            print(f"Title: {pr['title']}")
            print(f"Body: {pr['body'][:200]}...")
            print(f"Files: {details['filename'].tolist()}")
            break

    # --- Case 2: Devin/Codex Production Feature Case ---
    # Criteria: Agent=Devin, Merged=True, Files=Mixed or Production, Additions > 200
    print("\nSearching for Devin Production Feature Case...")
    devin_prs = merged_pr_df[
        (merged_pr_df['agent'] == 'Devin') & 
        (merged_pr_df['merged_at'].notna())
    ]

    for idx, pr in devin_prs.head(100).iterrows():
        pr_id = pr['id']
        details = pr_details_df[pr_details_df['pr_id'] == pr_id]
        
        types = details['file_type'].unique()
        total_adds = details['additions'].sum()
        
        if 'Production' in types and total_adds > 200:
            print(f"\n[FOUND] Devin Case ID: {pr_id}")
            print(f"Repo: {pr['repo_url']}")
            print(f"Title: {pr['title']}")
            print(f"Body: {pr['body'][:200]}...")
            print(f"Stats: +{total_adds} lines, {len(details)} files")
            print(f"Files (first 3): {details['filename'].head(3).tolist()}")
            break

if __name__ == "__main__":
    find_representative_cases()

