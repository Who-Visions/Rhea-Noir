# iOS Platform Integration

Setting up and optimizing for iOS.

## 1. Setup & Requirements
*   **macOS**: Required.
*   **Xcode**: Install latest via App Store.
*   **CocoaPods**: Required for native plugins (`sudo gem install cocoapods`).

### Simulator
```bash
open -a Simulator
```

## 2. Platform Views (iOS)
Embedding `UiKitView` (MapKit, WebKit).

### Implementation
1.  **Dart**: Use `UiKitView`.
    ```dart
    UiKitView(
      viewType: 'my_ios_view',
      creationParams: {},
      creationParamsCodec: StandardMessageCodec(),
    )
    ```
2.  **iOS (Swift)**:
    *   Implement `FlutterPlatformView`.
    *   Implement `FlutterPlatformViewFactory`.
    *   Register in `AppDelegate.swift`:
        ```swift
        let registrar = registrar(forPlugin: "my_plugin")
        registrar.register(MyFactory(), withId: "my_ios_view")
        ```

## 3. Native Bindings

## 4. Launch Screen
Customize the startup experience (required for App Store).
1.  **Open Project**: `open ios/Runner.xcworkspace`.
2.  **Storyboard**: Edit `Runner/LaunchScreen.storyboard` in Xcode Interface Builder.
3.  **Assets**: Add images to `Runner/Assets.xcassets` > `LaunchImage`.

## 5. Apple Framework Mappings
Common iOS frameworks and their Flutter plugin equivalents.

| iOS Framework | Usage | Flutter Plugin |
| :--- | :--- | :--- |
| **PhotoKit** | Photo Library | `image_picker` |
| **AVFoundation** | Camera | `camera` |
| **CoreLocation** | GPS | `geolocator` |
| **CoreMotion** | Sensors | `sensors_plus` |
| **StoreKit** | IAP | `in_app_purchase` |
| **HealthKit** | Health Data | `health` |
| **CoreML** | Machine Learning | `google_ml_kit` |
| **ARKit** | AR | `ar_flutter_plugin` |
| **WidgetKit** | Home Screen Widgets | `home_widget` |

---

## 6. iOS Embedding API

Native Objective-C/Swift classes for embedding Flutter in iOS applications.

### Core Engine Classes

| Class | Description |
|-------|-------------|
| `FlutterEngine` | Single Flutter execution environment. Manages Dart VM, channels, plugins. |
| `FlutterEngineGroup` | Collection of engines sharing resources for faster creation. |
| `FlutterEngineGroupOptions` | Configuration for engine group creation. |
| `FlutterViewController` | UIViewController hosting Flutter content. |
| `FlutterView` | UIView rendering Flutter UI. |
| `FlutterOverlayView` | Overlay view for Flutter content over platform views. |
| `FlutterDartProject` | Configuration for Dart assets and entrypoint. |
| `FlutterHeadlessDartRunner` | Runs Dart code without UI (background execution). |
| `FlutterCallbackCache` | Cache for Dart callback handles. |
| `FlutterCallbackInformation` | Callback info from `PluginUtilities.getCallbackHandle`. |

### Platform Channels

| Protocol/Class | Description |
|----------------|-------------|
| `FlutterBinaryMessenger` | Protocol for binary message passing. |
| `FlutterBinaryMessengerRelay` | Message relay between messengers. |
| `FlutterBasicMessageChannel` | Named channel for typed message passing. |
| `FlutterMethodChannel` | Named channel for method calls (RPC-style). |
| `FlutterMethodCall` | Represents method invocation (name + arguments). |
| `FlutterEventChannel` | Named channel for event streams. |
| `FlutterError` | Error object for method call failures. |
| `FlutterTaskQueue` | Threading abstraction for handlers. |

### Codecs

| Class | Description |
|-------|-------------|
| `FlutterMessageCodec` | Protocol for message encoding/decoding. |
| `FlutterMethodCodec` | Protocol for method call/result encoding. |
| `FlutterStandardMessageCodec` | Flutter standard binary encoding (default). |
| `FlutterStandardMethodCodec` | Standard method codec. |
| `FlutterJSONMessageCodec` | UTF-8 JSON encoding. |
| `FlutterJSONMethodCodec` | JSON method codec. |
| `FlutterBinaryCodec` | Raw `NSData` passthrough. |
| `FlutterStringCodec` | UTF-8 string encoding. |
| `FlutterStandardTypedData` | Typed data for standard codec. |
| `FlutterStandardReader` / `FlutterStandardWriter` | Custom serialization. |

### Plugin System

| Protocol/Class | Description |
|----------------|-------------|
| `FlutterPlugin` | Main plugin protocol. Implement for plugin functionality. |
| `FlutterPluginRegistrar` | Registration interface for plugins. |
| `FlutterPluginRegistry` | Registry managing plugin instances. |
| `FlutterApplicationLifeCycleDelegate` | App lifecycle events for plugins. |
| `FlutterAppLifeCycleProvider` | Protocol for lifecycle event broadcasting. |
| `FlutterPluginAppLifeCycleDelegate` | Forwards app lifecycle to registered plugins. |
| `FlutterAppDelegate` | Base `UIApplicationDelegate` with Flutter integration. |

