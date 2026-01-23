---
name: api-design
description: Enforces best practices for Next.js REST API routes, including Zod validation, TypeScript typing, and consistent error responses.
---

# API Design Skill

This skill ensures that all backend API routes are robust, type-safe, and secure.

## Standards

1.  **Framework**: Use Next.js App Router (`app/api/route.ts`).
2.  **Validation**: Use `zod` for all request body/query validation.
3.  **Typing**: 
    -   Define a `Request` schema.
    -   Define a `Response` interface.
4.  **Error Handling**:
    -   Use `try/catch` blocks.
    -   Return standard HTTP status codes (200, 400, 401, 500).
    -   Return JSON: `{ success: false, error: "message" }`.

## Template

When creating a new API route, use this structure:

```typescript
import { NextResponse } from 'next/server';
import { z } from 'zod';

// 1. Schema Definition
const RequestSchema = z.object({
  email: z.string().email(),
  // ... other fields
});

// 2. Handler
export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // 3. Validation
    const validatedData = RequestSchema.parse(body);

    // 4. Business Logic
    // ...

    return NextResponse.json({ success: true, data: ... });
  } catch (error) {
    if (error instanceof z.ZodError) {
        return NextResponse.json({ success: false, error: error.errors }, { status: 400 });
    }
    return NextResponse.json({ success: false, error: "Internal Server Error" }, { status: 500 });
  }
}
```

## Checklist
- [ ] Is input validated with Zod?
- [ ] Are sensitive errors masked in production?
- [ ] Is the response type explicitly clear?
