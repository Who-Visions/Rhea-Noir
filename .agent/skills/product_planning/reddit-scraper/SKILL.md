---
name: reddit-scraper
description: Scrapes top posts from a specified subreddit. Use when the user wants to see what's trending on Reddit or gather data from a community.
---

# Reddit Scraper Skill

This skill executes a Python script to fetch the latest top 5 posts from a subreddit.

## Instructions

1.  **Identify the Subreddit**: Extract the subreddit name from the user's request (e.g., "singularity", "python").
2.  **Execute Script**: Run the helper script located in `scripts/`.

    ```bash
    python scripts/scrape_reddit.py <subreddit_name>
    ```

3.  **Present Results**: 
    -   Parse the JSON output.
    -   Format it as a clean Markdown list or table for the user.
    -   Include the Title, Score, and Link.

## Example
**User**: "What's going on in r/machinelearning?"
**Agent**:
*Runs `python scripts/scrape_reddit.py machinelearning`*
*Outputs:*
> Here are the top posts from r/MachineLearning this week:
> 1. **[D] New Architecture Released** (Score: 450) - [Link](...)
> ...
