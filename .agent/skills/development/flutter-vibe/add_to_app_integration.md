# Add-to-App Integration

Integrating Flutter into existing Android/iOS apps with high performance and debuggability.

## 1. Multiple Flutters (`FlutterEngineGroup`)
Efficiently host multiple independent Flutter views/screens.
*   **Memory Cost**: ~180kB fixed cost per additional engine (vs typically much higher).
*   **Benefits**: Shared resources (GPU context, font metrics, isolate snapshot).
*   **Isolation**: Each engine has its own Isolates, UI, and Navigation stack.

### usage
**Android**:
```kotlin
val engineGroup = FlutterEngineGroup(context)
val engine1 = engineGroup.createAndRunEngine(context, DartEntrypoint.createDefault())
val engine2 = engineGroup.createAndRunEngine(context, DartEntrypoint.createDefault())
```

**iOS**:
```swift
let engineGroup = FlutterEngineGroup(name: "my_group", project: nil)
let engine1 = engineGroup.makeEngine(withEntrypoint: nil, libraryURI: nil)
```

## 2. Load Sequence & Performance
Understanding the startup cost to optimize UX.

### Sequence
1.  **Find Resources**: Locate assets/JIT code in APK/IPA.
2.  **Load Library**: Map Shared Libraries into memory (Once per process).
3.  **Start Dart VM**: Initialize Dart Runtime (One-time cost).
4.  **Create Isolate**: Start Dart container (One per Engine).
5.  **Attach UI**: Connect to `FlutterActivity`/`FlutterViewController` (Render Surface).

### Optimization: Pre-warming
Avoid the "blank screen" delay by warming up the engine before navigating.
*   **Android**: `FlutterEngineCache`.
*   **iOS**: Keep a strong reference to `FlutterEngine`.

## 3. Debugging
### The `flutter attach` Command
Since the native host launches the app, use `attach` to connect tooling.
```bash
flutter attach -d <device-id>
```

### Wireless Debugging
*   **iOS**: Add `--vm-service-host=0.0.0.0` to Xcode Scheme Arguments.
*   **Android**: Use `adb connect <ip>`.

### IDE Config (VS Code)
`.vscode/launch.json` in the Module:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter: Attach",
      "type": "dart",
      "request": "attach"
    }
  ]
}
```
