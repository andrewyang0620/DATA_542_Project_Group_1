# DATA 542 Project - AI Coding Agents Analysis
### Group 1: Jingtao Yang, Xuanrui Qiu

## What is this project?

We're analyzing how different AI coding assistants (like GitHub Copilot, Claude Code, etc.) create pull requests. Basically, we want to see if they have different coding patterns and behaviors when contributing to open source projects.

The dataset comes from HuggingFace and contains over 33,000 pull requests created by 5 different AI agents.

## Files and folders

```
src/
  - data_loading.py         loads the dataset from HuggingFace
  - data_preprocessing.py   cleans the data (handles missing values, outliers)
  - plot_style.py          makes our plots look consistent
  - analysis_rq1.py        answers research question 1 about patch sizes

analysis_results/          where we save the plots
reports/                   final project reports
```

## How the code works

### Step 1: Load the data
The `data_loading.py` file pulls data from HuggingFace. We get two main datasets:
- PR information: 33,596 pull requests with title, description, which AI made it, etc.
- PR details: 711,923 individual file changes across all those PRs

### Step 2: Clean the data
Before analyzing, we need to handle some data quality issues:

**Missing descriptions:** About 360 PRs don't have a description. We replace these with a placeholder text and add a flag so we can filter them out later if needed.

**Missing file data:** Some rows are missing critical info like filename or number of lines changed. We remove these (only 5,132 rows, less than 1%).

**Outliers:** Some PRs are huge - like 1 million lines of code changed. These might be dependency updates or auto-generated code. We flag them but keep them in the dataset since they might be interesting to study separately. We found about 6,000 outlier PRs (18%).

The preprocessing adds some helpful columns:
- `has_description` - does this PR have an actual description?
- `is_outlier_additions` - did this PR add an unusually large amount of code?
- `is_outlier_deletions` - did this PR delete an unusually large amount of code?
- `is_outlier_files_changed` - did this PR touch way more files than normal?
- `is_any_outlier` - is this PR an outlier in any way?

### Step 3: Analyze
Right now we have one analysis script for RQ1 that looks at patch characteristics:
- How many lines do different AI agents typically add/delete?
- How many files do they usually change?
- Are the differences between agents statistically significant?

The script creates box plots comparing the 5 AI agents and runs Kruskal-Wallis tests to check if the differences are real or just random variation.

## How to run it

Just run the analysis script:
```bash
python src/analysis_rq1.py
```

This will:
1. Load the data from HuggingFace
2. Clean it up
3. Create visualizations
4. Save results to `analysis_results/`

If you want to run parts separately:
```bash
python src/data_loading.py         # just load the data
python src/data_preprocessing.py   # load and clean
```

## What we learned from preprocessing

Out of 33,596 PRs and 711,923 file changes:
- Kept all PRs (100%)
- Removed 5,132 file changes with missing data (0.72%)
- Flagged 6,058 PRs as outliers (18%)

Most of the data is clean and ready to use.

## The AI agents we're studying

- **Claude Code** - Anthropic's coding assistant
- **GitHub Copilot** - Microsoft/OpenAI's tool
- **OpenAI Codex** - The model behind early Copilot
- **Cursor** - AI-powered code editor
- **Devin** - Autonomous AI software engineer
