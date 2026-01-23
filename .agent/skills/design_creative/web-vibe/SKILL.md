---
name: web-vibe
description: A skill for scaffolding premium, "Vibe-Coded" web applications using Vite, React, and Vanilla CSS.
---

# Web Scaffold Skill ("Vibe Engine")

This skill provides a standardized way to generate high-quality, aesthetically pleasing web applications. It leverages a custom "Vibe" CSS engine to deliver a premium look (Glassmorphism, Neon, Dark Mode) out of the box.

## Usage

When the user asks to "start a new website" or "build a web app", choose the best tool:

1. **Web App (Route-Heavy)**: Use `npx create-next-app@latest .` (TypeScript, ESLint, Tailwind=No, Src=Yes, AppRouter=Yes).
2. **Prototype / Visuals**: Use `npx create-vite@latest ./ --template react-ts`.

## Templates

### 1. The Vibe Engine (`globals.css` / `index.css`)

This CSS file establishes the design system. It works for both Vite (`index.css`) and Next.js (`app/globals.css`).

```css
:root {
  /* 🌌 Deep Space Palette */
  --bg-deep: #0a0a12;
  --bg-surface: #13131f;
  --bg-card: rgba(25, 25, 35, 0.6);
  --bg-glass: rgba(255, 255, 255, 0.05);

  /* ⚡ Neon Accents */
  --accent-primary: #6c5ce7; /* Electric Indigo */
  --accent-secondary: #00cec9; /* Cyber Cyan */
  --accent-glow: rgba(108, 92, 231, 0.4);
  --accent-danger: #ff7675;

  /* 🌟 Typography */
  --text-primary: #ffffff;
  --text-secondary: #a4b0be;
  --font-main: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* 💎 Glassmorphism */
  --glass-border: 1px solid rgba(255, 255, 255, 0.1);
  --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  --backdrop-blur: blur(12px);

  /* 🚀 Animations */
  --ease-elastic: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-deep);
  background-image: 
    radial-gradient(circle at 10% 20%, rgba(108, 92, 231, 0.15) 0%, transparent 20%),
    radial-gradient(circle at 90% 80%, rgba(0, 206, 201, 0.15) 0%, transparent 20%);
  color: var(--text-primary);
  font-family: var(--font-main);
  min-height: 100vh;
  overflow-x: hidden;
  line-height: 1.6;
}

/* --- Utilities --- */

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.glass-panel {
  background: var(--bg-card);
  backdrop-filter: var(--backdrop-blur);
  -webkit-backdrop-filter: var(--backdrop-blur);
  border: var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: 16px;
  padding: 2rem;
}

.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(8px);
  border: var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform 0.3s var(--ease-elastic), box-shadow 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(108, 92, 231, 0.2);
  border-color: rgba(108, 92, 231, 0.3);
}

.title-gradient {
  background: linear-gradient(135deg, #fff 0%, var(--text-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
  letter-spacing: -0.05em;
}

.btn-neon {
  background: linear-gradient(135deg, var(--accent-primary) 0%, #a29bfe 100%);
  border: none;
  border-radius: 50px;
  padding: 0.8rem 2rem;
  color: white;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px var(--accent-glow);
}

.btn-neon:hover {
  box-shadow: 0 6px 25px var(--accent-glow);
  transform: scale(1.05);
}

/* --- Keyframes --- */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}
```

### 2. The App Shell (`App.tsx`)

A clean, modern shell that demonstrates the vibe.

```tsx
import { useState } from 'react';
import './index.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '4rem', paddingTop: '4rem' }}>
        <h1 className="title-gradient" style={{ fontSize: '4rem', marginBottom: '1rem' }}>
          Vibe Scaffold
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>
          Premium Aesthetics. Ready to Code.
        </p>
      </header>

      <main style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        
        <div className="glass-panel animate-float">
          <h2 style={{ marginBottom: '1rem', color: 'var(--accent-secondary)' }}>✨ Glassmorphism</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Built-in support for frosted glass effects using the <code>.glass-panel</code> and <code>.glass-card</code> classes.
          </p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div className="glass-card" style={{ flex: 1, textAlign: 'center' }}>Card 1</div>
            <div className="glass-card" style={{ flex: 1, textAlign: 'center' }}>Card 2</div>
          </div>
        </div>

        <div className="glass-panel" style={{ animationDelay: '1s' }}>
          <h2 style={{ marginBottom: '1rem', color: 'var(--accent-primary)' }}>🚀 Interactive</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Buttons and interactions are tuned for delight.
          </p>
          <div style={{ textAlign: 'center' }}>
            <button className="btn-neon" onClick={() => setCount(c => c + 1)}>
              Count is {count}
            </button>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
```

