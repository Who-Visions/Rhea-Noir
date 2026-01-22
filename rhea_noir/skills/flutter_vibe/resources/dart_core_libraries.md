# Core Dart Libraries & Engine Layers

This resource provides a reference for the fundamental libraries in Dart and the lowest-level services in Flutter (`dart:ui`), guiding you from the language core to the rendering engine.

## 1. dart:core (The Foundation)
Built-in types, collections, and core functionality automatically imported in every Dart program.

### Primitives
- **Numbers**: `int` (integers), `double` (floating-point).
- **Strings**: `String` (UTF-16), `StringBuffer` (efficient builder), `RegExp`.
- **Booleans**: `bool`.
- **Date & Time**: `DateTime`, `Duration`, `Stopwatch`.
- **Errors**: `Error`, `Exception`, `ArgumentError`, `StateError`.

### Basic Collections
- **List**: Ordered collection (array). `['A', 'B']`.
- **Set**: Unordered unique collection. `{'A', 'B'}`.
- **Map**: Key-value pairs. `{'key': 'value'}`.
- **Iterable**: Common interface for collections (`map`, `where`, `reduce`).

### Key Utilities
- **Uri**: Uniform Resource Identifiers.
- **print()**: Output to console.
- **identityHashCode()**: Object identity.

---

## 2. dart:async (Asynchronous Programming)
Fundamental building blocks for non-blocking operations.

### Future
Represents a computation whose return value might not yet be available.
- **Usage**: HTTP requests, file I/O, platform channel calls.
- **Methods**: `then`, `catchError`, `whenComplete`.
- **Async/Await**: Syntactic sugar for handling Futures.

### Stream
An asynchronous sequence of data.
- **Usage**: User input events, file reading (chunks), WebSocket messages, Firebase snapshots.
- **StreamController**: Manually control a stream (add events/errors).
- **Transform**: `stream.transform(utf8.decoder)` converts bytes to strings.
- **Broadcast Stream**: Allows multiple listeners (vs single-subscription default).

### Zones
`Zone` represents an environment that remains stable across asynchronous calls.
- **runZonedGuarded**: The standard way to catch global unhandled errors in Flutter apps (e.g., for Crashlytics).
- **Zone Values**: Pass data implicitly down the async call stack (like thread-local storage).

---

## 3. dart:math (Mathematics)
Mathematical constants, functions, and random number generation.

### Utilities
- **Random**: Generator for bool, int, or double values.
- **Point**: 2D position `Point(x, y)`.
- **Rectangle**: Axis-aligned rectangle (Immutable and Mutable versions).

