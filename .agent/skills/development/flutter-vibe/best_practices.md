# Flutter Best Practices

Source: Awesome Flutter Community & Vibe Coding Standards

## Architecture Patterns

### Feature-First Architecture (Vibe Default)

```
lib/
├── core/                    # Shared app-level concerns
│   ├── constants/           # Colors, dimensions, strings
│   ├── theme/               # Theme configuration
│   ├── router/              # Navigation setup
│   └── utils/               # Helpers and extensions
├── features/                # Feature modules
│   └── [feature]/
│       ├── data/            # Repositories, DTOs, data sources
│       ├── domain/          # Entities, failures (freezed)
│       └── presentation/    # Screens, widgets, providers
└── shared/                  # Reusable widgets
```

### Clean Architecture (Alternative)

```
lib/
├── data/
│   ├── datasources/
│   ├── models/
│   └── repositories/
├── domain/
│   ├── entities/
│   ├── repositories/
│   └── usecases/
└── presentation/
    ├── bloc/
    ├── pages/
    └── widgets/
```

---

## State Management Best Practices

### Riverpod (Recommended)

```dart
// ✅ Good: Use NotifierProvider for state with actions
final counterProvider = NotifierProvider<CounterNotifier, int>(CounterNotifier.new);

class CounterNotifier extends Notifier<int> {
  @override
  int build() => 0;
  
  void increment() => state++;
}

// ✅ Good: Use AsyncNotifierProvider for async operations
final userProvider = AsyncNotifierProvider<UserNotifier, User>(UserNotifier.new);

// ✅ Good: Use ref.invalidate() for refresh
ref.invalidate(userProvider);

// ❌ Bad: Modifying state outside notifier
ref.read(counterProvider.notifier).state = 5; // Avoid direct state mutation
```

### Don'ts

```dart
// ❌ Never use setState in StatefulWidget for business logic
setState(() { /* business logic */ });

// ❌ Never create providers inside build methods
Widget build(BuildContext context) {
  final myProvider = Provider((ref) => ...); // WRONG!
}

// ❌ Never call async functions directly in build
Widget build(BuildContext context, WidgetRef ref) {
  ref.read(fetchData()); // WRONG - use ref.watch with AsyncValue
}
```

---

## Widget Best Practices

### Performance

```dart
// ✅ Use const constructors
const MyWidget({super.key});

// ✅ Extract widgets to their own classes (not methods)
class _ItemWidget extends StatelessWidget { ... }

// ❌ Avoid widget methods
Widget _buildItem() { ... } // Creates new widget every build

// ✅ Use Keys for lists with dynamic order
ListView(
  children: items.map((item) => ItemWidget(key: ValueKey(item.id))).toList(),
);

// ✅ Use RepaintBoundary for isolated animations
RepaintBoundary(
  child: AnimatedWidget(),
);
```

### Layout

```dart
// ✅ Use Expanded/Flexible in Row/Column
Row(children: [Expanded(child: Text('Long text...'))]);

// ✅ Use LayoutBuilder for responsive designs
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth > 600) return DesktopLayout();
    return MobileLayout();
  },
);

// ✅ Use MediaQuery.sizeOf for size-only queries (no rebuilds on other changes)
final size = MediaQuery.sizeOf(context);
```

### Animations

```dart
// ✅ Use flutter_animate for declarative animations
Text('Hello').animate()
  .fadeIn(duration: 300.ms)
  .slideY(begin: 0.2, end: 0);

// ✅ Use AnimatedSwitcher for widget swaps
AnimatedSwitcher(
  duration: const Duration(milliseconds: 300),
  child: isLoading ? Spinner() : Content(key: ValueKey('content')),
);

// ✅ Use Hero for shared element transitions
Hero(tag: 'avatar-${user.id}', child: Avatar(user));
```

---

## Navigation Best Practices

### GoRouter

