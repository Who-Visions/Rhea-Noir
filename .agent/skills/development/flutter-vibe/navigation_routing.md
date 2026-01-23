# Navigation & Routing

Move between screens using Imperative or Declarative approaches.

## 1. Imperative Navigation (`Navigator`)
The standard stack-based approach. Best for simple apps or prototyping.

### Basic Push/Pop
```dart
// Navigate to SecondScreen
Navigator.of(context).push(
  MaterialPageRoute(builder: (context) => const SecondScreen()),
);

// Go back
Navigator.of(context).pop();
```

### Advanced Imperative Methods
*   **`pushReplacement`**: Replace current route (good for Splash Screens).
*   **`pushAndRemoveUntil`**: Clear stack (good for Logout).
*   **`popUntil`**: Go back multiple steps.

```dart
// Replace top (A -> B, A is gone)
Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => LoginScreen()));

// Clear stack (A -> B -> C -> Logout -> Login)
Navigator.pushAndRemoveUntil(
  context,
  MaterialPageRoute(builder: (_) => LoginScreen()),
  (route) => false, // Remove all previous routes
);
```

### Named Routes (Not Recommended for complex apps)
Define routes in `MaterialApp`.

```dart
MaterialApp(
  routes: {
    '/': (context) => HomeScreen(),
    '/second': (context) => SecondScreen(),
  },
);

// Usage
Navigator.pushNamed(context, '/second');
```

**Limitations**:
*   Deep linking is rigid.
*   Browser forward button doesn't work well.
*   Hard to handle complex state changes.

## 2. Declarative Navigation (`go_router`)
Recommended for deep linking, web support, and complex flows.

### Setup
Add `go_router` to `pubspec.yaml`.

```dart
final _router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => HomeScreen(),
    ),
    GoRoute(
      path: '/details/:id',
      builder: (context, state) {
        final id = state.pathParameters['id'];
        return DetailsScreen(id: id);
      },
    ),
  ],
);

MaterialApp.router(
  routerConfig: _router,
);
```

### Usage
```dart
// Go to a route (replaces stack logic appropriately)
context.go('/details/123');

// Push a route (adds to stack)
context.push('/details/123');
```

## 3. Data Passing

### Navigator
Pass arguments via constructor.
```dart
Navigator.push(context, MaterialPageRoute(
  builder: (context) => DetailsScreen(data: myData),
));
```

### GoRouter
Pass via path parameters or extra object.
```dart
// Path Parameters (Recommended for deep links)
context.go('/details/$id');

// Extra Object (Not deep linkable)
// Extra Object (Not deep linkable)
context.go('/details', extra: myObject);
```

### Returning Data
Pass data back when popping.

```dart
// Screen A: Wait for result
final result = await Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => SelectionScreen()),
);
ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("$result")));

// Screen B: Return result
Navigator.pop(context, 'User Selection');
```

## Resources
*   [Navigation & Routing Overview](https://docs.flutter.dev/ui/navigation)
---

## 4. Advanced: The Router API (Navigator 2.0)

Underneath `go_router` lies the low-level **Router API**. Use this only if you need completely custom navigation logic (e.g. specialized history stacks).

### Key Components
1.  **`Page`**: Immutable configuration for a `Route`. (e.g. `MaterialPage`).
2.  **`Router`**: Widget that listens to OS events and configures the Navigator.
3.  **`RouterDelegate`**: The "Brain". Rebuilds the Navigator based on app state.
4.  **`RouteInformationParser`**: Converts URL string <-> App State.

### Conceptual Flow
OS Event (URL Change) -> `RouteInformationParser` -> `RouterDelegate` -> `Navigator(pages: [...])`

### Declarative History (`pages` api)
Instead of `push()`, you provide a list of Pages.

```dart
Navigator(
  pages: [
    MaterialPage(child: HomeScreen()),
    if (selectedId != null) MaterialPage(child: DetailScreen(id: selectedId)),
  ],
  onPopPage: (route, result) {
    if (!route.didPop(result)) return false;
    // Update state to remove top page
    setState(() => selectedId = null);
    return true;
  },
)
### Custom Transitions (`TransitionDelegate`)
Customize how routes animate when the `pages` list changes.

```dart
class MyTransitionDelegate extends DefaultTransitionDelegate<dynamic> {
  // Override resolve() to customize push/pop animations
}

Navigator(
  transitionDelegate: MyTransitionDelegate(),
  pages: [...],
  ...
)
```

### Back Button Dispatcher
Handles system back button presses (Android).
*   **`RootBackButtonDispatcher`**: Listens to system events.
---

## 5. Navigation Design Concepts
Understanding *how* users move through the app.

### A. Lateral Navigation
Moving between screens at the same hierarchy level (Top-Level).

1.  **Bottom Navigation Bar** (3-5 destinations, Mobile)
    ```dart
    Scaffold(
      bottomNavigationBar: NavigationBar(
        onDestinationSelected: (int index) { ... },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.explore), label: 'Explore'),
        ],
      ),
    )
    ```
2.  **Navigation Drawer** (5+ destinations, Mobile/Tablet/Desktop)
    ```dart
    // Programmatic Control:
    // Scaffold.of(context).openDrawer();
    // Navigator.pop(context); // Close drawer
    Scaffold(
      drawer: NavigationDrawer(
        children: [
          NavigationDrawerDestination(icon: Icon(Icons.inbox), label: 'Inbox'),
          NavigationDrawerDestination(icon: Icon(Icons.send), label: 'Outbox'),
        ],
      ),
    )
    ```
3.  **Tabs** (Any level, dataset pivoting)
    
    a. **DefaultTabController** (Simplest)
    Automatically coordinates the `TabBar` and `TabBarView`.
    ```dart
    DefaultTabController(
      length: 3, 
      child: Scaffold(
        appBar: AppBar(
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.car_rental)),
              Tab(icon: Icon(Icons.train)),
              Tab(icon: Icon(Icons.pedal_bike)),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            Icon(Icons.car_rental),
            Icon(Icons.train),
            Icon(Icons.pedal_bike),
          ],
        ),
      ),
    )
    ```

    b. **Manual TabController** (Advanced)
    Use when you need to control selection programmatically or listen to changes.
    *   **Create**: In `initState`, `_controller = TabController(length: 3, vsync: this)`.
    *   **Dispose**: In `dispose`, `_controller.dispose()`.
    *   **Pass**: To both `TabBar(controller: _controller)` and `TabBarView(controller: _controller)`.

### B. Forward Navigation
Moving deeper into the hierarchy (Parent -> Child).
*   **Lists/Cards**: Tapping an item to see details.
*   **Search**: Bypassing hierarchy to find specific content.
*   **Buttons**: Advancing a flow (e.g. Checkout).

### C. Reverse Navigation
Moving back.

1.  **Chronological (Back Button)**: System Back / Browser Back. Returns to *previous view*.
2.  **Upward (Up Action)**: Arrow in AppBar. Returns to *hierarchical parent*.

**Handling Up Button**:
```dart
AppBar(
  leading: IconButton(
    icon: Icon(Icons.arrow_back),
    onPressed: () => Navigator.pop(context), // Or context.pop()
  ),
)
```