### Platform Views

| Protocol/Class | Description |
|----------------|-------------|
| `FlutterPlatformView` | Protocol for native views embedded in Flutter. |
| `FlutterPlatformViewFactory` | Factory for creating platform views. |
| `FlutterPlatformViewsController` | Manages platform view lifecycle. |
| `FlutterTouchInterceptingView` | Intercepts touches for platform views. |
| `FlutterClippingMaskView` | Clipping mask for platform views. |
| `FlutterClippingMaskViewPool` | Pool of reusable clipping views. |
| `ChildClippingView` | Child view with clipping support. |

### Text Input

| Class | Description |
|-------|-------------|
| `FlutterTextInputPlugin` | iOS text input implementation. |
| `FlutterTextInputView` | UIView conforming to `UITextInput`. |
| `FlutterSecureTextInputView` | Secure (password) text input. |
| `FlutterInactiveTextInput` | Inactive text input placeholder. |
| `FlutterTextPosition` | Text position in input. |
| `FlutterTextRange` | Text range selection. |
| `FlutterTextSelectionRect` | Selection rectangle. |
| `FlutterTokenizer` | Word/paragraph tokenizer. |
| `FlutterSpellCheckPlugin` | Spell check support. |
| `FlutterUndoManagerPlugin` | Undo/redo support. |

### Keyboard & Input

| Class | Description |
|-------|-------------|
| `FlutterKeyboardManager` | Manages physical keyboard events. |
| `FlutterChannelKeyResponder` | Channel-based key responder. |
| `FlutterEmbedderKeyResponder` | Embedder-level key responder. |
| `FlutterDelayingGestureRecognizer` | Delays gestures for platform views. |
| `ForwardingGestureRecognizer` | Forwards gestures to Flutter. |

### Accessibility

| Class | Description |
|-------|-------------|
| `AccessibilityBridge` (C++) | Bridge between iOS VoiceOver and Flutter semantics. |
| `SemanticsObject` | Base accessibility element. |
| `FlutterSemanticsObject` | Flutter-specific semantics element. |
| `FlutterScrollableSemanticsObject` | Scrollable accessibility element. |
| `FlutterSwitchSemanticsObject` | Switch accessibility element. |
| `FlutterPlatformViewSemanticsContainer` | Accessibility for platform views. |
| `FlutterCustomAccessibilityAction` | Custom accessibility actions. |
| `FlutterSemanticsScrollView` | Scroll view with accessibility. |

### Textures

| Protocol/Class | Description |
|----------------|-------------|
| `FlutterTexture` | Protocol for external textures. |
| `FlutterTextureRegistry` | Protocol for registering textures. |
| `FlutterTextureRegistryRelay` | Texture registry relay. |
| `IOSExternalTextureMetal` (C++) | Metal-based external texture. |

### Rendering & Graphics

| Class (C++) | Description |
|-------------|-------------|
| `IOSContext` | Manages on/off-screen rendering contexts. |
| `IOSContextMetalImpeller` | Metal + Impeller context. |
| `IOSContextNoop` | Noop context for simulators. |
| `IOSSurface` | Rendering surface. |
| `IOSSurfaceMetalImpeller` | Metal + Impeller surface. |
| `FlutterMetalLayer` | CAMetalLayer subclass for Flutter rendering. |
| `FlutterDrawable` | Metal drawable wrapper. |
| `VSyncClient` | Vsync timing client. |
| `DisplayLinkManager` | Display link management. |

### Scene Lifecycle (iOS 13+)

| Protocol/Class | Description |
|----------------|-------------|
| `FlutterSceneDelegate` | Base `UIWindowSceneDelegate` for multi-window. |
| `FlutterSceneLifeCycleDelegate` | Scene lifecycle delegate protocol. |
| `FlutterPluginSceneLifeCycleDelegate` | Forwards scene lifecycle to plugins. |
| `FlutterSwiftUIAppSceneDelegate` | SwiftUI app scene integration. |

### Internal/Utilities

| Class | Description |
|-------|-------------|
| `FlutterPlatformPlugin` | Platform behaviors (haptics, clipboard, system UI). |
| `FlutterRestorationPlugin` | State restoration support. |
| `FLTSerialTaskQueue` | Serial task queue implementation. |
| `FlutterDartVMServicePublisher` | Publishes Dart VM service for debugging. |
| `FlutterSharedApplication` | Shared UIApplication access. |
| `FlutterTimerProxy` | Timer proxy for animations. |
| `FlutterHourFormat` | 12/24-hour format detection. |

### C++ Namespaces

| Namespace | Description |
|-----------|-------------|
| `flutter::` | Core Flutter embedding classes. |
| `flutter::testing::` | Test utilities and mocks. |
| `flutter::internal::` | Internal implementation details. |
| `fml::` | Flutter foundation library utilities. |
