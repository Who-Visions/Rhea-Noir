# Animations & Motion

Bring your UI to life with Implicit and Explicit animations.

## 1. Implicit Animations (Simple)
"Fire and forget". You change a value, Flutter animates to it.

### Built-in Widgets
`AnimatedContainer`, `AnimatedOpacity`, `AnimatedPadding`, etc.

```dart
AnimatedContainer(
  duration: const Duration(seconds: 1),
  curve: Curves.fastOutSlowIn,
  width: _selected ? 200.0 : 100.0,
  height: _selected ? 100.0 : 200.0,
  decoration: BoxDecoration(
    color: _selected ? Colors.blue : Colors.red,
    borderRadius: _borderRadius, // e.g. BorderRadius.circular(8)
  ),
  child: const Center(child: Text('Tap Me')),
)
// Trigger animation by calling setState(() { _selected = !_selected; });
```

### Fade In/Out (`AnimatedOpacity`)
Smoothly toggle visibility without jarring transitions.

```dart
AnimatedOpacity(
  opacity: _visible ? 1.0 : 0.0,
  duration: const Duration(milliseconds: 500),
  child: const Text('Now you see me'),
)
```

### Custom Values (`TweenAnimationBuilder`)
Animate *any* value without a controller.

```dart
TweenAnimationBuilder<double>(
  tween: Tween(begin: 0, end: 1),
  duration: const Duration(seconds: 1),
  builder: (context, value, child) {
    return Opacity(opacity: value, child: child);
  },
  child: const Text('Fade In'), // Child optimization
)
```

## 2. Explicit Animations (Advanced)
Requires an `AnimationController`. You control start/stop/reverse/repeat.

### Components
1.  **`AnimationController`**: Manages time (0.0 -> 1.0). Requires `SingleTickerProviderStateMixin`.
2.  **`CurvedAnimation`**: Applies a non-linear curve.
3.  **`Tween`**: Maps 0.0-1.0 to your data range (e.g. Colors, Sizes).
4.  **`AnimatedBuilder`**: Rebuilds only the animated part.

### Implementation Pattern

```dart
class MyAnim extends StatefulWidget {
  @override
  _MyAnimState createState() => _MyAnimState();
}

class _MyAnimState extends State<MyAnim> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _animation = CurvedAnimation(parent: _controller, curve: Curves.bounceOut);
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose(); // CRITICAL
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.scale(
          scale: _animation.value, // 0.0 -> 1.0 (curved)
          child: child,
        );
      },
      child: const FlutterLogo(size: 100),
### Refactoring: `AnimatedWidget` & `AnimatedBuilder`
Avoid `setState()` spam by separating concerns.

1.  **`AnimatedWidget`**:
    Subclass it to create a reusable animating component.
    ```dart
    class SpinningLogo extends AnimatedWidget {
      const SpinningLogo({super.key, required Animation<double> animation})
        : super(listenable: animation);

      @override
      Widget build(BuildContext context) {
        final animation = listenable as Animation<double>;
        return Transform.rotate(angle: animation.value, child: FlutterLogo());
      }
    }
    ```

2.  **`AnimatedBuilder`** (Preferred for composition):
    Animate *any* widget without creating a new class.
    ```dart
    AnimatedBuilder(
      animation: _controller,
      child: const FlutterLogo(), // Cached child (performance optimization)
      builder: (context, child) {
        return Transform.rotate(
          angle: _controller.value * 2.0 * math.pi,
          child: child,
        );
      },
    )
    ```

### Simultaneous Animations
Use multiple Tweens with the same Controller.
```dart
final _sizeTween = Tween(begin: 0.0, end: 300.0);
final _opacityTween = Tween(begin: 0.1, end: 1.0);

// In build()
Opacity(
  opacity: _opacityTween.evaluate(_controller),
  child: SizedBox(
    width: _sizeTween.evaluate(_controller),
    child: child,
  ),
)
```

## 3. Common Patterns

### Hero (Shared Element)
Animate a widget from Screen A to Screen B. Tags MUST match.

#### Standard Hero
```dart
// Screen A
Hero(
  tag: 'avatar_1', 
  child: Image.asset('avatar.png'),
)