```dart
// ✅ Use typed routes with go_router_builder
@TypedGoRoute<HomeRoute>(path: '/')
class HomeRoute extends GoRouteData {
  @override
  Widget build(BuildContext context, GoRouterState state) => const HomePage();
}

// ✅ Use context.push for stack navigation
context.push('/details/${item.id}');

// ✅ Use context.go for replacement navigation
context.go('/login'); // Clears back stack

// ✅ Use redirect for auth guards
GoRouter(
  redirect: (context, state) {
    final isLoggedIn = ref.read(authProvider);
    if (!isLoggedIn && state.matchedLocation != '/login') {
      return '/login';
    }
    return null;
  },
);
```

---

## Error Handling

```dart
// ✅ Use freezed for typed failures
@freezed
class Failure with _$Failure {
  const factory Failure.network(String message) = NetworkFailure;
  const factory Failure.server(int code) = ServerFailure;
  const factory Failure.unknown() = UnknownFailure;
}

// ✅ Use Either or AsyncValue for error handling
AsyncValue<User>.when(
  data: (user) => UserCard(user),
  loading: () => const Spinner(),
  error: (e, st) => ErrorWidget(e.toString()),
);

// ✅ Use ErrorBoundary widgets
ErrorBoundary(
  onError: (error, stack) => logError(error, stack),
  child: RiskyWidget(),
);
```

---

## Testing Best Practices

```dart
// ✅ Use ProviderScope overrides for testing
testWidgets('shows user name', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        userProvider.overrideWithValue(AsyncValue.data(mockUser)),
      ],
      child: const MyApp(),
    ),
  );
});

// ✅ Use golden tests for UI verification
testWidgets('matches golden', (tester) async {
  await tester.pumpWidget(const MyWidget());
  await expectLater(
    find.byType(MyWidget),
    matchesGoldenFile('goldens/my_widget.png'),
  );
});

// ✅ Use integration_test for E2E
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  testWidgets('full flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    // ...
  });
}
```

---

## Performance Tips

1. **Use `const` everywhere possible** - Prevents widget rebuilds
2. **Profile with DevTools** - Identify jank and memory leaks
3. **Lazy load heavy widgets** - Use `Visibility.maintain` or deferred loading
4. **Compress images** - Use WebP, limit resolution
5. **Use `compute()` for heavy operations** - Offload to isolate
6. **Avoid `BuildContext` in async gaps** - Check `mounted` state
7. **Use `AutomaticKeepAliveClientMixin`** - For PageView/TabBarView state preservation

---

## Accessibility Checklist

- [ ] Add `Semantics` labels to icons and images
- [ ] Ensure touch targets are 44x44 minimum
- [ ] Test with TalkBack/VoiceOver
- [ ] Support dynamic text scaling
- [ ] Provide sufficient color contrast (4.5:1 for text)
- [ ] Use `ExcludeSemantics` for decorative elements

---

## CLI Cheatsheet

### Core Commands
| Command | Description |
|---------|-------------|
| `flutter create my_app` | Create new standard Flutter app |
| `flutter create --empty my_app` | Create minimal app (no comments/tests) |
| `flutter run` | Run in Debug mode (Hot Reload enabled) |
| `flutter run --profile` | Run in Profile mode (DevTools enabled) |
| `flutter run --release` | Run in Release mode (Optimized) |

### Analysis & Testing
| Command | Description |
|---------|-------------|
| `flutter analyze` | Static analysis of Dart code |
| `flutter test` | Run unit/widget tests |
| `flutter test integration_test/` | Run integration tests |
| `dart fix --apply` | Auto-apply quick fixes |

### Packages
| Command | Description |
|---------|-------------|
| `flutter pub get` | Install dependencies |
| `flutter pub outdated` | Check for newer versions |
| `flutter pub upgrade` | Upgrade to latest compatible versions |
| `flutter pub add [package]` | Add a dependency |

### Build (Release)
| Command | Description |
|---------|-------------|
| `flutter build apk` | Android APK |
| `flutter build appbundle` | Android App Bundle (Play Store) |
| `flutter build ipa` | iOS Archive (App Store) |
| `flutter build web --wasm` | Web (Wasm + CanvasKit) |
| `flutter build macos/windows` | Desktop Release |

