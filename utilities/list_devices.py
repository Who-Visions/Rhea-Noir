#!/usr/bin/env python3
"""List audio input devices"""
import sounddevice as sd

print("=== Audio INPUT Devices ===\n")
for i, d in enumerate(sd.query_devices()):
    if d["max_input_channels"] > 0:
        marker = "→ " if "G7" in d["name"] else "  "
        print(f"{marker}{i}: {d['name']} (channels: {d['max_input_channels']})")
