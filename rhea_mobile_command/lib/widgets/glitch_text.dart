import 'package:flutter/material.dart';

class GlitchText extends StatefulWidget {
  final String text;
  final TextStyle style;

  const GlitchText(this.text, {super.key, required this.style});

  @override
  State<GlitchText> createState() => _GlitchTextState();
}

class _GlitchTextState extends State<GlitchText> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  
  @override
  void initState() {
    super.initState();
    // Random glitch intervals managed by repeating status listener or timer
    _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 200));
    _loopGlitch();
  }

  void _loopGlitch() async {
    while (mounted) {
       // Wait random 3-10 seconds
       final wait = 3000 + (DateTime.now().second % 7) * 1000;
       await Future.delayed(Duration(milliseconds: wait));
       if (!mounted) return;
       
       await _controller.forward();
       _controller.reset();
       
       // sometimes double glitch
       if (DateTime.now().millisecond % 3 == 0) {
          await _controller.forward();
          _controller.reset();
       }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        if (_controller.value == 0) {
          return Text(widget.text, style: widget.style);
        }
        
        // Glitch Offset
        final offset = (5.0 * _controller.value) * ((_controller.value > 0.5) ? -1 : 1);
        
        return Stack(
          clipBehavior: Clip.none,
          children: [
             // Cyan Channel
             Positioned(
               left: offset,
               top: -offset/2,
               child: Opacity(
                 opacity: 0.7,
                 child: Text(widget.text, 
                   style: widget.style.copyWith(color: Colors.cyanAccent)),
               ),
             ),
             // Red Channel
             Positioned(
               left: -offset,
               top: offset/2,
               child: Opacity(
                 opacity: 0.7,
                 child: Text(widget.text, 
                   style: widget.style.copyWith(color: Colors.redAccent)),
               ),
             ),
             // Main Text (White)
             Text(widget.text, style: widget.style),
          ],
        );
      },
    );
  }
}
