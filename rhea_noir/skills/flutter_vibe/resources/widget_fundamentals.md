# Flutter Widget Fundamentals

Source: Official Flutter Documentation - Building User Interfaces

## Core Concept

Flutter widgets are built using a React-inspired framework. The central idea:

1. **Build UI from widgets** - Widgets describe the view given current configuration and state
2. **Declarative rebuilds** - When state changes, widgets rebuild their description
3. **Efficient diffing** - Framework diffs against previous description, applies minimal changes to render tree

---

## Widget Types

### StatelessWidget

Use when the widget doesn't manage state. Receives arguments from parent, stores in `final` variables.

```dart
class MyWidget extends StatelessWidget {
  final String title;
  
  const MyWidget({super.key, required this.title});
  
  @override
  Widget build(BuildContext context) {
    return Text(title);
  }
}
```

### StatefulWidget

Use when the widget needs to manage mutable state. Creates a separate `State` object.

```dart
class Counter extends StatefulWidget {
  const Counter({super.key});
  
  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;
  
  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () => setState(() => _count++),
      child: Text('Count: $_count'),
    );
  }
}
```

**Why separate objects?**
- `Widget` = temporary, describes current state presentation
- `State` = persistent between builds, remembers information

---

## Basic Widgets

| Widget | Purpose |
|--------|---------|
| `Text` | Styled text run |
| `Row` | Horizontal flex layout (like CSS flexbox) |
| `Column` | Vertical flex layout |
| `Stack` | Overlay widgets in paint order (like CSS absolute positioning) |
| `Container` | Rectangular visual element with decoration, margins, padding |
| `Expanded` | Fill remaining space in Row/Column |

### Layout Pattern

```dart
Row(
  children: [
    Icon(Icons.star),
    Expanded(child: Text('Title')), // Takes remaining space
    Icon(Icons.menu),
  ],
)
```

---

## Material Components

Start with `MaterialApp` for theme data inheritance:

```dart
MaterialApp(
  home: Scaffold(
    appBar: AppBar(title: Text('My App')),
    body: Center(child: Text('Hello')),
    floatingActionButton: FloatingActionButton(
      onPressed: () {},
      child: Icon(Icons.add),
    ),
  ),
)
```

**pubspec.yaml requirement:**
```yaml
flutter:
  uses-material-design: true
```

> **Note**: For iOS-centric design, use `CupertinoApp` and Cupertino components.

---

## Gesture Handling

### GestureDetector

Detects taps, drags, scales without visual representation:

```dart
GestureDetector(
  onTap: () => print('Tapped!'),
  onLongPress: () => print('Long pressed!'),
  onDoubleTap: () => print('Double tapped!'),
  child: Container(
    color: Colors.blue,
    child: Text('Tap me'),
  ),
)
```

### Built-in Gesture Widgets

- `IconButton` → `onPressed`
- `ElevatedButton` → `onPressed`
- `FloatingActionButton` → `onPressed`
- `InkWell` → `onTap` (with ripple effect)

---

## State Management Patterns

### State Flow

- **Notifications flow UP** via callbacks
- **State flows DOWN** to stateless widgets for presentation

### Lifting State Up

```dart
// Parent holds state
class Parent extends StatefulWidget {
  @override
  State<Parent> createState() => _ParentState();
}

class _ParentState extends State<Parent> {
  int _count = 0;
  
  void _increment() => setState(() => _count++);
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CounterDisplay(count: _count),        // Stateless, receives state
        CounterButton(onPressed: _increment), // Stateless, sends events up
      ],
    );
  }
}

class CounterDisplay extends StatelessWidget {
  final int count;
  const CounterDisplay({super.key, required this.count});
  
  @override
  Widget build(BuildContext context) => Text('$count');
}

class CounterButton extends StatelessWidget {
  final VoidCallback onPressed;
  const CounterButton({super.key, required this.onPressed});
  
  @override
  Widget build(BuildContext context) {
    return ElevatedButton(onPressed: onPressed, child: Text('Increment'));
  }
}
```

---

## Widget Lifecycle

### StatefulWidget Lifecycle

1. `createState()` - Framework creates State object
2. `initState()` - Called once after insertion into tree
3. `build()` - Called whenever state changes
4. `didUpdateWidget(oldWidget)` - Called when parent rebuilds with new widget
5. `dispose()` - Called when removed from tree

```dart
class MyStateful extends StatefulWidget {
  @override
  State<MyStateful> createState() => _MyStatefulState();
}

class _MyStatefulState extends State<MyStateful> {
  @override
  void initState() {
    super.initState(); // Required first
    // Configure animations, subscribe to services
  }
  
  @override
  void didUpdateWidget(MyStateful oldWidget) {
    super.didUpdateWidget(oldWidget);
    // React to parent providing new widget
  }
  
  @override
  void dispose() {
    // Cancel timers, unsubscribe from services
    super.dispose(); // Required last
  }
  
  @override
  Widget build(BuildContext context) => Container();
}
```

---

## Keys

### When to Use Keys

Keys help the framework match widgets during rebuilds. Essential for:
- Lists with dynamic order
- Preserving state when widgets move

### Local Keys (ValueKey, ObjectKey)

Unique among siblings:

```dart
ListView(
  children: items.map((item) => ListTile(
    key: ValueKey(item.id), // Semantic identity
    title: Text(item.name),
  )).toList(),
)
```

### Global Keys

Unique across entire widget hierarchy. Used to access state from outside:

```dart
final _formKey = GlobalKey<FormState>();

Form(
  key: _formKey,
  child: TextFormField(),
)

// Access form state
_formKey.currentState?.validate();
```

---

## Best Practices

### Widget Design

1. **Prefer StatelessWidget** - Use StatefulWidget only when needed
2. **Keep widgets small** - Single responsibility
3. **Use const constructors** - Enables widget reuse

### State Management

1. **Don't modify widget properties directly** - Call parent callbacks instead
2. **Always wrap mutations in setState()** - Framework won't rebuild otherwise
3. **Store state as high as needed, as low as possible**

### Rebuild Efficiency

- Framework compares newly built widgets with previous ones
- Applies only differences to underlying RenderObject
- Creating new widget instances is cheap; actual rendering is optimized

---

## API References

