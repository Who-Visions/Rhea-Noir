# Accessibility

Building apps usable by everyone, including people with disabilities.

## 1. Accessibility Checklist
Before shipping, verify these items:

*   **Tappable Targets**: Minimum **48x48** logical pixels.
*   **Contrast Ratios**: At least **4.5:1** for text/controls vs background.
*   **Active Interactions**: Feedback for every interaction (e.g. `SnackBar` on press).
*   **Screen Reader**: Test with **TalkBack** (Android) and **VoiceOver** (iOS). Elements must be reachable and descriptively labeled.
*   **Context Switching**: Avoid changing context automatically (e.g. valid input moving focus) without user confirmation.
*   **Errors**: Provide suggestions for correction; allow undoing important actions.
*   **Color Blindness**: Ensure app is usable in grayscale/color-blind modes.
*   **Scale Factors**: Text/UI remains legible at large scale factors.

## 2. Semantics & Widgets
Flutter provides the `Semantics` widget to annotate the UI tree for accessibility services.

### `Semantics` Widget
Wrap widgets to provide descriptions, headers, or state information to screen readers.

```dart
Semantics(
  label: 'Profile Picture',
  image: true,
  onTap: () { /* ... */ },
  child: Image.asset('profile.png'),
)
```

### `MergeSemantics`
Group related widgets into a single focusable node (e.g. a Label + Value).

### `ExcludeSemantics`
Hide decorative elements from screen readers.

## 3. Standards & Regulations
*   **WCAG 2**: Web Content Accessibility Guidelines (Global standard).
*   **Section 508**: US requirement for federal agencies.
*   **EN 301 549**: European accessibility standard.

## 4. Testing Tools
*   **Android**: TalkBack, Accessibility Scanner.
*   **iOS**: VoiceOver, Accessibility Inspector.
*   **Flutter**: `SemanticsDebugger` (Draws serialization of semantics).
    ```dart
    MaterialApp(
      showSemanticsDebugger: true,
      // ...
    )
    ```

### Automated Testing
Use `flutter_test` with accessibility guidelines.

```dart
testWidgets('Accessibility test', (tester) async {
  final SemanticsHandle handle = tester.ensureSemantics();
  await tester.pumpWidget(const MyApp());

  // Check Android tap targets (48x48)
  await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  // Check iOS tap targets (44x44)
  await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
  // Check text contrast (3:1 / 4.5:1)
  await expectLater(tester, meetsGuideline(textContrastGuideline));

  handle.dispose();
});
```

## 5. Web Accessibility
Flutter translates the Semantics tree into an accessible HTML DOM (ARIA).

*   **Enabling**: By default, requires user interaction. Force enable:
    ```dart
    if (kIsWeb) SemanticsBinding.instance.ensureSemantics();
    ```
*   **Debug**: `flutter run -d chrome --profile --dart-define=FLUTTER_WEB_DEBUG_SHOW_SEMANTICS=true`

### Semantic Roles (Web)
Assign explicit roles for better screen reader announcements.
```dart
Semantics(
  role: SemanticsRole.list,
  child: Column(
    children: [
      Semantics(role: SemanticsRole.listItem, child: Text('Item 1')),
      Semantics(role: SemanticsRole.listItem, child: Text('Item 2')),
    ],
  ),
)
```
