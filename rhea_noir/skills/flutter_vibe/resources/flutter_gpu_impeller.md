# Flutter GPU & Impeller Reference

Source: Flutter Cookbook Internal Docs

## What is Flutter GPU?

A low-level graphics API for building arbitrary renderers from scratch using Dart and GLSL. No native platform code required.

> **Status:** Early preview, requires Impeller + master channel

---

## Setup

```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_gpu:
    sdk: flutter
```

Import in Dart:
```dart
import 'package:flutter_gpu/gpu.dart';
```

---

## The `gpu` Library API

The `flutter_gpu` package provides direct access to GPU resources.

### Core Classes for Rendering
- **GpuContext**: Handle to the graphics context. Main entry point (property: `gpuContext`).
- **CommandBuffer**: Records commands to be executed by the GPU.
- **RenderPass**: A pass that outputs to a `RenderTarget` (screen or texture).
- **RenderPipeline**: Defines state (shaders, blending, depth, stencil) for draw calls.

### Buffers & Memory
- **DeviceBuffer**: Memory allocated on the GPU.
- **HostBuffer**: Bump allocator for managing blocks of DeviceBuffers (efficient for uploading data).
- **BufferView**: A specific range within a buffer.

### Shaders & Textures
- **Shader**: Compiled shader program (vertex/fragment).
- **ShaderLibrary**: Collection of shaders.
- **Texture**: GPU-resident image data.
- **SamplerOptions**: How to sample textures (filtering, wrapping).

### Configuration Enums
- **BlendFactor / BlendOperation**: How pixels mix.
- **CompareFunction**: Depth/Stencil comparisons (Less, Equal, etc.).
- **CullMode**: Front/Back face culling.
- **PrimitiveType**: Triangle, Line, Point.
- **PixelFormat**: RGBA8888, etc.

---

## Requirements

1. **Impeller enabled** (required)
2. **Master channel** (recommended)
3. **Dart Native Assets** (experimental feature)

---

## How It Works

Flutter GPU communicates with Flutter Engine via Dart FFI, calling exported symbols prefixed with `InternalFlutterGpu`.

**Important:** Direct usage of exported symbols is NOT supported. Always use `package:flutter_gpu`.

---

## Use Cases

- Custom 3D renderers
- Game engines
- Specialized visualizations
- VR/AR applications

---

## Related Resources

- [Getting Started Article](https://medium.com/flutter/getting-started-with-flutter-gpu-f33d497b7c11)
- [Flutter Scene (3D Package)](https://pub.dev/packages/flutter_scene)
- [Project Dashboard](https://github.com/orgs/flutter/projects/134/views/1)
- [flutter_gpu Source](https://github.com/flutter/engine/tree/main/lib/gpu)

---

## Impeller Overview

Impeller is Flutter's next-generation rendering engine, replacing Skia for certain platforms.

### Benefits
- Predictable performance (no shader compilation jank)
- Better mobile GPU utilization
- Modern graphics API usage (Metal, Vulkan)

### Availability
- **iOS**: Default since Flutter 3.10
- **Android**: Opt-in, improving rapidly
- **Desktop**: In development

### Enable Impeller (Android)

```bash
flutter run --enable-impeller
```

Or in `AndroidManifest.xml`:
```xml
<meta-data
    android:name="io.flutter.embedding.android.EnableImpeller"
    android:value="true" />
```

---

## MoltenVK for macOS

For Vulkan-based testing on macOS:

1. Install MoltenVK via Homebrew or manual download
2. Set `VK_ICD_FILENAMES` environment variable
3. Run with Vulkan backend enabled

See: [Setting up MoltenVK on macOS](https://github.com/flutter/flutter/blob/main/engine/src/flutter/docs/impeller/Setting-up-MoltenVK-on-macOS-for-Impeller.md)