- [StatelessWidget](https://api.flutter.dev/flutter/widgets/StatelessWidget-class.html)
- [StatefulWidget](https://api.flutter.dev/flutter/widgets/StatefulWidget-class.html)
- [State](https://api.flutter.dev/flutter/widgets/State-class.html)
- [Key](https://api.flutter.dev/flutter/foundation/Key-class.html)
- [GlobalKey](https://api.flutter.dev/flutter/widgets/GlobalKey-class.html)
- [GestureDetector](https://api.flutter.dev/flutter/widgets/GestureDetector-class.html)

---

## Widget Catalog

### Design Systems

Flutter ships with two design systems in the SDK:

| System | Description | Use Case |
|--------|-------------|----------|
| **Material 3** | Visual, behavioral, motion-rich widgets | Cross-platform default |
| **Cupertino** | Apple Human Interface Guidelines | iOS/macOS native feel |

**Community Design Systems:**
- [fluent_ui](https://pub.dev/packages/fluent_ui) - Windows Fluent Design
- [macos_ui](https://pub.dev/packages/macos_ui) - macOS native widgets
- [yaru](https://pub.dev/packages/yaru) - Ubuntu design system

### Widget Categories

| Category | Purpose |
|----------|---------|
| **Accessibility** | Screen readers, semantics, focus |
| **Animation & Motion** | Implicit/explicit animations, transitions |
| **Assets, Images, Icons** | Asset management, image display, icon sets |
| **Async** | FutureBuilder, StreamBuilder, async patterns |
| **Basics** | Core widgets every app needs |
| **Input** | Text fields, sliders, checkboxes |
| **Interaction Models** | Gestures, routing, navigation |
| **Layout** | Row, Column, Stack, Grid, Flex |
| **Painting & Effects** | Visual effects without layout changes |
| **Scrolling** | ListView, GridView, CustomScrollView |
| **Styling** | ThemeData, MediaQuery, padding |
| **Text** | Text display and styling |

### Essential Base Widgets

```dart
// Layout
Row, Column, Stack, Wrap, Flow
Expanded, Flexible, Spacer
Container, SizedBox, ConstrainedBox
Padding, Align, Center

// Scrolling
ListView, GridView, CustomScrollView
SingleChildScrollView, PageView
Sliver*, NestedScrollView

// Async
FutureBuilder, StreamBuilder
RefreshIndicator

// Input
TextField, TextFormField
Checkbox, Radio, Switch, Slider

// Images & Assets
Image, Icon, CircleAvatar
AssetImage, NetworkImage

// Painting
DecoratedBox, ClipRRect, ClipOval
Opacity, BackdropFilter, ShaderMask
Transform, CustomPaint
```

---

## Cupertino Widgets (iOS/macOS)

Widgets aligned with Apple's Human Interface Guidelines.

### App Structure

| Widget | Description |
|--------|-------------|
| `CupertinoApp` | Root application widget for Cupertino design |
| `CupertinoPageScaffold` | Basic page layout with nav bar and content |
| `CupertinoTabScaffold` | Tabbed app structure with tab bar |
| `CupertinoTabBar` | iOS-style bottom tab bar |
| `CupertinoTabView` | Content for each tab with parallel navigation |

### Navigation

| Widget | Description |
|--------|-------------|
| `CupertinoNavigationBar` | Top navigation bar (use with CupertinoPageScaffold) |
| `CupertinoSliverNavigationBar` | Large title nav bar (iOS 11 style) |
| `CupertinoNavigationBarBackButton` | Standard back button |
| `CupertinoPageRoute` | iOS-style page transition |
| `CupertinoPageTransition` | Page transition animation |
| `CupertinoFullscreenDialogTransition` | Fullscreen dialog animation |

### Dialogs & Sheets

| Widget | Description |
|--------|-------------|
| `CupertinoAlertDialog` | iOS-style alert dialog |
| `CupertinoDialogAction` | Button in alert dialog |
| `CupertinoActionSheet` | Modal bottom action sheet |
| `CupertinoActionSheetAction` | Button in action sheet |
| `CupertinoContextMenu` | Long-press context menu |
| `CupertinoContextMenuAction` | Button in context menu |
| `CupertinoPopupSurface` | Rounded popup surface |

### Input Controls

| Widget | Description |
|--------|-------------|
| `CupertinoButton` | iOS-style button |
| `CupertinoTextField` | iOS-style text field |
| `CupertinoTextFormFieldRow` | Text field in form row |
| `CupertinoSearchTextField` | iOS search field |
| `CupertinoSwitch` | iOS toggle switch |
| `CupertinoSlider` | iOS range slider |
| `CupertinoCheckBox` | macOS-style checkbox |
| `CupertinoRadio` | macOS-style radio button |
| `CupertinoSlidingSegmentedControl` | iOS 13 segmented control |

### Pickers

| Widget | Description |
|--------|-------------|
| `CupertinoPicker` | iOS wheel picker |
| `CupertinoDatePicker` | Date/time picker |
| `CupertinoTimerPicker` | Countdown timer picker |

### Lists & Forms

| Widget | Description |
|--------|-------------|
| `CupertinoListSection` | iOS-style list container |
| `CupertinoListTile` | iOS-style list row |
| `CupertinoListTileChevron` | Trailing chevron indicator |
| `CupertinoFormSection` | iOS-style form section |
| `CupertinoFormRow` | iOS-style form row |

### Feedback & Indicators

| Widget | Description |
|--------|-------------|
| `CupertinoActivityIndicator` | Circular spinner |
| `CupertinoScrollbar` | iOS-style scrollbar |
| `CupertinoSliverRefreshControl` | Pull-to-refresh control |

### Text Selection

| Widget | Description |
|--------|-------------|
| `CupertinoTextSelectionToolbar` | iOS text selection toolbar |
| `CupertinoTextSelectionToolbarButton` | Toolbar button |
| `CupertinoDesktopTextSelectionToolbar` | macOS text selection |
| `CupertinoMagnifier` | Text magnifier loupe |
| `CupertinoSpellCheckSuggestionsToolbar` | Spell check UI |

### Theming

| Widget | Description |
|--------|-------------|
| `CupertinoTheme` | Applies Cupertino styling |
| `CupertinoThemeData` | Theme configuration |
| `CupertinoTextThemeData` | Typography theme |
| `CupertinoColors` | iOS color palette |
| `CupertinoDynamicColor` | Adaptive colors (light/dark) |

### Usage Example

```dart
CupertinoApp(
  theme: const CupertinoThemeData(
    primaryColor: CupertinoColors.activeBlue,
    brightness: Brightness.dark,
  ),
  home: CupertinoPageScaffold(
    navigationBar: const CupertinoNavigationBar(
      middle: Text('My App'),
    ),
    child: Center(
      child: CupertinoButton.filled(
        onPressed: () {},
        child: const Text('Press Me'),
      ),
    ),
  ),
)
```

---

## Material 3 Widgets

Material 3 is Flutter's default design language (since Flutter 3.16). Visual, behavioral, and motion-rich widgets.

### Actions

| Widget | Description |
|--------|-------------|
| `ElevatedButton` | Primary action button with elevation |
| `FilledButton` | Filled button (Material 3) |
| `FilledButton.tonal` | Tonal filled button |
| `OutlinedButton` | Button with outline border |
| `TextButton` | Flat text button |
| `FloatingActionButton` | Floating icon button for key action |
| `FloatingActionButton.extended` | FAB with text label and icon |
| `IconButton` | Clickable icon for supplementary actions |
| `SegmentedButton` | Single/multi select options in a row |

### Communication

| Widget | Description |
|--------|-------------|
| `Badge` | Notification indicator with count/status |
| `LinearProgressIndicator` | Horizontal loading bar |
| `CircularProgressIndicator` | Circular loading spinner |
| `SnackBar` | Brief message at bottom of screen |

### Containment

| Widget | Description |
|--------|-------------|
| `AlertDialog` | Modal dialog for decisions |
| `SimpleDialog` | Simple choice dialog |
| `BottomSheet` | Supplementary content anchored to bottom |
| `Card` | Rounded container with elevation |
| `Divider` | Thin line separator |
| `ListTile` | Single row with text and icons |
| `ExpansionTile` | Collapsible list tile |
| `ExpansionPanel` | Expandable panel |

### Navigation

| Widget | Description |
|--------|-------------|
| `AppBar` | Top app bar with title and actions |
| `SliverAppBar` | Scrollable/collapsible app bar |
| `BottomAppBar` | Bottom app bar with actions |
| `NavigationBar` | Bottom navigation (Material 3) |
| `NavigationRail` | Side navigation for tablet/desktop |
| `NavigationDrawer` | Slide-out drawer navigation |
| `Drawer` | Basic drawer container |
| `TabBar` | Tab navigation |
| `TabBarView` | Tab content container |

### Selection

| Widget | Description |
|--------|-------------|
| `Checkbox` | Multi-select toggle |
| `CheckboxListTile` | ListTile with checkbox |
| `Radio` | Single-select from group |
| `RadioListTile` | ListTile with radio |
| `Switch` | On/off toggle |
| `SwitchListTile` | ListTile with switch |
| `Slider` | Range value selector |
| `RangeSlider` | Two-thumb range selector |
| `Chip` | Compact element for info/actions |
| `InputChip` | Chip representing user input |
| `FilterChip` | Chip for filtering content |
| `ChoiceChip` | Chip for single selection |
| `ActionChip` | Chip that triggers action |
| `DropdownButton` | Dropdown selection |
| `DropdownMenu` | Material 3 dropdown menu |
| `MenuAnchor` | Anchor for popup menus |
| `PopupMenuButton` | Icon that opens popup menu |

### Pickers

| Widget | Description |
|--------|-------------|
| `showDatePicker` | Date picker dialog |
| `showDateRangePicker` | Date range picker dialog |
| `showTimePicker` | Time picker dialog |
| `CalendarDatePicker` | Inline calendar widget |

### Text Input

| Widget | Description |
|--------|-------------|
| `TextField` | Text input field |
| `TextFormField` | TextField with Form integration |
| `SearchBar` | Material 3 search bar |
| `SearchAnchor` | Search with suggestions |
| `Autocomplete` | Text field with autocomplete |

### Layout & Structure

| Widget | Description |
|--------|-------------|
| `Scaffold` | Basic material page structure |
| `MaterialApp` | Root application widget |
| `Material` | Material design surface |
| `Ink` | Ink splashes for touch feedback |
| `InkWell` | Rectangular touch feedback area |
| `InkResponse` | Circular touch feedback area |

### Usage Example

```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
    colorSchemeSeed: Colors.deepPurple,
    brightness: Brightness.dark,
  ),
  home: Scaffold(
    appBar: AppBar(
      title: const Text('Material 3'),
      actions: [
        IconButton(icon: const Icon(Icons.search), onPressed: () {}),
      ],
    ),
    body: ListView(
      children: [
        ListTile(
          leading: const Icon(Icons.star),
          title: const Text('Item'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {},
        ),
      ],
    ),
    floatingActionButton: FloatingActionButton(
      onPressed: () {},
      child: const Icon(Icons.add),
    ),
    bottomNavigationBar: NavigationBar(
      destinations: const [
        NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
        NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
      ],
    ),
  ),
)
```

---

## Accessibility Widgets

Make your app accessible to screen readers, search engines, and assistive technologies.

| Widget | Description |
|--------|-------------|
| `Semantics` | Annotates widget tree with meaning for accessibility tools |
| `MergeSemantics` | Merges semantics of descendants into single node |
| `ExcludeSemantics` | Hides descendants from accessibility tree |

### Usage Examples

```dart
// Add semantic label to custom widget
Semantics(
  label: 'Play button',
  button: true,
  child: GestureDetector(
    onTap: _play,
    child: CustomPlayIcon(),
  ),
)

// Merge multiple widgets into one semantic node
MergeSemantics(
  child: Row(
    children: [
      Icon(Icons.star),
      Text('Favorite'),
    ],
  ),
)

// Hide decorative elements from screen readers
ExcludeSemantics(
  child: DecorativeBackground(),
)
```

### Accessibility Best Practices

1. **Always label icons** - Use `semanticLabel` on `Icon` or wrap in `Semantics`
2. **44x44 minimum touch targets** - Ensure tappable areas meet size guidelines
3. **Test with TalkBack/VoiceOver** - Use actual screen readers
4. **Support dynamic type** - Respect user's text scaling preferences
5. **Color contrast 4.5:1** - Meet WCAG requirements for text
6. **Exclude decorative elements** - Use `ExcludeSemantics` for visual-only content

---

## Animation & Motion Widgets

### Implicit Animations (Animated*)

Auto-animate when properties change. No controller needed.

| Widget | Animates |
|--------|----------|
| `AnimatedContainer` | Size, color, padding, margin, decoration |
| `AnimatedOpacity` | Opacity (fade in/out) |
| `AnimatedAlign` | Alignment position |
| `AnimatedPositioned` | Position in Stack |
| `AnimatedSize` | Size changes of child |
| `AnimatedDefaultTextStyle` | Text style changes |
| `AnimatedPhysicalModel` | Elevation, shape, color |
| `AnimatedCrossFade` | Cross-fade between two children |
| `AnimatedSwitcher` | Transition between different children |

```dart
// Implicit animation - just change the value
AnimatedContainer(
  duration: const Duration(milliseconds: 300),
  curve: Curves.fastOutSlowIn,
  width: _expanded ? 200 : 100,
  height: _expanded ? 200 : 100,
  color: _expanded ? Colors.blue : Colors.red,
  child: const FlutterLogo(),
)

// Animated opacity
AnimatedOpacity(
  duration: const Duration(milliseconds: 300),
  opacity: _visible ? 1.0 : 0.0,
  child: const Text('Fade me'),
)
```

### Explicit Animations (*Transition)

Controlled by `AnimationController`. More control, more code.

| Widget | Animates |
|--------|----------|
| `FadeTransition` | Opacity |
| `SlideTransition` | Position offset |
| `ScaleTransition` | Scale transform |
| `RotationTransition` | Rotation |
| `SizeTransition` | Size with clipping |
| `AlignTransition` | Alignment |
| `PositionedTransition` | Positioned in Stack |
| `RelativePositionedTransition` | Relative position |
| `DecoratedBoxTransition` | Box decoration |
| `DefaultTextStyleTransition` | Text style |
| `MatrixTransition` | Matrix4 transform |
| `SliverFadeTransition` | Sliver opacity |

```dart
class _MyWidgetState extends State<MyWidget> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _animation = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _animation,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.3),
          end: Offset.zero,
        ).animate(_animation),
        child: const Text('Animated!'),
      ),
    );
  }
}
```

### Hero Animations

Shared element transitions between routes.

```dart
// Source screen
Hero(
  tag: 'avatar-${user.id}',
  child: CircleAvatar(backgroundImage: user.avatar),
)

// Destination screen (same tag)
Hero(
  tag: 'avatar-${user.id}',
  child: Image(image: user.avatar),
)
```

### Animated Lists

```dart
final _listKey = GlobalKey<AnimatedListState>();

AnimatedList(
  key: _listKey,
  initialItemCount: items.length,
  itemBuilder: (context, index, animation) {
    return SlideTransition(
      position: animation.drive(
        Tween(begin: const Offset(1, 0), end: Offset.zero),
      ),
      child: ListTile(title: Text(items[index])),
    );
  },
)

// Insert item with animation
_listKey.currentState?.insertItem(index);

// Remove item with animation
_listKey.currentState?.removeItem(
  index,
  (context, animation) => SizeTransition(
    sizeFactor: animation,
    child: removedItem,
  ),
);
```

### Building Blocks

| Widget/Class | Purpose |
|--------------|---------|
| `AnimatedBuilder` | Rebuild widget when animation changes |
| `AnimatedWidget` | Base class for animated widgets |
| `ImplicitlyAnimatedWidget` | Base class for implicit animations |
| `AnimatedModalBarrier` | Animated modal overlay |
| `AnimationController` | Controls animation timing |
| `Tween` | Interpolates between values |
| `CurvedAnimation` | Applies curve to animation |

---

## Assets, Images & Icons

### Core Widgets

| Widget | Description |
|--------|-------------|
| `Image` | Display images from assets, network, memory, or file |
| `Icon` | Material Design icon |
| `RawImage` | Display dart:ui.Image directly |
| `AssetBundle` | Access resources asynchronously |

### Image Sources

```dart
// From assets (pubspec.yaml must declare asset)
Image.asset('assets/images/logo.png')

// From network
Image.network('https://example.com/image.png')

// From file
Image.file(File('/path/to/image.png'))

// From memory (Uint8List)
Image.memory(bytes)

// With configuration
Image.asset(
  'assets/hero.png',
  width: 200,
  height: 200,
  fit: BoxFit.cover,
  semanticLabel: 'App hero image',
)
```

### Icons

```dart
// Material icon
Icon(Icons.star, size: 24, color: Colors.amber)

// With semantic label for accessibility
Icon(
  Icons.favorite,
  semanticLabel: 'Favorite',
  color: Colors.red,
)

// Cupertino icon
Icon(CupertinoIcons.heart_fill)
```

### Asset Configuration (pubspec.yaml)

```yaml
flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/
  fonts:
    - family: CustomFont
      fonts:
        - asset: assets/fonts/CustomFont-Regular.ttf
        - asset: assets/fonts/CustomFont-Bold.ttf
          weight: 700
```

### Image Caching & Performance

```dart
// Precache images for smoother loading
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(AssetImage('assets/large_image.png'), context);
}

// Use cached_network_image package for network images
CachedNetworkImage(
  imageUrl: 'https://example.com/image.png',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
)
```

---

## Text Widgets

### Core Widgets

| Widget | Description |
|--------|-------------|
| `Text` | Single-style text run |
| `RichText` | Multi-style text using TextSpan tree |
| `DefaultTextStyle` | Inherited text style for descendants |
| `SelectableText` | Text that can be selected/copied |

### Basic Text

```dart
// Simple text
Text('Hello, World!')

// Styled text
Text(
  'Styled Text',
  style: TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: Colors.blue,
    letterSpacing: 1.2,
  ),
)

// Multi-line with overflow
Text(
  'Long text that might overflow...',
  maxLines: 2,
  overflow: TextOverflow.ellipsis,
  textAlign: TextAlign.center,
)
```

### Rich Text (Multiple Styles)

```dart
RichText(
  text: TextSpan(
    style: DefaultTextStyle.of(context).style,
    children: [
      TextSpan(text: 'Hello '),
      TextSpan(
        text: 'World',
        style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue),
      ),
      TextSpan(text: '!'),
    ],
  ),
)

// Or use Text.rich shorthand
Text.rich(
  TextSpan(
    children: [
      TextSpan(text: 'Price: '),
      TextSpan(
        text: '\$99.99',
        style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold),
      ),
    ],
  ),
)
```

### Selectable Text

```dart
SelectableText(
  'This text can be selected and copied',
  style: TextStyle(fontSize: 18),
)

// With custom selection controls
SelectableText(
  'Custom selection',
  showCursor: true,
  cursorColor: Colors.blue,
  cursorWidth: 2,
)
```

### Default Text Style

```dart
// All descendant Text widgets inherit this style
DefaultTextStyle(
  style: TextStyle(
    fontSize: 16,
    color: Colors.grey[800],
    height: 1.5,
  ),
  child: Column(
    children: [
      Text('Inherits default style'),
      Text('Also inherits'),
      Text(
        'Override with explicit style',
        style: TextStyle(color: Colors.red),
      ),
    ],
  ),
)
```

### Google Fonts

```dart
// Using google_fonts package
Text(
  'Custom Font',
  style: GoogleFonts.outfit(
    fontSize: 24,
    fontWeight: FontWeight.bold,
  ),
)

// Set as theme default
ThemeData(
  textTheme: GoogleFonts.interTextTheme(),
)
```

---

## Styling Widgets

### Core Widgets

| Widget | Description |
|--------|-------------|
| `Theme` | Apply theme to descendant widgets |
| `MediaQuery` | Access screen size, orientation, accessibility settings |
| `Padding` | Add space around child widget |

### Theme

```dart
// Apply custom theme to subtree
Theme(
  data: Theme.of(context).copyWith(
    colorScheme: ColorScheme.dark(),
  ),
  child: MyWidget(),
)

// Access theme data
final theme = Theme.of(context);
final primaryColor = theme.colorScheme.primary;
final textTheme = theme.textTheme;

// Full theme configuration
ThemeData(
  useMaterial3: true,
  colorSchemeSeed: Colors.deepPurple,
  brightness: Brightness.dark,
  textTheme: GoogleFonts.interTextTheme(),
  appBarTheme: AppBarTheme(
    elevation: 0,
    centerTitle: true,
  ),
)
```

### MediaQuery

```dart
// Get screen dimensions
final size = MediaQuery.sizeOf(context);  // Efficient, only rebuilds on size change
final width = size.width;
final height = size.height;

// Full MediaQuery data
final mediaQuery = MediaQuery.of(context);
final padding = mediaQuery.padding;        // Safe area insets
final orientation = mediaQuery.orientation;
final textScaler = mediaQuery.textScaler;  // User's text scaling
final platformBrightness = mediaQuery.platformBrightness;

// Responsive layout
Widget build(BuildContext context) {
  final width = MediaQuery.sizeOf(context).width;
  
  if (width > 1200) return DesktopLayout();
  if (width > 600) return TabletLayout();
  return MobileLayout();
}
```

### Padding

```dart
// Uniform padding
Padding(
  padding: EdgeInsets.all(16),
  child: Text('Padded'),
)

// Directional padding
Padding(
  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
  child: Text('Padded'),
)

// Specific sides
Padding(
  padding: EdgeInsets.only(left: 16, top: 8),
  child: Text('Padded'),
)

// Safe area padding (respects notches, home indicator)
SafeArea(
  child: MyContent(),
)

// Sliver padding in scrollable
SliverPadding(
  padding: EdgeInsets.all(16),
  sliver: SliverList(...),
)
```

---

## Scrolling Widgets

### Core Scrollables

| Widget | Description |
|--------|-------------|
| `ListView` | Most common scrollable, linear list |
| `GridView` | 2D grid of items |
| `PageView` | Page-by-page scrolling |
| `SingleChildScrollView` | Scroll a single child |
| `CustomScrollView` | Custom scroll effects with slivers |
| `NestedScrollView` | Nested scrollables with linked positions |

### ListView

```dart
// Simple list
ListView(
  children: [
    ListTile(title: Text('Item 1')),
    ListTile(title: Text('Item 2')),
  ],
)

// Builder (lazy loading, efficient for long lists)
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ListTile(
    title: Text(items[index]),
  ),
)

// Separated (with dividers)
ListView.separated(
  itemCount: items.length,
  itemBuilder: (context, index) => ListTile(title: Text(items[index])),
  separatorBuilder: (context, index) => Divider(),
)
```

### GridView

```dart
// Fixed column count
GridView.count(
  crossAxisCount: 2,
  children: items.map((item) => Card(child: Text(item))).toList(),
)

// Fixed item extent
GridView.extent(
  maxCrossAxisExtent: 200,
  children: items.map((item) => Card(child: Text(item))).toList(),
)

// Builder (lazy loading)
GridView.builder(
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 3,
    crossAxisSpacing: 8,
    mainAxisSpacing: 8,
  ),
  itemCount: items.length,
  itemBuilder: (context, index) => Card(child: Text(items[index])),
)
```

### PageView

```dart
PageView(
  controller: PageController(viewportFraction: 0.8),
  children: [
    Page1(),
    Page2(),
    Page3(),
  ],
)

// Builder
PageView.builder(
  itemCount: pages.length,
  itemBuilder: (context, index) => pages[index],
)
```

### Pull-to-Refresh

```dart
RefreshIndicator(
  onRefresh: () async {
    await fetchData();
  },
  child: ListView.builder(...),
)
```

### Reorderable List

```dart
ReorderableListView(
  onReorder: (oldIndex, newIndex) {
    setState(() {
      if (newIndex > oldIndex) newIndex--;
      final item = items.removeAt(oldIndex);
      items.insert(newIndex, item);
    });
  },
  children: items.map((item) => ListTile(
    key: ValueKey(item.id),
    title: Text(item.name),
  )).toList(),
)
```

### Scrollbar

```dart
Scrollbar(
  thumbVisibility: true,
  child: ListView.builder(...),
)
```

---

## Sliver Widgets

Slivers are scrollable areas that can have custom scroll effects.

### Core Slivers

| Widget | Description |
|--------|-------------|
| `SliverList` | Linear list in CustomScrollView |
| `SliverGrid` | Grid in CustomScrollView |
| `SliverAppBar` | Collapsible/floating app bar |
| `SliverToBoxAdapter` | Single non-sliver widget |
| `SliverPadding` | Padding around sliver |
| `SliverFillRemaining` | Fill remaining viewport |
| `SliverPersistentHeader` | Sticky/pinned header |
| `SliverFixedExtentList` | List with fixed item heights (faster) |

### CustomScrollView

```dart
CustomScrollView(
  slivers: [
    // Collapsible app bar
    SliverAppBar(
      expandedHeight: 200,
      floating: false,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: Text('Title'),
        background: Image.asset('header.png', fit: BoxFit.cover),
      ),
    ),
    
    // Padding
    SliverPadding(
      padding: EdgeInsets.all(16),
      sliver: SliverList(
        delegate: SliverChildBuilderDelegate(
          (context, index) => ListTile(title: Text('Item $index')),
          childCount: 20,
        ),
      ),
    ),
    
    // Grid
    SliverGrid(
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
      ),
      delegate: SliverChildBuilderDelegate(
        (context, index) => Card(child: Text('Grid $index')),
        childCount: 10,
      ),
    ),
    
    // Single widget
    SliverToBoxAdapter(
      child: Container(height: 100, color: Colors.blue),
    ),
    
    // Fill remaining space
    SliverFillRemaining(
      child: Center(child: Text('End of list')),
    ),
  ],
)
```

### SliverAppBar Modes

```dart
// Floating - appears when scrolling up
SliverAppBar(floating: true, pinned: false)

// Pinned - always visible at top
SliverAppBar(floating: false, pinned: true)

// Snap - floating with snap effect
SliverAppBar(floating: true, snap: true)

// Stretch - iOS-style overscroll
SliverAppBar(stretch: true)
```

### Scroll Notifications

```dart
NotificationListener<ScrollNotification>(
  onNotification: (notification) {
    if (notification is ScrollEndNotification) {
      // User stopped scrolling
    }
    if (notification.metrics.pixels == notification.metrics.maxScrollExtent) {
      // Reached bottom - load more
    }
    return false;
  },
  child: ListView.builder(...),
)
```

---

## Painting & Effects Widgets

Apply visual effects without changing layout, size, or position.

### Core Widgets

| Widget | Description |
|--------|-------------|
| `Opacity` | Make child partially transparent |
| `BackdropFilter` | Apply blur/filter to background |
| `Transform` | Apply matrix transformation |
| `RotatedBox` | Rotate by quarter turns |
| `ClipRect` | Clip with rectangle |
| `ClipOval` | Clip with oval/circle |
| `ClipPath` | Clip with custom path |
| `DecoratedBox` | Apply decoration (background, border) |
| `CustomPaint` | Draw custom graphics |
| `FractionalTranslation` | Translate by fraction of size |

### Opacity

```dart
Opacity(
  opacity: 0.5,  // 0.0 = invisible, 1.0 = fully visible
  child: Image.asset('photo.png'),
)

// Animated version
AnimatedOpacity(
  duration: Duration(milliseconds: 300),
  opacity: _visible ? 1.0 : 0.0,
  child: MyWidget(),
)
```

### BackdropFilter (Glassmorphism)

```dart
// Blur background - expensive, use sparingly
BackdropFilter(
  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
  child: Container(
    color: Colors.white.withOpacity(0.2),
    child: Text('Frosted Glass'),
  ),
)

// Glassmorphism card
ClipRRect(
  borderRadius: BorderRadius.circular(16),
  child: BackdropFilter(
    filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
    child: Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: content,
    ),
  ),
)
```

### Transform

```dart
// Rotate
Transform.rotate(
  angle: math.pi / 4,  // 45 degrees
  child: Icon(Icons.arrow_forward),
)

// Scale
Transform.scale(
  scale: 1.5,
  child: Text('Big'),
)

// Translate
Transform.translate(
  offset: Offset(50, 20),
  child: Container(),
)

// Custom matrix
Transform(
  transform: Matrix4.identity()
    ..setEntry(3, 2, 0.001)  // Perspective
    ..rotateX(0.5),
  alignment: Alignment.center,
  child: Card(),
)
```

### Clipping

```dart
// Circular clip
ClipOval(
  child: Image.asset('avatar.png', width: 100, height: 100),
)

// Rounded rectangle
ClipRRect(
  borderRadius: BorderRadius.circular(16),
  child: Image.asset('photo.png'),
)

// Custom path
ClipPath(
  clipper: MyCustomClipper(),
  child: Container(color: Colors.blue),
)

class MyCustomClipper extends CustomClipper<Path> {
  @override
  Path getClip(Size size) {
    final path = Path();
    path.lineTo(0, size.height - 50);
    path.quadraticBezierTo(
      size.width / 2, size.height,
      size.width, size.height - 50,
    );
    path.lineTo(size.width, 0);
    path.close();
    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => false;
}
```

### DecoratedBox

```dart
DecoratedBox(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      colors: [Colors.purple, Colors.blue],
    ),
    borderRadius: BorderRadius.circular(16),
    boxShadow: [
      BoxShadow(
        color: Colors.black26,
        blurRadius: 10,
        offset: Offset(0, 4),
      ),
    ],
  ),
  child: Padding(
    padding: EdgeInsets.all(16),
    child: Text('Decorated'),
  ),
)
```

### CustomPaint

```dart
CustomPaint(
  size: Size(200, 200),
  painter: MyPainter(),
)

class MyPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    canvas.drawCircle(
      Offset(size.width / 2, size.height / 2),
      50,
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

---

## Layout Widgets

### Single-Child Layout

| Widget | Description |
|--------|-------------|
| `Container` | Combines painting, positioning, sizing |
| `Center` | Centers child within itself |
| `Align` | Aligns child with optional sizing |
| `Padding` | Insets child by padding |
| `SizedBox` | Forces specific width/height |
| `ConstrainedBox` | Imposes additional constraints |
| `AspectRatio` | Sizes child to aspect ratio |
| `FittedBox` | Scales child to fit |
| `FractionallySizedBox` | Sizes to fraction of available space |
| `LimitedBox` | Limits size when unconstrained |
| `Expanded` | Expands in Row/Column/Flex |
| `Flexible` | Flexes in Row/Column without forcing fill |
| `IntrinsicWidth` | Sizes to child's intrinsic width |
| `IntrinsicHeight` | Sizes to child's intrinsic height |
| `Baseline` | Positions by child's baseline |
| `Offstage` | Lays out but doesn't paint |
| `OverflowBox` | Allows child to overflow |

### Multi-Child Layout

| Widget | Description |
|--------|-------------|
| `Row` | Horizontal flex layout |
| `Column` | Vertical flex layout |
| `Stack` | Overlay children in paint order |
| `Wrap` | Wraps to next line/column |
| `Flow` | Custom flow layout |
| `Table` | Rows and columns table |
| `ListBody` | Sequential along axis |
| `ListView` | Scrollable linear list |
| `GridView` | Scrollable 2D grid |
| `IndexedStack` | Stack showing single child |
| `LayoutBuilder` | Build based on parent constraints |
| `CustomMultiChildLayout` | Custom delegate positioning |

### Row & Column

```dart
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  crossAxisAlignment: CrossAxisAlignment.center,
  children: [
    Icon(Icons.star),
    Expanded(child: Text('Title')),  // Takes remaining space
    IconButton(icon: Icon(Icons.more), onPressed: () {}),
  ],
)

Column(
  mainAxisSize: MainAxisSize.min,  // Shrink to content
  crossAxisAlignment: CrossAxisAlignment.start,
  children: [
    Text('Header', style: TextStyle(fontWeight: FontWeight.bold)),
    SizedBox(height: 8),
    Text('Description'),
  ],
)
```

### Stack & Positioned

```dart
Stack(
  children: [
    Image.asset('background.png'),
    Positioned(
      bottom: 16,
      right: 16,
      child: FloatingActionButton(onPressed: () {}),
    ),
    Positioned.fill(
      child: Center(child: Text('Overlay')),
    ),
  ],
)
```

### Wrap

```dart
Wrap(
  spacing: 8,        // Horizontal gap
  runSpacing: 8,     // Vertical gap
  children: tags.map((tag) => Chip(label: Text(tag))).toList(),
)
```

### LayoutBuilder (Responsive)

```dart
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 600) {
      return WideLayout();
    }
    return NarrowLayout();
  },
)
```

### Sizing Widgets

```dart
// Fixed size
SizedBox(width: 100, height: 100, child: content)

// Fill available space
SizedBox.expand(child: content)

// Shrink to zero
SizedBox.shrink()

// Constrain within bounds
ConstrainedBox(
  constraints: BoxConstraints(
    minWidth: 100,
    maxWidth: 300,
    minHeight: 50,
    maxHeight: 200,
  ),
  child: content,
)

// Force aspect ratio
AspectRatio(
  aspectRatio: 16 / 9,
  child: Image.asset('video.png'),
)
```

---

## Interaction Widgets

### Touch Interactions

| Widget | Description |
|--------|-------------|
| `GestureDetector` | Detects taps, drags, scales |
| `InkWell` | Material ripple tap effect |
| `Dismissible` | Swipe to dismiss |
| `Draggable` | Drag widget to DragTarget |
| `DragTarget` | Receives dragged widgets |
| `LongPressDraggable` | Long press to start drag |
| `InteractiveViewer` | Pan and zoom |
| `AbsorbPointer` | Prevents subtree from receiving events |
| `IgnorePointer` | Invisible to hit testing |

### GestureDetector

```dart
GestureDetector(
  onTap: () => print('Tap'),
  onDoubleTap: () => print('Double tap'),
  onLongPress: () => print('Long press'),
  onPanUpdate: (details) => print('Pan: ${details.delta}'),
  onScaleUpdate: (details) => print('Scale: ${details.scale}'),
  child: Container(color: Colors.blue),
)
```

### Dismissible (Swipe to Delete)

```dart
Dismissible(
  key: ValueKey(item.id),
  direction: DismissDirection.endToStart,
  background: Container(
    color: Colors.red,
    alignment: Alignment.centerRight,
    padding: EdgeInsets.only(right: 16),
    child: Icon(Icons.delete, color: Colors.white),
  ),
  onDismissed: (direction) {
    removeItem(item);
  },
  child: ListTile(title: Text(item.name)),
)
```

### Drag and Drop

```dart
// Draggable source
Draggable<String>(
  data: 'Hello',
  feedback: Material(
    child: Text('Dragging...', style: TextStyle(fontSize: 20)),
  ),
  childWhenDragging: Opacity(opacity: 0.5, child: card),
  child: card,
)

// Drop target
DragTarget<String>(
  onAcceptWithDetails: (details) {
    print('Dropped: ${details.data}');
  },
  builder: (context, candidateData, rejectedData) {
    return Container(
      color: candidateData.isNotEmpty ? Colors.green : Colors.grey,
      child: Text('Drop here'),
    );
  },
)
```

### InteractiveViewer (Pan/Zoom)

```dart
InteractiveViewer(
  minScale: 0.5,
  maxScale: 4.0,
  child: Image.asset('large_image.png'),
)
```

### Routing

| Widget | Description |
|--------|-------------|
| `Navigator` | Manages route stack |
| `Hero` | Shared element transitions |

```dart
// Push new route
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => DetailPage()),
);

// Pop current route
Navigator.pop(context);

// Named routes
Navigator.pushNamed(context, '/details');

// Replace route
Navigator.pushReplacement(context, newRoute);

// Pop until
Navigator.popUntil(context, (route) => route.isFirst);
```

---

## Input Widgets

### Core Widgets

| Widget | Description |
|--------|-------------|
| `Form` | Container for grouping form fields |
| `FormField` | Single form field with validation |
| `TextFormField` | TextField with Form integration |
| `Autocomplete` | Text input with suggestions |
| `KeyboardListener` | Listen to keyboard events |

### Form with Validation

```dart
final _formKey = GlobalKey<FormState>();

Form(
  key: _formKey,
  child: Column(
    children: [
      TextFormField(
        decoration: InputDecoration(labelText: 'Email'),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter email';
          }
          if (!value.contains('@')) {
            return 'Please enter valid email';
          }
          return null;
        },
      ),
      TextFormField(
        decoration: InputDecoration(labelText: 'Password'),
        obscureText: true,
        validator: (value) {
          if (value == null || value.length < 8) {
            return 'Password must be at least 8 characters';
          }
          return null;
        },
      ),
      ElevatedButton(
        onPressed: () {
          if (_formKey.currentState!.validate()) {
            // Form is valid, submit
            _formKey.currentState!.save();
          }
        },
        child: Text('Submit'),
      ),
    ],
  ),
)
```

### Autocomplete

```dart
Autocomplete<String>(
  optionsBuilder: (textEditingValue) {
    if (textEditingValue.text.isEmpty) {
      return const Iterable<String>.empty();
    }
    return suggestions.where((option) =>
      option.toLowerCase().contains(textEditingValue.text.toLowerCase())
    );
  },
  onSelected: (selection) {
    print('Selected: $selection');
  },
)
```

---

## Basic Widgets (Essential)

Widgets to know before building your first Flutter app:

| Widget | Description |
|--------|-------------|
| `Scaffold` | Basic Material page layout |
| `AppBar` | Top app bar |
| `Container` | Painting, positioning, sizing |
| `Row` | Horizontal layout |
| `Column` | Vertical layout |
| `Text` | Display text |
| `Image` | Display images |
| `Icon` | Material icons |
| `ElevatedButton` | Primary action button |
| `FlutterLogo` | Flutter logo widget |
| `Placeholder` | Placeholder for missing widgets |

---

## Async Widgets

### FutureBuilder

Builds based on Future snapshot:

```dart
FutureBuilder<User>(
  future: fetchUser(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return CircularProgressIndicator();
    }
    
    if (snapshot.hasError) {
      return Text('Error: ${snapshot.error}');
    }
    
    if (!snapshot.hasData) {
      return Text('No data');
    }
    
    final user = snapshot.data!;
    return Text('Hello, ${user.name}');
  },
)
```

### StreamBuilder

Builds based on Stream snapshots:

```dart
StreamBuilder<int>(
  stream: counterStream,
  initialData: 0,
  builder: (context, snapshot) {
    if (snapshot.hasError) {
      return Text('Error: ${snapshot.error}');
    }
    
    switch (snapshot.connectionState) {
      case ConnectionState.none:
        return Text('Not connected');
      case ConnectionState.waiting:
        return Text('Waiting...');
      case ConnectionState.active:
        return Text('Count: ${snapshot.data}');
      case ConnectionState.done:
        return Text('Stream closed');
    }
  },
)
```

### Best Practices

```dart
// ❌ Don't create Future in build
Widget build(BuildContext context) {
  return FutureBuilder(
    future: fetchData(), // Creates new Future every build!
    ...
  );
}

