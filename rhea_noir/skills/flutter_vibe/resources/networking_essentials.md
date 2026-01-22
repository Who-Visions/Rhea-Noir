# Networking & Integration

This guide covers how to integrate your Flutter app with backend services, focusing on HTTP, WebSockets, and best practices for data handling.

## 1. The HTTP Package
The standard way to make network requests.
```yaml
dependencies:
  http: ^1.0.0
```

### Basic Request
```dart
import 'package:http/http.dart' as http;

Future<void> fetchData() async {
  final response = await http.get(Uri.parse('https://api.example.com/data'));
  if (response.statusCode == 200) {
    print(response.body);
  } else {
    throw Exception('Failed to load data');
  }
}
```

## 2. Cookbook: Common Network Recipes

### Make Authenticated Requests
To fetch unauthorized data, you typically need to pass an `Authorization` header.
```dart
final response = await http.get(
  Uri.parse('https://api.example.com/user'),
  headers: {
    HttpHeaders.authorizationHeader: 'Bearer $token',
  },
);
```

### Send Data (POST)
Use `jsonEncode` to convert your Dart object (Map) to a JSON string.
```dart
import 'dart:convert';

Future<http.Response> createAlbum(String title) {
  return http.post(
    Uri.parse('https://jsonplaceholder.typicode.com/albums'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{
      'title': title,
    }),
  );
}
```

### Update Data (PUT)
Similar to POST, but typically replaces the entire resource.
```dart
Future<http.Response> updateAlbum(String title) {
  return http.put(
    Uri.parse('https://jsonplaceholder.typicode.com/albums/1'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(<String, String>{
      'title': title,
    }),
  );
}
```

### Delete Data (DELETE)
```dart
Future<http.Response> deleteAlbum(String id) async {
  final http.Response response = await http.delete(
    Uri.parse('https://jsonplaceholder.typicode.com/albums/$id'),
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
  );
  return response;
}
```

### Communicate with WebSockets
For real-time two-way communication. Use `web_socket_channel`.
```dart
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

final channel = WebSocketChannel.connect(
  Uri.parse('wss://echo.websocket.events'),
);

// Listen
channel.stream.listen((message) {
  print(message);
});

// Send
channel.sink.add('Hello!');

// Close
channel.sink.close(status.goingAway);
```

### Parse JSON in the Background
Parsing large JSON strings on the main thread can cause UI jank (dropped frames). Use `compute` to parse in a separate Isolate.

```dart
import 'dart:convert';
import 'package:flutter/foundation.dart';

// Top-level function, not a closure
List<Photo> parsePhotos(String responseBody) {
  final parsed = jsonDecode(responseBody).cast<Map<String, dynamic>>();
  return parsed.map<Photo>((json) => Photo.fromJson(json)).toList();
}

Future<List<Photo>> fetchPhotos(http.Client client) async {
  final response = await client.get(Uri.parse('https://jsonplaceholder.typicode.com/photos'));
  // Use compute to run parsePhotos in a background isolate
  return compute(parsePhotos, response.body);
}
```

## 3. Platform Configuration
- **Android**: Add `INTERNET` permission to `AndroidManifest.xml`.
- **macOS**: Add `com.apple.security.network.client` entitlement.
- **iOS**: Arbitrary loads are blocked by default. Configure `NSAppTransportSecurity` if needed (though HTTPS is preferred).
