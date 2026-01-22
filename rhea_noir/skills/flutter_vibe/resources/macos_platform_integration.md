# macOS Platform Integration

## macOS Development
Building macOS apps with Flutter involves specific considerations including look and feel, distribution, and security entitlements.

### Integrating with macOS look and feel
While Flutter allows for any visual style, aligning with the macOS aesthetic often improves user experience.
- **Cupertino Widgets**: Flutter's iOS-style widgets (sliders, switches, segmented controls) work well on macOS.
- **macos_ui Package**: For a deeper integration, the [macos_ui](https://pub.dev/packages/macos_ui) package provides widgets implementing the macOS design language (MacosWindow, toolbars, modal dialogs).

### Building for Distribution
Distribute your app via the Mac App Store or as a standalone `.app`.
1.  **Build Release**: `flutter build macos`
2.  **Open Xcode Workspace**: `open macos/Runner.xcworkspace`
3.  **Notarization**: Apps distributed outside the App Store must be notarized to pass Gatekeeper.
4.  **Signing**: Ensure your app is signed with a valid certificate.

### Entitlements and App Sandbox
macOS builds are signed and sandboxed by default. You must explicitly request permissions (Entitlements) in Xcode.

**Configuration Files**:
- `macos/Runner/Runner-DebugProfile.entitlements`
- `macos/Runner/Runner-Release.entitlements`

**Critical Entitlements**:
- **Network Client**: `com.apple.security.network.client` - Required for *any* outbound network requests.
- **Network Server**: `com.apple.security.network.server` - Required for incoming connections (enabled by default in Debug/Profile).
- **File Access**: `com.apple.security.files.user-selected.read-only` (or `read-write`) - Required for file pickers.
- **Hardware**: Camera, Microphone, etc., require specific keys (e.g., `com.apple.security.device.camera`).

> **Important**: Always keep Debug/Profile and Release entitlements in sync unless you have a specific reason not to. Missing entitlements in Release mode will cause crashes or failures that don't appear in Debug mode.

### Hardened Runtime
Required for apps distributed outside the App Store (notarization).
- Enable "Hardened Runtime" in Xcode.
- This may require additional entitlements compared to just the App Sandbox (e.g., `com.apple.security.device.audio-input`).

### Resources
- [Flutter macOS Desktop Support](https://flutter.dev/multi-platform/desktop)
- [Apple Entitlements Documentation](https://developer.apple.com/documentation/bundleresources/entitlements)
