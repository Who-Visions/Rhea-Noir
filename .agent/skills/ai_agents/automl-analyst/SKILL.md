---
name: automl-analyst
description: Automatically analyzes datasets to perform classification, regression, or clustering. Generates Python training scripts and HTML reports.
---

# AutoML Analyst Skill

This skill turns the agent into a data scientist that autonomously trains models and reports results.

## Workflow

1.  **Data Analysis**:
    -   Read the input file (CSV/JSON).
    -   Determine the problem type:
        -   **Regression**: Predicting a number (e.g., predicted_ltv).
        -   **Classification**: Predicting a category (e.g., churn/no_churn).
        -   **Clustering**: grouping data (e.g., customer_segments) if no target is specified.

2.  **Code Generation**:
    -   Write a python script (e.g., `train_model.py`) using `pandas` and `scikit-learn`.
    -   The script MUST output metrics and generate plots (saved as images).

3.  **Reporting**:
    -   Read `resources/report_template.html`.
    -   Inject the results (metrics, plot images, summary) into the template.
    -   Save the final report as `report.html`.

## Code Guidelines
-   Handle missing values (impute or drop).
-   Encode categorical variables.
-   Use `matplotlib` or `seaborn` for plots.

## Example
**User**: "Analyze this customer_churn.csv."
**Agent**:
1.  Detects 'churn' column -> Classification problem.
2.  Writes `train_churn.py` -> Trains Random Forest -> Accuracy 85%.
3.  Generates `churn_report.html` with feature importance plot.
