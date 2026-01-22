# Fragment Shaders & Graphics

Create custom visual effects using GLSL shaders on the GPU.

## 1. Setup

### Declare Shader
Shaders (.frag) must be declared in `pubspec.yaml` under `flutter: shaders:`.

```yaml
flutter:
  shaders:
    - shaders/myshader.frag
```

### Loading
Load the `FragmentProgram` at runtime (usually in `initState`).

```dart
late FragmentProgram program;

void loadShader() async {
  program = await FragmentProgram.fromAsset('shaders/myshader.frag');
}
```

## 2. Usage APIs

### Canvas (CustomPainter)
Draw shapes filled with the shader.

```dart
void paint(Canvas canvas, Size size) {
  final shader = program.fragmentShader();
  
  // Set Uniforms (Float: index based on order in GLSL)
  shader.setFloat(0, size.width);  // uSize.x
  shader.setFloat(1, size.height); // uSize.y
  shader.setFloat(2, 42.0);        // uCustomValue

  canvas.drawRect(
    Offset.zero & size,
    Paint()..shader = shader,
  );
}
```

### ImageFilter (BackdropFilter)
**Note**: Only supported on **Impeller** backend.

```dart
BackdropFilter(
  filter: ImageFilter.shader(program.fragmentShader()),
  child: ...
)
```

## 3. Writing Shaders (GLSL)

Use `#include <flutter/runtime_effect.glsl>` for helpers like `FlutterFragCoord()`.

```glsl
#version 460 core
#include <flutter/runtime_effect.glsl>

uniform vec2 uSize;
uniform float uTime;
uniform sampler2D uTexture;

out vec4 fragColor;

void main() {
  vec2 uv = FlutterFragCoord().xy / uSize;
  
  // Simple effect: Grayscale
  vec4 color = texture(uTexture, uv);
  float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
  
  fragColor = vec4(vec3(gray), color.a);
}
```

### Limitations
- No UBOs/SSBOs.
- `sampler2D` only.
- No `gl_FragCoord` (use `FlutterFragCoord()`).

## 4. Uniforms Mapping

| GLSL Type | Dart Method | Indexing |
|-----------|-------------|----------|
| `float` | `setFloat(i, val)` | Increments per float |
| `vec2` | `setFloat(i, x); setFloat(i+1, y)` | Takes 2 slots |
| `vec3` | `setFloat` x 3 | Takes 3 slots |
| `vec4` (Color) | `setFloat` x 4 | Takes 4 slots (R, G, B, A) |
| `sampler2D` | `setImageSampler(i, image)` | Separate index counter (0, 1...) |

## Resources
- [The Book of Shaders](https://thebookofshaders.com/)
- [ShaderToy](https://www.shadertoy.com/)