// ✅ Store Future in initState
late Future<Data> _dataFuture;

@override
void initState() {
  super.initState();
  _dataFuture = fetchData();
}

Widget build(BuildContext context) {
  return FutureBuilder(
    future: _dataFuture, // Reuses same Future
    ...
  );
}

// ✅ Or use Riverpod FutureProvider
final dataProvider = FutureProvider((ref) => fetchData());

// In widget
ref.watch(dataProvider).when(
  data: (data) => DataWidget(data),
  loading: () => CircularProgressIndicator(),
  error: (e, st) => ErrorWidget(e),
);
```

---

## Desktop Design Systems

### Yaru Theme (Ubuntu/Linux)

Official Flutter theme and widget suite for Ubuntu/GNOME applications.

**Package:** [yaru](https://pub.dev/packages/yaru)

```yaml
dependencies:
  yaru: ^latest
  yaru_icons: ^latest
```

**Setup:**

```dart
import 'package:yaru/yaru.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return YaruTheme(
      builder: (context, yaru, child) {
        return MaterialApp(
          theme: yaru.theme,
          darkTheme: yaru.darkTheme,
          home: const HomePage(),
        );
      },
    );
  }
}
```

**Yaru Widgets:**

| Widget | Description |
|--------|-------------|
| `YaruMasterDetailPage` | Master-detail layout |
| `YaruNavigationPage` | Navigation rail layout |
| `YaruTabbedPage` | Tabbed page layout |
| `YaruWindowTitleBar` | Custom window title bar |
| `YaruDialogTitleBar` | Dialog title bar |
| `YaruBanner` | Info banner |
| `YaruInfoBox` | Info box container |
| `YaruCheckButton` | Checkbox button |
| `YaruRadioButton` | Radio button |
| `YaruToggleButton` | Toggle button |
| `YaruPopupMenuButton` | Popup menu |

**Yaru Icons:**

```dart
import 'package:yaru_icons/yaru_icons.dart';

