# Package Management & Curated List

Guide to using and managing dependencies in Flutter.

## 1. Package Management Guide
### Packages vs Plugins
*   **Package**: Pure Dart code (e.g., `http`, `bloc`).
*   **Plugin**: Platform-specific code (Kotlin/Swift) (e.g., `camera`, `url_launcher`). Requires native rebuilds.

### Versioning & Constraints
*   **Caret Syntax (`^`)**: `^1.2.3` equivalent to `>=1.2.3 <2.0.0`. Safe for non-breaking updates.
*   **Overrides**: Force a version to resolve conflicts (use sparingly).
    ```yaml
    dependency_overrides:
      url_launcher: '5.4.0'
    ```

### Dependencies
*   **Pub**: `flutter pub add name`.
*   **Git**:
    ```yaml
    dependencies:
      my_pkg:
        git:
          url: https://github.com/user/repo.git
          ref: main
    ```
*   **Local**: `path: ../my_local_pkg`.

## 2. Essential Categories (Curated)
*   **State Management**: `flutter_bloc`, `provider`, `riverpod`.
*   **Navigation**: `go_router`, `auto_route`.
*   **Network**: `dio`, `http`, `chopper`.
*   **UI/UX**: `google_fonts`, `flutter_svg`, `lottie`.
