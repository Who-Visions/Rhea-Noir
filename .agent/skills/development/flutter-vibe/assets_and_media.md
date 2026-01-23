# Assets & Media

Manage static files (images, fonts, JSON) and network media.

## 1. Local Assets (`pubspec.yaml`)

### Setup
Register assets in `pubspec.yaml` to bundle them with the app.

```yaml
flutter:
  assets:
    - assets/images/my_icon.png
    - assets/data/config.json
    # Or include entire directory (doesn't include subdirs)
    - assets/backgrounds/
```

### Loading Images
Use `Image.asset` widget.

```dart
Image.asset('assets/images/my_icon.png')
```

### Loading Other Files (JSON/Text)
Use `rootBundle` from `services.dart`.

```dart
import 'package:flutter/services.dart' show rootBundle;

Future<String> loadConfig() async {
  return await rootBundle.loadString('assets/data/config.json');
}
```

## 2. Resolution-Aware Images
Flutter automatically picks the correct density (1x, 2x, 3x) if organized correctly.

**Directory Structure**:
```text
assets/
  icon.png          (1.0x - mdpi)
  2.0x/
    icon.png        (2.0x - xhdpi)
  3.0x/
    icon.png        (3.0x - xxhdpi)
```

**Usage**:
Just reference the base file. Flutter handles the rest.
```dart
Image.asset('assets/icon.png')
```

## 3. Network Images
Load images from the web.

```dart
Image.network('https://picsum.photos/200/300')
```

### Caching & Advanced Loading
For production, use `cached_network_image` package or handle loading states.

```dart
Image.network(
  'https://example.com/image.jpg',
  loadingBuilder: (context, child, loadingProgress) {
    if (loadingProgress == null) return child;
    return CircularProgressIndicator();
  },
)
```

## 4. Platform Assets (Icons/Splash)
These are configured in the native Android/iOS projects, NOT in Flutter code.

*   **App Icon**: 
    *   Android: `android/app/src/main/res/` (mipmap folders)
    *   iOS: `ios/Runner/Assets.xcassets/AppIcon.appiconset`
    *   *Tip*: Use `flutter_launcher_icons` package to generate these.

*   **Splash Screen**:
    *   Android: `android/app/src/main/res/drawable/launch_background.xml`
---

## 5. Advanced Images (Fade-In)
Avoid jarring pop-ins using `FadeInImage`.

### Memory Placeholder (Transparent)
Requires `transparent_image` package or a small byte array.

```dart
FadeInImage.memoryNetwork(
  placeholder: kTransparentImage, // from package:transparent_image
  image: 'https://picsum.photos/250?image=9',
  fadeInDuration: Duration(milliseconds: 500),
)
```

### Asset Placeholder (Loading GIF)
```dart
FadeInImage.assetNetwork(
  placeholder: 'assets/loading.gif',
  image: 'https://picsum.photos/250?image=9',
)
```

## 6. Video Player
Use `video_player` package.

### Setup
1.  **Add Dependency**: `flutter pub add video_player`
2.  **Permissions**:
    *   **Android**: Add `INTERNET` permission in `AndroidManifest.xml`.
    *   **iOS**: Add `NSAppTransportSecurity` in `Info.plist` (for HTTP).

### Implementation
Must handle `initialize()` (Future) and `dispose()`.

```dart
class VideoScreen extends StatefulWidget {
  @override
  _VideoScreenState createState() => _VideoScreenState();
}

class _VideoScreenState extends State<VideoScreen> {
  late VideoPlayerController _controller;
  late Future<void> _initializeVideoPlayerFuture;

  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.networkUrl(
      Uri.parse('https://flutter.github.io/assets-for-api-docs/assets/videos/butterfly.mp4'),
    );
    _initializeVideoPlayerFuture = _controller.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: _initializeVideoPlayerFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          return AspectRatio(
            aspectRatio: _controller.value.aspectRatio,
            child: VideoPlayer(_controller),
          );
        } else {
          return Center(child: CircularProgressIndicator());
        }
      },
    );
  }
}
```

### Play/Pause controls
```dart
FloatingActionButton(
  onPressed: () {
    setState(() {
      _controller.value.isPlaying ? _controller.pause() : _controller.play();
    });
  },
---

## 7. Asset Transformation (Build-Time)

Automate optimization (e.g., SVG compilation) in `pubspec.yaml`.

### Configuration
Link a transformer package to an asset path.

```yaml
flutter:
  assets:
    - path: assets/logo.svg
      transformers:
        - package: vector_graphics_compiler
          args: ['--tessellate']
```

### Chaining
Transformers run sequentially.

```yaml
flutter:
  assets:
    - path: assets/bird.png
      transformers:
        - package: grayscale_filter
        - package: png_optimizer
```

### Usage
Consumed as standard assets, but optimized at build time.

```dart
// Example with vector_graphics package
const Widget logo = VectorGraphic(
  loader: AssetBytesLoader('assets/logo.svg'), // Loads the precompiled binary
);
```
