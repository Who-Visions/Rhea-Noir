# Firebase Integration

Backend-as-a-Service (BaaS) for Flutter apps.

## 1. Setup (FlutterFire)
The modern way to set up Firebase is via the **FlutterFire CLI**.

1.  **Install CLI**:
    ```bash
    dart pub global activate flutterfire_cli
    ```
2.  **Configure Project**:
    ```bash
    flutterfire configure
    ```
    (Select your project and platforms. This generates `firebase_options.dart`).

3.  **Initialize**:
    ```dart
    import 'package:firebase_core/firebase_core.dart';
    import 'firebase_options.dart';

    void main() async {
      WidgetsFlutterBinding.ensureInitialized();
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MyApp());
    }
    ```

## 2. Cloud Firestore (Database)
Realtime NoSQL database.

**Dependencies**: `cloud_firestore`

### Add Data
```dart
final db = FirebaseFirestore.instance;
final user = <String, dynamic>{
  "first": "Ada",
  "last": "Lovelace",
  "born": 1815
};

await db.collection("users").add(user);
```

### Read Data (Realtime)
```dart
StreamBuilder<QuerySnapshot>(
  stream: db.collection('users').snapshots(),
  builder: (context, snapshot) {
    if (!snapshot.hasData) return CircularProgressIndicator();
    
    return ListView(
      children: snapshot.data!.docs.map((doc) {
        return ListTile(
          title: Text(doc['first']),
          subtitle: Text(doc['last']),
        );
      }).toList(),
    );
  },
);
```

## 3. Authentication
**Dependencies**: `firebase_auth`

```dart
// Sign in anonymously
await FirebaseAuth.instance.signInAnonymously();

// Listen to auth state
FirebaseAuth.instance.authStateChanges().listen((User? user) {
  if (user == null) {
    print('User is currently signed out!');
  } else {
    print('User is signed in!');
  }
});
```
