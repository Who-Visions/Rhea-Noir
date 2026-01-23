---
name: cybernetic-chat
description: Implements a high-density, 3-pane "Command Center" chat interface with Sidebar, Command Log, and System Diagnostics.
---

# Cybernetic Chat Skill

This skill defines the architecture and styling for the "Rhea Command" Chat Interface. It moves away from standard mobile chat layouts to a desktop-class "Command Center" view.

## 1. Layout Architecture (3-Pane)

The interface is divided into three distinct vertical columns locked to the viewport (no window scrolling).

```dart
Row(
  children: [
    // [Pane 1] Sidebar (Projects/History)
    // Width: Fixed ~280px or Flex 2
    Expanded(flex: 2, child: SidebarPanel()),
    
    // [Pane 2] Command Log (Chat)
    // Width: Flex 5 (Main Focus)
    Expanded(flex: 5, child: CommandLogPanel()),
    
    // [Pane 3] Diagnostics (System Status)
    // Width: Fixed ~320px or Flex 2
    Expanded(flex: 2, child: DiagnosticsPanel()),
  ],
)
```

## 2. Visual Language

- **Background**: Deep Void (`#050505`) to Sidebar Deep Purple (`#0F0518`).
- **Borders**: Subtle, semi-transparent lines (`Colors.white.withOpacity(0.1)`).
- **Typography**: 
    - Headers: `Outfit` (Bold, Uppercase, Spaced).
    - Data: `Monospace` (Cyan/Red/Green).

## 3. Component Specs

### Pane 1: Project Sidebar
- **Header**: "PROJECTS", "GROUPS", "OLD CHATS".
- **Items**:
    - Active: `kColorSecondary` tint + Border.
    - Inactive: Transparent.
    - Icon: Neon folder/people icons.

### Pane 2: Command Log (Center)
- **Header**: "RHEA COMMAND" (Large) + "COMMAND LOG" (Status Bar).
- **Messages**:
    - **Rhea**: Full-width "System Block" style. Cyan header bar, dark glass body.
    - **Alerts**: Red specific "SYSTEM ALERT" blocks.
- **Input**:
    - Floating pill at bottom.
    - "Action Pills" (Summarise, Next steps) above input.

### Pane 3: System Diagnostics
- **Sections**: "WATCHTOWER UPLINK STATUS", "ACTIVE COMMAND UNITS", "RESOURCE USAGE".
- **Widgets**:
    - Key-Value Data Rows (Label: Gray, Value: White Mono).
    - Mini Charts (Line charts for CPU/Mem/Net).
    - Audio visualizer bars (simulated).

## 4. Implementation Guide

### Message Bubble (Command Style)
Instead of chat bubbles, use "Log Entries":

```dart
Container(
  margin: EdgeInsets.only(bottom: 16),
  decoration: BoxDecoration(
    color: Colors.white.withOpacity(0.05),
    border: Border(left: BorderSide(color: isAlert ? Colors.red : Colors.cyan, width: 4)),
    borderRadius: BorderRadius.circular(4)
  ),
  child: Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      // Header
      Container(
        color: (isAlert ? Colors.red : Colors.cyan).withOpacity(0.1),
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        child: Text("RHEA ${timestamp}", style: TextStyle(color: accentColor, fontSize: 10)),
      ),
      // Content
      Padding(
        padding: EdgeInsets.all(12),
        child: Text(content, style: TextStyle(fontFamily: "Inter")),
      )
    ],
  )
)
```

## 5. Training Data References
- **Source Image**: `uploaded_image_1769143683783.png`
- **Palette**: #1A0B2E (BG), #00E5FF (Cyan), #FF5252 (Red Alert).