### Functions
- **Trigonometry**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`.
- **Powers/Logs**: `pow(x, exponent)`, `sqrt`, `log`, `exp`.
- **Min/Max**: `min(a,b)`, `max(a,b)`.

### Constants
- **pi**: 3.14159...
- **e**: Base of natural logarithms.
- **sqrt2**: Square root of 2.

---

## 4. dart:collection (Advanced Collections)
Specialized data structures beyond the basic List/Set/Map.

### Maps
- **HashMap**: Unordered, fast lookup.
- **LinkedHashMap**: Insertion ordered (default Dart `Map`).
- **SplayTreeMap**: Sorted keys (Red-Black tree).
- **UnmodifiableMapView**: Read-only wrapper.

### Sets
- **HashSet**: Unordered.
- **LinkedHashSet**: Insertion ordered (default Dart `Set`).
- **SplayTreeSet**: Sorted values.

### Queues
- **Queue**: Double-ended queue interface.
- **ListQueue**: List-based implementation.
- **DoubleLinkedQueue**: Linked-list based implementation.

### Lists
- **LinkedList**: Doubly-linked list where elements know their position.
- **UnmodifiableListView**: Read-only wrapper.

---

## 5. dart:convert (Data Encoding)
Encoders and decoders for converting between different data representations.

### JSON
- **JsonCodec**: `json` (default instance).
- **encode**: Object/Map/List → String.
- **decode**: String → Object/Map/List.

### UTF-8
- **Utf8Codec**: `utf8` (default instance).
- **encode**: String → `List<int>` (bytes).
- **decode**: `List<int>` → String.

### Other Codecs
- **Base64**: `base64` (Standard and URL-safe).
- **Latin1**: `latin1` (ISO-8859-1).
- **Ascii**: `ascii` (7-bit).
- **HtmlEscape**: Sanitize strings for HTML output.

---

## 6. dart:typed_data (Binary Data)
Efficient handling of fixed-size data and SIMD numeric types.

### Byte Buffers
- **ByteBuffer**: Raw sequence of bytes.
- **ByteData**: Random-access read/write of different types (Int16, Float32) from a buffer.
- **BytesBuilder**: Efficiently build a list of bytes.
- **Endian**: Define byte order (Little Endian / Big Endian).

### Typed Lists
- **Uint8List**: 8-bit unsigned integers (Bytes). Most common for binary data (images, files).
- **Int32List / Float64List**: Specific numeric types.
- **SIMD types**: `Float32x4`, `Int32x4` for vector operations.

---

## 7. dart:ffi (Foreign Function Interface)
Interoperability with C libraries. *Native platforms only.*

### Core Concepts
- **DynamicLibrary**: Load a `.so`, `.dll`, or `.dylib`.
- **Pointer<T>**: Pointer to native memory.
- **Struct / Union**: Define C data structures in Dart.
- **NativeFunction**: C function signature.

### Memory Management
- **Allocator**: `calloc`, `malloc` for managing native heap.
- **NativeFinalizer**: Clean up native resources when Dart object is garbage collected.

---

## 8. dart:io (I/O for Non-Web)
File, socket, HTTP, and process support. *Not available on Web.*

### File System
- **File**: Read/Write files. `File('path.txt').readAsString()`.
- **Directory**: List contents, create/delete folders.
- **FileSystemEntity**: Base class (exists, stat, delete).

### Networking
- **HttpClient**: Low-level HTTP client (use `package:http` for general use).
- **HttpServer**: Bind to a port and listen for requests.
- **WebSocket**: Full-duplex communication.
- **Socket / ServerSocket**: Raw TCP sockets.

### System
- **Process**: Run native commands (`Process.run`, `Process.start`).
- **Platform**: OS details (`Platform.isAndroid`, `Platform.environment`).
- **stdin / stdout / stderr**: Standard streams.

---

## 9. dart:isolate (Concurrency)
Independent workers that do not share memory. *Native platforms only.*

### Key Classes
- **Isolate**: Execution context. `Isolate.spawn(entryPoint, message)`.
- **SendPort**: Send messages *to* an isolate.
- **ReceivePort**: Receive messages *from* other isolates.
- **Capability**: Unforgeable token for security/identity.

---

## 10. dart:developer (Developer Tools)
Interaction with the runtime, debugger, and inspector. *Not for production use.*

### Debugging & Inspection
- **debugger()**: Programmatically trigger a breakpoint.
- **inspect(obj)**: Send object reference to attached debugger/inspector.
- **log()**: Emit log events to DevTools logging view.
- **Timeline**: Add sync/async events to the DevTools performance timeline.

---

## 11. dart:ui (The Engine Layer)
The lowest-level services that Flutter frameworks use to bootstrap applications.

### Key Classes
- **Canvas**: Recording graphical operations.
- **Paint**: Style description (color, stroke, shaders).
- **PictureRecorder**: Recording operations for rendering.
- **SceneBuilder**: Composited scene for the GPU.
- **PlatformDispatcher**: Native platform messages and frame scheduling.

### Graphics Primitives
- **Color**: ARGB immutable value.
- **Offset / Size**: 2D geometry.
- **Rect / RRect**: Rectangles.
- **Gradient**: Shaders.

---

## 12. dart:ui_web (Web Engine)
Web-specific primitives (only available on Web).

### Key Classes
- **AssetManager**: Network asset loading.
- **PlatformViewRegistry**: Registering HTML elements (`div`, `video`, etc.) as platform views.
- **UrlStrategy**: Implementation of URL handling (Hash vs Path).
- **BrowserDetection**: Detect browser engine.

---

## 13. Web Interop (package:web & dart:js_interop)
Modern, lightweight browser API bindings and JS interop. Replaces `dart:html`.

### package:web
Browser APIs generated from Web IDL. Wasm-compatible.
- **DOM Access**: `document.querySelector('div')`.
- **Event Handling**: `element.onClick.listen(...)`.
- **Helpers**: `web.helpers` for easier usage.

### dart:js_interop
Core abstraction for JS values and types.
- **JSAny / JSObject**: Base types for JS interaction.
- **JSExport**: Annotate Dart classes to export to JS.
- **createJSInteropWrapper**: Wrap Dart objects for JS consumption.
- **Type Conversions**: `toJS`, `toDart` extensions (e.g., `String` <-> `JSString`).

### dart:js_interop_unsafe
**Use with Caution**: Dynamic JS manipulation when types aren't known statically.
- **setProperty / getProperty**: Dynamic access.
- **callMethod**: Dynamic function calls.

---

## 14. Essential Utilities (package:async)
Expands on `dart:async` with powerful tools for streams, futures, and caching.

### Stream Enhancements
- **StreamGroup**: Merge multiple streams into one.
- **StreamQueue**: Pull-based interface for consuming streams (great for testing protocols).
- **StreamZip**: Combine values from multiple streams (Zip operator).
- **StreamSplitter**: Split a single stream into multiple branches.

### Future Utilities
- **CancelableOperation**: A wrapper around a Future that can be canceled.
- **AsyncMemoizer**: Run an async function exactly once and cache the result.
- **FutureGroup**: Wait for a collection of futures to complete.

### Caching
- **AsyncCache**: Runs async functions and caches results for a duration.

---

## 15. Testing Selectors (package:boolean_selector)
- **BooleanSelector**: Parse and evaluate boolean expressions (used in `package:test` platform selectors).

---

## 16. String Handling (package:characters)
Safe string operations handling Unicode grapheme clusters (essential for emojis and complex scripts).

### Classes
- **Characters**: The characters of a string as grapheme clusters. `myString.characters`.
- **CharacterRange**: A mutable range of characters.

### Usage
```dart
// Standard String length counts code units
'🇧🇷'.length; // 4

