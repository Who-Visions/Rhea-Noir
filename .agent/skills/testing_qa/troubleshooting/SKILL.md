---
name: troubleshooting
description: Systematically diagnoses and fixes errors, bugs, or unexpected behavior. Use when the user reports a crash, error message, or "it's not working".
---

# Troubleshooting Skill

This skill guides the debugging process to ensure root causes are identified before applying fixes.

## Instructions

1.  **Information Gathering**:
    -   If an error message is missing, ASK for it.
    -   If the reproduction steps are unclear, ASK for them.
    -   *Action*: "Can you share the error stack trace?" or "How can I reproduce this?"

2.  **Hypothesis Generation**:
    -   List 2-3 potential causes based on the evidence.
    -   Example: "1. API key is missing. 2. Network timeout. 3. Invalid JSON format."

3.  **Verification (The "Science" Part)**:
    -   Don't guess—verify!
    -   Add print statements or logs to confirm assumptions.
    -   Check environment variables.

4.  **The Fix**:
    -   Apply the fix.
    -   **Critical**: Verify the fix worked by running the code again.

## Common Patterns
-   **ImportError**: Check `sys.path` or circular imports.
-   **TypeError**: Check input types (use `type()`).
-   **403/401**: Check tokens/permissions.
