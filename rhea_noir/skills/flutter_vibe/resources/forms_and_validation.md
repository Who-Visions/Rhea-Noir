# Forms & Input Handling

## 1. Text Fields Basics

### `TextField` (Simple Input)
Best for search bars or simple interactions.
-   **`onChanged`**: React to every keystroke immediately.
-   **`decoration`**: Add labels, icons, borders.

```dart
TextField(
  decoration: InputDecoration(
    border: OutlineInputBorder(),
    labelText: 'Search',
    prefixIcon: Icon(Icons.search),
  ),
  onChanged: (value) => print('Typing: $value'),
)
```

### `TextFormField` (Form Integrated)
Best for data entry (Login, Sign up) requiring validation.
-   Wraps `TextField` in a `FormField`.
-   Access to `Form.save()` and `Form.validate()`.

## 2. Validation Logic

### Setup
1.  **`GlobalKey<FormState>`**: To identify and control the form.
2.  **`Form` Widget**: Container for fields.
3.  **`validator`**: Function returning `null` (valid) or String (error).

```dart
class MyForm extends StatefulWidget {
  @override
  _MyFormState createState() => _MyFormState();
}

class _MyFormState extends State<MyForm> {
  final _formKey = GlobalKey<FormState>(); // 1. Key

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey, // 2. Assign Key
      child: Column(
        children: [
          TextFormField(
            validator: (value) { // 3. Validator
              if (value == null || value.isEmpty) return 'Required';
              return null;
            },
          ),
          ElevatedButton(
            onPressed: () {
              // 4. Trigger Validation
              if (_formKey.currentState!.validate()) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Processing...')),
                );
              }
            },
            child: Text('Submit'),
          ),
        ],
      ),
    );
  }
}
```

## 3. Controllers (`TextEditingController`)

To read/write text programmatically or listen to changes.

**Rules**:
-   **Initialize** in `initState` or variable declaration.
-   **Dispose** in `dispose` to prevent memory leaks.

```dart
class ControllerExample extends StatefulWidget { ... }

class _ControllerExampleState extends State<ControllerExample> {
  final _controller = TextEditingController();

  @override
  void initState() {
    super.initState();
    _controller.addListener(() {
      print("Current Text: ${_controller.text}");
    });
  }

  @override
  void dispose() {
    _controller.dispose(); // CRITICAL
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(controller: _controller);
  }
}
```

## 4. Focus Management

Control keyboard focus programmatically.

### Auto Focus
`TextField(autofocus: true)`

### Manual Focus (`FocusNode`)
1.  Create `FocusNode` (and `dispose` it!).
2.  Attach to `TextField(focusNode: myNode)`.
3.  Call `myNode.requestFocus()`.

```dart
// inside State class...
late FocusNode myFocusNode;

@override
void initState() {
  super.initState();
  myFocusNode = FocusNode();
}

@override
void dispose() {
  myFocusNode.dispose();
  super.dispose();
}

// inside build...
TextField(focusNode: myFocusNode);
// trigger...
myFocusNode.requestFocus();
```