// Characters length counts grapheme clusters
'🇧🇷'.characters.length; // 1
```

---

## 17. Time & Testing (package:clock)
A provider for the "current time" that eases testing by allowing you to mock time WITHOUT standard libraries via `FakeAsync` or manual overrides.

### Core Concepts
- **Clock**: Provider for current time.
- **clock**: The default global clock (returns system time by default).
- **withClock**: Run a callback with a mocked clock.

### Usage
```dart
// Code
DateTime get now => clock.now();

// Test
withClock(Clock.fixed(DateTime(2025, 1, 1)), () {
  expect(now, DateTime(2025, 1, 1));
});
```

---

## 18. Cryptography (package:crypto)
Implementations of SHA, MD5, and HMAC functions.

### Hash Functions
- **SHA**: `sha1`, `sha256`, `sha512`.
- **MD5**: `md5` (Legacy, not generally recommended for security).

### Usage
```dart
import 'package:crypto/crypto.dart';
import 'dart:convert'; // for utf8

var bytes = utf8.encode("foobar"); 
var digest = sha256.convert(bytes);
print("Digest as hex: $digest");
```

---

## 19. Async Testing (package:fake_async)
Mock the passage of time within a zone, allowing you to test complex async logic and timers synchronously.

### Core Concepts
- **FakeAsync**: Controls a zone where time is simulated.
- **elapse(duration)**: Advance the simulated time.
- **flushMicrotasks()**: Execute all pending microtasks.

### Usage
```dart
import 'package:fake_async/fake_async.dart';

fakeAsync((async) {
  // logic that uses Timer, Future.delayed
  const duration = Duration(seconds: 5);
  late bool fired;
  Timer(duration, () => fired = true);

  // Time hasn't passed yet
  expect(fired, isFalse); 

  // Fast-forward time
  async.elapse(duration);
  expect(fired, isTrue);
});
```

---

## 20. File System Abstraction (package:file)
A pluggable file system abstraction that allows you to swap out the backend (e.g., for testing).

### Implementations
- **LocalFileSystem**: Wraps `dart:io`. Uses real OS file operations.
- **MemoryFileSystem**: In-memory implementation. Fast and isolated, perfect for tests.
- **ChrootFileSystem**: Provides a view into another FileSystem restricted to a specific path.

### Classes
- **FileSystem**: The base interface.
- **Directory / File / Link**: Abstract representations of FS entities.

### Usage
```dart
// Inject FileSystem into your class
class ConfigManager {
  final FileSystem fs;
  ConfigManager(this.fs);

  void save() => fs.file('config.json').writeAsStringSync('data');
}

