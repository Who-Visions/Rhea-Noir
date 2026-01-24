import 'package:flutter/material.dart';
import '../main.dart'; // For constants like kColorError

class SystemAlertPanel extends StatefulWidget {
  final String text;
  const SystemAlertPanel({super.key, required this.text});

  @override
  State<SystemAlertPanel> createState() => _SystemAlertPanelState();
}

class _SystemAlertPanelState extends State<SystemAlertPanel> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(vsync: this, duration: const Duration(seconds: 2))..repeat(reverse: true);
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
        return Container(
          width: double.infinity,
          margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 0),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: kColorError.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: kColorError.withValues(alpha: 0.3 + 0.3 * _controller.value),
              width: 1 + 2 * _controller.value,
            ),
            boxShadow: [
              BoxShadow(
                color: kColorError.withValues(alpha: 0.1 * _controller.value),
                blurRadius: 10,
                spreadRadius: 2,
              )
            ],
          ),
          child: Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: kColorError, size: 24),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      "SYSTEM ALERT",
                      style: TextStyle(
                          color: kColorError,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 2),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.text,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 13,
                          fontFamily: "monospace"),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
