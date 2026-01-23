# Android Native Features

Advanced integration with the Android platform.

## 1. Predictive Back Gesture (Android 13+)
Allows users to peek at the destination before completing the back gesture.

### Setup
1.  **Manifest**: Enable in `android/app/src/main/AndroidManifest.xml`
    ```xml
    <application android:enableOnBackInvokedCallback="true" ...>
    ```
2.  **Theme**: Enable in `MaterialApp`
    ```dart
    MaterialApp(
      theme: ThemeData(
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: <TargetPlatform, PageTransitionsBuilder>{
            TargetPlatform.android: PredictiveBackPageTransitionsBuilder(),
          },
        ),
      ),
    );
    ```

## 2. Launching Native Activites (Jetpack Compose)
Mix Flutter with full-screen native Android screens.

### Dart Side
Invoke a method channel to request the activity launch.
```dart
const platform = MethodChannel('com.example/activity');
await platform.invokeMethod('launchActivity', {'msg': 'Hello from Flutter'});
```

### Android Side (Kotlin)
1.  **Dependencies** (`android/app/build.gradle`):
    ```gradle
    buildFeatures { compose true }
    dependencies {
        implementation(platform("androidx.compose:compose-bom:2024.06.00"))
        implementation("androidx.compose.material3:material3")
        implementation("androidx.activity:activity-compose")
    }
    ```

2.  **MainActivity** (`MainActivity.kt`):
    ```kotlin
    class MainActivity: FlutterActivity() {
      private val CHANNEL = "com.example/activity"

      override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler {
          call, result ->
          if (call.method == "launchActivity") {
             val intent = Intent(this, SecondActivity::class.java)
             intent.putExtra("msg", call.argument<String>("msg"))
             startActivity(intent)
             result.success(true)
          } else {
             result.notImplemented()
          }
        }
      }
    }
    ```

3.  **SecondActivity** (Jetpack Compose):
    ```kotlin
    class SecondActivity : ComponentActivity() {
      override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
          MaterialTheme {
             Text("Hello from Jetpack Compose!")
          }
        }
      }
    }
    ```

4.  **Manifest**: Register the new activity.
    ```xml

## 3. State Restoration
Restore app state after OS kills background process.
1.  **Wrap App**: `RootRestorationScope` in `MaterialApp(restorationScopeId: 'root')`.
2.  **Mixins**: Use `RestorationMixin` in State classes.
3.  **Properties**: Use `RestorableInt`, `RestorableTextEditingController`.

```dart
class _MyState extends State<MyWidget> with RestorationMixin {
  final RestorableInt _counter = RestorableInt(0);

  @override
  String? get restorationId => 'counter_widget';

  @override
  void restoreState(RestorationBucket? oldBucket, bool initialRestore) {
    registerForRestoration(_counter, 'count');
  }
}
```

## 4. Sensitive Content (Android 35+)
Obscure content during screen sharing/recording.
```dart
SensitiveContent(
  sensitivity: ContentSensitivity.sensitive, // Obscures screen on projection
  child: MySecureWidget(),
);
```

## 5. ChromeOS Targets
Run Android apps on ChromeOS.
*   **Linting**: Use `flutter analyze` with `chrome-os-manifest-checks` in `analysis_options.yaml`.
*   **Network**: Enable networking for DevTools if blocked.

---

## 6. Android Embedding Engine API

Core Java/Kotlin classes for embedding Flutter in Android applications.

### `io.flutter.embedding.engine`

| Class | Description |
|-------|-------------|
| `FlutterEngine` | A single Flutter execution environment. Manages Dart VM, platform channels, and plugins. |
| `FlutterEngine.EngineLifecycleListener` | Callbacks for engine lifecycle events (created, destroyed). |
| `FlutterEngineCache` | Static singleton cache holding `FlutterEngine` instances by String keys. Pre-warm engines for faster startup. |
| `FlutterEngineGroup` | Collection of `FlutterEngine`s that share resources for faster creation and lower memory. |
| `FlutterEngineGroup.Options` | Configuration for `FlutterEngineGroup.createAndRunEngine()`. |
| `FlutterEngineGroupCache` | Static singleton cache for `FlutterEngineGroup` instances. |
| `FlutterJNI` | Interface between Java embedding code and Flutter's C/C++ engine via JNI. |
| `FlutterJNI.AccessibilityDelegate` | Creates/updates Android accessibility caches from Flutter's semantics tree. |
| `FlutterJNI.AsyncWaitForVsyncDelegate` | Callback for vsync timing. |
| `FlutterOverlaySurface` | Overlay surface for platform views. |
| `FlutterShellArgs` | Arguments passed to the Flutter shell at creation (e.g., `--trace-startup`). |

#### FlutterEngine Usage
```kotlin
// Create and cache an engine for pre-warming
val engine = FlutterEngine(context)
engine.dartExecutor.executeDartEntrypoint(DartExecutor.DartEntrypoint.createDefault())
FlutterEngineCache.getInstance().put("my_engine", engine)