// Test with MemoryFileSystem
final fs = MemoryFileSystem();
final manager = ConfigManager(fs);
manager.save();
expect(fs.file('config.json').existsSync(), isTrue);
```

---

## 21. Compiler Hints (`dart:js_util`, `dart2js`)
Annotations for low-level compiler control. *Experimental, for framework authors.*

### dart2js Pragmas
- **`@pragma('dart2js:noInline')`**: Prevent inlining of a method.
- **`@pragma('dart2js:tryInline')`**: Request aggressive inlining.

---

## 22. Metadata Annotations (`package:meta`)
Semantic annotations that tools use to provide better developer experience.

### Common Annotations
| Annotation | Purpose |
|------------|---------|
| `@deprecated` | Mark as deprecated (in dart:core) |
| `@override` | Explicitly override a member (in dart:core) |
| `@required` | Named parameter must be provided |
| `@protected` | Only visible within class hierarchy |
| `@visibleForTesting` | Public for testing purposes only |
| `@visibleForOverriding` | Public for overriding only |
| `@immutable` | Class and subtypes must be immutable |
| `@sealed` | Class cannot be extended outside package |

### Method Behavior
| Annotation | Purpose |
|------------|---------|
| `@mustCallSuper` | Overrides must call super |
| `@mustBeOverridden` | Concrete subclasses must override |
| `@nonVirtual` | Cannot be overridden |
| `@alwaysThrows` | Method always throws |
| `@factory` | Must return new instance or null |

### Value Handling
| Annotation | Purpose |
|------------|---------|
| `@useResult` | Return value must be used |
| `@doNotStore` | Value should not be stored |
| `@doNotSubmit` | For local development only |
| `@literal` | Const constructor should use `const` keyword |

### Testing & Development
| Annotation | Purpose |
|------------|---------|
| `@isTest` | Marks a test function |
| `@isTestGroup` | Marks a test group function |
| `@experimental` | API may change without notice |
| `@internal` | Not part of public API |

### Meta-Annotations (`meta_meta`)
Annotations that describe the intended use of other annotations.
- **`@Target(kinds)`**: Specifies valid targets for a custom annotation.
- **`TargetKind`**: Enum of target kinds (class, method, field, etc.).

---

## 23. Path Manipulation (`package:path`)
Cross-platform path manipulation. Import with prefix: `import 'package:path/path.dart' as p;`

### Top-Level Functions
| Function | Purpose |
|----------|---------|
| `p.join(parts...)` | Join path parts with platform separator |
| `p.basename(path)` | Get filename from path |
| `p.dirname(path)` | Get directory from path |
| `p.extension(path)` | Get file extension |
| `p.normalize(path)` | Simplify path (resolve `.`, `..`) |
| `p.isAbsolute(path)` | Check if absolute |
| `p.relative(path)` | Convert to relative path |
| `p.split(path)` | Split into components |

### Cross-Platform Contexts
```dart
var windowsPath = p.windows.join('C:', 'Users', 'file.txt');
var posixPath = p.posix.join('/home', 'user', 'file.txt');
var urlPath = p.url.join('https://example.com', 'path');
```

---

## 24. Platform Abstraction (`package:platform`)
Testable platform detection (alternative to `dart:io` statics).

- **`Platform`**: Interface for platform properties.
- **`LocalPlatform`**: Delegates to `dart:io`.
- **`FakePlatform`**: Mutable mock for testing.

```dart
// Inject for testability
class MyService {
  final Platform platform;
  MyService(this.platform);
  
  bool get isDesktop => platform.isWindows || platform.isMacOS || platform.isLinux;
}
```

---

## 25. Process Management (`package:process`)
Testable process execution.

- **`ProcessManager`**: Interface for spawning processes.
- **`LocalProcessManager`**: Real process execution.
- **`ProcessWrapper`**: Convenience wrapper around `Process`.

```dart
final processManager = LocalProcessManager();
final result = await processManager.run(['flutter', 'pub', 'get']);
```

---

## 26. Source Locations (`package:source_span`)
Track locations and ranges in source files (for parsers, linters, compilers).

- **`SourceFile`**: Represents a source file.
- **`SourceLocation`**: A position (line, column, offset) in a file.
- **`SourceSpan`**: A range of text in a file.
- **`SourceSpanException`**: Exception with source context.

---

## 27. Stack Traces (`package:stack_trace`)
Parse and format stack traces in a human-readable way.

- **`Trace`**: A parsed stack trace (list of frames).
- **`Frame`**: A single location in the call stack.
- **`Chain`**: Multiple stack traces (for async errors).
- **`Chain.capture(callback)`**: Capture full async stack traces.

---

## 28. Stream Channels (`package:stream_channel`)
Abstract two-way communication channels.

- **`StreamChannel<T>`**: Base class for bidirectional streams.
- **`IsolateChannel<T>`**: Channel over ReceivePort/SendPort pairs.
- **`MultiChannel<T>`**: Multiplex virtual channels over one transport.
- **`StreamChannelController<T>`**: Create custom channels.

---

## 29. String Scanning (`package:string_scanner`)
Parse strings using sequential pattern matching.

- **`StringScanner`**: Scan through a string with patterns.
- **`LineScanner`**: Tracks line/column numbers.
- **`SpanScanner`**: Returns matched ranges as `FileSpan`s.

```dart
var scanner = StringScanner('hello 123');
scanner.expect('hello');
scanner.scan(RegExp(r'\s+'));
var number = scanner.scan(RegExp(r'\d+'));
```

---

## 30. Sync HTTP (`package:sync_http`)
Synchronous HTTP client (blocking, for simple scripts).

- **`SyncHttpClient`**: Blocking HTTP client.
- **`SyncHttpClientRequest`**: Build request.
- **`SyncHttpClientResponse`**: Read response.

> [!WARNING]
> Avoid in Flutter apps; use async HTTP instead.

---

## 31. Terminal Glyphs (`package:term_glyph`)
Unicode/ASCII box-drawing characters for CLI output.

- **`glyphs`**: Current glyph set (Unicode or ASCII based on `ascii` flag).
- **`ascii`**: Toggle to use ASCII-only characters.
- **Box Drawing**: `horizontalLine`, `verticalLine`, `topLeftCorner`, `bottomRightCorner`, etc.
- **Arrows**: `leftArrow`, `rightArrow`, `upArrow`, `downArrow`.
- **Bullets**: `bullet`.

```dart
import 'package:term_glyph/term_glyph.dart' as glyph;

