# Themes & Design System

Learn to share colors and font styles throughout an app.

---

## 1. Creating an App Theme

Set the `theme` property in `MaterialApp`. Flutter defaults to **Material 3**.

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true, (default in 3.16+)
    
    // 1. Color Scheme (Seed-based)
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.purple,
      brightness: Brightness.dark,
    ),

    // 2. Text Theme
    textTheme: TextTheme(
      displayLarge: const TextStyle(
        fontSize: 72,
        fontWeight: FontWeight.bold,
      ),
      titleLarge: GoogleFonts.oswald(
        fontSize: 30,
        fontStyle: FontStyle.italic,
      ),
      bodyMedium: GoogleFonts.merriweather(),
    ),
  ),
)
```

## 2. Applying the Theme

Access theme data using `Theme.of(context)`.

```dart
Container(
  color: Theme.of(context).colorScheme.primary, // Background color
  child: Text(
    'Hello Theme',
    style: Theme.of(context).textTheme.bodyMedium!.copyWith(
      color: Theme.of(context).colorScheme.onPrimary, // Text color on primary
    ),
  ),
)
```

## 3. Overriding Themes

### Method A: Nested Theme Widget
Override theme for a specific subtree.

```dart
Theme(
  data: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.pink)),
  child: FloatingActionButton(...),
)
```

### Method B: Extending Parent Theme (Recommended)
Inherit properties and override only specific ones.

```dart
Theme(
  data: Theme.of(context).copyWith(
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.pink),
  ),
  child: FloatingActionButton(...),
)
```

## 4. Hierarchy of Styling

1.  **Widget Property**: Direct style (e.g., `Text(style: ...)`).
2.  **Parent Theme**: Nested `Theme` widget.
3.  **App Theme**: `MaterialApp(theme: ...)`.

---

## 5. Material 3 Migration & Details

As of Flutter 3.16, **Material 3 is the default**.

### Key Changes
1.  **Color Scheme**: Moved to generated schemes.
    *   **Old**: `ColorScheme.light(primary: Colors.blue)`
    *   **New**: `ColorScheme.fromSeed(seedColor: Colors.blue)`
2.  **Typography**: Updated scale (Display/Headline/Title/Body/Label).
3.  **Components**:
    *   `BottomNavigationBar` -> `NavigationBar` (taller, pill indicators).
    *   `Drawer` -> `NavigationDrawer`.
    *   `AppBar`: No shadow by default, uses `surfaceTint` for elevation color.
    *   `ElevatedButton`: No default drop shadow; primarily uses filled colors.

### Migration Example (NavigationBar)

**Old (Material 2)**:
```dart
BottomNavigationBar(
  items: [
    BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
    BottomNavigationBarItem(icon: Icon(Icons.work), label: 'Work'),
  ],
)
```

**New (Material 3)**:
```dart
NavigationBar(
  destinations: [
    NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
    NavigationDestination(icon: Icon(Icons.work), label: 'Work'),
  ],
)
```

---

## 6. Typography & Fonts

### Semantic Type Scale
Material 3 uses a 15-point scale (5 categories x 3 sizes).

| Category | Usage |
|----------|-------|
| **Display** | Large, short text (e.g., hero numbers) |
| **Headline**| Primary screen titles |
| **Title** | Medium emphasis (e.g., app bar title) |
| **Body** | Long-form content |
| **Label** | Buttons, captions, small text |

### Using Google Fonts
Use the `google_fonts` package for dynamic loading or bundling.

```dart
Text(
  'Styled Text',
  style: GoogleFonts.lato(
    textStyle: Theme.of(context).textTheme.displayLarge,
    fontWeight: FontWeight.w700,
  ),
)
```

### Variable Fonts & Features
Modify font axes (weight, slant, width) at runtime.

```dart
Text(
  'Variable Font',
  style: TextStyle(
    fontVariations: [
      FontVariation('wght', 700), // Weight
      FontVariation('slnt', -10), // Slant
    ],
    fontFeatures: [
      FontFeature.tabularFigures(), // Monospaced numbers
    ],
  ),
)
```

---

## 7. Custom Fonts (Local Assets)

### 1. Import Font Files
Supported: `.ttf`, `.otf`, `.ttc`. (WOFF not supported on desktop).
Place files in: `fonts/` (root) or `assets/fonts/`.

### 2. Declare in `pubspec.yaml`
```yaml
flutter:
  fonts:
    - family: Raleway
      fonts:
        - asset: fonts/Raleway-Regular.ttf
        - asset: fonts/Raleway-Italic.ttf
          style: italic
    - family: RobotoMono
      fonts:
        - asset: fonts/RobotoMono-Bold.ttf
          weight: 700
