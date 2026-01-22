# Persistence

Storing data locally on the device.

## 1. Shared Preferences (`shared_preferences`)
Best for simple key-value pairs (settings, flags, simple data).

```yaml
dependencies:
  shared_preferences: ^2.0.0
```

### Usage
```dart
import 'package:shared_preferences/shared_preferences.dart';

// Save
final prefs = await SharedPreferences.getInstance();
await prefs.setInt('counter', 10);
await prefs.setBool('is_dark_mode', true);

// Read
final counter = prefs.getInt('counter') ?? 0;
final isDarkMode = prefs.getBool('is_dark_mode') ?? false;

// Remove
await prefs.remove('counter');
```

## 2. File Storage (`path_provider`)
Best for larger files, blobs, or offline caches.

```yaml
dependencies:
  path_provider: ^2.0.0
```

### Reading/Writing Files
```dart
import 'dart:io';
import 'package:path_provider/path_provider.dart';

Future<String> get _localPath async {
  final directory = await getApplicationDocumentsDirectory();
  return directory.path;
}

Future<File> get _localFile async {
  final path = await _localPath;
  return File('$path/data.txt');
}

Future<File> writeData(String data) async {
  final file = await _localFile;
  return file.writeAsString(data);
}

Future<String> readData() async {
  try {
    final file = await _localFile;
    return await file.readAsString();
  } catch (e) {
    return '';
  }
}
```
