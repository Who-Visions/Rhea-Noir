# Networking

Making HTTP requests and handling data in Flutter.

## 1. Setup (`http` package)

Add dependencies:
```yaml
dependencies:
  http: ^1.0.0
```

### Platform Permissions

*   **Android** (`android/app/src/main/AndroidManifest.xml`):
    ```xml
    <uses-permission android:name="android.permission.INTERNET" />
    ```
*   **macOS** (`macos/Runner/DebugProfile.entitlements` & `Release.entitlements`):
    ```xml
    <key>com.apple.security.network.client</key>
    <true/>
    ```
*   **iOS/Web**: Usually enabled by default.

## 2. Basic Requests

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> fetchData() async {
  final url = Uri.parse('https://api.example.com/data');
  
  try {
    final response = await http.get(url);
    
    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      print('Data: $json');
    } else {
      print('Request failed: ${response.statusCode}');
    }
  } catch (e) {
    print('Error: $e');
  }
}
```

## 3. JSON Serialization
Don't parse JSON manually in production. Use `json_serializable` or `dart:convert` with typed models.

### Manual with Dart 3 Pattern Matching (Small Projects)
```dart
factory User.fromJson(Map<String, dynamic> json) {
  return switch (json) {
    {'name': String name, 'age': int age} => User(name: name, age: age),
    _ => throw const FormatException('Failed to load user.'),
  };
}
```

### Code Generation (Medium/Large Projects)
1.  **Add Dependencies**:
    ```bash
    flutter pub add json_annotation dev:build_runner dev:json_serializable
    ```
2.  **Annotate Model**:
    ```dart
    import 'package:json_annotation/json_annotation.dart';
    part 'user.g.dart';

    @JsonSerializable(explicitToJson: true)
    class User {
      final String name;
      @JsonKey(name: 'registration_date')
      final int regDate;

      User(this.name, this.regDate);

      factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
      Map<String, dynamic> toJson() => _$UserToJson(this);
    }
    ```
3.  **Run Builder**:
    *   One-time: `dart run build_runner build --delete-conflicting-outputs`
    *   Watch: `dart run build_runner watch --delete-conflicting-outputs`

## 4. Fetching & Displaying Data
**Best Practice**: Call fetch method in `initState` (or `didChangeDependencies`) to avoid re-fetching on every build.

```dart
class UserProfile extends StatefulWidget {
  @override
  _UserProfileState createState() => _UserProfileState();
}

class _UserProfileState extends State<UserProfile> {
  late Future<User> _userFuture;

  @override
  void initState() {
    super.initState();
    _userFuture = fetchUser(); // Cache the future
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<User>(
      future: _userFuture,
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return Text(snapshot.data!.name);
        } else if (snapshot.hasError) {
          return Text('Error: ${snapshot.error}');
        }
        return const CircularProgressIndicator();
      },
    );
  }
}
```