// Retrieve cached engine
val cachedEngine = FlutterEngineCache.getInstance().get("my_engine")
```

#### FlutterEngineGroup (Multi-Engine)
```kotlin
// Share resources across multiple engines
val group = FlutterEngineGroup(context)
val engine1 = group.createAndRunDefaultEngine(context)
val engine2 = group.createAndRunDefaultEngine(context) // Shares GPU context with engine1
```

---

### `io.flutter.embedding.engine.dart`

| Class | Description |
|-------|-------------|
| `DartExecutor` | Configures, bootstraps, and executes Dart code. Access via `FlutterEngine.dartExecutor`. |
| `DartExecutor.DartEntrypoint` | Specifies the Dart entrypoint (`main()` by default) and asset path. |
| `DartExecutor.DartCallback` | Specifies a Dart callback function for background execution (e.g., background isolates). |
| `DartExecutor.IsolateServiceIdListener` | Callback when the isolate service ID becomes available. |
| `PlatformMessageHandler` | Receives messages from Dart code (internal). |
| `PlatformTaskQueue` | `BinaryMessenger.TaskQueue` that posts to the platform/main thread. |

#### DartEntrypoint Examples
```kotlin
// Default entrypoint (lib/main.dart -> main())
val defaultEntry = DartExecutor.DartEntrypoint.createDefault()

// Custom entrypoint
val customEntry = DartExecutor.DartEntrypoint(
    FlutterInjector.instance().flutterLoader().findAppBundlePath(),
    "package:myapp/background.dart",
    "backgroundMain"  // Function name
)

engine.dartExecutor.executeDartEntrypoint(customEntry)
```

---

### `io.flutter.embedding.engine.loader`

| Class | Description |
|-------|-------------|
| `FlutterLoader` | Finds Flutter resources in the APK and loads Flutter's native library (`libflutter.so`). |
| `FlutterLoader.Settings` | Configuration for `FlutterLoader` initialization. |
| `ApplicationInfoLoader` | Loads application metadata from `AndroidManifest.xml`. |
| `FlutterApplicationInfo` | Encapsulates Flutter-specific manifest metadata (AOT shared lib, VM snapshot, etc.). |

#### FlutterLoader Initialization
```kotlin
// Async initialization (recommended)
val loader = FlutterInjector.instance().flutterLoader()
loader.startInitialization(context)
loader.ensureInitializationComplete(context, null)