print('${glyph.topLeftCorner}${glyph.horizontalLine}${glyph.topRightCorner}');
// Outputs: ┌─┐ (or +-+ if glyph.ascii = true)
```

---

## 32. Typed Buffers (`package:typed_data`)
Growable typed-data lists with auto-resizing buffers.

- **`Uint8Buffer`**, **`Int32Buffer`**, **`Float64Buffer`**, etc.
- Queue variants: **`Uint8Queue`**, **`Float32Queue`**, etc.

```dart
var buffer = Uint8Buffer();
buffer.addAll([1, 2, 3]);
buffer.add(4);
```

---

## 33. Hashing (`package:quiver/hash`)
Utility for combining hash codes.

- **`hashObjects(iterable)`**: Combine multiple values into one hash.

```dart
@override
int get hashCode => hashObjects([field1, field2, field3]);
```

---

## 34. Vector Math (`package:vector_math`)
3D math library for games, simulations, and rendering.

### Core Types
| Type | Description |
|------|-------------|
| `Vector2`, `Vector3`, `Vector4` | N-dimensional vectors |
| `Matrix2`, `Matrix3`, `Matrix4` | N-dimensional matrices |
| `Quaternion` | Rotation representation |

### Collision Detection
- **`Aabb2`/`Aabb3`**: Axis-aligned bounding boxes.
- **`Sphere`**, **`Plane`**, **`Ray`**, **`Frustum`**, **`Triangle`**.

### OpenGL Utilities
| Function | Purpose |
|----------|---------|
| `makePerspectiveMatrix` | Perspective projection |
| `makeOrthographicMatrix` | Orthographic projection |
| `makeViewMatrix` | Camera view matrix |
| `pickRay` | Screen-to-world raycasting |

### Color Utilities
- **`Colors`**: HSL/RGB conversion, named colors.

### Geometry Generators (`vector_math_geometry`)
- **Generators**: `CubeGenerator`, `SphereGenerator`, `CylinderGenerator`, `RingGenerator`, `CircleGenerator`.
- **Filters**: `ColorFilter`, `FlatShadeFilter`, `InvertFilter`, `TransformFilter`.
- **Utilities**: `generateNormals()`, `generateTangents()`.

### Vector Lists (`vector_math_lists`)
Memory-efficient vector storage over `Float32List`.
- **`Vector2List`**, **`Vector3List`**, **`Vector4List`**: Lists backed by typed data.

> [!NOTE]
> Use `vector_math_64` (double precision) for Flutter apps. It has the same API but uses 64-bit floats, which Flutter's rendering engine expects.

### SIMD Operations (`vector_math_operations`)
High-performance matrix operations on raw buffers.
- **`Matrix44Operations`**: Operates on `Float32List`.
- **`Matrix44SIMDOperations`**: SIMD-optimized operations on `Float32x4List`.

---

## 35. VM Service (`package:vm_service`)
Dart VM debugging and profiling API. Used by DevTools.

- **`VmService`**: Client for VM service protocol.
- **`vmServiceConnectUri(wsUri)`**: Connect to a running VM.
- **Key Classes**: `Isolate`, `Breakpoint`, `Frame`, `Instance`, `Script`, `HeapSnapshotGraph`.

```dart
import 'package:vm_service/vm_service_io.dart';

final service = await vmServiceConnectUri('ws://127.0.0.1:8181/ws');
final vm = await service.getVM();
```

> [!NOTE]
> Primarily for tooling/DevTools. Not typically used in app code.
