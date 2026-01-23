# Windows Platform Integration

Building, customizing, and distributing Flutter apps for Windows.

## 1. Setup & Requirements
*   **Operating System**: Windows 10 (1903)+.
*   **Visual Studio 2022**: Install "Desktop development with C++" workload.
*   **Toolchain Check**: `flutter doctor -v`.

## 2. C++ Runner Customization
The Windows host app is a C++ executable (`windows/runner/main.cpp`).

### Window Properties
Customize initial size and title in `main.cpp`:
```cpp
Win32Window::Point origin(10, 10);
Win32Window::Size size(1280, 720);
if (!window.CreateAndShow(L"My Premium App", origin, size)) {
    return EXIT_FAILURE;
}
```

### Executable Name
Edit `windows/CMakeLists.txt`:
```cmake
set(BINARY_NAME "MyPremiumApp")
```

### Version Info
Edit `windows/runner/Runner.rc`.

## 3. Win32 APIs & FFI
*   **`package:win32`**: Access to thousands of Win32 APIs (COM, Shell, System).
*   **`dart:ffi`**: Call C-based APIs directly.

## 4. Distribution (MSIX)
Packager for the Microsoft Store.

1.  **Add Package**: `dart pub add msix`.
2.  **Config**: Add `msix_config:` to `pubspec.yaml`.
3.  **Build**: `dart run msix:create`.

## 5. Visual Guide
*   **Fluent UI**: Use `fluent_ui` package for Windows 11 style controls.
*   **Title Bar**: Use `bitsdojo_window` for custom owner-drawn title bars.