// Get paths
val appBundlePath = loader.findAppBundlePath()
val libPath = loader.getLookupKeyForAsset("assets/data.json")
```

---

### `io.flutter.embedding.engine.mutatorsstack`

Used for applying visual transformations (clips, transforms) to platform views.

| Class/Enum | Description |
|------------|-------------|
| `FlutterMutatorsStack` | Stack of mutators (transforms, clips) applied to platform views. |
| `FlutterMutatorsStack.FlutterMutatorType` | Enum: `CLIP_RECT`, `CLIP_RRECT`, `CLIP_PATH`, `TRANSFORM`, `OPACITY`. |
| `FlutterMutatorView` | Android `View` that applies `FlutterMutatorsStack` transforms to its children. |

> [!NOTE]
> Mutators are used internally by the platform views system to ensure native Android views are clipped and transformed correctly to match their Flutter-side positioning.

---

### `io.flutter.embedding.engine.plugins`

Core plugin interface and binding:

| Interface/Class | Description |
|-----------------|-------------|
| `FlutterPlugin` | Interface for plugins to register with a `FlutterEngine`. |
| `FlutterPlugin.FlutterAssets` | Access to Flutter asset lookup (asset path resolution). |
| `FlutterPlugin.FlutterPluginBinding` | Resources for plugins: `BinaryMessenger`, `AssetManager`, `FlutterEngine`. |
| `PluginRegistry` | Legacy registry for plugin instances (prefer `FlutterPlugin`). |

#### Plugin Sub-packages

**`io.flutter.embedding.engine.plugins.activity`**

| Interface | Description |
|-----------|-------------|
| `ActivityAware` | Plugin interested in Activity lifecycle events. Implement for Activity access. |
| `ActivityControlSurface` | Control surface for Activity attachment to `FlutterEngine`. |
| `ActivityPluginBinding` | Provides `Activity`, `Lifecycle`, and result callbacks to plugins. |
| `ActivityPluginBinding.OnSaveInstanceStateListener` | Callback for `onSaveInstanceState`. |

**`io.flutter.embedding.engine.plugins.broadcastreceiver`**

| Interface | Description |
|-----------|-------------|
| `BroadcastReceiverAware` | Plugin that runs within a `BroadcastReceiver`. |
| `BroadcastReceiverControlSurface` | Control surface for BroadcastReceiver attachment. |
| `BroadcastReceiverPluginBinding` | Provides access to the associated `BroadcastReceiver`. |

**`io.flutter.embedding.engine.plugins.contentprovider`**

| Interface | Description |
|-----------|-------------|
| `ContentProviderAware` | Plugin that runs within a `ContentProvider`. |
| `ContentProviderControlSurface` | Control surface for ContentProvider attachment. |
| `ContentProviderPluginBinding` | Provides access to the associated `ContentProvider`. |

**`io.flutter.embedding.engine.plugins.lifecycle`**

| Interface | Description |
|-----------|-------------|
| `FlutterLifecycleAdapter` | Converts `Lifecycle` to Flutter-specific lifecycle events. |
| `HiddenLifecycleReference` | Internal lifecycle reference holder. |

**`io.flutter.embedding.engine.plugins.service`**

| Interface | Description |
|-----------|-------------|
| `ServiceAware` | Plugin that runs within an Android `Service`. |
| `ServiceControlSurface` | Control surface for Service attachment. |
| `ServicePluginBinding` | Provides access to the associated `Service`. |

#### Complete Plugin Implementation
```kotlin
class MyPlugin : FlutterPlugin, ActivityAware, MethodChannel.MethodCallHandler {
    private lateinit var channel: MethodChannel
    private var activity: Activity? = null

    // FlutterPlugin
    override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel = MethodChannel(binding.binaryMessenger, "my_channel")
        channel.setMethodCallHandler(this)
    }

    override fun onDetachedFromEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel.setMethodCallHandler(null)
    }

    // ActivityAware
    override fun onAttachedToActivity(binding: ActivityPluginBinding) {
        activity = binding.activity
        binding.addActivityResultListener { requestCode, resultCode, data -> true }
    }

    override fun onDetachedFromActivity() { activity = null }
    override fun onDetachedFromActivityForConfigChanges() { activity = null }
    override fun onReattachedToActivityForConfigChanges(binding: ActivityPluginBinding) {
        activity = binding.activity
    }

    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        // Handle method calls, activity is available here
    }
}

---

### `io.flutter.embedding.engine.renderer`

| Class/Interface/Enum | Description |
|----------------------|-------------|
| `FlutterRenderer` | Renders Flutter UI to an Android `Surface`. |
| `FlutterRenderer.ViewportMetrics` | Mutable viewport metrics: dimensions, padding, insets. |
| `FlutterRenderer.DisplayFeature` | Physical display features (folds, hinges, cutouts). |
| `FlutterRenderer.DisplayFeatureType` | Enum: `FOLD`, `HINGE`, `CUTOUT`. |
| `FlutterRenderer.DisplayFeatureState` | Enum: `UNKNOWN`, `POSTURE_FLAT`, `POSTURE_HALF_OPENED`. |
| `FlutterUiDisplayListener` | Callback when Flutter starts/stops rendering. |
| `RenderSurface` | Interface for surfaces that display Flutter output. |
| `SurfaceTextureWrapper` | Tracks `SurfaceTexture` release state. |

