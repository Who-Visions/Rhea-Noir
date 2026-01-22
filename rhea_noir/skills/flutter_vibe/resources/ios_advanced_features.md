# iOS Advanced Features

Extend your Flutter app with App Clips and Native Extensions.

## 1. App Clips
A lightweight version of your app (under 15MB for iOS 16+) accessible via NFC, QR codes, or Maps.

### Setup
1.  **Xcode**: Add Target > **App Clip**.
2.  **Groups**: Delete default files except `Info.plist` and `.entitlements`.
3.  **Build Settings**: Ensure `iOS Deployment Target` matches the main app (min 16.0 recommended).
4.  **Embed Flutter**:
    *   Add `Run Script` phases (same as Runner) to `xcode_backend.sh build` and `embed_and_thin`.
    *   Reference `Runner-Bridging-Header.h`.

### Limitations & Tips
*   **Size**: Strict limit (15MB uncompressed payload).
*   **Debugging**: Networking restricted. Use `flutter attach --debug-uri <URI>`.
*   **Code Sharing**: Target membership for `Assets.xcassets`, `Main.storyboard`, etc.

## 2. App Extensions (Share, Widget, etc.)
Expose app functionality to system interfaces (Share Sheet, Home Screen).

### Common Setup
1.  **Xcode**: Add Target > e.g., **Share Extension**.
2.  **Frameworks**: Link `Flutter.framework`.
3.  **App Groups**: Essential for sharing data between App and Extension.
    *   Enable **App Groups** capability in both targets.
    *   Use `shared_preferences_app_group` or file paths via `path_provider`.

### Embedding Flutter UI
Render a Flutter screen inside an extension (e.g., Share Sheet).

1.  **User Script Sandboxing**: Set to `No` in Extension Build Settings.
2.  **Principal Class**: Set `NSExtensionPrincipalClass` to `ShareViewController` (or Swift equivalent).
3.  **ShareViewController.swift**:
    ```swift
    import UIKit
    import Flutter

    class ShareViewController: UIViewController {
      override func viewDidLoad() {
        super.viewDidLoad()
        showFlutter()
      }

      func showFlutter() {
        let engine = FlutterEngine(name: "extension_engine")
        engine.run()
        // Register Plugins explicitly
        GeneratedPluginRegistrant.register(with: engine)
        
        let flutterVC = FlutterViewController(engine: engine, nibName: nil, bundle: nil)
        addChild(flutterVC)
        view.addSubview(flutterVC.view)
        flutterVC.view.frame = view.bounds
      }
    }
    ```
