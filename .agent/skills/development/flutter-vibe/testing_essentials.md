# Testing Essentials

This guide covers the entire spectrum of testing in Flutter, from unit tests to full-blown integration tests driving the app on a device.

## 1. Widget Testing (`flutter_test`)
Built on top of `package:test`, this library allows you to verify the UI and logic of individual widgets or screens in a headless environment.

### Core Concepts

**WidgetTester**: The programmatic interface to interact with widgets.
**Finder**: Locates widgets in the tree (`find.text`, `find.byType`).
**Matcher**: Asserts the state of found widgets (`findsOneWidget`, `findsNothing`).

### Basic Test Structure

```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('MyWidget has a title and message', (WidgetTester tester) async {
    // 1. Pump the widget
    await tester.pumpWidget(const MyWidget(title: 'T', message: 'M'));

    // 2. Finders
    final titleFinder = find.text('T');
    final messageFinder = find.text('M');

    // 3. Matchers
    expect(titleFinder, findsOneWidget);
    expect(messageFinder, findsOneWidget);
  });
}
```

### Key Matchers
- **Common**: `findsOneWidget`, `findsNothing`, `findsNWidgets(n)`, `findsAtLeastNWidgets(n)`.
- **Content**: `find.text('Submit')`, `find.byIcon(Icons.add)`.
- **Type**: `find.byType(CircularProgressIndicator)`.
- **Keys**: `find.byKey(Key('submit_btn'))`.
- **Golden Files**: `matchesGoldenFile('goldens/my_widget.png')`.

### Advanced Interaction
- **Tapping**: `await tester.tap(find.text('Save'))`.
- **Entering Text**: `await tester.enterText(find.byType(TextField), 'Hello')`.
- **Scrolling**: `await tester.drag(find.byType(ListView), const Offset(0, -300))`.
- **Pumping**:
  - `tester.pump()`: Triggers a frame (duration: 0).
  - `tester.pumpAndSettle()`: Repeatedly calls pump until no animations are valid.

---

## 2. Integration Testing (`integration_test`)
The modern framework for end-to-end tests that run on a real device/emulator.

### Setup
Add `integration_test` to dev_dependencies.

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  // Initialize the binding
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('end-to-end test example', (tester) async {
    app.main();
    await tester.pumpAndSettle();

    final fab = find.byTooltip('Increment');
    await tester.tap(fab);
    await tester.pumpAndSettle();

    expect(find.text('1'), findsOneWidget);
  });
}
```

### Core Classes
- **IntegrationTestWidgetsFlutterBinding**: Binds the test framework to the real app engine. Reports results to the host.
- **VmServiceProxyGoldenFileComparator**: Compares image pixels against a golden image on the host file system (bypassing device file system limitations).

### Driver Adaptor (`integration_test_driver`)
Utilities to run integration tests via `flutter drive` (often for CI/CD or specialized workflows).

- **integrationDriver**: Adaptor function to run the test.
  ```dart
  import 'package:integration_test/integration_test_driver.dart';

  Future<void> main() => integrationDriver();
  ```
- **writeResponseData**: Writes JSON-serializable data to `testOutputsDirectory`.
- **testOutputsDirectory**: The directory where test outputs are stored.

### Extended Driver (`integration_test_driver_extended`)
Provides enhanced driver capabilities, specifically for handling screenshots on failure or success.

- **integrationDriver**: Extended version that accepts callbacks.
  ```dart
  import 'package:integration_test/integration_test_driver_extended.dart';

  Future<void> main() async {
    await integrationDriver(
      onScreenshot: (String name, List<int> image, [Map<String, Object?>? args]) async {
        // Handle screenshot (e.g., save to disk)
        final File imageFile = File('screenshots/$name.png');
        await imageFile.writeAsBytes(image);
        return true;
      },
      writeResponseOnFailure: true,
    );
  }
  ```

### Common Utilities (`common`)
Classes often used in driver-side or hybrid tests.
- **CallbackManager**: Interfaces for handling driver-side inputs.
- **DriverTestMessage**: Communication protocol between app and driver.
- **WebDriverCommand**: Commands sent to the WebDriver (for web integration).
- **IntegrationTestResults**: Standard interface for test reporting.

---

## 3. Legacy Testing (`flutter_driver`)
**Note**: Deprecated in favor of `integration_test` for most use cases, but useful for pure black-box testing.

### Setup (`driver_extension`)
```dart
// test_driver/app.dart
import 'package:flutter_driver/driver_extension.dart';
void main() {
  enableFlutterDriverExtension();
  app.main();
}
```
Requires a separate driver script on the host to control the app via VM Service.

---

## 4. Leak Tracking (`leak_tracker` / `leak_tracker_flutter_testing`)
Detect memory leaks in your widgets and classes during tests.

### Core Classes
- **LeakTracking**: Main class providing leak tracking functionality.
- **LeakTrackingConfig**: Configuration for leak tracking behavior.
- **LeakDiagnosticConfig**: Settings for diagnostic output.
- **Leaks**: Detailed information about found leaks.
- **LeakSummary**: Statistical summary of leaks.
- **LeakReport**: Individual leak information for troubleshooting.

### Ignoring Leaks
- **IgnoredLeaks**: Total set of leaks to ignore.
- **IgnoredLeaksSet**: Set of classes to ignore during tracking.

### Memory Baselining
- **MemoryBaseline**: Snapshot of memory state.
- **MemoryBaselining**: Settings for measuring memory footprint.
- **PhaseSettings**: Leak tracking settings for specific execution phases.

### Utilities
- **forceGC()**: Forces garbage collection by aggressive memory allocation.
- **formattedRetainingPath(ref)**: Returns nicely formatted retaining path for a WeakReference target.

### Usage
```dart
import 'package:leak_tracker_flutter_testing/leak_tracker_flutter_testing.dart';