// Screen B
Hero(
  tag: 'avatar_1', 
  child: Image.asset('avatar_large.png'),
)
```

#### Radial Hero (Circle to Square)
To animate shape changes (or custom flight paths), use `createRectTween`.
```dart
Hero(
  tag: 'transform_1',
  createRectTween: (begin, end) {
    return MaterialRectCenterArcTween(begin: begin, end: end);
  },
  child: RadialExpansion(
    maxRadius: 100, 
    child: Photo(),
  ),
)
  ),
)
```

### Custom Page Transitions (`PageRouteBuilder`)
Animate screen transitions (e.g. Slide Up).

```dart
Navigator.of(context).push(
  PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) => Page2(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      const begin = Offset(0.0, 1.0);
      const end = Offset.zero;
      const curve = Curves.ease;

      var tween = Tween(begin: begin, end: end).chain(CurveTween(curve: curve));

      return SlideTransition(
        position: animation.drive(tween),
        child: child,

### Physics Simulations
Move widgets with realistic physics (e.g. springing back after drag).

1.  **Dependencies**: `import 'package:flutter/physics.dart';`
2.  **Simulation**: Use `SpringSimulation` with `AnimationController.animateWith()`.

```dart
void _runSpringAnimation(Offset pixelsPerSecond, Size size) {
  _animation = _controller.drive(
    AlignmentTween(begin: _dragAlignment, end: Alignment.center),
  );

  final unitsPerSecondX = pixelsPerSecond.dx / size.width;
  final unitsPerSecondY = pixelsPerSecond.dy / size.height;
  final unitVelocity = Offset(unitsPerSecondX, unitsPerSecondY).distance;

  const spring = SpringDescription(mass: 30, stiffness: 1, damping: 1);
  final simulation = SpringSimulation(spring, 0, 1, -unitVelocity);

  _controller.animateWith(simulation);
}
```

### Staggered Animations (List/Menu)
Coordinate multiple animations with `Interval`.

```dart
// Controller duration should cover the entire sequence
_controller = AnimationController(duration: const Duration(seconds: 2), vsync: this);

// Create intervals for a list of items
final List<Interval> _itemIntervals = [];
for (var i = 0; i < itemCount; i++) {
  final startTime = i * 0.1; // 10% staggered delay
  final endTime = startTime + 0.5; // Each item takes 50% of total time
  _itemIntervals.add(Interval(startTime, endTime, curve: Curves.easeOut));
}

// In build():
for (var i = 0; i < itemCount; i++) {
  // Use AnimatedBuilder or similar
  final animationVal = _itemIntervals[i].transform(_controller.value);
  // Apply opacity/transform based on animationVal
}
```

## Resources
*   [Flutter Animation Overview](https://docs.flutter.dev/ui/animations)
## 4. Architecture & Concepts

### Core Classes
*   **`Animation<T>`**: Abstract class representing a value changing over time.
    *   **Status**: `dismissed` (start), `forward`, `reverse`, `completed` (end).
    *   **Listeners**: `addListener` (value change), `addStatusListener` (state change).
*   **`Animatable<T>`**: Stateless object that maps `double` (0.0-1.0) to `T`.
    *   **Tween**: A linear interpolation `Animatable`.
    *   **Curve**: Maps time (0-1) to curve progress (0-1).
*   **`AnimationController`**: Stateful `Animation<double>`. Manages the **Ticker**.
*   **`Ticker`**: Calls a callback once per frame (synced with screen refresh).

### Conceptual Flow
`Ticker` (Frame Callback) -> `AnimationController` (Time 0.0-1.0) -> `Curve` (Non-linear Time) -> `Tween` (Data Mapping) -> `Widget` (Render)

### Performance
*   **`AnimatedBuilder`**: Rebuilds *only* the part that needs to change.
*   **`RepaintBoundary`**: Use if animation causes frequent repaints of static subtrees.
