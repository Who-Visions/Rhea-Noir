# Android Platform Views

Embedding native Android views (Google Maps, WebViews) into the Flutter widget tree.

## 1. Composition Modes

### A. Virtual Display (VD)
*   **Mechanism**: Renders native view to a virtual display, then to a GL texture.
*   **Pros**: Supported on older Android versions.
*   **Cons**: No a11y support on some versions, slower touch handling.
*   **Usage**: Default fallback for `AndroidView`.

### B. Hybrid Composition (HC)
*   **Mechanism**: Physically overlays the native Android View on top of (or interleaved with) Flutter's Surface using `platform_views` API.
*   **Pros**: Native fidelity (a11y, keyboard).
*   **Cons**: Performance impact (synchronization between threads). Low FPS for Flutter UI if heavy.
*   **Usage**: `PlatformViewsService.initExpensiveAndroidView`.

### C. Texture Layer Hybrid Composition (TLHC) - *Recommended (Android 10+)*
*   **Mechanism**: Native view renders to a Surface backed by a Texture. Flutter renders that Texture.
*   **Pros**: Best Flutter performance (no thread blocking). Good native performance.
*   **Cons**: Scrolling native lists can be janky. Magnifier issues.
*   **Usage**: `PlatformViewsService.initSurfaceAndroidView`.

## 2. Implementation Guide

### Dart Side
```dart
Widget build(BuildContext context) {
  // TLHC Implementation
  return PlatformViewLink(
    viewType: 'my_native_view',
    surfaceFactory: (context, controller) {
      return AndroidViewSurface(
        controller: controller as AndroidViewController,
        gestureRecognizers: const <Factory<OneSequenceGestureRecognizer>>{},
        hitTestBehavior: PlatformViewHitTestBehavior.opaque,
      );
    },
    onCreatePlatformView: (params) {
      return PlatformViewsService.initSurfaceAndroidView(
        id: params.id,
        viewType: 'my_native_view',
        layoutDirection: TextDirection.ltr,
        creationParams: {},
        creationParamsCodec: const StandardMessageCodec(),
        onFocus: () => params.onFocusChanged(true),
      )
      ..addOnPlatformViewCreatedListener(params.onPlatformViewCreated)
      ..create();
    },
  );
}
```

### Android Side (Kotlin)
1.  **View**: `class MyNativeView : PlatformView`
2.  **Factory**: `class MyFactory : PlatformViewFactory`
3.  **Registration**: `flutterEngine.platformViewsController.registry.registerViewFactory`

## 3. Performance Tips
*   **Avoid if possible**: Platform views are heavy. Use pure Flutter when you can.
*   **Gestures**: Platform views swallow gestures. Use `gestureRecognizers` to forward specific gestures to Flutter.