testWidgets('Memory check', (tester) async {
  await tester.pumpWidget(MyLeakingWidget());
  await tester.pumpWidget(Container()); 
  // Leak tracker automatically verifies disposal
});
```

### Testing Support (`leak_tracker_testing`)
Provides test-specific helpers and matchers.

- **LeakTesting**: Configuration class for test-specific leak tracking settings.
- **isLeakFree**: Matcher that checks if a leak collection is empty.

```dart
import 'package:leak_tracker_testing/leak_tracker_testing.dart';

expect(leaks, isLeakFree);
```

---

## 5. Mocking & Fakes
- **Mockito**: Standard mocking.
- **Fake**: `flutter_test` provides `Fake` for creating dummy objects that throw on un-overridden method calls.
- **TestVSync**: `flutter_test` provides `TestVSync` for granular control over animation ticks.

---

## 6. Configuration
`flutter_test_config.dart` allows per-directory configuration.

```dart
Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  setUpAll(() { /* Global Setup */ });
  await testMain();
}
```

---

## 7. Matchers (`package:matcher` / `expect`)
The foundation of test assertions. Used with `expect()` and `expectLater()`.

### Core Functions
- **`expect(actual, matcher)`**: Synchronous assertion.
- **`expectLater(actual, matcher)`**: Returns a Future for async matchers.
- **`fail(message)`**: Immediately fail the test.

### Value Matchers
| Matcher | Description |
|---------|-------------|
| `equals(x)` | Structural equality |
| `same(x)` | Identity (identical) |
| `isA<T>()` | Type check |
| `isNull` / `isNotNull` | Null checks |
| `isTrue` / `isFalse` | Boolean checks |
| `anything` | Matches any value |

### Numeric Matchers
| Matcher | Description |
|---------|-------------|
| `greaterThan(x)` | `> x` |
| `lessThan(x)` | `< x` |
| `closeTo(x, delta)` | Within delta of x |
| `inInclusiveRange(low, high)` | `low <= x <= high` |
| `isPositive` / `isNegative` / `isZero` | Sign checks |

### Collection Matchers
| Matcher | Description |
|---------|-------------|
| `isEmpty` / `isNotEmpty` | Empty checks |
| `hasLength(n)` | Length check |
| `contains(x)` | Contains element |
| `containsAll(iterable)` | Contains all (any order) |
| `orderedEquals(iterable)` | Exact order match |
| `unorderedEquals(iterable)` | Same elements, any order |
| `everyElement(matcher)` | All elements match |
| `anyElement(matcher)` | At least one matches |

### String Matchers
| Matcher | Description |
|---------|-------------|
| `startsWith(prefix)` | Prefix check |
| `endsWith(suffix)` | Suffix check |
| `matches(regex)` | Regex match |
| `equalsIgnoringCase(s)` | Case-insensitive |
| `equalsIgnoringWhitespace(s)` | Whitespace-insensitive |
| `stringContainsInOrder(list)` | Substrings in order |

### Exception Matchers
| Matcher | Description |
|---------|-------------|
| `throwsA(matcher)` | Throws matching exception |
| `throwsArgumentError` | Throws ArgumentError |
| `throwsStateError` | Throws StateError |
| `returnsNormally` | No exception thrown |

### Async Matchers
| Matcher | Description |
|---------|-------------|
| `completes` | Future completes successfully |
| `completion(matcher)` | Future completes with value |
| `doesNotComplete` | Future never completes |
| `emits(matcher)` | Stream emits matching event |
| `emitsInOrder(list)` | Stream emits in order |
| `emitsDone` | Stream closes |

### Combining Matchers
- **`allOf(m1, m2, ...)`**: All matchers must match (AND).
- **`anyOf(m1, m2, ...)`**: At least one must match (OR).
- **`isNot(matcher)`**: Negation.

### Custom Matchers
```dart
class IsPositive extends Matcher {
  @override
  bool matches(item, Map matchState) => item is num && item > 0;

  @override
  Description describe(Description d) => d.add('a positive number');
}
```

---

## 8. WebDriver (`package:webdriver`)
Browser automation for end-to-end testing.

### Core Classes
- **`WebDriver`**: Main driver instance.
- **`WebElement`**: DOM element handle.
- **`By`**: Element locator strategies (id, css, xpath, etc.).
- **`Keyboard`**, **`Mouse`**: Input device control.

### Variants
- **Async**: `async_io` (dart:io), `async_html` (dart:html).
- **Sync**: `sync_io`, `sync_core` (blocking, for scripts).
- **Debug**: `StdioStepper` for command-line stepping through tests.

### Usage
```dart
import 'package:webdriver/async_io.dart';

final driver = await createDriver();
await driver.get('https://example.com');
final button = await driver.findElement(By.id('submit'));
await button.click();
await driver.quit();
```

### Common Exceptions
- `NoSuchElementException`, `StaleElementReferenceException`
- `TimeoutException`, `SessionNotCreatedException`

### Support Utilities
- **`waitFor(condition)`**: Poll until condition matches (with timeout/interval).
- **`Clock`**, **`Lock`**: Timing and synchronization helpers.
- **`FirefoxProfile`**: Configure Firefox profiles for testing.
