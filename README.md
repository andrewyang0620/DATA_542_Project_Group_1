# **DATA 542 – Project Milestone 1**  **Group 1:** Jingtao Yang, Xuanrui Qiu

## **RQ1: How do Agentic-PRs change code, and what are the different characteristics (e.g., additions, deletions, files touched)?**

**Methodology**

* Data Extraction: the pull\_request subset and pr\_commit\_details subset, join using pull\_request.id \= pr\_commit\_details.pr\_id to obtain file-level diffs for each PR.  
* Data Wrangling: For each PR, compute three patch metrics: total additions, total deletions, and number of unique files changed. Merge these aggregated patch statistics with the agent label to compare patch behavior across AI tools.  
* Visualization: distributions using boxplots or violin plots to examine differences in PR size and file-touch patterns.  
* Statistical Testing: Perform statistical significance tests with ANOVA or Kruskal–Wallis to evaluate whether patch characteristics differ across AI agents.  
* Interpretation: how PR size and scope relate to maintainability concerns and potential differences in agent behavior.

## **RQ2: How consistent are PR descriptions with the actual code changes?**

**Methodology**

* Data Extraction: use pull\_request and pr\_commit\_details, join using pull\_request.id \= pr\_commit\_details.pr\_id to associate each PR with its actual code changes.  
* Text Preparation: Construct PR description with title and body fields, and aggregate all patches for each PR to obtain a unified representation of the actual code modifications.   
* Matrics applied: Apply NLP techniques, TF-IDF for example, with cosine similarity or sentence-embedding models to quantify the semantic similarity between the PR description and the patch.  
* Comparison Analysis: Merge similarity scores with PR status metadata to compare consistency patterns between merged and unmerged PRs.  
* Visualization: Plot similarity distributions across agents and PR outcomes using kernel density estimates and boxplots for visualization  
* Statistical Analysis: Use t-tests, Mann–Whitney U, or logistic regression to evaluate whether low similarity between text and patch correlates with higher rejection rate (merged\_at/not)

## **RQ3: How does the distribution of modified file types (e.g., production code vs. test files) characterize the structural composition of patches produced by different AI agents?**

**Methodology**

* Data Extraction: Join the pull\_request table with pr\_commit\_details from the curated subset to access file-level information.  
* File Classification: Apply heuristic rules (regex matching on file paths) to classify touched files into categories: Production (e.g., .py, .java), Test (e.g., test\_\*.py, \*.spec.ts), and Configuration/Docs.  
* Metric Computation: Calculate the "File Type Ratio" per PR (e.g., % of files that are tested) to define the patch's structural profile.  
* Comparative Analysis: Group data by the five agents (Copilot, Devin, Codex, Cursor, Claude Code) to compare the propensity of each agent to touch specific file combinations.  
* Statistical Testing: Use Chi-square tests or multi-class comparisons to determine the distribution of "Mixed-Type Patches" (code \+ test) vs. "Single-Type Patches" differs significantly among agents.