### 3. The App Shell (Next.js App Router)

For Next.js projects, use these templates for `app/layout.tsx` and `app/page.tsx`.

**`app/layout.tsx`**

```tsx
import './globals.css';
import type { Metadata, Viewport } from 'next';

export const metadata: Metadata = {
  title: 'Vibe Scaffold',
  description: 'Premium Aesthetics. Ready to Code.',
};

export const viewport: Viewport = {
  themeColor: '#0a0a12',
  colorScheme: 'dark',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

**`app/page.tsx`**

```tsx
export default function Home() {
  return (
    <div className="container">
      <header style={{ textAlign: 'center', marginBottom: '4rem', paddingTop: '4rem' }}>
        <h1 className="title-gradient" style={{ fontSize: '4rem', marginBottom: '1rem' }}>
          Vibe Scaffold
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>
          Next.js 16 App Router Edition
        </p>
      </header>

      <main style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        <div className="glass-panel animate-float">
          <h2 style={{ marginBottom: '1rem', color: 'var(--accent-secondary)' }}>✨ Glassmorphism</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
             Built-in support for frosted glass effects.
          </p>
        </div>
      </main>
    </div>
  );
}
```

**`app/loading.tsx`**

```tsx
export default function Loading() {
  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center' 
    }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <div className="title-gradient animate-float">Loading Vibe...</div>
      </div>
    </div>
  );
}
```

**`components/Navbar.tsx`**

```tsx
import Link from 'next/link';

export function Navbar() {
  return (
    <nav className="glass-panel" style={{ marginBottom: '2rem', display: 'flex', gap: '1rem' }}>
      <Link href="/" className="btn-neon" style={{ background: 'transparent', boxShadow: 'none' }}>Home</Link>
      <Link href="/about" className="btn-neon" style={{ background: 'transparent', boxShadow: 'none' }}>About</Link>
    </nav>
  );
}
```

### 4. Client vs Server Pattern ("Vibe Bridge")

Use this pattern to add interactivity (Client) to your static (Server) pages while maintaining the Vibe.

**`components/NeonInteractive.tsx` (Client)**

```tsx
'use client';

import { useState } from 'react';

export function NeonInteractive() {
  const [active, setActive] = useState(false);

  return (
    <div 
      className={`glass-card ${active ? 'active' : ''}`}
      onClick={() => setActive(!active)}
      style={{ 
        cursor: 'pointer',
        border: active ? '1px solid var(--accent-secondary)' : 'var(--glass-border)'
      }}
    >
      <h3 style={{ color: active ? 'var(--accent-secondary)' : 'inherit' }}>
        {active ? '⚡ Active State' : 'Click Me'}
      </h3>
    </div>
  );
}
```

**`app/page.tsx` (Server)**

```tsx
import { NeonInteractive } from '@/components/NeonInteractive';

export default function Page() {
  return (
    <div className="container">
       <div className="glass-panel">
         <h2>Hybrid Vibe</h2>
         {/* Interactivity injected here */}
         <NeonInteractive />
       </div>
    </div>
  );
}
```

### 5. Vibe Cache Pattern (Next.js Cache Components)

Use this pattern to cache expensive data fetches or computations, creating a fast static shell.

**`components/CachedData.tsx` (Server)**

```tsx
import { cacheLife } from 'next/cache';

async function fetchVibeStats() {
  'use cache';
  cacheLife('hours'); // Cache for hours
  
  // Simulate expensive fetch
  await new Promise(resolve => setTimeout(resolve, 100)); 
  return { users: 1240, active: 85 };
}

export async function CachedVibeStats() {
  const stats = await fetchVibeStats();
  
  return (
    <div className="glass-card">
       <h4 style={{ color: 'var(--accent-primary)' }}>Cached Stats</h4>
       <p>Users: {stats.users}</p>
       <p>Active: {stats.active}</p>
       <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>
         Updated: {new Date().toLocaleTimeString()}
       </p>
    </div>
  );
}
```

## Advanced Patterns

### Integrating with Gemini

Instantiate `GoogleGenerativeAI` in a dedicated `services/gemini.ts` file.

```typescript
// services/gemini.ts
import { GoogleGenerativeAI } from "@google/generative-ai";

