# Zero to One with Flutter: Animations & Tweens

*Adapted from Mikkel Ravn's zero-to-one guide.*

---

## Core Concepts

### 1. Widgets & Trees
Flutter UIs are trees of immutable widgets.
- **Construction**: Configuration phase (`Constructor`)
- **Building**: Implementation phase (`build()`)
- **State**: Mutable objects attached to `StatefulWidget`

### 2. Tweens (The Functional Approach)
A `Tween<T>` models a path between two values of type `T` over time `t` (0.0 to 1.0).

> "Animate Ts by tracing out a path in the space of all Ts as the animation value runs from zero to one. Model the path with a Tween<T>."

---

## 2. Implementing a Chart Animation (Step-by-Step)

### Step 1: The Model (Bar)

First, define the domain model we want to animate. It needs `lerp` capabilities.

```dart
// bar.dart
import 'dart:ui' show lerpDouble;
import 'package:flutter/widgets.dart';

class Bar {
  final double height;
  
  Bar(this.height);

  static Bar lerp(Bar begin, Bar end, double t) {
    return Bar(lerpDouble(begin.height, end.height, t)!);
  }
}

class BarTween extends Tween<Bar> {
  BarTween(Bar begin, Bar end) : super(begin: begin, end: end);

  @override
  Bar lerp(double t) {
    return Bar.lerp(begin!, end!, t);
  }
}
```

### Step 2: The Painter (CustomPaint)

Efficient custom painting that repaints only when the animation ticks.

```dart
class BarChartPainter extends CustomPainter {
  final Bar bar;

  BarChartPainter(this.bar);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = Colors.blue[400]!.withOpacity(0.8);
    // Draw bar from bottom-center
    canvas.drawRect(
      Rect.fromLTWH(
        (size.width - 20) / 2,
        size.height - bar.height,
        20,
        bar.height,
      ),
      paint,
    );
  }

  @override
  bool shouldRepaint(BarChartPainter oldDelegate) => bar.height != oldDelegate.bar.height;
}
```

### Step 3: The State (AnimationController)

Orchestrates the animation using `AnimationController` and `Tween`.

```dart
class ChartPage extends StatefulWidget {
  @override
  _ChartPageState createState() => _ChartPageState();
}

class _ChartPageState extends State<ChartPage> with TickerProviderStateMixin {
  late final AnimationController _controller;
  late BarTween _tween;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _tween = BarTween(Bar(0), Bar(50));
    _controller.forward();
  }

  void _randomize() {
    setState(() {
      _tween = BarTween(
        _tween.evaluate(_controller), // Start from current visual state
        Bar(100.0 * Random().nextDouble()), // Animate to new random height
      );
      _controller.forward(from: 0);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: CustomPaint(
          size: Size(200, 100),
          painter: BarChartPainter(_tween.animate(_controller).value),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _randomize,
        child: Icon(Icons.refresh),
      ),
    );
  }
}
```

---

## Why this pattern matters

1. **Separation of Concerns**: 
   - `Bar` defines *what* it is and how it interpolates.
   - `BarTween` defines the *path* (0 -> 1).
   - `AnimationController` defines the *timing*.
   - `CustomPainter` handles the *rendering*.

2. **Smooth Transitions**: 
   - By starting the new tween from `_tween.evaluate(_controller)`, we ensure perfectly smooth transitions even if interrupted mid-animation.

3. **Performance**: 
   - `CustomPaint` only repaints the canvas, not the entire widget tree.

See [widget_fundamentals.md](./widget_fundamentals.md) for more on `CustomPaint` and `AnimationController`.