---

### `io.flutter.embedding.engine.systemchannels`

System channels for Flutter-Android platform communication:

#### Core Channels

| Channel | Description |
|---------|-------------|
| `AccessibilityChannel` | Accessibility/semantics data and requests. |
| `BackGestureChannel` | Predictive back gesture events (Android 13+). |
| `KeyboardChannel` | Keyboard show/hide and method handler. |
| `KeyEventChannel` | Physical key events (`FlutterKeyEvent`). |
| `LifecycleChannel` | App lifecycle states (resumed, paused, inactive, detached). |
| `LocalizationChannel` | Locale data from system. |
| `MouseCursorChannel` | Mouse cursor shape changes. |
| `NavigationChannel` | System navigation (back button, deep links). |

#### Platform & UI Channels

| Channel | Description |
|---------|-------------|
| `PlatformChannel` | Clipboard, haptics, sounds, system chrome. |
| `PlatformChannel.Brightness` | Enum: `LIGHT`, `DARK`. |
| `PlatformChannel.HapticFeedbackType` | `STANDARD`, `LIGHT_IMPACT`, `MEDIUM_IMPACT`, `HEAVY_IMPACT`, `SELECTION_CLICK`. |
| `PlatformChannel.SoundType` | `CLICK`, `ALERT`. |
| `PlatformChannel.SystemUiMode` | `LEAN_BACK`, `IMMERSIVE`, `IMMERSIVE_STICKY`, `EDGE_TO_EDGE`. |
| `PlatformChannel.SystemChromeStyle` | Status/nav bar colors and brightness. |
| `PlatformChannel.DeviceOrientation` | `PORTRAIT_UP`, `PORTRAIT_DOWN`, `LANDSCAPE_LEFT`, `LANDSCAPE_RIGHT`. |

#### Platform Views

| Channel | Description |
|---------|-------------|
| `PlatformViewsChannel` | Platform view create/resize/dispose. |
| `PlatformViewsChannel2` | Updated platform views protocol. |
| `PlatformViewCreationRequest` | Request payload for view creation. |
| `PlatformViewCreationRequest.RequestedDisplayMode` | `TEXTURE_WITH_HYBRID_FALLBACK`, `TEXTURE_WITH_VIRTUAL_FALLBACK`, `HYBRID_ONLY`. |
| `PlatformViewTouch` | Touch event data for platform views. |

#### Input & Text

| Channel | Description |
|---------|-------------|
| `TextInputChannel` | IME/soft keyboard text input. |
| `TextInputChannel.Configuration` | Input type, actions, autofill config. |
| `TextInputChannel.TextEditState` | Current text, selection, composing region. |
| `TextInputChannel.TextCapitalization` | `NONE`, `CHARACTERS`, `WORDS`, `SENTENCES`. |
| `TextInputChannel.InputType` | `TEXT`, `NUMBER`, `PHONE`, `DATETIME`, `EMAIL`, `URL`, `MULTILINE`. |
| `SpellCheckChannel` | Spell check requests/results. |
| `ScribeChannel` | Handwriting/stylus input (Scribe). |

#### Other Channels

| Channel | Description |
|---------|-------------|
| `DeferredComponentChannel` | Deferred component installation requests. |
| `ProcessTextChannel` | Text processing (translate, share, etc.). |
| `RestorationChannel` | State restoration data exchange. |
| `SensitiveContentChannel` | Content sensitivity for screen sharing. |
| `SettingsChannel` | Text scale, 24-hour time, accessibility settings. |
| `SystemChannel` | General system messages. |

---

## 7. Platform Channels & Messaging

### `io.flutter.plugin.common`

Core platform channel infrastructure for Flutter-Android communication.

#### Message Channels

