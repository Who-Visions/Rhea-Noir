# Windows Platform Integration

## 1. Setup
To build Flutter apps for Windows, you need:
- **Visual Studio 2022** (Community Edition is free).
- **"Desktop development with C++"** workload installed.
- **Windows 10/11** SDK.

Run `flutter doctor` to verify your environment.

## 2. Configuration (`windows/runner/`)
- **App Title**: Modify `window.CreateAndShow(L"My App", origin, size)` in `main.cpp`.
- **Minimum Size**: Handle `WM_GETMINMAXINFO` in `flutter_window.cpp` to enforce window constraints.
- **Icons**: Replace `resources/app_icon.ico`.

## 3. Distribution: The Indie Way (.exe)
While you can use MSIX for the data store, many indie developers prefer a simple `.exe` installer. We recommend using **Inno Setup**.

### Step 1: Build Release
Open your terminal in the project root:
```bash
flutter build windows --release
```
This generates the executable and assets in:
`build\windows\runner\Release`

### Step 2: Include Visual C++ Runtime DLLs
The generated `.exe` is not standalone; it depends on Visual C++ runtime libraries. You must ship these with your app if the user doesn't have them (and you can't assume they do).

Copy the following DLLs from your Visual Studio installation (e.g., `C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Redist\MSVC\...\x64\Microsoft.VC143.CRT\`):
- `msvcp140.dll`
- `msvcp140_1.dll`
- `msvcp140_2.dll`
- `vcruntime140.dll`
- `vcruntime140_1.dll`

Paste them into your `build\windows\runner\Release` folder alongside your app's `.exe`.

### Step 3: Create Installer with Inno Setup
1.  Download and install **Inno Setup**.
2.  Use the **Script Wizard**.
3.  **App Info**: Enter Name, Version, Publisher.
4.  **Application Files**:
    - **Main Executable**: Select your `your_app.exe` from the Release folder.
    - **Add Files**: Select ALL `.dll` files from the Release folder (including the VC++ ones you added).
    - **Add Folder**: Select the `data` folder from the Release folder.
        - **Critical**: When prompted, set the "Destination Subfolder" to `data`. If you don't do this, assets will be scattered and the app will crash.
5.  **Settings**: Allow shortcuts, license file (optional), and custom icons.
6.  **Compile**: Run the script to generate your `mysetup.exe`.

### Step 4: Distribute
You now have a single `mysetup.exe` file.
- Upload to GitHub Releases.
- Distribute via your website.
- Users can simply double-click to install.

## 4. MSIX Distribution (Microsoft Store)
If targeting the Microsoft Store, use the `msix` pub package.
```bash
flutter pub add --dev msix
flutter pub run msix:create
```
*Note: This requires a valid publisher certificate.*
