import 'dart:ui';
import 'package:flutter/material.dart';
import '../main.dart'; // For constants like kColorBg

class VoidBackground extends StatefulWidget {
  const VoidBackground({super.key});

  @override
  State<VoidBackground> createState() => _VoidBackgroundState();
}

class _VoidBackgroundState extends State<VoidBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  FragmentProgram? _program;
  bool _shadersSupported = true; // Fallback if unsupported

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
        vsync: this, duration: const Duration(minutes: 10))
      ..repeat();

    _loadShader();
  }

  Future<void> _loadShader() async {
    try {
      final program = await FragmentProgram.fromAsset('shaders/void.frag');
      if (mounted) {
        setState(() {
          _program = program;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _shadersSupported = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_program == null) {
      if (!_shadersSupported) {
         return Container(
            decoration: const BoxDecoration(
              gradient: RadialGradient(
                center: Alignment.topRight,
                radius: 1.5,
                colors: [Color(0xFF1A0B2E), kColorBg],
              ),
            ),
         );
      }
      return Container(color: kColorBg);
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return CustomPaint(
          size: Size.infinite,
          painter: _VoidShaderPainter(
            shader: _program!.fragmentShader(),
            time: _controller.value * 600.0, 
          ),
        );
      },
    );
  }
}

class _VoidShaderPainter extends CustomPainter {
  final FragmentShader shader;
  final double time;

  _VoidShaderPainter({required this.shader, required this.time});

  @override
  void paint(Canvas canvas, Size size) {
    shader.setFloat(0, time);
    shader.setFloat(1, size.width);
    shader.setFloat(2, size.height);

    final paint = Paint()..shader = shader;
    canvas.drawRect(Offset.zero & size, paint);
    
    final gridPaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.035)
      ..strokeWidth = 1;

    const double step = 42;
    for (double x = 0; x <= size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
    }
    for (double y = 0; y <= size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _VoidShaderPainter oldDelegate) =>
      oldDelegate.time != time;
}
