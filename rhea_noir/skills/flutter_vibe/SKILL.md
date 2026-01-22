---
name: flutter_vibe
description: Generate premium, production-ready Flutter apps with Vibe-Coded standards (Riverpod, GoRouter, Material 3) backed by deep Flutter internals knowledge.
---

# Flutter Vibe Skill

This skill provides a "Vibe-Coded" foundation for building premium Flutter applications. It enforces modern best practices, including Riverpod for state management, GoRouter for navigation, and a deep-space aesthetic by default.

> [!NOTE]
> This skill is backed by deep knowledge from the Flutter Engine source and official internal docs, enabling precise guidance on performance, platform integration, and rendering.

---

## 1. Vibe Engine (The Aesthetic)

The "Vibe Engine" is a philosophy: high-contrast, deep-space palettes with neon accents and fluid animations.

### Color Palette (Deep Space)

| Token | Value | Usage |
|-------|-------|-------|
| `vibePrimary` | `#6C63FF` | Electric Violet - buttons, accents |
| `vibeSecondary` | `#00E5FF` | Cyan Neon - highlights, links |
| `vibeSurface` | `#121212` | Deep Matte - cards, dialogs |
| `vibeBackground` | `#050505` | Void Black - scaffolds |
| `vibeError` | `#FF5252` | Neon Red - errors |
| `vibeSuccess` | `#00E676` | Neon Green - confirmations |

### Typography

- **Headings**: `Outfit` or `Space Grotesk` (Bold, letter-spacing: -0.5)
- **Body**: `Inter` or `Roboto` (Clean, readable)

### Animations

```dart
const vibeCurve = Curves.fastOutSlowIn;
const vibeQuickDuration = Duration(milliseconds: 200);
const vibeStandardDuration = Duration(milliseconds: 300);
```

---

## 2. Architecture (Feature-First)

```
lib/
├── core/
│   ├── constants/       # VibeColors, VibeDimens
│   ├── theme/           # VibeTheme (Material 3)
│   ├── router/          # GoRouter configuration
│   └── utils/           # Helpers
├── features/
│   └── [feature]/
│       ├── data/        # Repositories & DTOs
│       ├── domain/      # Entities (freezed)
│       └── presentation/
│           ├── providers/   # Riverpod Notifiers
│           └── screens/     # Screens & Widgets
├── shared/              # VibeButton, VibeCard, etc.
└── main.dart            # ProviderScope + VibeApp
```

---

## 3. Actions

### `scaffold_app`
Generate complete app structure with theme, router, and home screen.

### `generate_widget`
Generate premium widgets with animations and theme integration.

### `generate_feature`
Generate full feature slice: domain → data → presentation.

### `generate_screen`
Generate a screen with state management (HooksConsumerWidget).

### `explain_code`
Mentor-style analysis with Vibe standards verification.

### `review_code`
Compliance score (0-100) with specific fixes.

---

## 4. Core Templates

### Main Entry Point

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/theme/vibe_theme.dart';

void main() {
  runApp(const ProviderScope(child: VibeApp()));
}

class VibeApp extends ConsumerWidget {
  const VibeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp.router(
      title: 'Vibe App',
      theme: VibeTheme.dark(),
      routerConfig: ref.watch(routerProvider),
      debugShowCheckedModeBanner: false,
    );
  }
}
```

### Riverpod Notifier Pattern

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

@freezed
class FeatureState with _$FeatureState {
  const factory FeatureState({
    @Default(false) bool isLoading,
    String? error,
  }) = _FeatureState;
}

final featureProvider = NotifierProvider<FeatureNotifier, FeatureState>(
  FeatureNotifier.new,
);

class FeatureNotifier extends Notifier<FeatureState> {
  @override
  FeatureState build() => const FeatureState();

  Future<void> load() async {
    state = state.copyWith(isLoading: true);
    // ... fetch data ...
    state = state.copyWith(isLoading: false);
  }
}
```

---

## 5. Flutter Engine Internals

> [!TIP]
> Understanding engine internals helps write performant code.

### Life of a Frame