| Class | Description |
|-------|-------------|
| `BasicMessageChannel<T>` | Named channel for async message passing with typed messages. |
| `BasicMessageChannel.MessageHandler<T>` | Handler for incoming messages. |
| `BasicMessageChannel.Reply<T>` | Reply callback for messages. |
| `MethodChannel` | Named channel for async method calls (RPC-style). |
| `MethodChannel.MethodCallHandler` | Handler for incoming method calls. |
| `MethodChannel.Result` | Callback for method call results (success/error/notImplemented). |
| `MethodCall` | Represents a method invocation (method name + arguments). |
| `EventChannel` | Named channel for async event streams (Dart → Android). |
| `EventChannel.StreamHandler` | Handler for stream setup/teardown. |
| `EventChannel.EventSink` | Sink for sending events back to Flutter. |

#### Codecs

| Codec | Description |
|-------|-------------|
| `MessageCodec<T>` | Interface for message encoding/decoding. |
| `MethodCodec` | Interface for method call/result encoding. |
| `StandardMessageCodec` | Flutter standard binary encoding (default). |
| `StandardMethodCodec` | Method codec using standard binary encoding. |
| `JSONMessageCodec` | UTF-8 JSON message encoding. |
| `JSONMethodCodec` | UTF-8 JSON method call encoding. |
| `BinaryCodec` | Raw `ByteBuffer` passthrough (no encoding). |
| `StringCodec` | UTF-8 string encoding. |

#### Binary Messenger

| Interface/Class | Description |
|-----------------|-------------|
| `BinaryMessenger` | Low-level binary message passing facility. |
| `BinaryMessenger.BinaryMessageHandler` | Handler for raw binary messages. |
| `BinaryMessenger.BinaryReply` | Binary reply callback. |
| `BinaryMessenger.TaskQueue` | Threading policy abstraction for handlers. |
| `BinaryMessenger.TaskQueueOptions` | Task queue configuration. |

#### Plugin Registry Listeners

| Interface | Description |
|-----------|-------------|
| `PluginRegistry.ActivityResultListener` | Handles `onActivityResult`. |
| `PluginRegistry.NewIntentListener` | Handles `onNewIntent`. |
| `PluginRegistry.RequestPermissionsResultListener` | Handles permission results. |
| `PluginRegistry.UserLeaveHintListener` | Handles `onUserLeaveHint`. |
| `PluginRegistry.WindowFocusChangedListener` | Handles window focus changes. |

#### Utilities

| Class | Description |
|-------|-------------|
| `ErrorLogResult` | `MethodChannel.Result` that logs errors to Android log. |
| `FlutterException` | Exception thrown when Flutter method call fails. |
| `JSONUtil` | JSON utilities. |

#### Platform Channel Examples
```kotlin
// MethodChannel
val methodChannel = MethodChannel(binaryMessenger, "com.example/method")
methodChannel.setMethodCallHandler { call, result ->
    when (call.method) {
        "getBatteryLevel" -> result.success(getBatteryLevel())
        else -> result.notImplemented()
    }
}

// EventChannel (for streams)
val eventChannel = EventChannel(binaryMessenger, "com.example/events")
eventChannel.setStreamHandler(object : EventChannel.StreamHandler {
    override fun onListen(arguments: Any?, events: EventChannel.EventSink) {
        events.success("event data")  // Send event to Flutter
    }
    override fun onCancel(arguments: Any?) { /* cleanup */ }
})

// BasicMessageChannel
val msgChannel = BasicMessageChannel(binaryMessenger, "com.example/msg", StringCodec.INSTANCE)
msgChannel.setMessageHandler { message, reply ->
    reply.reply("Response to: $message")
}
```

---

### `io.flutter.plugin.editing`

Text input and editing implementation.

| Class | Description |
|-------|-------------|
| `TextInputPlugin` | Android implementation of Flutter's text input. |
| `InputConnectionAdaptor` | Adapts Android `InputConnection` to Flutter. |
| `InputConnectionAdaptor.KeyboardDelegate` | Keyboard event delegation. |
| `SpellCheckPlugin` | Spell check implementation for text input. |
| `ScribePlugin` | Handwriting/stylus text input (Scribe). |
| `TextEditingDelta` | Represents text editing changes. |

