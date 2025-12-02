import pandas as pd

def load_data():
    all_pr_df = pd.read_parquet("hf://datasets/hao-li/AIDev/all_pull_request.parquet", columns=['id', 'agent', 'merged_at'])
    pr_part_df = pd.read_parquet("hf://datasets/hao-li/AIDev/pull_request.parquet", columns=['id', 'title', 'body', 'state'])
    pr_details_df = pd.read_parquet("hf://datasets/hao-li/AIDev/pr_commit_details.parquet", columns=['pr_id', 'filename', 'additions', 'deletions', 'patch'])

    pr_df = pd.merge(pr_part_df, all_pr_df[['id','agent','merged_at']], on='id', how='inner')

    print(f"pr loaded: {len(pr_df)} rows")
    print(f"pr commit detail loaded: {len(pr_details_df)} rows")

    return pr_df, pr_details_df

if __name__ == "__main__":
    load_data()
