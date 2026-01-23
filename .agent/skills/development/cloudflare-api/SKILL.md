---
name: Cloudflare API
description: Comprehensive Cloudflare API reference and interaction guide.
---

# Cloudflare API Skill

> **Source**: `developers.cloudflare.com/api` & `github.com/cloudflare/api-schemas`
> **Version**: Live OpenAPI Spec

This skill provides deep knowledge and interaction capabilities for the Cloudflare API, based on the official OpenAPI 3.0 specification.

## 1. Core Resource: OpenAPI Spec
The "Gold Standard" map of the API is located at:
`resources/openapi.json`

**Usage**:
- **Search**: Grep this file to find endpoint definitions, required parameters, and schemas.
- **Reference**: Use `jq` to extract specific paths (e.g., `cat openapi.json | jq '.paths["/zones/{zone_id}/dns_records"]'`).

## 2. Key Concepts

### Authentication
Most endpoints require an API Token.
Header: `Authorization: Bearer <YOUR_TOKEN>`

### Base URL
`https://api.cloudflare.com/client/v4`

## 3. Coverage Verified
This skill covers the **complete** Cloudflare ecosystem, including but not limited to:
- **AI & Data**: Vectorize, AI Gateway, AI Search, R2, D1, Queues, Hyperdrive.
- **Compute**: Workers, Durable Objects, Workflows, Pages.
- **Security**: Zero Trust, WAF, Turnstile, Bot Management, SSL/TLS.
- **Network**: Magic Transit, Spectrum, DNS, Zones, Load Balancers.
- **Observability**: GraphQL Analytics, Logpush, Radar.

## 4. Workflow: "Scrape and Scour"
To "scour" the API for a specific capability:
1.  **Search the Spec**: `grep -i "capability_name" resources/openapi.json`
2.  **Inspect Definition**: Read the full JSON node for the matching endpoint.
3.  **Construct Request**: Build a `curl` command or script based on the required properties.

## 4. Example: Listing DNS Records
```bash
# 1. Find the endpoint in spec
grep -r "dns_records" resources/openapi.json

# 2. Construct Call
curl -X GET "https://api.cloudflare.com/client/v4/zones/<ZONE_ID>/dns_records" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json"
```
