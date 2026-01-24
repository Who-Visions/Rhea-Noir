import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class CyberneticTypingEffect extends StatefulWidget {
  final String text;
  final Widget Function(BuildContext context, String text) builder;
  final Duration duration;
  final bool autoPlay;

  const CyberneticTypingEffect({
    super.key,
    required this.text,
    required this.builder,
    this.duration = const Duration(milliseconds: 800),
    this.autoPlay = true,
  });

  @override
  State<CyberneticTypingEffect> createState() => _CyberneticTypingEffectState();
}

class _CyberneticTypingEffectState extends State<CyberneticTypingEffect> {
  late String _displayedText;
  final _chars = '01#@%&*<>?/_+=-';
  
  @override
  void initState() {
    super.initState();
    if (widget.autoPlay) {
      _displayedText = "";
      _startEffect();
    } else {
      _displayedText = widget.text;
    }
  }

  @override
  void didUpdateWidget(covariant CyberneticTypingEffect oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.text != widget.text) {
      if (widget.autoPlay) {
         _displayedText = "";
        _startEffect();
      } else {
        setState(() {
          _displayedText = widget.text;
        });
      }
    }
  }

  void _startEffect() async {
    // 60 chars per second approx speed
    final stepTime = (1000 / 60).round(); 
    
    for (int i = 0; i < widget.text.length; i++) {
      if (!mounted) return;
      if (_displayedText.length >= widget.text.length) break;

      // Matrix-style flicker for last char
      for (int f = 0; f < 2; f++) {
        await Future.delayed(Duration(milliseconds: stepTime ~/ 2));
        if (!mounted) return;
        setState(() {
          final safeI = i < widget.text.length ? i : widget.text.length - 1;
           // Append random char temporarily
           _displayedText = widget.text.substring(0, safeI) + 
              _chars[DateTime.now().millisecond % _chars.length];
        });
      }

      setState(() {
        _displayedText = widget.text.substring(0, i + 1);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return widget.builder(context, _displayedText);
  }
}
