# AIDev Dataset Programming Guide for LLMs

## 1. Dataset Overview & Context
**AIDev** is a comprehensive dataset capturing "Agentic-PRs"—pull requests authored specifically by Autonomous Coding Agents on GitHub[cite: 8, 989]. [cite_start]This dataset is designed to support research on AI adoption, developer productivity, and human-AI collaboration (SE 3.0)[cite: 988, 992].

* [cite_start]**Scale (Challenge Snapshot):** Contains **932,791 Agentic-PRs** across **116,211 repositories** involving **72,189 developers**[cite: 990, 991].
* [cite_start]**Target Agents:** OpenAI Codex, Devin, GitHub Copilot, Cursor, and Claude Code[cite: 990].
* **Data Structure:**
    * [cite_start]**Full Dataset:** Covers all ~932k PRs with core metadata[cite: 990].
    * [cite_start]**Enriched Subset (AIDEV-POP):** A curated subset of **33,596 PRs** from popular repositories (>100 stars), containing detailed artifacts like review comments, commit diffs, and timelines[cite: 991, 1006].

---

## 2. Database Schema (Relational)
The dataset follows a relational schema centered on the `pull_request` table. [cite_start]Use the following definitions for SQL or Pandas operations[cite: 426, 1050].

### A. Core Metadata (Available for All Records)
* **`pull_request`** (Primary Table)
    * [cite_start]**Key Fields:** `id` (PK), `number`, `title`, `body`, `user_id` (FK), `repo_id` (FK), `state` (open/closed/merged), `created_at`, `merged_at`, `closed_at`[cite: 1050].
    * **Description:** The central table containing basic PR info.
* **`repository`**
    * [cite_start]**Key Fields:** `id` (PK), `full_name`, `language` (e.g., Python, TypeScript), `stars`, `forks`[cite: 1050].
    * **Description:** Project-level metadata. Join via `repo_id`.
* **`user`**
    * [cite_start]**Key Fields:** `id` (PK), `login`, `type` (User/Bot), `company`, `location`[cite: 1050].
    * **Description:** Developer or Agent identity. Join via `user_id`.

### B. Enriched Artifacts (Subset Only: >100 Stars)
* **`pr_comments` / `pr_reviews`**
    * [cite_start]**Key Fields:** `pr_id` (FK), `body`, `state` (e.g., APPROVED), `author_association`[cite: 1050].
    * **Usage:** Analyze discussion sentiment and review outcomes.
* **`pr_commits` / `pr_commit_details`**
    * [cite_start]**Key Fields:** `pr_id` (FK), `sha`, `additions`, `deletions`, `filename`, `patch`[cite: 435, 1050].
    * **Usage:** Analyze code complexity and file churn.
* **`pr_timeline`**
    * [cite_start]**Key Fields:** `pr_id` (FK), `event` (e.g., committed, mentioned, labeled), `created_at`[cite: 1050].
    * **Usage:** Reconstruct the exact lifecycle of the PR.
* **`pr_task_type`**
    * [cite_start]**Key Fields:** `pr_id` (FK), `task_type` (e.g., `feat`, `fix`, `docs`, `refactor`)[cite: 1050].
    * [cite_start]**Source:** Generated via GPT-4 based on Conventional Commits specification[cite: 450].

---

## 3. Agent Identification Logic
The dataset uses specific filters to identify which agent authored a PR. [cite_start]Use these criteria when filtering `pull_request` or `user` tables[cite: 184]:

| Agent Name | Identification Rule / Query |
| :--- | :--- |
| **OpenAI Codex** | `is:pr head:codex/` |
| **Devin** | `author:devin-ai-integration[bot]` |
| **GitHub Copilot** | [cite_start]`is:pr head:copilot/` **AND** user login is "copilot" [cite: 192] |
| **Cursor** | `is:pr head:cursor/` |
| **Claude Code** | PR body or commits contain `"Co-Authored-By: Claude"` |

*Note: Launch dates vary (e.g., Codex in May 2025, Devin in Dec 2024). [cite_start]Verify timestamps when analyzing trends[cite: 184].*

---

## 4. Key Analysis Metrics & Goals
When writing analysis code, focus on these verified metrics from the research:

1.  **Acceptance Rate (Merges):**
    * *Formula:* `Count(merged_at is not NULL) / Total PRs`.
    * [cite_start]*Context:* Agents often have lower acceptance rates than humans, particularly for `feat` and `fix` tasks[cite: 473].
2.  **Resolution Time (Speed):**
    * *Formula:* `closed_at` - `created_at`.
    * [cite_start]*Context:* Agents like Copilot and Codex can resolve PRs significantly faster (median < 20 mins) than humans[cite: 555, 611].
3.  **Review Dynamics:**
    * *Approach:* Classify reviewers into "Human" vs "Bot" using the `user` table.
    * [cite_start]*Pattern:* Look for "Provider-Specific Loops" (e.g., GitHub Copilot PRs reviewed by `copilot-pull-request-reviewer`)[cite: 698, 701].
4.  **Code Quality & Complexity:**
    * *Approach:* Calculate `additions` + `deletions` in `pr_commit_details`.
    * [cite_start]*Insight:* Agentic PRs often introduce less structural complexity (lower Cyclomatic Complexity changes) compared to humans[cite: 109, 779].

---

## 5. Data Handling Instructions for LLMs
* [cite_start]**Date Parsing:** All timestamp fields (e.g., `2025-05-16T...`) must be converted to datetime objects immediately[cite: 194].
* [cite_start]**Subset Filtering:** When querying `pr_commits` or `pr_reviews`, **always** join with `repository` and filter for `stars > 100` (or ensuring the PR exists in the subset), as these tables are not populated for the full 932k dataset[cite: 1011].
* [cite_start]**Task Types:** Use the pre-computed `pr_task_type` table rather than attempting to re-classify titles, as it uses a standardized GPT-based classification[cite: 450].