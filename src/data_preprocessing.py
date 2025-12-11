import pandas as pd

def preprocess_data(pr_df, pr_details_df):
    """
    Preprocess PR and commit details data
    - Handle missing descriptions
    - Flag outliers in additions, deletions, files changed
    - Clean commit details
    """
    pr = pr_df.copy()
    details = pr_details_df.copy()
    # Handle missing descriptions
    pr['body'] = pr['body'].fillna('[No description]')
    pr['body'] = pr['body'].apply(lambda x: '[No description]' if str(x).strip() == '' else x)
    pr['has_description'] = pr['body'] != '[No description]'

    details = details.dropna(subset=['filename', 'additions', 'deletions'])
    pr_metrics = details.groupby('pr_id').agg({
        'additions': 'sum',
        'deletions': 'sum',
        'filename': 'nunique'
    }).reset_index()
    
    pr_metrics = pr_metrics.rename(columns={'filename': 'files_changed'})
    # Identify outliers using IQR method
    for col in ['additions', 'deletions', 'files_changed']:
        Q1 = pr_metrics[col].quantile(0.25)
        Q3 = pr_metrics[col].quantile(0.75)
        IQR = Q3 - Q1
        upper_limit = Q3 + 3 * IQR
        pr_metrics[f'is_outlier_{col}'] = pr_metrics[col] > upper_limit
        
    pr_metrics['is_any_outlier'] = (
        pr_metrics['is_outlier_additions'] |
        pr_metrics['is_outlier_deletions'] |
        pr_metrics['is_outlier_files_changed']
    )
    pr = pr.merge(
        pr_metrics[['pr_id', 'is_outlier_additions', 'is_outlier_deletions',
                    'is_outlier_files_changed', 'is_any_outlier']],
        left_on='id',
        right_on='pr_id',
        how='left'
    )
    pr = pr.drop(columns=['pr_id'])
    flag_cols = [
        'is_outlier_additions', 'is_outlier_deletions',
        'is_outlier_files_changed', 'is_any_outlier'
    ]
    for c in flag_cols:
        pr[c] = pr[c].fillna(False)
        
    # checking
    pr = pr.drop_duplicates(subset=['id'])
    details = details[(details['additions'] >= 0) & (details['deletions'] >= 0)]
    details = details[details['pr_id'].isin(pr['id'])]
    return pr, details

if __name__ == "__main__":
    from data_loading import load_data
    pr_df, pr_details_df = load_data()
    pr_clean, details_clean = preprocess_data(pr_df, pr_details_df)
    print(f"\nPreprocessed: {len(pr_clean)} PRs, {len(details_clean)} file changes")
    print(f"Outliers flagged: {pr_clean['is_any_outlier'].sum()} "
          f"({pr_clean['is_any_outlier'].mean() * 100:.1f}%)")
    print(f"Without description: {(~pr_clean['has_description']).sum()}")
