# Actions and Shortcuts

Bind physical keyboard events to logical actions in the UI.

## 1. Concepts
*   **Shortcut**: Key combination (e.g., `Ctrl+C`).
*   **Intent**: Abstract user intention (e.g., `SelectAllIntent`).
*   **Action**: Concrete implementation of the intent (e.g., `SelectAllAction`).

**Data Flow**:
Key Press -> `Shortcuts` Widget -> Maps to `Intent` -> `Actions` Widget -> Finds `Action` for `Intent` -> Invokes `Action`.

## 2. Basic Setup

### Step 1: Define Intent
Extends `Intent`. Can hold data.

```dart
class SelectAllIntent extends Intent {
  const SelectAllIntent();
}
```

### Step 2: Bind Keys to Intent (`Shortcuts`)
Place higher in the widget tree.

```dart
Shortcuts(
  shortcuts: <ShortcutActivator, Intent>{
    SingleActivator(LogicalKeyboardKey.keyA, control: true): SelectAllIntent(),
  },
  child: ...
)
```

### Step 3: Define Action (`Actions`)
Maps the `Intent` to logic.

```dart
Actions(
  actions: <Type, Action<Intent>>{
    SelectAllIntent: CallbackAction<SelectAllIntent>(
      onInvoke: (intent) => print('Select All Triggered!'),
    ),
  },
  child: ...
)
```

## 3. Why Separate Actions/Intents?
*   **Decoupling**: Key bindings (shortcuts) can be defined globally, while actions (logic) can depend on local context (e.g., which widget is focused).
*   **Reusability**: One `CopyIntent` can be handled differently by a Text Field vs a Image Gallery.

## 4. Advanced: Custom Actions
Subclass `Action<T>` for complex logic.

```dart
class MySelectAction extends Action<SelectAllIntent> {
  final TextEditingController controller;
  MySelectAction(this.controller);

  @override
  void invoke(covariant SelectAllIntent intent) {
    controller.selection = TextSelection(
      baseOffset: 0,
      extentOffset: controller.text.length,
    );
  }
}
```

## Resources
---

## 5. Keyboard Focus System

Control where keyboard input is directed.

### Concepts
*   **FocusNode**: A single focusable element. Long-lived object (dispose it!).
*   **FocusScope**: A group of nodes (e.g., a Form). Limits traversal.
*   **Primary Focus**: The one node currently receiving input.

### `Focus` Widget
Wraps a child to make it focusable or to listen to key events.

```dart
Focus(
  onFocusChange: (hasFocus) => setState(() => _color = hasFocus ? Colors.blue : Colors.grey),
  onKeyEvent: (node, event) {
    if (event.logicalKey == LogicalKeyboardKey.escape) {
      print('Escape pressed!');
      return KeyEventResult.handled;
    }
    return KeyEventResult.ignored;
  },
  child: Container(color: _color, child: Text('Focus Me')),
)
```

### Controlling Traversal (`FocusTraversalGroup`)
Control Tab order.

```dart
FocusTraversalGroup(
  policy: OrderedTraversalPolicy(), // Use numeric order
  child: Column(
    children: [
      FocusTraversalOrder(
        order: NumericFocusOrder(2),
        child: TextField(decoration: InputDecoration(labelText: 'Second')),
      ),
      FocusTraversalOrder(
        order: NumericFocusOrder(1),
        child: TextField(decoration: InputDecoration(labelText: 'First')),
      ),
    ],
  ),
)
```

### Best Practices
1.  **Don't** create `FocusNode` in `build()`. Create in `initState`, dispose in `dispose`.
2.  **Do** use `autofocus: true` sparingly (one per scope).
3.  **Do** use `FocusScope.of(context).requestFocus(node)` (or `node.requestFocus()`) to move focus.