Icon(YaruIcons.folder)
Icon(YaruIcons.document)
Icon(YaruIcons.settings)
```

### Other Desktop Design Systems

| Package | Platform | Description |
|---------|----------|-------------|
| [fluent_ui](https://pub.dev/packages/fluent_ui) | Windows | Windows 11 Fluent Design |
| [macos_ui](https://pub.dev/packages/macos_ui) | macOS | macOS native widgets |
| [yaru](https://pub.dev/packages/yaru) | Linux | Ubuntu/GNOME theme |
| [libadwaita](https://pub.dev/packages/libadwaita) | Linux | GTK4/Adwaita theme |

---

### macOS UI (macOS Native)

Comprehensive Flutter widgets implementing macOS design language.

**Package:** [macos_ui](https://pub.dev/packages/macos_ui)

```yaml
dependencies:
  macos_ui: ^latest
```

**App Structure:**

```dart
import 'package:macos_ui/macos_ui.dart';

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MacosApp(
      theme: MacosThemeData.light(),
      darkTheme: MacosThemeData.dark(),
      home: MacosWindow(
        sidebar: Sidebar(
          minWidth: 200,
          builder: (context, scrollController) {
            return SidebarItems(
              currentIndex: 0,
              items: const [
                SidebarItem(label: Text('Home')),
                SidebarItem(label: Text('Settings')),
              ],
              onChanged: (index) {},
            );
          },
        ),
        child: MacosScaffold(
          toolBar: ToolBar(
            title: const Text('My App'),
            actions: [
              ToolBarIconButton(
                label: 'Add',
                icon: const MacosIcon(CupertinoIcons.add),
                onPressed: () {},
              ),
            ],
          ),
          children: [
            ContentArea(builder: (context, scrollController) {
              return const Center(child: Text('Content'));
            }),
          ],
        ),
      ),
    );
  }
}
```

**macOS Layout Widgets:**

| Widget | Description |
|--------|-------------|
| `MacosWindow` | Main app window with sidebar |
| `MacosScaffold` | Page scaffold with toolbar |
| `Sidebar` | Left/right navigation sidebar |
| `SidebarItems` | Sidebar navigation items |
| `ToolBar` | Toolbar with actions |
| `SliverToolBar` | Scrollable toolbar |
| `MacosTabView` | Tabbed page view |
| `MacosListTile` | macOS-style list tile |
| `ContentArea` | Main content area |
| `ResizablePane` | Resizable panel |

**macOS Buttons:**

| Widget | Description |
|--------|-------------|
| `PushButton` | Standard macOS button |
| `MacosCheckbox` | Checkbox (on/off/mixed) |
| `MacosRadioButton` | Radio button |
| `MacosSwitch` | Toggle switch |
| `MacosPopupButton` | Dropdown popup menu |
| `MacosPulldownButton` | Pulldown menu |
| `HelpButton` | Help (?) button |
| `MacosSegmentedControl` | Segmented control |

**macOS Dialogs:**

```dart
// Alert dialog
showMacosAlertDialog(
  context: context,
  builder: (_) => MacosAlertDialog(
    appIcon: FlutterLogo(size: 64),
    title: Text('Alert'),
    message: Text('This is an alert'),
    primaryButton: PushButton(
      controlSize: ControlSize.large,
      child: Text('OK'),
      onPressed: () => Navigator.pop(context),
    ),
  ),
);

