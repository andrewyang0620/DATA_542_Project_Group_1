# DATA 542 Project - AI Coding Agents Analysis
### Group 1: *Jingtao Yang*, *Xuanrui Qiu*

## What is this project?

This project analyzes how different AI coding agents generate pull requests (PRs) when contributing to open-source software. Using the [AIDev](https://huggingface.co/datasets/hao-li/AIDev) dataset from HuggingFace—which contains over 33,000 AI-generated pull requests and more than 700,000 file-level code modifications—we study whether these AI systems exhibit distinct coding patterns, patch characteristics, and semantic behaviors.

## Contributions
- Xuanrui Qiu
    - Dataset early investigation and project topic selection
    - RQ2 methodology design and code implementation
    - RQ3 methodology design and code implementation
    - For report, edited the abstract, introduction, and sections related to RQ2 and RQ3
- Jingtao Yang
    - Set up GitHub workflows, managed repo updates
    - Design data extraction and cleaning metrics, with code implementation
    - RQ1 methodology design and code implementation
    - For report, edited the conclusion, contribution section, and sections related to data cleaning and RQ1
  
## Files and folders

```
src/
  - data_loading.py         loads the dataset from HuggingFace
  - data_preprocessing.py   cleans the data (handles missing values, outliers)
  - plot_style.py          makes our plots look consistent
  - analysis_rq1.py    answers research question 1 (run this directly to get the results)
  - analysis_rq2.py    answers research question 2 (run this directly to get the results)

analysis_results/          where we save the plots
reports/                   final project reports
```

## Research Questions

- RQ1: Patch Characteristics. How do Agentic-PRs change code, and what are the different
characteristics (e.g., additions, deletions, files touched)?
- RQ2: Semantic Consistency. How consistent are PR descriptions with the actual code
changes?
- RQ3: File-Type Modification Patterns Across AI Agents. How does the distribution of
modified file types (e.g., production code vs. test files) characterize the structural composition
of patches produced by different AI agents? (Not yet complete for milestone 2)

## How to run it

Just run the analysis script:
```bash
python src/analysis_rq1.py  # takes about 28 seconds for loading and processing
python src/analysis_rq2.py  # takes about 236 seconds for loading and processing
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

### Step 3: Analyze

#### **RQ1 — Patch Characteristics (`analysis_rq1.py`)**

This script examines how different AI agents modify code, focusing on three patch-level metrics:

- Total additions  
- Total deletions  
- Number of unique files touched  

For each PR, we aggregate file-level diffs and compare distributions across agents using boxplots.  
We also apply the **Kruskal–Wallis H-test** to test for statistically significant differences between agents.

**Estimated running time:** **~28 seconds**  
**Output:** `analysis_results/rq1_patch_characteristics.png`

---

#### **RQ2 — Description Consistency (`analysis_rq2.py`)**

For each PR, we measure how well the description (title + body) matches the actual code changes.

Steps:
1. Concatenate all patch hunks for each PR  
2. Compute **TF–IDF vectors** for descriptions and patches  
3. Compute **cosine similarity**  
4. Compare similarity scores between merged and unmerged PRs using the **Mann–Whitney U test**

This helps evaluate whether reviewers rely on semantic clarity when deciding whether to merge AI-generated PRs.

**Estimated running time:** **~236 seconds**  
**Output:** `analysis_results/rq2_similarity_consistency.png`


The script creates box plots comparing the 5 AI agents and runs Kruskal-Wallis tests to check if the differences are real or just random variation.
