---
name: convex-integration
description: Provides best practices and patterns for building backends with Convex (Real-time DB + Functions). Use when the user specifically asks for "Convex" or a "real-time database".
---

# Convex Integration Skill

This skill guides the implementation of the Convex backend platform.

## Core Concepts
1.  **Database**: Defined in `convex/schema.ts`.
2.  **Functions**:
    -   `query`: Read-only, reactive.
    -   `mutation`: Write operations.
    -   `action`: 3rd party API calls (non-deterministic).

## Directory Structure
-   `convex/`
    -   `schema.ts`: Database schema definition.
    -   `myFunctions.ts`: API endpoints.
    -   `auth.config.ts`: Authentication setup (Clerk/Auth0).

## Implementation Rules
1.  **Define Schema First**: Always define tables in `schema.ts` using `defineSchema` and `defineTable`.
2.  **Type Safety**: Use `v` from `convex/values` to validate arguments.
3.  **Real-time UI**: Use the `useQuery` hook in React components for automatic updates.

## Example Code
### Schema (`convex/schema.ts`)
```typescript
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
  }),
});
```

### Mutation (`convex/todos.ts`)
```typescript
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const createTask = mutation({
  args: { text: v.string() },
  handler: async (ctx, args) => {
    await ctx.db.insert("tasks", { text: args.text, isCompleted: false });
  },
});
```