// Sheet
showMacosSheet(
  context: context,
  builder: (_) => MySheet(),
);
```

**macOS Fields:**

| Widget | Description |
|--------|-------------|
| `MacosTextField` | Text input field |
| `MacosSearchField` | Search with results |
| `MacosTooltip` | Hover tooltip |

**macOS Indicators:**

| Widget | Description |
|--------|-------------|
| `ProgressCircle` | Circular progress |
| `ProgressBar` | Linear progress bar |
| `CapacityIndicator` | Capacity bar (disk usage) |
| `RatingIndicator` | Star rating |
| `MacosSlider` | Continuous/discrete slider |

**macOS Selectors:**

| Widget | Description |
|--------|-------------|
| `MacosDatePicker` | Date picker (textual/graphical/combined) |
| `MacosTimePicker` | Time picker |
| `MacosColorWell` | Native color picker |

**Modern Window Setup (macOS 10.14.6+):**

```dart
import 'package:macos_window_utils/macos_window_utils.dart';

Future<void> _configureMacosWindowUtils() async {
  const config = MacosWindowUtilsConfig(
    toolbarStyle: NSWindowToolbarStyle.unified,
  );
  await config.apply();
}

void main() async {
  await _configureMacosWindowUtils();
  runApp(const MyApp());
}
```

---

### Fluent UI (Windows)

Unofficial implementation of Windows 11 Fluent Design for Flutter.

**Package:** [fluent_ui](https://pub.dev/packages/fluent_ui)

```yaml
dependencies:
  fluent_ui: ^4.13.0
