# State Management

Managing data flow and UI updates in Flutter apps.

## 1. Concepts

### Thinking Declaratively
Flutter is **declarative**. You don't mutate the UI (e.g. `widget.setText()`); you change the **state**, and the UI rebuilds from scratch.
> **UI = f(state)**

### Types of State
1.  **Ephemeral State** (UI State):
    *   **Definition**: Local to a single widget. No need to serialize or share.
    *   **Examples**: `PageView` index, active tab, animation progress, text field scroll position.
    *   **Solution**: `StatefulWidget` + `setState()`.
2.  **App State** (Shared State):
    *   **Definition**: Shared across the app, preserved between sessions.
    *   **Examples**: User login, shopping cart, unread notifications, user preferences.
    *   **Solution**: State management packages (Provider, Riverpod, etc).

> **Rule of Thumb**: "Do whatever is less awkward." Start with `setState`. If access is needed elsewhere, promote to App State.

## 2. Default Approaches

### `setState` (Ephemeral)
Simplest way to rebuild a widget when data changes.
```dart
class Counter extends StatefulWidget {
  @override
  _CounterState createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;

  void _increment() {
    setState(() {
      _count++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(onPressed: _increment, child: Text('$_count'));
  }
}
```

### `InheritedWidget` (Low Level)
Efficiently propagate data down the tree. Used internally by `Provider` and `Theme`.
Generally too verbose for direct use; prefer a package.

## 3. Popular Packages

### Provider (Recommended for Beginners)
Wrapper around `InheritedWidget`. Simple and widely used.
```dart
// 1. Define Model
class CartModel extends ChangeNotifier {
  final List<Item> _items = [];
  UnmodifiableListView<Item> get items => UnmodifiableListView(_items);

  void add(Item item) {
    _items.add(item);
    notifyListeners();
  }
}

// 2. Provide
ChangeNotifierProvider(
  create: (context) => CartModel(),
  child: MyApp(),
)

// 3. Consume
Consumer<CartModel>(
  builder: (context, cart, child) {
    return Text("Total: ${cart.items.length}");
  },
)
```

### Riverpod (Modern Provider)
Compile-time safe, no context dependency, highly testable.
```dart
// 1. Define Provider
final cartProvider = ChangeNotifierProvider((ref) => CartModel());

// 2. Consume (ConsumerWidget)
class CartLabel extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cart = ref.watch(cartProvider);
    return Text("Total: ${cart.items.length}");
  }
}
```

### Bloc / Cubit (Enterprise)
Predictable state management using streams and events. Good for complex logic.

## 4. Best Practices
1.  **Lift State Up**: Move state to the lowest common ancestor of widgets that need it.
2.  **Immutability**: Prefer immutable state objects (especially with Bloc/Riverpod).
3.  **Separation**: Keep business logic out of UI code.
