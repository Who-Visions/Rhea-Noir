# Swift Package Manager (SPM) for Flutter

Migration and usage guide for native iOS/macOS dependencies.

> **Warning**: SPM support is in development. Verify compatibility.

## 1. Setup & Migration
### Enable SPM
```bash
flutter config --enable-swift-package-manager
```
*   **Disable**: `flutter config --no-enable-swift-package-manager`
*   **Project Config**: `pubspec.yaml` > `flutter: config: enable-swift-package-manager: false`.

### App Migration
Running `flutter run` automatically attempts migration.
*   **Manual Steps**: Add `FlutterGeneratedPluginSwiftPackage` to Xcode Package Dependencies and Link Binary with Libraries.

## 2. For Plugin Authors
Support both CocoaPods and SPM.

### file Structure
```text
plugin_name/
  ios/
    plugin_name/
      Package.swift
      Sources/
        plugin_name/ (Code moved here)
```

### `Package.swift` Template
```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "plugin_name",
    platforms: [.iOS("13.0"), .macOS("10.15")],
    products: [
        .library(name: "plugin-name", targets: ["plugin_name"])
    ],
    targets: [
        .target(
            name: "plugin_name",
            resources: [
                // .process("PrivacyInfo.xcprivacy")
            ]
        )
    ]
)
```

### Resources
Use `Bundle.module` to access resources bundled with SPM.
```swift
#if SWIFT_PACKAGE
     let url = Bundle.module.url(forResource: "img", withExtension: "png")
#else
     let url = Bundle(for: Self.self).url(...)
#endif
```
