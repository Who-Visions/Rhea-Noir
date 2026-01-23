# Design System: Rhea Mobile Command
**Project ID:** `rhea-mobile-command`

## 1. Visual Theme & Atmosphere
The interface embodies a **Cybernetic Void** aesthetic. It is immersive, dark, and utilitarian, evoking the feeling of a futuristic command terminal. 
The background is a deep, near-black void (`#050505`) accented by sharp, vigilant neon highlights. Surfaces are translucent and glass-like, using alpha-blended whites to create depth without opacity. The mood is "Vigilant," "High-Tech," and "Precise."

## 2. Color Palette & Roles
* **Deep Void Black (#050505)**: The infinite canvas background. Used to create a sense of depth and immersion.
* **Cybernetic Purple (#6C63FF)**: Primary system accent. Used for active states, branding elements, and primary call-to-actions.
* **Neon Cyan (#00E5FF)**: Secondary data accent. Used for "Rhea" system responses, active indicators, and high-priority data points.
* **Muted Warning Red (#CF6679)**: Error and alert state. Used for "Link Unstable" warnings and system failures.
* **Translucent Surface (White @ 5-10% Alpha)**: Used for card backgrounds, panels, and container fills to simulate glass.

## 3. Typography Rules
* **Titles (Outfit)**: A geometric, tech-forward sans-serif used for headers ("RHEA COMMAND", "SYSTEM VARIANTS"). Bold weights with generous letter-spacing (1.5 - 2.0) to enhance the terminal look.
* **Body (Inter)**: A highly legible, clean sans-serif used for chat logs and dense information. Neutral white color with varying opacity for hierarchy.
* **Code/Technical (Monospace)**: Used for system logs and specific data values (`MessageState`, error codes). 

## 4. Component Stylings
* **Command Panels (`HudPanel`)**: 
    * **Shape**: Moderately rounded corners (Radius 12-18px).
    * **Surface**: Glassmorphic (Blur Sigma 14) with a faint accent-colored border (0.9px width).
    * **Shadow**: Soft, accent-colored glow (Spread 1, Blur 22) to simulate internal illumination.
* **Variant Cards**: 
    * **Interactive**: Scale and Glow on hover (`ScaleTransition`, `BoxShadow`).
    * **Shape**: Uniform pill/rectangles with icon-centric layout.
* **Chat Bubbles**: 
    * **Rhea**: Left-aligned, Neon Cyan accents, "Cybernetic Typing" effect for text appearance.
    * **User**: Right-aligned, Cybernetic Purple accents.
    * **Decor**: Technical "Corner Brackets" frame key input areas.

## 5. Layout Principles
* **Spatial Density**: High. Designed for information density while maintaining readability through distinct grouping.
* **Grid Alignment**: strict alignment of HUD elements. A background grid (`dashes`) provides a subtle spatial reference.
* **Safe Areas**: generous padding (24px) from edges to frame the content like a monitor display.