```

### 3. Usage
```dart
Text(
  'Custom Font',
  style: TextStyle(fontFamily: 'Raleway'),
)
```

---

## 8. Exporting Fonts from Packages

Share fonts across projects or libraries.

### 1. Package Structure
Place fonts in the package's `lib/fonts/` directory.
`awesome_package/lib/fonts/Raleway-Regular.ttf`

### 2. App Declaration
In the **consuming app's** `pubspec.yaml`, prefix with `packages/<package_name>/`.

```yaml
flutter:
  fonts:
    - family: Raleway
      fonts:
        - asset: packages/awesome_package/fonts/Raleway-Regular.ttf
```

### 3. Usage
No separate package argument needed in `TextStyle` if declared this way.

```dart
Text('Package Font', style: TextStyle(fontFamily: 'Raleway'))
```

---

## 9. Google Fonts Package Deep Dive

The `google_fonts` package (v7.1.0+) supports HTTP fetching and asset bundling.

### A. Dynamic Loading (HTTP)
Default behavior. useful for development.

```dart
Text('Dynamically Loaded', style: GoogleFonts.lato())
```

### B. Bundling (Production)
For offline support and faster load times:

1.  **Download** fonts from fonts.google.com.
2.  **Move** to asset folder (e.g., `assets/google_fonts/`).
3.  **Declare** asset folder in `pubspec.yaml` (under `assets`, NOT `fonts`).

```yaml
flutter:
  assets:
    - assets/google_fonts/
