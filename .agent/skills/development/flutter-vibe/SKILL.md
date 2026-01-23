---
name: flutter-vibe
description: Generate premium, production-ready Flutter apps with Vibe-Coded standards (Riverpod, GoRouter, Material 3).
---

# Flutter Vibe Skill

This skill provides a "Vibe-Coded" foundation for building premium Flutter applications. It enforces modern best practices, including Riverpod for state management, GoRouter for navigation, and a deep-space aesthetic by default.

## 1. Vibe Engine (The Aesthetic)

The "Vibe Engine" isn't just a theme; it's a philosophy. It defaults to high-contrast, deep-space palettes with neon accents and fluid animations.

### Color Palette (Deep Space)

- **Primary**: `Color(0xFF6C63FF)` (Electric Violet)
- **Secondary**: `Color(0xFF00E5FF)` (Cyan Neon)
- **Surface**: `Color(0xFF121212)` (Deep Matte Black)
- **Background**: `Color(0xFF050505)` (Void Black)
- **Error**: `Color(0xFFFF5252)` (Neon Red)

### Typography

- **Headings**: `Outfit` or `Space Grotesk` (Bold, Tight Spacing)
- **Body**: `Inter` or `Roboto` (Clean, Readable)

### Animations

- **Curve**: `Curves.fastOutSlowIn` (The standard vibe curve)
- **Duration**: `300ms` (Snappy but noticeable)

---

## 2. Architecture (Feature-First)

We follow a **Feature-First** architecture to keep codebases scalable and modular.

```
lib/
├── core/
│   ├── constants/       # App-wide constants (VibeColors, VibeDimens)
│   ├── theme/           # Theme definitions (VibeTheme)
│   ├── router/          # GoRouter configuration
│   ├── utils/           # Helper functions
│   └── exceptions/      # Custom exception classes
├── features/
│   ├── auth/            # Feature: Authentication
│   │   ├── data/        # Repositories & DTOs
│   │   ├── domain/      # Entities & Failures
│   │   └── presentation/# Widgets, Providers, Screens
│   └── home/            # Feature: Home
├── shared/              # Reusable widgets (VibeButton, VibeCard)
└── main.dart            # Entry point
```

---

## 3. Core Templates

### Main Entry Point (`main.dart`)

Sets up the `ProviderScope` and runs the app.

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';

void main() {
  runApp(const ProviderScope(child: VibeApp()));
}

class VibeApp extends ConsumerWidget {
  const VibeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'Vibe App',
      theme: VibeTheme.dark(), 
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
```

### Router Setup (`core/router/app_router.dart`)

Uses `riverpod` to listen to auth state changes for redirection.

```dart
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/home/presentation/home_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) => const HomeScreen(),
      ),
    ],
  );
});
```

### Riverpod Provider (`.../presentation/providers/xyz_provider.dart`)

Standard `AutoDisposeNotifier` for state management. Avoid `stateful` widgets for logic!

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

// State Class
class MyState {
  final bool isLoading;
  final String? error;
  
  const MyState({this.isLoading = false, this.error});
}

// Provider
final myProvider = AutoDisposeNotifierProvider<MyNotifier, MyState>(MyNotifier.new);

class MyNotifier extends AutoDisposeNotifier<MyState> {
  @override
  MyState build() => const MyState();

  Future<void> doSomething() async {
    state = const MyState(isLoading: true);
    // ... logic ...
    state = const MyState(isLoading: false);
  }
}
```

---

## 4. Documentation References

> [!TIP]
> Use these links for deep dives into specific subsystems.

- **Widgets**: [Widget Catalog](https://docs.flutter.dev/ui/widgets)
- **State Management**: [Riverpod Docs](https://riverpod.dev/) (External), [Flutter General State](https://docs.flutter.dev/data-and-backend/state-mgmt)
- **Navigation**: [GoRouter](https://docs.flutter.dev/ui/navigation)
- **Embedders**:
  - [Android (Javadoc)](https://api.flutter.dev/javadoc/index.html)
  - [iOS Embedder](https://api.flutter.dev/ios-embedder/index.html)
  - [macOS Embedder](https://api.flutter.dev/macos-embedder/index.html)
  - [Windows Embedder](https://api.flutter.dev/windows-embedder/index.html)
- **Web**: [`dart:ui_web`](https://api.flutter.dev/flutter/dart-ui_web/dart-ui_web-library.html)

## 5. Rules of the Vibe

1. **Immutability First**: Use `freezed` or `extensions` for state updates.
2. **No `setStates`**: Use `ConsumerWidget` for reactive UI.
3. **Clean Layers**: Don't put API calls in Widgets. Use Repositories.
4. **Premium Feel**: Always add a `Hero` or `AnimatedSwitcher` where possible.

## 6. Advanced Platform Integrations

### Android Warm Start

Avoid cold boot delays by pre-warming the Flutter engine in your Application class.

```java
// Android Native (Application Class)
flutterEngine = new FlutterEngine(this);
flutterEngine.getDartExecutor().executeDartEntrypoint(DartEntrypoint.createDefault());
FlutterEngineCache.getInstance().put("my_engine_id", flutterEngine);

// Launching Activity
startActivity(FlutterActivity.withCachedEngine("my_engine_id").build(this));
```

### Platform Channels (MethodChannel)

Use standard channels for native communication.

```dart
// Dart Side
static const platform = MethodChannel('com.example.vibe/battery');
final int result = await platform.invokeMethod('getBatteryLevel');

// Android Side (Java/Kotlin)
new MethodChannel(flutterEngine.getDartExecutor(), "com.example.vibe/battery")
    .setMethodCallHandler((call, result) -> { ... });
```

### Windows C++ Integration

Typical `flutter_window.cpp` setup.

```cpp
#include <flutter/method_channel.h>
// ... inside OnCreate ...
flutter::MethodChannel<> channel(
    flutter_controller_->engine()->messenger(), "samples.flutter.io/battery",
    &flutter::StandardMethodCodec::GetInstance());
channel.SetMethodCallHandler(
    [](const flutter::MethodCall<>& call,
       std::unique_ptr<flutter::MethodResult<>> result) {
      if (call.method_name() == "getBatteryLevel") { ... }
    });
```

### Web Interop (`dart:js_interop`)

Modern web integration without `dart:html`.

```dart
// Pubspec.yaml
// dependencies:
//   web: ^0.5.0

import 'dart:js_interop';
import 'package:web/web.dart' as web;

void consoleLog(String msg) {
  web.window.console.log(msg.toJS);
}
```

## 7. Source-Backed Precision

> [!NOTE]
> These insights are derived from deep-scraping `flutter/flutter` framework source.

### Theming Internals (`color_scheme.dart`)

We use `ColorScheme.fromSeed` because it internally leverages `material_color_utilities` to generate harmonized tonal palettes. However, for the **Vibe Engine**, we explicitly override `surface` and `background` to `Color(0xFF050505)` because the default tonal spot generation often produces gray-washed dark modes required by standard Material 3 specs (lines 309-463 of `color_scheme.dart`).

### Element Lifecycle (`framework.dart`)

Flutter's `Widget.canUpdate` (line 382) checks `runtimeType` and `key` equality.

- **Rule**: If you change the *structure* of the tree (e.g., swapping a `Row` for a `Column`), state is lost because `runtimeType` changes.
- **Fix**: Use `GlobalKey` only when absolutely necessary to reparent state (expensive, line 128 of `framework.dart`), otherwise rely on proper nesting.
