# Rhea Audit Report: Omniverse Nights
**Target**: `C:/Users/super/Documents/GitHub/omniverse-nights`
**Agent**: Rhea Noir (v3.1)

## 📂 Project Structure
```
- omniverse-nights/
  - .env.local
  - .gitignore
  - eslint.config.mjs
  - next-env.d.ts
  - next.config.ts
  - package.json
  - postcss.config.mjs
  - README.md
  - tailwind.config.ts
  - tsconfig.json
  - vibe-report-final.txt
  - vibe-report.txt
  - app/
    - favicon.ico
    - globals.css
    - layout.tsx
    - page.tsx
    - about/
      - page.tsx
    - dashboard/
      - page.tsx
    - events/
      - page.tsx
      - map/
        - page.tsx
    - forums/
      - page.tsx
    - gallery/
      - page.tsx
    - help/
      - page.tsx
    - legal/
      - tos/
        - page.tsx
    - resources/
      - page.tsx
    - special-events/
      - page.tsx
    - tickets/
      - page.tsx
    - worlds/
      - page.tsx
  - components/
    - canvas/
      - EnergyField.tsx
      - Scene.tsx
      - SceneWrapper.tsx
    - ui/
      - EventGrid.tsx
      - FeatureGrid.tsx
      - Footer.tsx
      - GalleryGrid.tsx
      - GlassCard.tsx
      - HeroSection.tsx
      - HeroVideo.tsx
      - Navbar.tsx
      - TicketSection.tsx
      - VibeButton.tsx
      - VibeCard.tsx
      - WorldsSection.tsx
  - lib/
    - firebase-admin.ts
    - firebase.ts
    - utils.ts
  - public/
    - file.svg
    - globe.svg
    - next.svg
    - nova-hime.jpg
    - vercel.svg
    - window.svg
    - assets/
      - void_tunnel.jpg
  - validators/
    - arch-guard.js
    - vibe-check.js
```

## ⚙️ Configuration Analysis
### next.config.ts
```json
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export default nextConfig;

```

### package.json
```json
{
  "name": "omniverse-nights",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "validate:arch": "node validators/arch-guard.js",
    "validate:vibe": "node validators/vibe-check.js",
    "validate": "npm run validate:arch && npm run validate:vibe"
  },
  "dependencies": {
    "@notionhq/client": "^5.7.0",
    "@react-three/drei": "^10.7.7",
    "@react-three/fiber": "^9.5.0",
    "@react-three/postprocessing": "^3.0.4",
    "@types/three": "^0.182.0",
    "clsx": "^2.1.1",
    "firebase": "^12.8.0",
    "firebase-admin": "^13.6.0",
    "framer-motion": "^12.27.1",
    "lucide-react": "^0.562.0",
    "next": "16.1.3",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "tailwind-merge": "^3.4.0",
    "three": "^0.182.0",
    "zod": "^4.3.5"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.1.3",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}

```

### README.md
```json
This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

```

### tailwind.config.ts
```json
import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        void: "#050505",
        "neon-cyan": "#00E5FF", 
        "neon-pink": "#FF00FF",
        "acid-green": "#00FF99",
        "highlight-gold": "#FFD700",
        "primary-violet": "#6C63FF",
      },
      fontFamily: {
        sans: ["var(--font-inter)"],
        heading: ["var(--font-outfit)"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
export default config;

```

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    ".next/dev/types/**/*.ts",
    "**/*.mts"
  ],
  "exclude": ["node_modules"]
}

```

