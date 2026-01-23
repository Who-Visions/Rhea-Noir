---
name: nextjs-google-kit
description: Optimized integration of Google services (GTM, GA4, Maps, YouTube) using @next/third-parties.
---

# Next.js Google Kit Skill

This skill leverages `@next/third-parties` to optimize the loading performance of Google's third-party libraries. It shifts the loading of heavy scripts to after hydration or when needed.

## 1. Analytics & Tagging

**Library**: `@next/third-parties/google`

### Google Tag Manager (GTM)

**Best Practice**: Load in `RootLayout`. It automatically defers the script until after hydration.

`app/layout.tsx`:

```tsx
import { GoogleTagManager } from '@next/third-parties/google'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <GoogleTagManager gtmId="GTM-XYZ" />
      <body>{children}</body>
    </html>
  )
}
```

**Sending Events**:
Use `sendGTMEvent` in Client Components.

```tsx
'use client'
import { sendGTMEvent } from '@next/third-parties/google'

export function BuyButton() {
  return (
    <button onClick={() => sendGTMEvent({ event: 'purchase', value: '100' })}>
      Buy Now
    </button>
  )
}
```

### Google Analytics (GA4)

**Note**: If you use GTM, configure GA4 inside GTM instead of using this component to avoid duplicate tags.

`app/layout.tsx`:

```tsx
import { GoogleAnalytics } from '@next/third-parties/google'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
      <GoogleAnalytics gaId="G-XYZ" />
    </html>
  )
}
```

## 2. Optimized Embeds

These components use facades (lite-embeds) to drastically improve Initial Page Load (LCP/TBT).

### YouTube Embed

Replaces the heavy iframe with a lightweight facade (`lite-youtube-embed`).

`app/page.tsx`:

```tsx
import { YouTubeEmbed } from '@next/third-parties/google'

export default function VideoSection() {
  return (
    <YouTubeEmbed 
      videoid="ogfYd705cRs" 
      height={400} 
      params="controls=0" 
    />
  )
}
```

### Google Maps Embed

Lazy-loads the map iframe below the fold by default.

`app/contact/page.tsx`:

```tsx
import { GoogleMapsEmbed } from '@next/third-parties/google'

export default function ContactPage() {
  return (
    <GoogleMapsEmbed
      apiKey="YOUR_API_KEY"
      height={200}
      width="100%"
      mode="place"
      q="Brooklyn+Bridge,New+York,NY"
    />
  )
}
```

## 3. Checklist

- [ ] **Install**: `npm install @next/third-parties@latest`
- [ ] **GTM**: Added to `RootLayout`?
- [ ] **Events**: Using `sendGTMEvent` instead of `window.dataLayer.push`?
- [ ] **Embeds**: Replaced raw `<iframe>` with `YouTubeEmbed` / `GoogleMapsEmbed`?
