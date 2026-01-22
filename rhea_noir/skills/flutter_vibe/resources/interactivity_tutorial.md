# Interactivity & Gestures

## 1. Stateful vs Stateless Widgets

*   **StatelessWidget**: Immutable. `Icon`, `Text`. Subclass `StatelessWidget`.
*   **StatefulWidget**: Mutable. `Checkbox`, `Slider`, `TextField`. Subclass `StatefulWidget` + `State`.

**Key Concept**: The `State` object persists while the Widget rebuilds. Call `setState()` to trigger a rebuild.

## 2. Managing State

### Approach A: Widget Manages Own State
Use for isolated interactions (e.g., simple color toggle).

```dart
class TapboxA extends StatefulWidget {
  @override
  State<TapboxA> createState() => _TapboxAState();
}

class _TapboxAState extends State<TapboxA> {
  bool _active = false;

  void _handleTap() {
    setState(() {
      _active = !_active;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _handleTap,
      child: Container(color: _active ? Colors.green : Colors.grey),
    );
  }
}
```

### Approach B: Parent Manages State (Callbacks)
Use when the state dictates behavior of other widgets. The child is stateless (dumb).

```dart
// Child
class TapboxB extends StatelessWidget {
  final bool active;
  final ValueChanged<bool> onChanged;

  const TapboxB({required this.active, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged(!active),
      child: Container(color: active ? Colors.green : Colors.grey),
    );
  }
}

// Parent
class ParentWidget extends StatefulWidget { ... } // Manages _active state
```

### Approach C: Mix-and-Match
Widget manages ephemeral state (highlight/animation), Parent manages logical state (value).

```dart
class TapboxC extends StatefulWidget {
  final bool active;
  final ValueChanged<bool> onChanged;
  ...
}

class _TapboxCState extends State<TapboxC> {
  bool _highlight = false;

  void _handleTapDown(TapDownDetails _) => setState(() => _highlight = true);
  void _handleTapUp(TapUpDetails _) => setState(() => _highlight = false);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTap: () => widget.onChanged(!widget.active),
      child: Container(
        color: widget.active ? Colors.green : Colors.grey,
        border: _highlight ? Border.all(color: Colors.teal) : null,
      ),
    );
  }
}
```

---

## 3. Gestures Deep Dive

### The Gesture System
1.  **Pointers**: Raw data (Down, Move, Up, Cancel).
2.  **Gestures**: Semantic actions (Tap, Drag, Scale).

### Gesture Detector
The primary widget for detecting gestures.

```dart
GestureDetector(
  onTap: () { print('Tap'); },
  onDoubleTap: () { print('Double Tap'); },
  onLongPress: () { print('Long Press'); },
  onVerticalDragUpdate: (details) { print(details.delta.dy); },
  child: Container(...),
)
```

### Gesture Disambiguation (The Arena)
When multiple recognizers want the stream (e.g., Vertical List vs Horizontal Swipe):
*   **The Arena**: Recognizers join the arena.
*   **Winning**:
    *   One recognizer remains (others leave).
    *   A recognizer explicitly declares victory (e.g., moved > 10px).

**Tip**: Use `Listener` to get raw pointer events if `GestureDetector` is too high-level (e.g., exact pixel coordinates).

### Common Callbacks
*   `onTap`: Complete press and release.
*   `onPanUpdate`: Dragging (horizontal/vertical unspecified).
*   `onScaleUpdate`: Pinch to zoom.

---

---

## 4. Drag and Drop

### In-App Dragging
Use `Draggable` and `DragTarget`.

```dart
// The Widget being dragged
Draggable<String>(
  data: 'Red Item',
  feedback: Container(color: Colors.red.withOpacity(0.5), width: 100, height: 100), // Shown under finger
  childWhenDragging: Container(color: Colors.grey, width: 100, height: 100), // Left behind
  child: Container(color: Colors.red, width: 100, height: 100),
)

// The Drop Zone
DragTarget<String>(
  onAcceptWithDetails: (details) => print('Dropped: ${details.data}'),
  builder: (context, candidateData, rejectedData) {
    return Container(
      color: candidateData.isNotEmpty ? Colors.blue.withOpacity(0.3) : Colors.blue,
      width: 200, height: 200,
    );
  },
)
```

### Cross-App Dragging
Use `super_drag_and_drop` package for desktop/web cross-application support (e.g., file drop).

## 5. Ripple Effects (InkWell)
Material Design touch ripples.

**Requirement**: Must have a `Material` widget ancestor.

```dart
Material(
  color: Colors.transparent,
  child: InkWell(
    onTap: () { print('Ripple!'); },
    splashColor: Colors.red.withOpacity(0.3),
    borderRadius: BorderRadius.circular(8),
    child: Container(
      padding: EdgeInsets.all(12),
      child: Text('Tap Me'),
    ),
  ),
)
```

**Note**: `InkWell` paints on the `Material` layer. If you put an opaque `Container` *inside* the `InkWell`, it will cover functionality.
*Fix*: Put `Ink` or `Material` *inside* the `InkWell`, or use `Ink.image`.

---

## Resources
*   [Flutter Gestures Cookbook](https://docs.flutter.dev/cookbook/gestures)
---

## 6. Swipe to Dismiss
A common pattern for lists (e.g., deleting emails).

### `Dismissible` Widget
Wraps a list item and provides swipe gestures.

**Key Parameters**:
*   `key`: **Unique** Key (critical for list consistency).
*   `background`: Widget revealed during swipe (e.g., Red background).
*   `onDismissed`: Callback to update data model.

```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    final item = items[index];
    
    return Dismissible(
      key: Key(item), // Must be unique per item, not just index!
      
      // Visual feedback (Delete icon on red background)
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerRight,
        padding: EdgeInsets.only(right: 20),
        child: Icon(Icons.delete, color: Colors.white),
      ),
      
      direction: DismissDirection.endToStart, // Limit swipe direction
      
      onDismissed: (direction) {
        // 1. Update Data Model (Must be synchronous)
        setState(() {
          items.removeAt(index);
        });
        
        // 2. Show feedback
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('$item dismissed')),
        );
      },
      
      child: ListTile(title: Text(item)),
    );
  },
)
```

**Common Pitfall**: Using `ValueKey(index)` is dangerous if the list order changes. Use `Key(item.id)` instead.