```

**Setup:**

```dart
import 'package:fluent_ui/fluent_ui.dart';

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return FluentApp(
      theme: FluentThemeData(
        accentColor: Colors.blue,
        brightness: Brightness.light,
      ),
      darkTheme: FluentThemeData(
        accentColor: Colors.blue,
        brightness: Brightness.dark,
      ),
      home: const HomePage(),
    );
  }
}
```

**Navigation View (Sidebar + Content):**

```dart
NavigationView(
  appBar: NavigationAppBar(
    title: Text('My App'),
    automaticallyImplyLeading: false,
  ),
  pane: NavigationPane(
    selected: _index,
    onChanged: (i) => setState(() => _index = i),
    displayMode: PaneDisplayMode.auto,
    items: [
      PaneItem(
        icon: Icon(FluentIcons.home),
        title: Text('Home'),
        body: HomePage(),
      ),
      PaneItem(
        icon: Icon(FluentIcons.settings),
        title: Text('Settings'),
        body: SettingsPage(),
      ),
    ],
  ),
)
```

**Fluent UI Widgets:**

| Widget | Description |
|--------|-------------|
| `NavigationView` | Main app layout with pane |
| `NavigationPane` | Side/top navigation |
| `PaneItem` | Navigation item |
| `ScaffoldPage` | Page scaffold |
| `CommandBar` | Toolbar with actions |
| `ContentDialog` | Modal dialog |
| `Flyout` | Popup flyout |
| `InfoBar` | Info/warning/error banner |
| `Expander` | Expandable section |
| `TreeView` | Hierarchical tree |

**Fluent Buttons:**

| Widget | Description |
|--------|-------------|
| `Button` | Standard button |
| `FilledButton` | Filled accent button |
| `OutlinedButton` | Outlined button |
| `HyperlinkButton` | Text link button |
| `IconButton` | Icon-only button |
| `ToggleButton` | Toggle on/off |
| `DropDownButton` | Button with dropdown |
| `SplitButton` | Split action button |

**Fluent Form Controls:**

| Widget | Description |
|--------|-------------|
| `TextBox` | Text input |
| `PasswordBox` | Password input |
| `AutoSuggestBox` | Autocomplete input |
| `ComboBox` | Dropdown selection |
| `Checkbox` | Checkbox toggle |
| `RadioButton` | Radio selection |
| `ToggleSwitch` | Toggle switch |
| `Slider` | Value slider |
| `RatingBar` | Star rating |
| `DatePicker` | Date selection |
| `TimePicker` | Time selection |
| `NumberBox` | Numeric input |

**System Accent Color:**

```dart
import 'package:system_theme/system_theme.dart';

