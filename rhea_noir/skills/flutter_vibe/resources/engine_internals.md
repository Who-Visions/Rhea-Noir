# Flutter Engine Deep Dive

Source: Flutter Cookbook Internal Docs

## Life of a Flutter Frame

All frames begin with `RequestFrame` in the Animator. A frame may be requested for:
- Resizing the Flutter view
- Lifecycle events (backgrounding/foregrounding)
- App requests via `PlatformDispatcher.scheduleFrame`
- Embedder requests via `FlutterEngineScheduleFrame`

### Frame Pipeline

```
RequestFrame → VSync Wait → BeginFrame → Widget Build → Scene → LayerTree → Rasterize → Present
```

1. **VSync**: Flutter waits for OS vsync signal before proceeding
2. **BeginFrame**: Reserves pipeline slot, triggers `PlatformDispatcher.onBeginFrame`
3. **Scene Production**: Framework builds widget tree → `Scene` via `FlutterView.render`
4. **Rasterization**: `LayerTree` converted to pixels on Raster thread
5. **Present**: Surface submitted via Metal/Vulkan/OpenGL

### Warm-Up Frame

The framework schedules a warm-up frame using `scheduleWarmUpFrame` to pre-build layouts before the engine requests real frames. This reduces first-frame jank by completing build/layout/paint work ahead of time.

---

## Compilation Modes

### Debug Mode
- All assertions enabled
- Debugging info included
- DevTools/service extensions enabled
- Script snapshot (tokenized sources)
- Optimized for fast develop/run cycles

### Release Mode
- All assertions stripped
- Debug info removed
- Service extensions disabled
- AOT snapshot with machine code
- Tree-shaking enabled
- Optimized for startup speed, execution, and size

### Profile Mode
- Same as release except:
  - Tracing enabled
  - Performance overlay service extension enabled
- For representative performance testing

### Artifact Types
- **Debug**: Script snapshot (tokenized, no machine code)
- **Profile/Release**: AOT snapshots as dylibs (iOS) or blobs (Android)

---

## Graphics Backends

| Platform | Options |
|----------|---------|
| iOS | Metal, Software, Impeller |
| Android | Vulkan, OpenGL, Software, Impeller |
| macOS | OpenGL, Software, Vulkan (MoltenVK) |
| Linux | OpenGL, Software |
| Windows | OpenGL, Software |

---

## Rasterization Process

1. `Rasterizer.Draw` pulls `LayerTree` from pipeline
2. Check headless mode (discard if backgrounded)
3. `Surface.AcquireFrame` gets platform-specific surface
4. Recursive `Preroll` and `Paint` through layers
5. Submit to GPU
6. Embedder presents via platform view

---

## Key Engine Files

- `shell/common/animator.h` - Frame scheduling
- `shell/common/pipeline.h` - UI/Raster thread coordination
- `shell/common/rasterizer.h` - Rasterization logic
- `shell/common/vsync_waiter.h` - VSync handling
- `flow/layers/layer_tree.h` - Layer tree structure
- `flow/surface.h` - Surface abstraction
