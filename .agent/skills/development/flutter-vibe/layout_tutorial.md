# Flutter Layout Tutorial

For complete widget reference, see [widget_fundamentals.md](./widget_fundamentals.md).

---

## Building Layouts Step-by-Step

### 1. Diagram the Layout First

Before coding, ask:
- Can you identify the rows and columns?
- Does the layout include a grid?
- Are there overlapping elements?
- Does the UI need tabs?
- What needs alignment, padding, or borders?

**Tip:** Create one widget for each part of your layout. Flutter redraws only what changes.

---

## Example: Lake App Layout

### Layout Breakdown

```
┌─────────────────────────────────────┐
│  ImageSection (image)               │
├─────────────────────────────────────┤
│  TitleSection (row)                 │
│  ┌─────────────────────┬───────────┐│
│  │ Column (text x2)    │ ★ 41     ││
│  └─────────────────────┴───────────┘│
├─────────────────────────────────────┤
│  ButtonSection (row)                │
│  ┌─────────┬─────────┬─────────────┐│
│  │  CALL   │  ROUTE  │   SHARE    ││
│  │  icon   │  icon   │   icon     ││
│  └─────────┴─────────┴─────────────┘│
├─────────────────────────────────────┤
│  TextSection (description)          │
└─────────────────────────────────────┘
```

---

### Step 1: App Base

```dart
import 'package:flutter/material.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Layout Demo',
      home: Scaffold(
        appBar: AppBar(title: const Text('Flutter Layout Demo')),
        body: const SingleChildScrollView(
          child: Column(
            children: [
              // Add sections here
            ],
          ),
        ),
      ),
    );
  }
}
```

---

### Step 2: Image Section

```dart
class ImageSection extends StatelessWidget {
  const ImageSection({super.key, required this.image});

  final String image;

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      image,
      width: 600,
      height: 240,
      fit: BoxFit.cover,
    );
  }
}
```

**pubspec.yaml:**
```yaml
flutter:
  assets:
    - images/lake.jpg
```

---

### Step 3: Title Section

```dart
class TitleSection extends StatelessWidget {
  const TitleSection({
    super.key,
    required this.name,
    required this.location,
  });

  final String name;
  final String location;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    name,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Text(
                  location,
                  style: TextStyle(color: Colors.grey[500]),
                ),
              ],
            ),
          ),
          Icon(Icons.star, color: Colors.red[500]),
          const Text('41'),
        ],
      ),
    );
  }
}
```

**Key patterns:**
- `Expanded` to use remaining space
- `crossAxisAlignment: CrossAxisAlignment.start` for left alignment
- `Padding` for spacing between text rows

---

### Step 4: Button Section

```dart
class ButtonSection extends StatelessWidget {
  const ButtonSection({super.key});

  @override
  Widget build(BuildContext context) {
    final Color color = Theme.of(context).primaryColor;
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        ButtonWithText(color: color, icon: Icons.call, label: 'CALL'),
        ButtonWithText(color: color, icon: Icons.near_me, label: 'ROUTE'),
        ButtonWithText(color: color, icon: Icons.share, label: 'SHARE'),
      ],
    );
  }
}

class ButtonWithText extends StatelessWidget {
  const ButtonWithText({
    super.key,
    required this.color,
    required this.icon,
    required this.label,
  });

  final Color color;
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, color: color),
        Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w400,
              color: color,
            ),
          ),
        ),
      ],
    );
  }
}
```

**Key patterns:**
- `MainAxisAlignment.spaceEvenly` for equal spacing
- Extract `ButtonWithText` as reusable widget
- `mainAxisSize: MainAxisSize.min` to shrink column

---

### Step 5: Text Section

```dart
class TextSection extends StatelessWidget {
  const TextSection({super.key, required this.description});

  final String description;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Text(
        description,
        softWrap: true,
      ),
    );
  }
}
```

**Key pattern:** `softWrap: true` wraps text at word boundaries.

---

### Complete Assembly

```dart
body: const SingleChildScrollView(
  child: Column(
    children: [
      ImageSection(image: 'images/lake.jpg'),
      TitleSection(
        name: 'Oeschinen Lake Campground',
        location: 'Kandersteg, Switzerland',
      ),
      ButtonSection(),
      TextSection(
        description: 'Lake Oeschinen lies at the foot of the '
            'Blüemlisalp in the Bernese Alps...',
      ),
    ],
  ),
),
```

---

## Layout Best Practices

| Practice | Why |
|----------|-----|
| Extract widgets for each section | Flutter only redraws what changes |
| Use `const` constructors | Enables widget reuse |
| Plan layout structure first | "Measure twice, cut once" |
| Use `Expanded` in Row/Column | Prevents overflow, distributes space |
| Add `SingleChildScrollView` | Handles content overflow gracefully |

---

## Quick Reference

| Widget | Use For |
|--------|---------|
| `Row` | Horizontal arrangement |
| `Column` | Vertical arrangement |
| `Expanded` | Fill remaining space |
| `Padding` | Add space around widget |
| `SizedBox` | Fixed spacing |
| `Container` | Decoration + sizing |
| `SingleChildScrollView` | Make content scrollable |

See [widget_fundamentals.md](./widget_fundamentals.md) for comprehensive widget catalog.