FluentThemeData(
  accentColor: SystemTheme.accentColor.accent.toAccentColor(),
)
```

**Localization:** Supports 30+ languages out of the box including English, German, French, Spanish, Chinese, Japanese, Korean, Arabic, and more.

---

## Layout Guide (Official)

### Core Concept

In Flutter, almost everything is a widget—even layout models. You create layouts by composing widgets to build more complex widgets.

### Laying Out a Widget

1. **Select a layout widget** (Center, Container, Row, Column)
2. **Create a visible widget** (Text, Image, Icon)
3. **Add visible widget to layout widget** (via `child` or `children`)
4. **Add layout widget to page** (in `build()` method)

```dart
Center(
  child: Text('Hello World'),
)
```

### Row & Column Alignment

**Main Axis:** Direction of layout (horizontal for Row, vertical for Column)
**Cross Axis:** Perpendicular to main axis

```dart
Row(
  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
  crossAxisAlignment: CrossAxisAlignment.center,
  children: [
    Image.asset('images/pic1.jpg'),
    Image.asset('images/pic2.jpg'),
    Image.asset('images/pic3.jpg'),
  ],
)
```

**MainAxisAlignment options:**
- `start` - Pack at start
- `end` - Pack at end
- `center` - Pack at center
- `spaceBetween` - Even space between children
- `spaceAround` - Even space around children
- `spaceEvenly` - Even space between, before, and after

### Sizing with Expanded

```dart
Row(
  children: [
    Expanded(child: Image.asset('pic1.jpg')),      // 1x space
    Expanded(flex: 2, child: Image.asset('pic2.jpg')), // 2x space
    Expanded(child: Image.asset('pic3.jpg')),      // 1x space
  ],
)
```

### Packing Widgets

```dart
Row(
  mainAxisSize: MainAxisSize.min,  // Shrink to fit content
  children: [
    Icon(Icons.star),
    Icon(Icons.star),
    Icon(Icons.star),
  ],
)
```

### Nesting Rows and Columns

```dart
Column(
  children: [
    Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [stars, Text('170 Reviews')],
    ),
    Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        Column(children: [Icon(Icons.kitchen), Text('PREP:'), Text('25 min')]),
        Column(children: [Icon(Icons.timer), Text('COOK:'), Text('1 hr')]),
        Column(children: [Icon(Icons.restaurant), Text('FEEDS:'), Text('4-6')]),
      ],
    ),
  ],
)
```

### Container Patterns

```dart
// Decorations
Container(
  decoration: BoxDecoration(
    color: Colors.black26,
    border: Border.all(width: 10, color: Colors.black38),
    borderRadius: BorderRadius.all(Radius.circular(8)),
  ),
  margin: EdgeInsets.all(4),
  padding: EdgeInsets.all(16),
  child: content,
)
```

### GridView

```dart
// Fixed column count
GridView.count(
  crossAxisCount: 2,
  children: [...],
)

// Max tile width
GridView.extent(
  maxCrossAxisExtent: 150,
  padding: EdgeInsets.all(4),
  mainAxisSpacing: 4,
  crossAxisSpacing: 4,
  children: [...],
)
```

### ListView

```dart
ListView(
  children: [
    ListTile(
      leading: Icon(Icons.theaters),
      title: Text('CineArts'),
      subtitle: Text('85 W Portal Ave'),
    ),
    Divider(),
    ListTile(
      leading: Icon(Icons.restaurant),
      title: Text('K\'s Kitchen'),
      subtitle: Text('757 Monterey Blvd'),
    ),
  ],
)
```

### Stack (Overlays)

```dart
Stack(
  alignment: Alignment(0.6, 0.6),
  children: [
    CircleAvatar(
      backgroundImage: AssetImage('images/pic.jpg'),
      radius: 100,
    ),
    Container(
      decoration: BoxDecoration(color: Colors.black45),
      child: Text('Label', style: TextStyle(color: Colors.white)),
    ),
  ],
)
```

### Card

```dart
SizedBox(
  height: 210,
  child: Card(
    elevation: 4,
    child: Column(
      children: [
        ListTile(
          leading: Icon(Icons.restaurant_menu),
          title: Text('Restaurant Name'),
          subtitle: Text('Address'),
        ),
        Divider(),
        ListTile(
          leading: Icon(Icons.phone),
          title: Text('(408) 555-1212'),
        ),
      ],
    ),
  ),
)
```

### Layout Decision Guide

| Need | Use |
|------|-----|
| Single child centered | `Center` |
| Single child with decoration | `Container` |
| Horizontal layout | `Row` |
| Vertical layout | `Column` |
| Overlapping widgets | `Stack` |
| Scrollable list | `ListView` |
| Scrollable grid | `GridView` |
| Constrain size | `SizedBox`, `ConstrainedBox` |
| Fill available space | `Expanded` |
| Flexible but don't force fill | `Flexible` |
| Wrap to next line | `Wrap` |

---

## Cookbook: Lists

### Basic ListView

```dart
ListView(
  children: const [
    ListTile(leading: Icon(Icons.map), title: Text('Map')),
    ListTile(leading: Icon(Icons.photo_album), title: Text('Album')),
    ListTile(leading: Icon(Icons.phone), title: Text('Phone')),
  ],
)
```

### Horizontal ListView

```dart
ListView(
  scrollDirection: Axis.horizontal,
  children: [
    for (final color in Colors.primaries)
      Container(width: 160, color: color),
  ],
)
```

### GridView

```dart
GridView.count(
  crossAxisCount: 2,  // 2 columns
  children: List.generate(100, (index) {
    return Center(
      child: Text('Item $index'),
    );
  }),
)
```

### Lists with Different Item Types

```dart
// 1. Define item types
abstract class ListItem {
  Widget buildTitle(BuildContext context);
  Widget buildSubtitle(BuildContext context);
}

class HeadingItem implements ListItem {
  final String heading;
  HeadingItem(this.heading);
  
  @override
  Widget buildTitle(BuildContext context) =>
    Text(heading, style: Theme.of(context).textTheme.headlineSmall);
  @override
  Widget buildSubtitle(BuildContext context) => const SizedBox.shrink();
}

class MessageItem implements ListItem {
  final String sender;
  final String body;
  MessageItem(this.sender, this.body);
  
  @override
  Widget buildTitle(BuildContext context) => Text(sender);
  @override
  Widget buildSubtitle(BuildContext context) => Text(body);
}

// 2. Generate items
final items = List<ListItem>.generate(
  1000,
  (i) => i % 6 == 0
      ? HeadingItem('Heading $i')
      : MessageItem('Sender $i', 'Message body $i'),
);

