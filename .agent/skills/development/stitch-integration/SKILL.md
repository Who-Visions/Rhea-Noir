# Google Stitch API Integration

> **Description**: Integration with Google Stitch API (`stitch.googleapis.com`) for AI-powered UI generation.
> **Category**: `development`
> **Tags**: `ui`, `ai`, `google-labs`, `generative-ui`

## Overview
Google Stitch API allows developers to generate and hydrate UI components dynamically using text, image, or code prompts. This skill provides the standard client implementation for Next.js applications.

## Integration Steps

1.  **Install SDK**: (Currently simulated via `lib/stitch.ts`)
2.  **Configure**: Set `STITCH_API_KEY` (Mocked for now).
3.  **Usage**: Use the `StitchProvider` to wrap your application or specific components.

## Example Usage

```typescript
import { StitchGenerator } from '@/lib/stitch';

const stitch = new StitchGenerator();
const ui = await stitch.generate('A beautiful pricing table for a tutoring service');
```
