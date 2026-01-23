# Deployment & Release

Guide to preparing your app for production release across all platforms.

## 1. Code Obfuscation (Dart)
Hide function and class names in release builds to hinder reverse engineering.

### Command
```bash
flutter build apk --obfuscate --split-debug-info=/<project-name>/debug-info
```
*   **`--split-debug-info`**: Directory to save symbol files (Required for obfuscation).
*   **Backup**: Save the files in this directory! You need them to decode crash stack traces.

### De-obfuscating Stack Traces
```bash
flutter symbolize -i <stack-trace-file> -d <debug-info-dir>
```

## 2. Android Flavors (Build Variants)
Manage different environments (e.g., Staging vs Production) with separate configs.

### Configuration (`android/app/build.gradle.kts`)
```kotlin
android {
    flavorDimensions += "env"
    productFlavors {
        create("staging") {
            dimension = "env"
            applicationIdSuffix = ".staging"
            resValue("string", "app_name", "MyApp (Staging)")
        }
        create("prod") {
            dimension = "env"
            resValue("string", "app_name", "MyApp")
        }
    }
}
```

### Usage
*   **Run**: `flutter run --flavor staging`
*   **Build**: `flutter build apk --flavor prod`
*   **Conditional Assets**: Use `flavors` key in `pubspec.yaml` assets (Flutter 3.16+).

## 3. iOS Flavors (Schemes)
iOS uses **Schemes** and **Build Configurations** to match Flutter flavors.

1.  **Schemes**: Create schemes named `staging` and `prod` in Xcode.
2.  **Configurations**: Duplicate `Debug`, `Release`, `Profile` as `Debug-staging`, `Release-staging`, etc.
3.  **Mapping**: Ensure Scheme `staging` uses `*-staging` configurations.
    *   `flutter run --flavor staging` -> Runs `staging` Scheme.

## 4. Android Release
### Signing key
1.  Generate: `keytool -genkey -v -keystore upload-keystore.jks ...`
2.  Properties: Create `android/key.properties`:
    ```properties
    storePassword=...
    keyPassword=...
    keyAlias=upload
    storeFile=../upload-keystore.jks
    ```
3.  Gradle: Load `key.properties` and set `signingConfigs` in `build.gradle.kts`.

### Build
```bash
# Generate App Bundle (Preferred for Play Store)
flutter build appbundle

# Generate APK (Split by ABI)
flutter build apk --split-per-abi
```

## 5. iOS Release
### Versioning
Update `pubspec.yaml`: `version: 1.0.0+1` (Version + Build Number).

### Build IPA
```bash
# Build Archive and IPA
flutter build ipa --obfuscate --split-debug-info=./debug-info
```
*   **Result**: `build/ios/ipa/*.ipa`.
*   **Upload**: Use **Transporter** app (macOS) or `xcrun altool`.

## 6. macOS Release
### Prerequisites
*   Apple Developer Program enrollment.
*   Certificates: Mac App Distribution & Mac Installer Distribution.

### Build & Package
```bash
# Build Release
flutter build macos --release

# Sign & Package (Manual or via tools)
xcrun productbuild --component "build/macos/Build/Products/Release/My.app" /Applications/ signed.pkg --sign "3rd Party Mac Developer Installer: ..."
```
*   **Upload**: Use **Transporter** app (macOS).

## 7. Windows Release (Microsoft Store)
### Prerequisites
*   Microsoft Partner Center account.
*   **MSIX Packaging**: Required format for the Store.

### Packaging (using `msix` package)
1.  Add dependency: `dev_dependencies: msix: ^3.0.0`.
2.  Configure `pubspec.yaml` (`msix_config`: display_name, publisher, identity_name).
3.  Build: `flutter pub run msix:create`.
4.  **Upload**: Submit `.msix` to Partner Center.

### Versioning Note
Store apps require the 4th digit to be 0 (e.g., `1.0.0.0`).

## 8. Web Release
### Build
```bash
flutter build web --release --wasm
```
*   **Flags**: `--wasm` (skwasm + canvaskit) or defaults to canvaskit.
*   **Output**: `build/web/`.

### Hosting (Firebase)
1.  `firebase init hosting` (Choose "Single Page App", direct to `build/web`).
2.  `firebase deploy`.

## 9. Continuous Delivery (CI/CD)
Automate builds and releases.

### Fastlane
Open-source tool for iOS/Android automation.
*   **Android**: `android/fastlane/Fastfile` (Play Store upload).
*   **iOS**: `ios/fastlane/Fastfile` (TestFlight upload, Match for certs).

### Cloud Providers
*   **Codemagic**: Dedicated Flutter CI/CD. Built-in workflow editor, auto-signing.
*   **GitHub Actions**: Use `subosito/flutter-action` to setup Flutter.
    ```yaml
    - uses: subosito/flutter-action@v2
    - run: flutter build apk
    ```