```

The package automatically prioritizes bundled files matching the Google Fonts naming convention.

### C. Text Themes
Apply a font family globally.

```dart
MaterialApp(
  theme: ThemeData(
    textTheme: GoogleFonts.latoTextTheme(),
  ),
)
```

### D. Licensing
Add licenses to registry for legal compliance.

```dart
void main() {
  LicenseRegistry.addLicense(() async* {
    final license = await rootBundle.loadString('assets/google_fonts/OFL.txt');
    yield LicenseEntryWithLineBreaks(['google_fonts'], license);
  });
  runApp(MyApp());
}
```

---

## Resources
*   [Material 3 Theme Builder](https://m3.material.io/theme-builder)
*   [Google Fonts Package](https://pub.dev/packages/google_fonts)

---

## 10. Material Color Utilities (`package:material_color_utilities`)
Low-level color science library powering Material 3 dynamic color.

### Blend (`blend`)
Functions for blending colors in HCT and CAM16 color spaces.
- **`Blend.harmonize(designColor, sourceColor)`**: Shifts a design color toward the source color for visual harmony.
- **`Blend.hctHue(from, to, amount)`**: Blend hue in HCT space.

### Contrast (`contrast`)
Utility methods for calculating and achieving contrast ratios.
- **`Contrast.ratioOfTones(toneA, toneB)`**: Calculate contrast ratio between two tones.
- **`Contrast.lighter(tone, ratio)`**: Find a lighter tone that meets the contrast ratio.
- **`Contrast.darker(tone, ratio)`**: Find a darker tone that meets the contrast ratio.

### Dislike Analyzer (`dislike`)
Checks and fixes universally disliked colors (e.g., muddy yellows).
- **`DislikeAnalyzer.isDisliked(hct)`**: Returns true if the color is universally disliked.
- **`DislikeAnalyzer.fixIfDisliked(hct)`**: Returns a corrected HCT if disliked.

### Dynamic Color (`dynamiccolor`)
Colors that adjust based on UI state and scheme.
- **`DynamicColor`**: A color that resolves itself based on `DynamicScheme`.
- **`DynamicScheme`**: Represents current UI state (dark/light, contrast level) and provides `TonalPalette`s.
- **`MaterialDynamicColors`**: Named color tokens in the Material Design system (primary, secondary, surface, etc.).
- **`ContrastCurve`**: A value that changes with the contrast level.
- **`ToneDeltaPair`**: Constraint between two colors ensuring their tones maintain a certain distance.
- **`TonePolarity`**: Enum describing tone difference direction (lighter/darker/nearer/farther).

### Scheme Variants (`variant`)
Theme styles supported by Dynamic Color.
- **`Variant`**: Enum of scheme types (TonalSpot, Vibrant, Expressive, Fidelity, Monochrome, etc.).
- Instantiate `SchemeTonalSpot`, `SchemeVibrant`, etc. to create colors for that theme.

### Color Appearance Models (`hct`)
Perceptually accurate color representations.
- **`Cam16`**: CAM16 color appearance model. Accounts for viewing conditions (ambient light, background).
- **`Hct`**: Hue-Chroma-Tone color space. Core of Material 3 color system.
  - **Hue**: 0-360 degrees (red=0, green=120, blue=240).
  - **Chroma**: Colorfulness (0 = gray, higher = more vivid).
  - **Tone**: Lightness (0 = black, 100 = white).
- **`HctSolver`**: Internal class that solves the HCT equation for color conversion.
- **`ViewingConditions`**: Environment parameters (ambient light, background) that affect how colors appear. Used by CAM16.

### Palettes (`palettes`)
Color palette structures for theme generation.
- **`CorePalette`**: Intermediate between key color and full scheme. Generates 5 tonal palettes (primary, secondary, tertiary, neutral, neutral-variant).
- **`TonalPalette`**: Colors constant in hue/chroma but varying in tone. Access via `palette.get(tone)`.

### Quantizers (`quantize`)
Extract dominant colors from images.
- **`QuantizerCelebi`**: High-quality quantizer combining Wu and WSMeans.
- **`QuantizerWu`**: Fast quantizer using Wu's algorithm.
- **`QuantizerWsmeans`**: Refines colors using weighted k-means.
- **`QuantizerMap`**: Simple map-based quantizer.
- **`QuantizerResult`**: Contains color-to-count mapping.

### Scheme Classes (`scheme`)
Pre-built dynamic color schemes. Use Flutter's `ColorScheme` directly when possible.
- **`Scheme`**: Base class (prefer Flutter's `ColorScheme` for direct use).
| Scheme | Description |
|--------|-------------|
| `SchemeTonalSpot` | Default Material You (Android 12+) |
| `SchemeVibrant` | Maximum colorfulness |
| `SchemeExpressive` | Detached from source color |
| `SchemeFidelity` | Source color in primary container |
| `SchemeContent` | Source color in primary container (similar to Fidelity) |
| `SchemeMonochrome` | Grayscale theme |
| `SchemeNeutral` | Near-grayscale |
| `SchemeRainbow` | Playful, varied hues |
| `SchemeFruitSalad` | Playful, source hue absent |

### Scoring & Temperature (`score`, `temperature`)
- **`Score`**: Ranks colors by suitability for UI themes.
- **`TemperatureCache`**: Color temperature utilities (warm/cool analogues, complements).

### Utilities
- **`ColorUtils`**: RGB/ARGB conversions, luminance calculations.
- **`MathUtils`**: Clamping, linear interpolation, angle operations.
- **`StringUtils`**: String manipulation utilities.
