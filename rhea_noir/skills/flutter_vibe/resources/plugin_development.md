# Plugin Development Guide

Creating modular packages and platform plugins for Flutter.

## 1. Package Types
*   **Dart Package**: Pure Dart (e.g., `utils`).
    ```bash
    flutter create --template=package my_package
    ```
*   **Plugin**: Platform-specific code (e.g., `camera`).
    ```bash
    flutter create --template=plugin --platforms=android,ios,web my_plugin
    ```
*   **FFI Plugin**: Native C/C++ binding (e.g., `sqlite`).
    ```bash
    flutter create --template=package_ffi my_ffi_plugin
    ```

## 2. Federated Plugins
Split implementation into separate packages for better scalability.
*   **App-Facing**: The package devs install (e.g., `url_launcher`).
*   **Platform Interface**: Defines the contract (e.g., `url_launcher_platform_interface`).
*   **Platform Implementation**: Actual code (e.g., `url_launcher_android`).

## 3. Platform Code
### Android (Kotlin)
Edit `android/src/main/kotlin/.../MyPlugin.kt`. Uses `MethodChannel`.

### iOS (Swift)
Edit `ios/Classes/MyPlugin.swift`. Uses `FlutterMethodChannel`.
*   **CocoaPods**: Add dependencies to `ios/my_plugin.podspec`.

### Web (Dart)
Pure Dart using `package:web`. Edit `lib/my_plugin_web.dart`.
*   **Register**: `MyPluginWeb.registerWith(registrar)`.

### Desktop (C++/Swift)
*   **Windows**: C++ in `windows/`.
*   **macOS**: Swift in `macos/`.
*   **Linux**: C++ in `linux/`.

## 4. Publishing
1.  **Dry Run**: `flutter pub publish --dry-run`.
2.  **Publish**: `flutter pub publish`.
*   **Docs**: Generated automatically on pub.dev.