const API_KEY = process.env.GEMINI_API_KEY!;
const genAI = new GoogleGenerativeAI(API_KEY);

export const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash-exp" });
```

### Server Actions (Mutations)

Use `'use server'` for form submissions and data mutations.

**`app/actions.ts`**

```tsx
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { headers } from 'next/headers'

export async function createPost(formData: FormData) {
  const headersList = await headers()
  const title = formData.get('title') as string
  
  // Mutate data...
  // await db.post.create({ data: { title } })
  
  // Refresh UI
  revalidatePath('/posts')
  redirect('/posts')
}
```

**`components/VibeForm.tsx`**

```tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

export function VibeForm() {
  const [state, action, pending] = useActionState(createPost, null)
  
  return (
    <form action={action} className="glass-panel">
      <input 
        name="title" 
        placeholder="Enter title..." 
        style={{ 
          background: 'var(--bg-glass)', 
          border: 'var(--glass-border)',
          padding: '1rem',
          borderRadius: '8px',
          color: 'var(--text-primary)'
        }} 
      />
      <button type="submit" className="btn-neon" disabled={pending}>
        {pending ? 'Creating...' : 'Create'}
      </button>
    </form>
  )
}
```

### Streaming with Suspense

**`app/feed/page.tsx`**

```tsx
import { Suspense } from 'react'

export default function FeedPage() {
  return (
    <div className="container">
      <h2 className="title-gradient">Live Feed</h2>
      
      <Suspense fallback={<FeedSkeleton />}>
        <VibeFeed />
      </Suspense>
    </div>
  )
}

function FeedSkeleton() {
  return (
    <div className="glass-card animate-pulse" style={{ height: '200px' }}>
      <div style={{ height: '20px', width: '60%', background: 'rgba(255,255,255,0.1)', borderRadius: '4px' }} />
    </div>
  )
}

async function VibeFeed() {
  const data = await fetch('https://api.example.com/feed', { cache: 'no-store' })
  const items = await data.json()
  
  return (
    <div style={{ display: 'grid', gap: '1rem' }}>
      {items.map((item: any, i: number) => (
        <div key={i} className="glass-card animate-float" style={{ animationDelay: `${i * 0.1}s` }}>
          {item.title}
        </div>
      ))}
    </div>
  )
}
```

### Error Boundaries

**`app/error.tsx`**

```tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <div className="glass-panel" style={{ maxWidth: '500px', margin: '0 auto' }}>
        <h2 style={{ color: 'var(--accent-danger)', marginBottom: '1rem' }}>
          ⚠️ Something went wrong
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          {error.message}
        </p>
        <button className="btn-neon" onClick={reset}>
          Try Again
        </button>
      </div>
    </div>
  )
}
```

**`app/not-found.tsx`**

```tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <div className="glass-panel animate-float" style={{ maxWidth: '500px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '6rem', marginBottom: '1rem', color: 'var(--accent-primary)' }}>404</h1>
        <h2 className="title-gradient" style={{ marginBottom: '1rem' }}>Page Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          The page you're looking for doesn't exist.
        </p>
        <Link href="/" className="btn-neon">
          Return Home
        </Link>
      </div>
    </div>
  )
}
```

## next.config.ts (Recommended)

```typescript
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Use Cache (PPR & Cache Components)
  experimental: {
    reactCompiler: true,
    ppr: true,
    dynamicIO: true,
    authInterrupts: true, // Allow forbidden() and unauthorized()
  },
  // Images
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  // Type Safety
  typedRoutes: true,
}

export default nextConfig
```

### Image Optimization

Use `next/image` for automatic WebP conversion and lazy loading.

**`components/VibeImage.tsx`**

```tsx
import Image from 'next/image';

export function VibeImage({ src, alt }: { src: string; alt: string }) {
  return (
    <div className="glass-card" style={{ overflow: 'hidden', position: 'relative' }}>
      <Image
        src={src}
        alt={alt}
        width={500}
        height={300}
        style={{ objectFit: 'cover', borderRadius: '8px' }}
        placeholder="blur"
        blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
      />
    </div>
  );
}
```

### Font Optimization

Use `next/font` for zero-layout-shift font loading.

**`app/layout.tsx` (with custom fonts)**

```tsx
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-main'
});

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono'
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

### Route Handlers (API Endpoints)

**`app/api/vibe/route.ts`**

```tsx
import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ 
    vibe: 'active', 
    timestamp: new Date().toISOString() 
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  // Process data...
  
  return NextResponse.json({ 
    success: true, 
    received: body 
  });
}
```

