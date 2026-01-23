# Web Platform Integration

Building high-performance web applications with Flutter (SPA & PWA).

## 1. Renderers & Architecture
Flutter Web uses a dual-rendering approach to balance performance and download size.

### A. Rendering Backends
| Renderer | Description | Best For |
| :--- | :--- | :--- |
| **HTML** | Uses HTML/CSS/Canvas/SVG. Smaller download size. | Text-heavy sites, fast load times. |
| **CanvasKit** | Uses Skia via WebAssembly. Pixel-perfect consistency. | Graphics-heavy apps, high fidelity. |
| **Skwasm** | *Experimental*. Multithreaded WebAssembly renderer. | Maximum performance (requires COOP/COEP headers). |

### B. Compilation Modes
*   **WebAssembly (Wasm)**: Compiles Dart to WasmGC. Near-native performance.
*   **JavaScript (JS)**: Transpiles Dart to JS. Wider compatibility.

## 2. Setup & Build
### Development
```bash
# Run with specific renderer
flutter run -d chrome --web-renderer canvaskit
```

### Production Build
```bash
# Build for production (minified)
flutter build web --wasm
```

## 3. Web-Specific Features
### PWA Support
Flutter Web apps are PWAs by default.
*   **Manifest**: `web/manifest.json` configures installability.
*   **Service Worker**: Handles offline caching.


### Optimization Tips
*   **Deferred Loading**: Use `deferred as` imports to split code chunks and reduce initial load time.
    ```dart
    import 'my_heavy_widget.dart' deferred as heavy;
    
    // Load when needed
    await heavy.loadLibrary();
    runApp(heavy.MyHeavyWidget());
    ```
*   **Assets**: Compress images (WebP) and fonts.

## 4. Web Dev Config (Flutter 3.38+)
Centralize dev server settings in `web_dev_config.yaml` at project root.

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  https:
    cert-path: "certs/cert.pem"
    cert-key-path: "certs/key.pem"
  headers:
    - name: "Cache-Control"
    value: "no-store"
  proxy:
    # Basic Prefix Proxy
    - target: "http://localhost:5000/"
      prefix: "/api/"
      replace: "/" 
    # Advanced Regex Proxy
    - target: "http://localhost:4000/"
```

## 5. WebAssembly (Wasm) Guide
WasmGC offers near-native performance but requires specific setup.

### Server Headers (Required)
To enable shared memory and high-performance multithreading, serve your app with:
```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: credentialless
# Or 'require-corp' if credentialless is unsupported
```

### JS Interop Migration
Legacy `dart:html` and `package:js` **do not** work with Wasm.
Use `package:web` and `dart:js_interop`:

```dart
// OLD (dart:html)
import 'dart:html';
void alert(String msg) => window.alert(msg);

// NEW (package:web)
import 'package:web/web.dart' as web;
void alert(String msg) => web.window.alert(msg);
```


### Build Command
```bash
flutter build web --wasm
```
*   **Fallback**: Generates both Wasm and JS. Browser picks automatically (JS if WasmGC unsupported).

## 6. Initialization & Bootstrapping
Customize startup via `web/flutter_bootstrap.js` or `index.html`.

### Custom Loader
```javascript
_flutter.loader.load({
  onEntrypointLoaded: async function(engineInitializer) {
    // 1. Initialize Engine (Optional: Enable Multi-View)
    const appRunner = await engineInitializer.initializeEngine({
      multiViewEnabled: true, // Required for Embedded Mode
    });
    // 2. Run App
    await appRunner.runApp();
  }
});
```

## 7. Embedding (Multi-View)
Embed Flutter into specific HTML elements (Divs) instead of taking over the full page.

### JavaScript Side
```javascript
// Add a view to a specific element
let viewId = app.addView({
  hostElement: document.querySelector('#my-flutter-div'),
  initialData: { user: 'Alice' }, // Optional data
});
```

### Dart Side
Use `runWidget` (instead of `runApp`) and handle `View` widgets.
```dart
void main() {
  runWidget(
    MultiViewApp(
      viewBuilder: (context) => const MyApp(),
    ),
  );
}


// Access View ID
final viewId = View.of(context).viewId;
```

## 8. Embedding Web Content
Display raw HTML or external web content within a Flutter widget.

### `HtmlElementView`
Render standard HTML elements (e.g., Video, Maps).
```dart
// Simple Tag-based
HtmlElementView.fromTagName(
  tagName: 'video',
  onElementCreated: (element) {
    (element as web.HTMLVideoElement)
      ..src = 'https://example.com/video.mp4'
      ..style.width = '100%';
  },
);
```

### `package:webview_flutter`
For embedding full webpages (iframe-based on web).
*   **Usage**: `WebViewWidget(controller: controller)`.
*   **Note**: On web, this renders an `iframe`.

## 9. Renderers & Build Modes
Choose between performance and download size.

### Build Modes
*   **Default**: Uses `canvaskit`. `flutter run -d chrome`.
*   **Wasm**: Uses `skwasm` (fallback to `canvaskit`). `flutter run -d chrome --wasm`.
*   **HTML**: `flutter run -d chrome --web-renderer html`.

### Runtime Selection
Override the renderer at runtime in `index.html` (before `loader.load`):
```javascript
const config = {
  renderer: useCanvasKit ? "canvaskit" : "skwasm",
};
_flutter.loader.load({ config: config });
```

## 10. Web Images & CORS
WebGL renderers (CanvasKit/Skwasm) require direct pixel access, triggering CORS.
*   **Issue**: `Image.network('https://other-domain.com/img.png')` fails if CORS headers are missing.
*   **Solutions**:
    1.  **CORS Proxy**: Route requests through a proxy adding `Access-Control-Allow-Origin: *`.
    2.  **HTML Fallback**: Use `HtmlElementView` with an `<img>` tag (doesn't require pixel access, but less flexible).
    3.  **Assets**: Bundle images with the app.

---

## 11. Plugins & URL Strategy (`flutter_web_plugins`)

### Plugin Registration
Web plugins use the `Registrar` class to bind Dart code to browser APIs.
- **Registrar**: The default plugin registrar (`webPluginRegistrar`).
- **UrlStrategy**: Abstract class for handling browser URL updates.

### URL Strategies
Control how the app's route is represented in the browser URL.

1.  **HashUrlStrategy** (Default)
    - URLs look like: `example.com/#/home`
    - No server config required.
    - Supported by `flutter_web_plugins` default.

2.  **PathUrlStrategy**
    - URLs look like: `example.com/home`
    - Requires server-side rewrite rules (SPA fallback).
    - **Usage**:
    ```dart
    import 'package:flutter_web_plugins/flutter_web_plugins.dart';

    void main() {
      usePathUrlStrategy(); // Enable path-based URLs
      runApp(MyApp());
    }
    ```
