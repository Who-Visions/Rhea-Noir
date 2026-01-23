# Adaptive Design & App Fundamentals

This guide covers adaptive design principles (responsive layouts, large screens, foldables) and core application lifecycle concepts.

---

## 1. Adaptive Design: General Approach

**Goal:** Create apps that fit the space (responsive) and are usable in that space (adaptive).

### The 3-Step Strategy

1.  **Abstract**: Identify widgets to make dynamic (navigation, dialogs). Extract shared data (e.g., `List<Destination>`).
2.  **Measure**: Determine available space.
    *   **`MediaQuery.sizeOf(context)`**: Use for full-screen decisions (e.g., "Phone vs. Tablet" navigation). Efficient; avoids full rebuilds unlike `.of`.
    *   **`LayoutBuilder`**: Use for local component sizing (e.g., "List vs. Grid" inside a flexible pane).
3.  **Branch**: Select UI based on breakpoints (e.g., `< 600px` → BottomNav, `>= 600px` → NavRail).

### Measuring Screen Size

**Option A: Global Window Size**
```dart
final size = MediaQuery.sizeOf(context);
if (size.width < 600) {
  // Mobile layout
} else {
  // Tablet/Desktop layout
}
```

**Option B: Local Constraints**
```dart
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 800) {
      return WideWidget();
    } else {
      return NarrowWidget();
    }
  },
)
```

### Common Breakpoints (Material 3)

| Width | Device Class | Navigation |
|-------|--------------|------------|
| < 600 | Compact (Phone) | Bottom Navigation Bar |
| 600 - 840 | Medium (Tablet) | Navigation Rail |
| > 840 | Expanded (Desktop) | Navigation Drawer |

---

## 2. SafeArea & MediaQuery

### SafeArea
Avoids OS intrusions (notches, status bars, home indicators).

```dart
Scaffold(
  body: SafeArea(
    child: MyContent(),
  ),
)
```

*   **Properties**: `top`, `bottom`, `left`, `right` (defaults to `true`).
*   **Tip**: `Scaffold` app bars and bottom nav bars handle safe areas automatically. Use `SafeArea` for the `body`.

### MediaQuery Data

Access device metrics:
*   `sizeOf(context)`: Screen dimensions.
*   `paddingOf(context)`: Safe area insets (physical notch size).
*   `orientationOf(context)`: Portrait vs Landscape.
*   `textScaleFactorOf(context)`: User's font size preference.

---

## 3. Large Screens & Foldables

### Why Large Screens Matter
- **Engagement**: Better use of space = longer sessions.
- **Store Visibility**: App Stores rate apps based on large screen support.
- **iPad**: Necessary for App Store acceptance.

### Layout Strategy: GridView vs ListView
**Problem**: Phone layouts (ListView) look stretched and empty on tablets.

**Solution**: Use `GridView` or `Wrap` to reflow content.

**Adaptive Grid Delegate**:
Instead of hardcoding column counts, use max extent or constraints.

```dart
GridView.builder(
  gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
    maxCrossAxisExtent: 200, // Items won't exceed 200px width
    childAspectRatio: 3 / 2,
    crossAxisSpacing: 20,
    mainAxisSpacing: 20,
  ),
  itemBuilder: (context, index) => Card(...),
)
```

**Alternative: Constrained Width**
Wrap content in a centered column with max width constraints.

```dart
Center(
  child: ConstrainedBox(
    constraints: BoxConstraints(maxWidth: 840), // Material 3 recommended width
    child: ListView(...),
  ),
)
```

### Foldables & Letterboxing
**Problem**: App is letterboxed on foldables when unfolded.
**Cause**: Portrait-locked apps (`setPreferredOrientations`) don't receive new window sizes.
**Fix**:
1. Support all orientations.
2. Use `MediaQuery.displayFeatures` to detect hinges/folds.

**Physical Display Metrics (Flutter 3.13+)**:
Use `View.of(context).display` to get physical pixel size/refresh rate, regardless of window size.

```dart
final display = View.of(context).display;
print('Physical size: ${display.size}');
print('Refresh rate: ${display.refreshRate}');
```

---

---

## 5. User Input & Accessibility

### Adaptive Input
A truly adaptive app handles more than just touch.

*   **Scroll Wheel**: Works by default with `ListView`/`SingleChildScrollView`. For custom scrolling, use `Listener` -> `PointerScrollEvent`.
*   **Mouse Cursors**: Use `MouseRegion(cursor: SystemMouseCursors.click)` for interactive elements.
*   **Hover Effects**: Use `InkWell(onHover: ...)` or `MouseRegion` for custom hover states.

### Keyboard Navigation & Shortcuts
*   **Focus**: Use `FocusableActionDetector` to handle focus + hover + shortcuts together.
*   **Traversal**: `FocusTraversalGroup` controls tab order.
*   **Shortcuts**:
    ```dart
    Shortcuts(
      shortcuts: {
        SingleActivator(LogicalKeyboardKey.keyN, control: true): CreateNewItemIntent(),
      },
      child: Actions(
        actions: {
          CreateNewItemIntent: CallbackAction(onInvoke: (_) => _newItem()),
        },
        child: Focus(autofocus: true, child: ...),
      ),
    )
    ```

### Visual Density
Adjust touch targets for different devices using `VisualDensity`.

```dart
// main.dart
ThemeData(
  visualDensity: VisualDensity.adaptivePlatformDensity, // or custom
)
```

---

## 6. Capabilities & Policies

Distinguish between what a device *can* do (Capability) and what it *should* do (Policy).