1. **RequestFrame** → Frame scheduled via `PlatformDispatcher.scheduleFrame`
2. **VSync** → Wait for OS vsync signal
3. **BeginFrame** → Framework builds widget tree → `Scene`
4. **Rasterization** → `LayerTree` converted to pixels on Raster thread
5. **Present** → Surface submitted to GPU via Metal/Vulkan/OpenGL

**Key Insight**: The warm-up frame (`scheduleWarmUpFrame`) pre-builds layouts before the first vsync, reducing first-frame jank.

### Compilation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Debug** | All assertions, debugger aids, script snapshot | Development |
| **Profile** | Release + tracing/overlay enabled | Performance testing |
| **Release** | Stripped, optimized AOT, no debug info | Production |

### Graphics Backends (Platform-specific)

- **iOS**: Metal (default), Impeller
- **Android**: Vulkan (default), OpenGL, Impeller
- **Desktop**: OpenGL, Software, Vulkan (via MoltenVK on macOS)

---

## 6. Platform Views (Android)

Three approaches for embedding native Android Views:

| Mode | Best For | SDK | Thread |
|------|----------|-----|--------|
| **Virtual Display (VD)** | Simple views | 20+ | Raster |
| **Hybrid Composition (HC)** | Full compatibility | 19+ | Platform |
| **Texture Layer HC (TLHC)** | Performance + compatibility | 23+ | Raster |

```dart
// Prefer TLHC (falls back to VD on older SDK)
PlatformViewsService.initAndroidView(
  id: viewId,
  viewType: 'my-view-type',
  layoutDirection: TextDirection.ltr,
);

// For SurfaceView content (maps, video), use HC
PlatformViewsService.initExpensiveAndroidView(...);
```

---

## 7. Flutter GPU (Impeller)

> [!WARNING]
> Flutter GPU is experimental and requires Impeller + master channel.

Low-level graphics API for custom renderers in pure Dart + GLSL.

```yaml
dependencies:
  flutter_gpu:
    sdk: flutter
```

**Use Cases**: Custom 3D renderers, game engines, specialized visualizations.

---

## 8. Platform Channels

### MethodChannel (Dart ↔ Native)

```dart
// Dart
const channel = MethodChannel('com.vibe/native');
final result = await channel.invokeMethod<int>('getBattery');

// Android (Kotlin)
MethodChannel(flutterEngine.dartExecutor, "com.vibe/native")
  .setMethodCallHandler { call, result ->
    when (call.method) {
      "getBattery" -> result.success(getBatteryLevel())
    }
  }
```

### Android Engine Warm Start

Pre-warm the Flutter engine to avoid cold boot delays:

```kotlin
// Application class
val engine = FlutterEngine(this).apply {
  dartExecutor.executeDartEntrypoint(DartEntrypoint.createDefault())
}
FlutterEngineCache.getInstance().put("main", engine)

// Activity launch
startActivity(FlutterActivity.withCachedEngine("main").build(this))
```

---

## 9. Rules of the Vibe

1. **No `setState`** → Use Riverpod Notifiers or hooks
2. **Const Everything** → Maximize widget reuse
3. **Animate Entrances** → FadeTransition/SlideTransition on screens
4. **Dark by Default** → Light mode is optional
5. **Blur & Glass** → `BackdropFilter` for premium surfaces
6. **Clean Layers** → No API calls in widgets; use repositories

---

## 10. Dependencies

```yaml
dependencies:
  flutter_riverpod: ^2.6.0
  hooks_riverpod: ^2.6.0
  flutter_hooks: ^0.20.0
  go_router: ^15.0.0
  google_fonts: ^6.0.0
  freezed_annotation: ^2.4.0
  flutter_animate: ^4.5.0

dev_dependencies:
  freezed: ^2.5.0
  build_runner: ^2.4.0
```

---

## 11. Resources

Deep knowledge extracted from Flutter Engine docs and community best practices:

