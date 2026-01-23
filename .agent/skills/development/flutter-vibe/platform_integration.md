# Platform Integration

Flutter supports Mobile (Android/iOS), Web, and Desktop (Windows/macOS/Linux).

## 1. Supported Platforms & Requirements
### Mobile
*   **Android**: API 21+ (Android 5.0). *Target API 34+ recommended.*
    *   Archi: ARM32, ARM64, x86_64.
*   **iOS**: iOS 12+.
    *   Archi: ARM64.

### Desktop
*   **Windows**: Windows 10 (1903)+.
    *   *Visual Studio 2022 w/ C++ workload required.*
*   **macOS**: macOS 10.14 (Mojave)+.
    *   *Xcode required.*
*   **Linux**: Debian 10+, Ubuntu 20.04+, Fedora Workstation.
    *   *Headers: CMake, Ninja, GTK3, Clang.*

### Web
*   Chrome, Firefox, Safari, Edge (Modern versions).
*   Renderers: CanvasKit (Mental/Performance), HTML (Load time).

## 2. Desktop Development
### Setup
Enable platforms in config:
```bash
flutter config --enable-windows-desktop
flutter config --enable-macos-desktop
flutter config --enable-linux-desktop
```

### Create & Run
```bash
# Create with platform support
flutter create .

# Run
flutter run -d windows
flutter run -d macos
flutter run -d linux
```

### Release Builds
```bash
flutter build windows
flutter build macos
flutter build linux
```

## 3. Plugin Support (Federation)
Flutter plugins use **Federation** to support multiple platforms.
*   **App-Facing Package**: `url_launcher` (The one you depend on).
*   **Platform Packages**: `url_launcher_android`, `url_launcher_windows` (The implementations).

### Plugin FFI (Desktop)

## 4. Platform Channels (Dart <-> Native)
Bridge Flutter calls to standard Android (Kotlin/Java) or iOS (Swift/ObjC) APIs.

### MethodChannel (Raw)
*   **Simple**: Good for one-off calls (e.g., `getBatteryLevel`).
*   **Thread**: Native handler usually runs on Main Thread.
```dart
// Dart
const channel = MethodChannel('com.example/battery');
final level = await channel.invokeMethod('getLevel');
```

```kotlin
// Android (Kotlin)
MethodChannel(flutterEngine.dartExecutor, "com.example/battery").setMethodCallHandler {
  call, result -> if (call.method == "getLevel") result.success(100)
}
```

### Pigeon (Type-Safe)
**Recommended**. Generates type-safe dart/android/ios code from a schema.
```dart
// schema.dart
@HostApi()
abstract class BatteryApi {
  int getLevel();
}
```
Run `flutter pub run pigeon` to generate bindings.

## 5. FFI (Foreign Function Interface)
Call C/C++/Rust directly from Dart. **Faster** than Platform Channels (synchronous, no serialization overhead).
*   **Use Cases**: High-performance number crunching, reusing C libraries (OpenCV, TensorFlowLite).

## 6. Android Splash Screen
Native launch screen prevents white screen during Flutter Engine warmup.

### Setup (Android 12+)
1.  **Define Theme** (`android/app/src/main/res/values/styles.xml`):
    ```xml
    <style name="LaunchTheme" parent="@android:style/Theme.Black.NoTitleBar">
        <!-- Android 12+ API -->
        <item name="android:windowSplashScreenBackground">@color/launch_background</item>
        <item name="android:windowSplashScreenAnimatedIcon">@drawable/launch_icon</item>
        <!-- Legacy -->
        <item name="android:windowBackground">@drawable/launch_background</item>
    </style>
    ```

2.  **Manifest Config** (`AndroidManifest.xml`):
    ```xml
    <activity
        android:name=".MainActivity"
        android:theme="@style/LaunchTheme">
        <!-- Switch to NormalTheme after launch -->
        <meta-data
            android:name="io.flutter.embedding.android.NormalTheme"
            android:resource="@style/NormalTheme"
            />
    </activity>
    ```
