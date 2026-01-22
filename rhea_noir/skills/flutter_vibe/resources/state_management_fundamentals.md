# State Management Fundamentals

State management is the discipline of managing the data that allows your app to function and react to user input. In Flutter, because the UI is declarative (UI = f(state)), managing state effectively is critical.

## 1. Overview

### Ephemeral State
- **Definition**: State that is contained within a single widget and doesn't need to be accessed elsewhere.
- **Examples**: Current page in a `PageView`, current animation progress, text in a `TextField`.
- **Solution**: `setState`, `hooks`.

### App State
- **Definition**: State that is shared across many parts of your app or kept between sessions.
- **Examples**: User authentication status, shopping cart contents, news feed data, user preferences.
- **Solution**: `Riverpod` (Vibe Standard), `Provider`, `Bloc`.

## 2. Built-in Approaches

### setState
The low-level approach. Calling `setState` tells the framework that the internal state of this object has changed and it needs to rebuild.
```dart
setState(() {
  _counter++;
});
```
*   **Pros**: Simple, built-in, easy to understand for beginners.
*   **Cons**: Hard to maintain in large apps, rebuilds entire widget subtrees, difficult to test logic in isolation.

### InheritedWidget & InheritedModel
The base class for widgets that propagate information down the tree. `Theme` and `MediaQuery` use this.
*   **Pros**: efficient, built-in.
*   **Cons**: Verbose boilerplate, complex to implement correctly from scratch.

### ValueNotifier & InheritedNotifier
A `ChangeNotifier` that holds a single value.
```dart
final count = ValueNotifier(0);
// ...
ValueListenableBuilder(
  valueListenable: count,
  builder: (context, value, child) => Text('$value'),
)
```

## 3. The Vibe Standard: Riverpod

For `flutter_vibe` projects, we use **Riverpod**. It solves the limitations of `Provider` and `InheritedWidget`.

### Why Riverpod?
1.  **Compile-safe**: No more `ProviderNotFoundException`. If it compiles, the provider exists.
2.  **No BuildContext**: Read providers from anywhere (controllers, repositories), not just widgets.
3.  **Testable**: Easy to override providers for testing without complex setups.
4.  **Async Native**: First-class support for `Future` and `Stream` via `AsyncValue`.

### Core Concepts

#### Providers
To create state, define a provider. (Using `riverpod_annotation` is recommended).
```dart
@riverpod
String helloWorld(Ref ref) {
  return 'Hello world';
}
```

#### Consumers
To read state in a widget, use a `ConsumerWidget`.
```dart
class MyApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final String value = ref.watch(helloWorldProvider);
    return Text(value);
  }
}
```

#### Notifiers
For mutable state, use `Notifier` (synchronous) or `AsyncNotifier` (asynchronous).
```dart
@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;

  void increment() => state++;
}
```

## 4. Community Packages
While we standardization on Riverpod, the ecosystem is vast:
- **Bloc / Cubit**: Rigid, event-driven pattern. Good for strict enterprise teams.
- **Provider**: The predecessor to Riverpod. Still widely used but less capable.
- **GetX**: "All-in-one" solution. **Avoid** in Vibe/Professional projects (anti-patterns, non-standard navigation).
