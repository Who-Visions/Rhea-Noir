# Architecture & Best Practices

Structuring Flutter apps for scalability, maintainability, and testability.

## 1. Layered Architecture
Separation of concerns is key. A common scalable approach divides the app into two main layers (UI & Data), with an optional Domain layer.

### A. Data Layer
Responsible for application data and business logic.
*   **Services**: Low-level wrappers for APIs/Plugins (e.g., `HttpService`, `BluetoothService`). No state, returns raw data (`Future<Map>`).
*   **Repositories**: The Single Source of Truth (SSOT). Coordinates data from Services (Network, DB). Handles caching, error handling, and converting raw data to **Domain Models**.

### B. Domain Layer (Optional)
Pure business logic, agnostic of Flutter.
*   **Models**: Immutable data classes.
*   **Use Cases**: Encapsulate complex business logic re-used across ViewModels.

### C. UI Layer (Presentation)
*   **Views**: Widgets that render state. No business logic.
*   **ViewModels**: Manages UI state. Converts Domain Models -> UI State. Handles User Events.

## 2. Dependency Injection (DI)
Decouple your classes. Don't create dependencies inside classes; pass them in.

### Using `get_it` (Service Locator)
```dart
final getIt = GetIt.instance;

void setup() {
  getIt.registerLazySingleton<ApiClient>(() => ApiClient());
  getIt.registerLazySingleton<AuthRepository>(() => AuthRepository(api: getIt()));
}
```

## 3. Project Structure (Hybrid: Feature + Type)
*   **Data/Domain**: Grouped by Type (shared across app).
*   **UI**: Grouped by Feature (View + ViewModel copule).

```
lib/
├── main.dart
├── core/                   # Shared widgets/utils
│   ├── theme/
│   └── widgets/
├── data/                   # Data Layer (By Type)
│   ├── repositories/
│   │   └── auth_repository.dart
│   └── services/
│       └── auth_api.dart
├── domain/                 # Domain Layer (By Type)
│   └── models/
│       └── user.dart
└── ui/                     # UI Layer (By Feature)
    ├── auth/
    │   ├── login_screen.dart
    │   └── login_viewmodel.dart
    └── products/
        ├── product_list_screen.dart
        └── product_list_viewmodel.dart
```

## 4. UI Layer (MVVM Details)
### ViewModel (State Holder)
Manages state and handles user events. Private properties prevent direct external modification.
```dart
class HomeViewModel extends ChangeNotifier {
  final BookingRepository _repo;

  HomeViewModel({required BookingRepository repo}) : _repo = repo {
    // Initialize Command
    loadCommand = Command0(_load)..execute();
  }

  // State
  List<Booking> _bookings = [];
  UnmodifiableListView<Booking> get bookings => UnmodifiableListView(_bookings);

  // Command Pattern (Safe Async Execution)
  late Command0 loadCommand;

  Future<Result> _load() async {
    final result = await _repo.getBookings();
    if (result.isOk) _bookings = result.asOk.value;
    notifyListeners();
    return result;
  }
}
```

### View (Widget)
Listens to ViewModel using `ListenableBuilder` (native) or `Consumer` (Riverpod).
```dart
class HomeScreen extends StatelessWidget {
  final HomeViewModel viewModel;

  const HomeScreen({required this.viewModel});

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: viewModel.loadCommand, // Listen to command state
      builder: (context, _) {
        if (viewModel.loadCommand.running) return CircularProgressIndicator();
        return ListView.builder(
          itemCount: viewModel.bookings.length,
          itemBuilder: (_, i) => Text(viewModel.bookings[i].title),
        );
      },
    );
  }
}
```

## 5. Dependency Injection (Provider Pattern)
Recommended by Google for simple DI.
```dart
MultiProvider(
  providers: [
    // 1. Services (Leaf nodes)
    Provider(create: (_) => ApiClient()),
    
    // 2. Repositories (Depend on Services)
    Provider(create: (context) => AuthRepository(
      api: context.read<ApiClient>(),
    )),

    // 3. ViewModels (Depend on Repositories)
    ChangeNotifierProvider(create: (context) => HomeViewModel(
      repo: context.read<AuthRepository>(),
    )),
  ],
  child: MyApp(),
);
```