**Bad Pattern**:
```dart
if (Platform.isIOS) { ... } // Fragile checks scattered everywhere
```

**Good Pattern (Policy Class)**:
```dart
class Policy {
  bool get shouldAllowPurchaseClick => !Platform.isIOS; // Centralized rule
}

class Capabilities {
  bool get hasCamera => true; // Could be async check
}
```

---

## 7. Automatic Platform Adaptations

Flutter adapts behavior automatically based on the platform (`Theme.of(context).platform`).

### Built-in Adaptations
*   **Scrolling**:
    *   **iOS**: Bouncy overscroll, no scrollbars by default, momentum.
    *   **Android**: Glow overscroll, visible scrollbars.
*   **Navigation**:
    *   **iOS**: Slide from right (LTR) or left (RTL). Edge swipe to go back.
    *   **Android**: Zoom fade/upwards transition. System back button pops route.
*   **Typography**:
    *   **iOS**: San Francisco (via Cupertino package).
    *   **Android**: Roboto (via Material package).
*   **Interactions**:
    *   **Haptics**: Select/Toggle feedback varies.
    *   **Text Editing**: Cursor movement, selection toolbar style (iOS vs Android), press-and-hold behavior.

### Adaptive Widgets
Use `.adaptive` constructors to automatically switch implementations.

| Component | Constructor | Android Render | iOS Render |
|-----------|-------------|----------------|------------|
| Switch | `Switch.adaptive` | Material Switch | Cupertino Switch |
| Slider | `Slider.adaptive` | Material Slider | Cupertino Slider |
| Loader | `CircularProgressIndicator.adaptive` | Spinner | UIActivityIndicator |
| Checkbox | `Checkbox.adaptive` | Material Checkbox | Cupertino Checkbox |
| Radio | `Radio.adaptive` | Material Radio | Cupertino Radio |
| Dialog | `AlertDialog.adaptive` | Material Dialog | Cupertino Dialog |

### Manual Adaptation Patterns

**Navigation Bars**:
```dart
Widget buildNavBar() {
  return Platform.isIOS
    ? CupertinoTabBar(items: ...)
    : NavigationBar(destinations: ...);
}
```

**Text Fields**:
---

## 8. Best Practices for Adaptive Design

### Design Strategy
1.  **Break Down Widgets**: Smaller widgets are easier to refactor and reuse across layouts.
2.  **Touch First**: Polish the touch experience first, then add density and mouse/keyboard accelerators.
3.  **Unique Strengths**: Don't just adapt layout—adapt features. (e.g., Camera on mobile vs Drag-and-drop on desktop).

### Implementation
1.  **Avoid Orientation Locking**:
    *   Phones split-screen, foldables, and tablets need rotation.
    *   Avoid reading `MediaQuery.orientation` for layout branching—use size breakpoints instead.

2.  **Don't Rely on Hardware Types**:
    *   Bad: `if (isPhone) ...`
    *   Good: `if (width < 600) ...`
    *   Checking device type fails on resizeable windows (ChromeOS/Desktop).

3.  **State Restoration**:
    *   Use `PageStorageKey` to save scroll positions during layout shifts.
    *   Ensure state survives rotation/window resizing (`StatefulWidget` or State Management).

### Checklist
- [ ] Responsive layout (e.g., GridView on large screens)
- [ ] Safe Area handling
- [ ] Adaptive input (Mouse/Keyboard support)
- [ ] Platform-specific adaptations (Navigation/Typography)
---

## 9. Additional Resources

### Example Apps
*   **[Wonderous](https://github.com/gskinnerTeam/flutter-wonderous-app)**: Showcase of adaptive/responsive design.
*   **[Flutter Adaptive Demo](https://github.com/flutter/samples/tree/main/experimental/adaptive_scaffold)**: Official scaffold samples.

### Guidelines
*   [Android Large Screen Guidelines](https://developer.android.com/guide/topics/large-screens/large-screen-quality)
*   [Material Design for Large Screens](https://m3.material.io/foundations/adaptive-design/large-screens/overview)
*   [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines)
*   [Microsoft Responsive Design](https://learn.microsoft.com/en-us/windows/apps/design/layout/responsive-design)



```dart
class AppLifecycleObserver extends StatefulWidget {
  @override
  _AppLifecycleObserverState createState() => _AppLifecycleObserverState();
}

class _AppLifecycleObserverState extends State<AppLifecycleObserver> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
     print('App state: $state');
     // resumed, inactive, paused, detached
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
```

### Orientation Locking
Avoid locking orientation unless necessary (`SystemChrome.setPreferredOrientations`). Prefer adaptive layouts.

---

## 5. Input & Accessibility

### Accessibility (Semantics)
Flutter builds a Semantics Tree for screen readers (TalkBack/VoiceOver).

*   **`Semantics` widget**: Annotate widgets with labels/actions.
*   **`ExcludeSemantics`**: Hide decorative elements.
*   **`MergeSemantics`**: Combine children into one focusable node.

```dart
Semantics(
  label: 'Settings',
  button: true,
  onTap: () => openSettings(),
  child: Icon(Icons.settings),
)
```

### Adaptive Inputs
*   **Touch**: Ripples, large targets (48x48dp min).
*   **Mouse**: Hover states, scroll wheels, right-click.
*   **Keyboard**: Tab navigation (FocusNodes), shortcuts.

---

## Resources for Adaptive Apps

*   [Flutter Adaptive Scaffolds](https://pub.dev/packages/flutter_adaptive_scaffold): Official package for adaptive layouts.
*   [Material 3 Adaptive Design](https://m3.material.io/foundations/adaptive-design/overview): Canonical design guidance.