| Resource | Description |
|----------|-------------|
| [Widget Fundamentals](./resources/widget_fundamentals.md) | Complete widget catalog: Material 3, Cupertino, layouts, animations, desktop UI |
| [Layout Tutorial](./resources/layout_tutorial.md) | Step-by-step guide to building Flutter layouts |
| [Interactivity Tutorial](./resources/interactivity_tutorial.md) | Managing state, gestures, and interactive widgets |
- [Adaptive Design](resources/adaptive_design_fundamentals.md)
- [Animations](resources/animations_motion.md)
- [Assets & Media](resources/assets_and_media.md)
- [Core Dart Libraries](resources/dart_core_libraries.md)
- [Data Persistence](resources/persistence.md)
- [Documentation](resources/building_flutter_reference_documentation.md)
- [Flutter GPU & Impeller](resources/flutter_gpu_impeller.md)
- [Forms & Inputs](resources/forms_and_validation.md)
- [Internationalization](resources/internationalization.md)
- [Integrations (Android)](resources/android_platform_integration.md)
- [Integrations (iOS)](resources/ios_integration.md)
- [Integrations (macOS)](resources/macos_platform_integration.md)
- [Integrations (Web)](resources/web_integration.md)
- [Integrations (Windows)](resources/windows_platform_integration.md)
- [Navigation](resources/navigation_routing.md)
- [Networking](resources/networking_essentials.md)
- [Package Management](resources/package_management.md)
- [State Management](resources/state_management_fundamentals.md)
- [Testing Essentials](resources/testing_essentials.md)
- [Theming](resources/themes_and_design.md)

## 12. State Management

State management is the discipline of managing the data that allows your app to function and react to user input.

### Overview
- **Ephemeral State**: Local state (e.g., `setState`, `pageController`). Use for single widgets.
- **App State**: Shared state across many parts of the app (e.g., user authentication, shopping cart).

### Built-in Approaches
- **setState**: Good for ephemeral state. Rebuilds the widget subtree.
- **InheritedWidget / InheritedModel**: Low-level method for passing data down the tree. Efficient but verbose.
- **ValueNotifier / InheritedNotifier**: Simple reactive programming using listeners.

### Vibe Standard: Riverpod
We strictly use **Riverpod** for application state in `flutter_vibe` projects.
- **Compile-safe**: Catch errors at compile time, not runtime.
- **No BuildContext dependency**: Read providers anywhere.
- **Testing**: easy to mock and override.

**Key Packages**:
- `flutter_riverpod`
- `hooks_riverpod`
- `riverpod_annotation`


---

## 13. Documentation Links

- [Widget Catalog](https://docs.flutter.dev/ui/widgets)
- [Riverpod](https://riverpod.dev/)
- [GoRouter](https://pub.dev/packages/go_router)
- [Impeller](https://docs.flutter.dev/perf/impeller)
- [Flutter GPU Article](https://medium.com/flutter/getting-started-with-flutter-gpu-f33d497b7c11)
- [Flutter Rendering Pipeline](https://www.youtube.com/watch?v=UUfXWzp0-DU)
- [Flutter API Reference](https://api.flutter.dev/)
- [Material Library](https://api.flutter.dev/flutter/material/material-library.html)
- [Foundation Library](https://api.flutter.dev/flutter/foundation/foundation-library.html)
- [Gestures Library](https://api.flutter.dev/flutter/gestures/gestures-library.html)
- [Rendering Library](https://api.flutter.dev/flutter/rendering/rendering-library.html)
- [Painting Library](https://api.flutter.dev/flutter/painting/painting-library.html)
- [Physics Library](https://api.flutter.dev/flutter/physics/physics-library.html)
- [Scheduler Library](https://api.flutter.dev/flutter/scheduler/scheduler-library.html)
- [Semantics Library](https://api.flutter.dev/flutter/semantics/semantics-library.html)
- [Services Library](https://api.flutter.dev/flutter/services/services-library.html)
- [Widget Previews Library](https://api.flutter.dev/flutter/widget_previews/widget_previews-library.html)
- [Widgets Library](https://api.flutter.dev/flutter/widgets/widgets-library.html)
- [dart:async Library](https://api.flutter.dev/flutter/dart-async/dart-async-library.html)
- [dart:ui Library](https://api.flutter.dev/flutter/dart-ui/dart-ui-library.html)
- [dart:ui_web Library](https://api.flutter.dev/flutter/dart-ui_web/dart-ui_web-library.html)
