---
name: GitLab API
description: Comprehensive GitLab API reference and interaction guide.
---

# GitLab API Skill

> **Source**: `docs.gitlab.com/api` & `gitlab.com/gitlab-org/gitlab`
> **Version**: SaaS (GitLab.com) & Self-Managed

This skill provides profound knowledge of the GitLab REST API, powered by the official OpenAPI specification.

## 1. Core Resource: OpenAPI Spec
The "Gold Standard" map of the API is located at:
`resources/openapi.yaml`

**Usage**:
- **Search**: Grep this file to find endpoint definitions, required parameters, and schemas.
- **Reference**: Use `yq` (if available) or `grep` to inspect paths.

## 2. Key Concepts

### Authentication
- **Personal/Project/Group Access Token**: `PRIVATE-TOKEN: <your_access_token>` (Recommended)
- **OAuth 2.0**: `Authorization: Bearer <access_token>` (Valid for 2 hours)
- **CI/CD Job Token**: `JOB-TOKEN: $CI_JOB_TOKEN` (Use in pipelines)

### Admin Capabilities ("Sudo")
Admins can execute actions *as another user* without knowing their credentials.
- **Header**: `Sudo: <username_or_id>`
- **Requirement**: Admin Token + `sudo` scope.
- **Example**: `curl --header "PRIVATE-TOKEN: <admin_token>" --header "Sudo: target_user" ...`

### Impersonation Tokens
Admins can create tokens that act exactly like a specific user's PAT. Use standard `PRIVATE-TOKEN` header.

### Base URL
- **SaaS**: `https://gitlab.com/api/v4`
- **Self-Managed**: `https://gitlab.example.com/api/v4`

### ID Encoding
Project and Group IDs can be integers (e.g., `123`) or URL-encoded paths (e.g., `user%2Fproject`).

### Pagination
GitLab uses Link headers for pagination.
- `x-next-page`
- `x-total-pages`

## 3. Workflow: "Scrape and Scour"
To "scour" the API for a specific capability:
1.  **Search the Spec**: `grep -i "capability_name" resources/openapi.yaml`
2.  **Inspect Definition**: Read the full YAML node for the matching endpoint.
3.  **Construct Request**: Build a `curl` command or script.

## 4. Comprehensive Resource Map ("Scoured")
This skill acknowledges and supports the entire GitLab API surface area:

### Project Resources
`Access Requests`, `Access Tokens`, `Agents`, `Branches`, `Commits`, `Container Registry`, `Deploy Keys`, `Deployments`, `Discussions`, `Environments`, `Events`, `Feature Flags`, `Issues`, `Jobs`, `Labels`, `Members`, `Merge Requests`, `Pipelines`, `Packages`, `Releases`, `Repositories`, `Runners`, `Snippets`, `Tags`, `Variables`, `Wikis`.

### Group Resources
`Epics`, `Group Badges`, `Group Variables`, `ITERATIONS`, `Milestones`, `Saml Group Links`.

### Standalone / Admin Resources
`Applications`, `Audit Events`, `Broadcast Messages`, `Geo Nodes`, `Keys`, `Namespaces`, `Settings`, `Sidekiq Metrics`, `System Hooks`, `Users`, `Version`.

### Template Resources
`Dockerfile Templates`, `Gitignore Templates`, `CI/CD YAML Templates`, `License Templates`.

## 5. Critical Engineering Nuances

### Pagination (Performance)
GitLab supports two modes. **Always prefer Keyset for large datasets.**
1.  **Offset (Default)**: `?page=1&per_page=100`. (Max offset limits apply).
2.  **Keyset (Recommended)**: `?pagination=keyset&per_page=100&order_by=id&sort=asc`.
    -   *Next Page*: extract URL from the `Link` header (`rel="next"`).