### Proxy (Request/Response Modification)

**`proxy.ts`**

```tsx
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  // Auth check example
  const session = request.cookies.get('session');
  
  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
};
```

### Dynamic OG Image Generation

**`app/opengraph-image.tsx`**

```tsx
import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default async function Image() {
  return new ImageResponse(
    (
      <div style={{
        background: 'linear-gradient(135deg, #0a0a12 0%, #13131f 100%)',
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
      }}>
        <div style={{
          fontSize: 72,
          fontWeight: 800,
          background: 'linear-gradient(135deg, #6c5ce7 0%, #00cec9 100%)',
          backgroundClip: 'text',
          color: 'transparent',
        }}>
          Vibe Scaffold
        </div>
        <div style={{ fontSize: 32, color: '#a4b0be', marginTop: 20 }}>
          Premium Aesthetics. Ready to Code.
        </div>
      </div>
    )
  );
}
```

## Quick Reference

| Pattern | File | Purpose |
|---------|------|---------|
| Layout | `app/layout.tsx` | Root shell + fonts |
| Page | `app/page.tsx` | Route UI |
| Loading | `app/loading.tsx` | Streaming skeleton |
| Error | `app/error.tsx` | Error boundary |
| Not Found | `app/not-found.tsx` | 404 page |
| Route Handler | `app/api/*/route.ts` | API endpoint |
| Server Action | `app/actions.ts` | Mutations |
| Proxy | `proxy.ts` | Request middleware |
| OG Image | `app/opengraph-image.tsx` | Social preview |

## Performance & Build

### Turbopack (Default)

Next.js 16 uses Turbopack by default for `next dev` and `next build`. No configuration needed.

### Bundle Analysis

To analyze bundle size and composition without a full build:
`npx next experimental-analyze`

### Edge Runtime

For strict performance requirements in Middleware or specific Route Handlers, opt-in to the Edge runtime:

```tsx
export const runtime = 'edge'; // 'nodejs' (default) | 'edge'
```

## Accessibility

Next.js 16 includes built-in accessibility features:

- **Route Announcements**: Screen readers automatically announce page title changes on navigation.
- **Linting**: `eslint-plugin-jsx-a11y` is included by default.

### Best Practices

- Ensure every page has a unique title.
- Use `next/link` for client-side transitions.
- Check color contrast (Vibe Engine uses accessible palettes by default).

## Development Workflow

### Fast Refresh

Enabled by default. Preserves component state during edits.

- **Reset State**: Add `// @refresh reset` to a file to force remount on edit.
- **Troubleshooting**: If state resets unexpectedly, check for anonymous arrow functions or non-component exports.

### CLI Tools

- `next dev --turbopack`: Starts dev server with Turbopack (default).
- `next typegen`: Generate TypeScript types without building.
- `next info`: Print system/environment details for debugging.

## Advanced Server Functions

### `unstable_rethrow`

If you use `try/catch` in a Server Component, you **must** rethrow internal Next.js errors (`notFound`, `redirect`).

```tsx
import { unstable_rethrow } from 'next/navigation';

try {
  // ...
} catch (err) {
  unstable_rethrow(err); // ⚠️ Critical: Let Next.js handle redirects/404s
  console.error(err);
}
```

### `after` (Experimental)

Schedule work to run *after* the response is sent (e.g., logging, analytics).

```tsx
import { after } from 'next/server';

export default function Layout({ children }) {
  after(() => {
    console.log('Response finished!');
  });
  return children;
}
```

### `cacheTag` & `updateTag`

- **`cacheTag('posts')`**: Tag a data fetch within a `use cache` scope.
- **`updateTag('posts')`**: **Immediately** purge cache in a Server Action (read-your-own-writes).

## Compiler & Support

### SWC Compiler

Next.js uses a Rust-based compiler (SWC) by default, replacing Babel/Terser.

- **Performance**: significantly faster builds and Fast Refresh.
- **Config**: Customized in `next.config.ts`.

  ```ts
  const nextConfig = {
    compiler: {
      removeConsole: { exclude: ['error'] }, // Remove console.log in prod
      reactRemoveProperties: true, // Remove properties like data-test
    }
  }
  ```

### Browser Support

Supports modern browsers (Chrome 111+, Edge 111+, Firefox 111+, Safari 16.4+) with zero config.

- **Polyfills**: Automatically injected (`fetch`, `URL`, `Object.assign`).
- **Legacy**: Use `browserslist` in `package.json` to target specific versions.