---

### `io.flutter.plugin.platform`

Platform views: embedding native Android views in Flutter.

| Class/Interface | Description |
|-----------------|-------------|
| `PlatformView` | Handle to an Android view embedded in Flutter hierarchy. |
| `PlatformViewFactory` | Factory for creating platform views. |
| `PlatformViewRegistry` | Registry for platform view factories. |
| `PlatformViewRegistryImpl` | Default registry implementation. |
| `PlatformViewsController` | Manages platform view lifecycle. |
| `PlatformViewsController2` | Updated platform views manager. |
| `PlatformViewWrapper` | Wraps views for gesture interception. |
| `PlatformOverlayView` | Host for Flutter content over platform views. |
| `PlatformPlugin` | Platform behavior (haptics, clipboard, system chrome). |
| `PlatformPlugin.PlatformPluginDelegate` | Customization delegate. |
| `PlatformViewsAccessibilityDelegate` | Accessibility bridge for embedded views. |

#### Render Targets

| Class | Description |
|-------|-------------|
| `PlatformViewRenderTarget` | Interface for offscreen rendering. |
| `ImageReaderPlatformViewRenderTarget` | Uses `ImageReader` for rendering. |
| `SurfaceTexturePlatformViewRenderTarget` | Uses `SurfaceTexture`. |
| `SurfaceProducerPlatformViewRenderTarget` | Uses `SurfaceProducer`. |

---

### `io.flutter.util`

Utility classes for Flutter embedding.

| Class/Interface | Description |
|-----------------|-------------|
| `Preconditions` | Argument validation (`checkNotNull`, `checkState`). |
| `PathUtils` | Path manipulation utilities. |
| `ViewUtils` | View hierarchy utilities. |
| `ViewUtils.DisplayUpdater` | Display metrics updater. |
| `ViewUtils.ViewVisitor` | View tree visitor pattern. |
| `HandlerCompat` | Compatibility wrapper for `Handler`. |
| `TraceSection` | Performance tracing utilities. |
| `Predicate<T>` | Functional predicate interface. |

---

### `io.flutter.view`

View, texture, and accessibility APIs.

#### Accessibility

| Class/Interface | Description |
|-----------------|-------------|
| `AccessibilityBridge` | Bridge between Android OS accessibility and Flutter. |
| `AccessibilityBridge.Action` | Accessibility actions. |
| `AccessibilityBridge.OnAccessibilityChangeListener` | Callback for accessibility state changes. |
| `AccessibilityStringBuilder` | Builds accessibility strings with spans. |
| `AccessibilityStringBuilder.StringAttribute` | Base attribute class. |
| `AccessibilityStringBuilder.LocaleStringAttribute` | Locale-tagged text. |
| `AccessibilityStringBuilder.SpellOutStringAttribute` | Spell-out text. |

#### Textures

| Class/Interface | Description |
|-----------------|-------------|
| `TextureRegistry` | Registry for backend textures. |
| `TextureRegistry.TextureEntry` | Base texture entry. |
| `TextureRegistry.SurfaceTextureEntry` | `SurfaceTexture`-based entry. |
| `TextureRegistry.SurfaceProducer` | `Surface`-based texture producer. |
| `TextureRegistry.SurfaceProducer.Callback` | Surface lifecycle callback. |
| `TextureRegistry.SurfaceLifecycle` | Enum: `MANUAL`, `AUTOMATIC`. |
| `TextureRegistry.ImageTextureEntry` | `Image`-based texture entry. |
| `TextureRegistry.GLTextureConsumer` | OpenGL texture consumer. |
| `TextureRegistry.ImageConsumer` | Image consumer interface. |
| `TextureRegistry.OnFrameConsumedListener` | Frame consumption callback. |
| `TextureRegistry.OnTrimMemoryListener` | Memory pressure callback. |

#### Other

| Class | Description |
|-------|-------------|
| `FlutterCallbackInformation` | Callback info for `PluginUtilities` registration. |
| `FlutterRunArguments` | Arguments for isolate entry. |
| `VsyncWaiter` | Vsync timing utility. |