### ID vs IID
-   **ID (`id`)**: Global unique identifier across the entire GitLab instance.
-   **Internal ID (`iid`)**: Context-specific ID (e.g., Issue #5 within Project A).
    -   *Rule*: Use `iid` for specific resources like Issues/MRs within a project scope (e.g., `GET /projects/:id/issues/:iid`).

### Encoding Namespaced Paths
**CRITICAL**: Forward slashes `/` in paths/branches must be URL-encoded as `%2F`.
-   *Wrong*: `GET /projects/group/project`
-   *Right*: `GET /projects/group%2Fproject`
-   *Right*: `GET /projects/1/files/src%2FREADME.md`

### Rate Limits (429 Prevention)
Monitor these headers in responses:
-   `RateLimit-Remaining`: Requests left in current window.
-   `RateLimit-Reset`: Unix timestamp when quota resets.

### Complex Parameters (Arrays & Hashes)
-   **Arrays**: `?import_sources[]=github&import_sources[]=bitbucket`
-   **Hashes**: `?override_params[visibility]=private`

### Tier Availability
Features may be restricted by Tier (Free, Premium, Ultimate). If you receive `403 Forbidden` on a valid endpoint, check the feature's tier requirement.

## 6. "Scraping" Workflow (On-Demand)
Since the API is vast, use this workflow to get deep details for any resource:
1.  **Identify Resource**: Pick from the list above.
2.  **Construct URL**: `https://docs.gitlab.com/api/<resource_snake_case>.html` (e.g., `.../api/merge_requests.html`)
3.  **Fetch**: Use `read_url_content` to "scrape" the specific parameter details when needed.

## 7. Recommended Community Libraries
While the API is REST-based, these clients are highly recommended for complex logic:
-   **Python**: `python-gitlab` (Excellent abstraction).
-   **Node.js**: `@gitbeaker/rest` (Full coverage).
-   **Rust**: `gitlab` crate.
-   **Go**: `xanzy/go-gitlab`.
-   **Ruby**: `gitlab` gem.

## 9. Critical Deprecations (v4 -> v5)
Avoid these legacy fields; they will break in future updates.

### Project & Merge Requests
-   **Merged By**: Use `merge_user` instead of `merged_by`.
-   **Merge Status**: Use `detailed_merge_status` instead of `merge_status`.
-   **Approvals**: "Approvers" loop endpoints are deprecated; use "Approval Rules".
-   **Managed Licenses**: Replaced by **License Approval Policies**.

### Infrastructure
-   **Geo**: `geo_nodes` is now `geo_sites`.
-   **Runners**: `active` field is deprecated; check `paused` (boolean). `ip_address` will disappear in v5.

### Other
-   **Users**: `private_profile` cannot be `null` (must be `true`/`false`).
-   **Import**: `namespace` param is deprecated (ambiguous); use `namespace_id` or `namespace_path`.

## 10. Interactive Testing (Manual)
For ad-hoc verification, use the **Interactive API Docs** on GitLab.com:
1.  Go to `https://gitlab.com/-/openapi`
2.  Click **Authorize** (Enter PAT).
3.  Use "Try it out" to generate valid `curl` commands.
*Note: As officially confirmed, this spec is partial. Use the "Scraping Workflow" (Section 6) for missing endpoints.*

## 11. Example: Creating a Project
```

## 12. Storage Automation & Cleanup
Automate cleanup to manage storage quotas (Free/Premium limits).
-   **Job Artifacts**: `DELETE /projects/:id/artifacts` (Bulk delete).
-   **Old Pipelines**: Script loop required (fetch pipelines -> check `created_at` -> delete).
-   **Container Registry**: Use Cleanup Policies (`PUT /projects/:id` with `container_expiration_policy_attributes`).

## 13. Troubleshooting (Advanced)
-   **400 Bad Request**: Check for validation errors in `message` JSON object.
-   **Spam Detection**: If `needs_captcha_response: true`, you must solve reCAPTCHA (v2) and pass `X-GitLab-Captcha-Response`.
-   **Reverse Proxy 404s**: If using a proxy (Nginx/Apache), define `AllowEncodedSlashes NoDecode` to support namespaced paths (`%2F`).

## 14. GitLab CLI (`glab`)
Official CLI for terminal-based interaction.
-   **Config**: `glab config set host gitlab.example.com` (Self-Managed).
-   **Auth**: `glab auth login` (Handles OAuth/PAT).
-   **Remotes**: Auto-detects context from `git remote -v`.
-   **Key Env Vars**: `GITLAB_TOKEN` (Auth), `GITLAB_HOST` (Target).

## 15. OAuth 2.0 Flows
For integrations requiring user context:
1.  **Code Flow (PKCE)**: Recommended for public clients (SPA/Mobile).
    -   *Authorize*: `GET /oauth/authorize?response_type=code`
    -   *Token*: `POST /oauth/token` (Exchange code for token).
2.  **Device Flow**: For headless terminals (`POST /oauth/authorize_device`).
3.  **Scopes**: `read_api`, `api`, `read_user`.

## 16. Webhooks (Real-Time)
-   **Events**: Push, Merge Request, Issue, Pipeline.
-   **Security**: Verify `X-Gitlab-Token` header.
-   **Reliability**: Endpoint MUST return `200` quickly. Use a queue (Redis) for processing.
-   **Auto-Disable**: GitLab disables hooks after 4 consecutive fails.

## 17. Editor Extensions
-   **VS Code**: GitLab Workflow (full feature set).
-   **JetBrains**: GitLab Duo (AI).
-   **Neovim**: GitLab.nvim.
*Use these for "in-flow" code reviews and AI monitoring.*

## 18. Integrations Ecosystem
-   **Security Partners**: integrations available for `Anchore`, `Checkmarx`, `Snyk`, `Tenable`, `Veracode`.
-   **Auth Providers**: LDAP, SAML, OmniAuth (Google/GitHub/etc).
-   **Project**: Native integrations for Jira, Slack, Jenkins.
-   **Troubleshooting**:
    -   *SSL Errors*: Use trusted certs or `gitlab_rails['http_client']['tls_client_cert_file']`.
    -   *Test Failed*: Push a test commit if "Test Failed. Save Anyway" appears on empty repos.