// 3. Build with ListView.builder
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    final item = items[index];
    return ListTile(
      title: item.buildTitle(context),
      subtitle: item.buildSubtitle(context),
    );
  },
)
```

### Spaced Items (Responsive + Scrollable)

When items should space evenly but also scroll if needed:

```dart
LayoutBuilder(
  builder: (context, constraints) {
    return SingleChildScrollView(
      child: ConstrainedBox(
        constraints: BoxConstraints(minHeight: constraints.maxHeight),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            ItemWidget(text: 'Item 1'),
            ItemWidget(text: 'Item 2'),
            ItemWidget(text: 'Item 3'),
          ],
        ),
      ),
    );
  },
)
```

**With Spacer/Expanded (use IntrinsicHeight):**

```dart
LayoutBuilder(
  builder: (context, constraints) {
    return SingleChildScrollView(
      child: ConstrainedBox(
        constraints: BoxConstraints(minHeight: constraints.maxHeight),
        child: IntrinsicHeight(
          child: Column(
            children: [
              ItemWidget(text: 'Item 1'),
              Spacer(),
              ItemWidget(text: 'Item 2'),
              Expanded(child: ItemWidget(text: 'Item 3')),
            ],
          ),
        ),
      ),
    );
  },
)
```

### Long/Infinite Lists (ListView.builder)

For large lists, use `ListView.builder` for lazy loading:

```dart
final items = List<String>.generate(10000, (i) => 'Item $i');

ListView.builder(
  itemCount: items.length,
  prototypeItem: ListTile(title: Text(items.first)),  // More efficient
  itemBuilder: (context, index) {
    return ListTile(title: Text(items[index]));
  },
)
```

**Item Extent (Performance):**

| Property | Use When |
|----------|----------|
| `prototypeItem` | Fixed size items (provide example item) |
| `itemExtent` | Fixed pixel height (e.g., `itemExtent: 56`) |
| `itemExtentBuilder` | Variable sizes known in advance |

---

## Cookbook: Scrolling

### Basic Scrolling Widgets

| Widget | Use For |
|--------|---------|
| `SingleChildScrollView` | Scroll single child |
| `ListView` | Vertical scrollable list |
| `GridView` | Scrollable grid |
| `PageView` | Page-by-page scrolling |

### Specialized Scrolling

| Widget | Use For |
|--------|---------|
| `DraggableScrollableSheet` | Draggable bottom sheet |
| `ListWheelScrollView` | Wheel/picker style scroll |
| `CustomScrollView` | Fancy effects with slivers |

### Sliver Scrolling (Fancy Effects)

For elastic scrolling, parallax, shrinking headers:

```dart
CustomScrollView(
  slivers: [
    SliverAppBar(
      expandedHeight: 200,
      floating: true,
      pinned: true,
      flexibleSpace: FlexibleSpaceBar(
        title: Text('Title'),
        background: Image.asset('header.jpg', fit: BoxFit.cover),
      ),
    ),
    SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) => ListTile(title: Text('Item $index')),
        childCount: 100,
      ),
    ),
  ],
)
```

### Nested Scrolling (ShrinkWrap vs Slivers)

❌ **Don't use `shrinkWrap: true`** for performance-critical nested lists.

✅ **Use slivers** for nested scrolling:

```dart
CustomScrollView(
  slivers: [
    SliverToBoxAdapter(child: Header()),
    SliverList(...),  // Better than shrinkWrap ListView
    SliverGrid(...),
  ],
)
```

### Scrolling Parallax Effect

Create a parallax effect where background images move slower than the list:

```dart
// Usage: ParallaxListItem(imageUrl: '...')
class ParallaxListItem extends StatelessWidget {
  final String imageUrl;
  final GlobalKey _backgroundImageKey = GlobalKey();

  ParallaxListItem({required this.imageUrl});

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 16 / 9,
      child: Flow(
        delegate: ParallaxFlowDelegate(
          scrollable: Scrollable.of(context),
          listItemContext: context,
          backgroundImageKey: _backgroundImageKey,
        ),
        children: [
          Image.network(imageUrl, key: _backgroundImageKey, fit: BoxFit.cover),
        ],
      ),
    );
  }
}

class ParallaxFlowDelegate extends FlowDelegate {
  final ScrollableState scrollable;
  final BuildContext listItemContext;
  final GlobalKey backgroundImageKey;

  ParallaxFlowDelegate({
    required this.scrollable,
    required this.listItemContext,
    required this.backgroundImageKey,
  }) : super(repaint: scrollable.position);

  @override
  BoxConstraints getConstraintsForChild(int i, BoxConstraints constraints) {
    return BoxConstraints.tightFor(width: constraints.maxWidth);
  }

  @override
  void paintChildren(FlowPaintingContext context) {
    // Calculate scroll offset
    final scrollableBox = scrollable.context.findRenderObject() as RenderBox;
    final listItemBox = listItemContext.findRenderObject() as RenderBox;
    final listItemOffset = listItemBox.localToGlobal(
      listItemBox.size.centerLeft(Offset.zero),
      ancestor: scrollableBox,
    );
    
    // Determine scroll fraction (0.0 to 1.0)
    final viewportDimension = scrollable.position.viewportDimension;
    final scrollFraction = (listItemOffset.dy / viewportDimension).clamp(0.0, 1.0);
    
    // Calculate alignment (0.0 -> top, 1.0 -> bottom)
    final verticalAlignment = Alignment(0.0, scrollFraction * 2 - 1);
    
    // Paint child
    final backgroundSize = (backgroundImageKey.currentContext!.findRenderObject() as RenderBox).size;
    final listItemSize = context.size;
    final childRect = verticalAlignment.inscribe(backgroundSize, Offset.zero & listItemSize);
    
    context.paintChild(
      0,
      transform: Transform.translate(offset: Offset(0.0, childRect.top)).transform,
    );
  }

  @override
  bool shouldRepaint(ParallaxFlowDelegate oldDelegate) {
    return scrollable != oldDelegate.scrollable ||
        listItemContext != oldDelegate.listItemContext ||
        backgroundImageKey != oldDelegate.backgroundImageKey;
  }
}
```

### Floating AppBar (SliverAppBar)

Place a floating app bar above a list using `CustomScrollView` and `SliverAppBar`.

```dart
Scaffold(
  body: CustomScrollView(
    slivers: [
      SliverAppBar(
        title: Text('Floating App Bar'),
        floating: true,  // Float when scrolling up
        pinned: true,    // Pin at top when collapsed
        snap: true,      // Snap into view
        expandedHeight: 200,
        flexibleSpace: FlexibleSpaceBar(
          background: Image.asset('header.png', fit: BoxFit.cover),
        ),
      ),
      SliverList(
        delegate: SliverChildBuilderDelegate(
          (context, index) => ListTile(title: Text('Item #$index')),
          childCount: 50,
        ),
      ),
    ],
  ),
)
```

---

## Cookbook: Flutter for Web Developers

### Common Layout Mappings

| CSS Property | Flutter Equivalent |
|--------------|--------------------|
| `background-color` | `Container(color:)` or `BoxDecoration(color:)` |
| `display: flex` | `Row` / `Column` |
| `justify-content` | `mainAxisAlignment` |
| `align-items` | `crossAxisAlignment` |
| `position: absolute` | `Stack(children: [Positioned(...)])` |
| `border-radius` | `BoxDecoration(borderRadius:)` |
| `box-shadow` | `BoxDecoration(boxShadow:)` |
| `transform: rotate` | `Transform.rotate` |
| `transform: scale` | `Transform.scale` |

### Styling & Alignment

**HTML/CSS:**
```css
.grey-box {
  background-color: #e0e0e0;
  width: 320px;
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

**Flutter:**
```dart
Container(
  width: 320,
  height: 240,
  color: Colors.grey[300],
  child: Center(  // Centers content (like flex + justify/align center)
    child: Text('Lorem ipsum'),
  ),
)
```

### Absolute Positioning

**HTML/CSS:**
```css
.parent { position: relative; }
.child { position: absolute; top: 24px; left: 24px; }
```

**Flutter:**
```dart
Stack(
  children: [
    Positioned(
      top: 24,
      left: 24,
      child: Container(child: Text('Absolute')),
    ),
  ],
)
```

### Linear Gradient

**HTML/CSS:**
```css
background: linear-gradient(180deg, #ef5350, rgba(0,0,0,0));
```

**Flutter:**
```dart
Container(
  decoration: BoxDecoration(
    gradient: LinearGradient(
      begin: Alignment.topCenter,
      end: Alignment.bottomCenter,
      colors: [Colors.red[400]!, Colors.transparent],
    ),
  ),
)
```

### Rounded Corners & Shadows

**HTML/CSS:**
```css
border-radius: 8px;
box-shadow: 0 2px 4px rgba(0,0,0,0.8);
```

**Flutter:**
```dart
Container(
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(8),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withOpacity(0.8),
        offset: Offset(0, 2),
        blurRadius: 4,
      ),
    ],
  ),
)
```
