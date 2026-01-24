import 'dart:convert';
import 'dart:ui';

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:http/http.dart' as http;

import 'widgets/cybernetic_typing.dart';
import 'widgets/glitch_text.dart';
import 'widgets/system_alert.dart';
import 'widgets/void_background.dart';

// -----------------------------------------------------------------------------
// CONSTANTS & CONFIG
// -----------------------------------------------------------------------------
const String kBridgeUrl = String.fromEnvironment(
  "BRIDGE_URL",
  defaultValue: "https://rhea-noir-145241643240.us-central1.run.app",
);

const Color kColorBg = Color(0xFF050505);
const Color kColorPrimary = Color(0xFF6C63FF);
const Color kColorSecondary = Color(0xFF00E5FF);
const Color kColorError = Color(0xFFCF6679);
const Color kColorSuccess = Color(0xFF00E676);
const Color kColorSurface = Color(0x0DFFFFFF);

// -----------------------------------------------------------------------------
// MAIN ENTRY POINT
// -----------------------------------------------------------------------------
void main() {
  runApp(const ProviderScope(child: RheaCommandApp()));
}

// -----------------------------------------------------------------------------
// ROUTING & APP
// -----------------------------------------------------------------------------
final _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const MainInterface(),
    ),
  ],
);

class RheaCommandApp extends StatelessWidget {
  const RheaCommandApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Rhea Mobile Command',
      routerConfig: _router,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: kColorBg,
        primaryColor: kColorPrimary,
        colorScheme: ColorScheme.fromSeed(
          seedColor: kColorPrimary,
          brightness: Brightness.dark,
          surface: kColorBg,
        ),
        textTheme: const TextTheme(
          bodyMedium: TextStyle(fontFamily: 'Inter', color: Colors.white),
          titleLarge: TextStyle(fontFamily: 'Outfit', fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}

// -----------------------------------------------------------------------------
// MODELS (Immutable)
// -----------------------------------------------------------------------------
enum MessageState { sent, sending, failed }

@immutable
class ChatMessage {
  final String role;
  final String text;
  final DateTime ts;
  final MessageState state;

  ChatMessage({
    required this.role,
    required this.text,
    DateTime? ts,
    this.state = MessageState.sent,
  }) : ts = ts ?? DateTime.now();

  ChatMessage copyWith({
    String? role,
    String? text,
    DateTime? ts,
    MessageState? state,
  }) {
    return ChatMessage(
      role: role ?? this.role,
      text: text ?? this.text,
      ts: ts ?? this.ts,
      state: state ?? this.state,
    );
  }
}

@immutable
class SystemState {
  final String status; // "INIT", "ONLINE", "OFFLINE", "ERROR"
  final List<String> gallery;
  final bool isLoading;

  const SystemState({
    this.status = "INIT",
    this.gallery = const [],
    this.isLoading = true,
  });

  SystemState copyWith({
    String? status,
    List<String>? gallery,
    bool? isLoading,
  }) {
    return SystemState(
      status: status ?? this.status,
      gallery: gallery ?? this.gallery,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

@immutable
class ChatState {
  final List<ChatMessage> messages;
  final bool isTyping;

  const ChatState({
    this.messages = const [],
    this.isTyping = false,
  });

  ChatState copyWith({
    List<ChatMessage>? messages,
    bool? isTyping,
  }) {
    return ChatState(
      messages: messages ?? this.messages,
      isTyping: isTyping ?? this.isTyping,
    );
  }
}

// -----------------------------------------------------------------------------
// PROVIDERS & NOTIFIERS
// -----------------------------------------------------------------------------

// System Notifier
class SystemNotifier extends StateNotifier<SystemState> {
  SystemNotifier() : super(const SystemState()) {
    relinkSystem();
  }

  Future<void> relinkSystem() async {
    state = state.copyWith(isLoading: true);

    // Check Status
    try {
      final s = await http.get(Uri.parse('$kBridgeUrl/health'))
          .timeout(const Duration(seconds: 3));
      state = state.copyWith(status: s.statusCode == 200 ? "ONLINE" : "ERROR");
    } catch (_) {
      state = state.copyWith(status: "OFFLINE");
    }

    // Fetch Gallery
    try {
      final g = await _fetchWithRetry('$kBridgeUrl/gallery');
      if (g != null && g.statusCode == 200) {
        final data = json.decode(g.body);
        final files = (data['files'] as List?)?.map((e) => e.toString()).toList() ?? [];
        state = state.copyWith(gallery: files, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (_) {
      state = state.copyWith(isLoading: false);
    }
  }

  Future<http.Response?> _fetchWithRetry(String url, {int retries = 3}) async {
    for (int i = 0; i < retries; i++) {
      try {
        return await http.get(Uri.parse(url)).timeout(const Duration(seconds: 5));
      } catch (_) {
        if (i == retries - 1) rethrow;
        await Future.delayed(Duration(milliseconds: 500 * (i + 1)));
      }
    }
    return null;
  }
}

final systemProvider = StateNotifierProvider<SystemNotifier, SystemState>((ref) {
  return SystemNotifier();
});

// Chat Notifier
class ChatNotifier extends StateNotifier<ChatState> {
  ChatNotifier() : super(ChatState(messages: [
    ChatMessage(role: "rhea", text: "Rhea-Noir Command Unit v3.0 Online. Awaiting directives.")
  ]));

  Future<void> sendMessage(String text, VoidCallback onScrollRequest, Function(String) onError) async {
    if (text.trim().isEmpty) return;

    final userMsg = ChatMessage(role: "user", text: text, state: MessageState.sending);
    final userIndex = state.messages.length;

    // Optimistic Update
    state = state.copyWith(messages: [...state.messages, userMsg]);
    onScrollRequest();

    try {
      final res = await http.post(
        Uri.parse('$kBridgeUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({"message": text}),
      );

      if (res.statusCode >= 200 && res.statusCode < 300) {
        final data = json.decode(res.body);
        final reply = data['response'] ?? data['reply'] ?? "System error.";

        // Typing Simulation
        state = state.copyWith(isTyping: true);
        onScrollRequest();

        await Future.delayed(const Duration(seconds: 1)); // UX pause

        // Update User Message to Sent and Add Reply
        final updatedMessages = List<ChatMessage>.from(state.messages);
        if (userIndex < updatedMessages.length) {
          updatedMessages[userIndex] = updatedMessages[userIndex].copyWith(state: MessageState.sent);
        }
        updatedMessages.add(ChatMessage(role: "rhea", text: reply.toString()));

        state = state.copyWith(isTyping: false, messages: updatedMessages);
        onScrollRequest();
      } else {
        _handleError(userIndex, "Link error: ${res.statusCode}", onError);
      }
    } catch (e) {
      _handleError(userIndex, "Connection Failed", onError);
    }
  }

  void _handleError(int index, String errorMsg, Function(String) onError) {
    final updatedMessages = List<ChatMessage>.from(state.messages);
    if (index < updatedMessages.length) {
      updatedMessages[index] = updatedMessages[index].copyWith(state: MessageState.failed);
      updatedMessages.add(ChatMessage(role: "rhea", text: "Error: $errorMsg"));
    }
    state = state.copyWith(isTyping: false, messages: updatedMessages);
    onError(errorMsg);
  }
}

final chatProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  return ChatNotifier();
});

// Tab State
final activeTabProvider = StateProvider<int>((ref) => 0);

// -----------------------------------------------------------------------------
// UI IMPLEMENTATION
// -----------------------------------------------------------------------------

class MainInterface extends ConsumerStatefulWidget {
  const MainInterface({super.key});

  @override
  ConsumerState<MainInterface> createState() => _MainInterfaceState();
}

class _MainInterfaceState extends ConsumerState<MainInterface> {
  // Controllers local to UI as they are transient input handlers
  final TextEditingController _chatController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _chatController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _jumpToBottom() {
    // Schedule post-frame to ensure list has updated before scrolling
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 500),
          curve: Curves.fastOutSlowIn,
        );
      }
    });
  }

  void _showError(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message, style: const TextStyle(color: Colors.white)),
        backgroundColor: kColorError.withValues(alpha: 0.8),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  /// Scoped method to handle message sending with try/catch logic
  void _sendMessage() {
    final text = _chatController.text;
    if (text.trim().isEmpty) return;

    try {
      ref.read(chatProvider.notifier).sendMessage(
        text,
        _jumpToBottom,
        _showError,
      );
      _chatController.clear();
    } catch (e) {
      _showError("Failed to dispatch command.");
    }
  }

  @override
  Widget build(BuildContext context) {
    final activeTab = ref.watch(activeTabProvider);
    final systemState = ref.watch(systemProvider);

    return Scaffold(
      body: Stack(
        children: [
          const Positioned.fill(child: VoidBackground()),
          Column(
            children: [
              _buildHeader(systemState.status),
              Expanded(
                child: activeTab == 0
                    ? _buildDashboard(systemState)
                    : _buildChatView(),
              ),
              _buildBottomNav(activeTab),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeader(String status) {
    return Container(
      padding: const EdgeInsets.only(top: 50, left: 24, right: 24, bottom: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const GlitchText("RHEA COMMAND",
                  style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 2)),
              Text("WATCHTOWER UPLINK",
                  style: TextStyle(
                      fontSize: 10,
                      color: Colors.white.withValues(alpha: 0.5))),
            ],
          ),
          _LinkBadge(status: status),
        ],
      ),
    );
  }

  Widget _buildDashboard(SystemState state) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Section 1: Variants (Compact Horizontal Strip)
          _buildSectionHeader("SYSTEM VARIANTS"),
          const SizedBox(height: 8),
          SizedBox(
            height: 90, // Fixed height for compact row
            child: _buildVariantRow(),
          ),
          
          const SizedBox(height: 24),
          
          // Section 2: Assets (Expanded Grid)
          _buildSectionHeader("VISUAL ASSETS"),
          const SizedBox(height: 8),
          Expanded(
            child: state.gallery.isEmpty
                ? Center(
                    child: state.isLoading
                        ? const CircularProgressIndicator()
                        : Text("No assets linked.", 
                            style: TextStyle(color: Colors.white.withValues(alpha: 0.5))),
                  )
                : _buildGalleryGrid(state.gallery),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Row(
      children: [
        Container(width: 4, height: 16, color: kColorSecondary),
        const SizedBox(width: 8),
        Text(title,
            style: const TextStyle(
                color: kColorSecondary,
                fontWeight: FontWeight.bold,
                fontSize: 12, // Cybernetic/Technical Size
                letterSpacing: 1.5)),
        const Spacer(),
        // Reconstruction Line
        Expanded(
          flex: 2,
          child: Container(height: 1, color: kColorSecondary.withValues(alpha: 0.2)),
        ),
      ],
    );
  }

  Widget _buildVariantRow() {
    final variants = [
      {"name": "Prime", "icon": Icons.security, "color": Colors.purpleAccent},
      {"name": "Shadow", "icon": Icons.nightlight_round, "color": Colors.blueAccent},
      {"name": "Queen", "icon": Icons.diamond, "color": Colors.amberAccent},
      {"name": "Ronin", "icon": Icons.flash_on, "color": Colors.cyanAccent},
    ];
    
    return Row(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: variants.map((v) {
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: _VariantCard(
              name: v['name'] as String,
              icon: v['icon'] as IconData,
              color: v['color'] as Color,
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildGalleryGrid(List<String> gallery) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: gallery.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.8,
      ),
      itemBuilder: (context, index) {
        return ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Container(
            color: Colors.white.withValues(alpha: 0.05),
            child: CachedNetworkImage(
              imageUrl: "$kBridgeUrl/assets/${gallery[index]}",
              fit: BoxFit.cover,
              placeholder: (c, u) =>
                  const Center(child: CircularProgressIndicator(strokeWidth: 1)),
              errorWidget: (c, u, e) => const Icon(Icons.broken_image),
            ),
          ),
        );
      },
    );
  }

  Widget _buildChatView() {
    final _chatState = ref.watch(chatProvider);
    final status = ref.watch(systemProvider).status;

    return Row(
      children: [
        // [Pane 1] Sidebar
        Expanded(
          flex: 2,
          child: Container(
            color: const Color(0xFF0F0518), // Deep purple sidebar
            child: _buildSidebar(),
          ),
        ),
        
        // [Pane 2] Command Log (Chat)
        Expanded(
          flex: 5,
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                decoration: BoxDecoration(
                  border: Border(bottom: BorderSide(color: Colors.white.withValues(alpha: 0.1))),
                ),
                child: Row(
                  children: [
                    const Text("COMMAND LOG", style: TextStyle(
                      fontFamily: "Outfit", fontWeight: FontWeight.bold, fontSize: 16, letterSpacing: 1.5,
                      color: kColorSecondary
                    )),
                    const SizedBox(width: 8),
                    const Text("CHANNEL: WATCHTOWER   MODE: CHAT", style: TextStyle(
                      fontSize: 10, color: Colors.white38, letterSpacing: 1.0
                    )),
                    const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          border: Border.all(color: status == "ONLINE" ? kColorSuccess : kColorError),
                           borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(status.toUpperCase(), style: TextStyle(color: status == "ONLINE" ? kColorSuccess : kColorError, fontSize: 10, fontWeight: FontWeight.bold)),
                      )
                  ],
                ),
              ),
              
              // Messages
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(24),
                  itemCount: _chatState.messages.length,
                  itemBuilder: (context, index) {
                    final msg = _chatState.messages[index];
                    return _ChatBubble(message: msg);
                  },
                ),
              ),
              
              // Input Area
              _buildModernInputArea(),
            ],
          ),
        ),
        
        // [Pane 3] Diagnostics
        Expanded(
          flex: 2,
          child: Container(
             color: const Color(0xFF0F0518),
             padding: const EdgeInsets.all(16),
             child: _buildDiagnosticsPanel(),
          ),
        ),
      ],
    );
  }

  Widget _buildSidebar() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const SizedBox(height: 8),
        _buildSidebarHeader("PROJECTS"),
        _buildSidebarItem("Project Chimera", Icons.folder, true),
        _buildSidebarItem("Operation Starlight", Icons.folder, false),
        _buildSidebarItem("Project Profiles", Icons.folder, false),
        const SizedBox(height: 24),
        _buildSidebarHeader("GROUPS"),
        _buildSidebarItem("Rhea Dev Team", Icons.people, false),
        _buildSidebarItem("Outer Rim Collective", Icons.people, false),
        const SizedBox(height: 24),
        _buildSidebarHeader("OLD CHATS"),
        _buildSidebarItem("2023-10-27: Rhea-Blanc", Icons.history, false),
      ],
    );
  }

  Widget _buildSidebarHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 4),
      child: Text(title, style: TextStyle(
        color: Colors.white.withValues(alpha: 0.6),
        fontWeight: FontWeight.bold,
        fontSize: 12,
        letterSpacing: 1.2
      )),
    );
  }

  Widget _buildSidebarItem(String title, IconData icon, bool active) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: active ? kColorSecondary.withValues(alpha: 0.1) : Colors.transparent,
        borderRadius: BorderRadius.circular(8),
        border: active ? Border.all(color: kColorSecondary.withValues(alpha: 0.3)) : null,
      ),
      child: ListTile(
        leading: Icon(icon, color: active ? kColorSecondary : Colors.cyan.withValues(alpha: 0.5), size: 20),
        title: Text(title, style: TextStyle(
          color: active ? Colors.white : Colors.white70,
          fontSize: 13
        )),
        dense: true,
        contentPadding: const EdgeInsets.symmetric(horizontal: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  Widget _buildDiagnosticsPanel() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("SYSTEM DIAGNOSTICS", style: TextStyle(
          fontFamily: "Outfit", fontWeight: FontWeight.bold, letterSpacing: 1.0, fontSize: 13,
          color: Colors.white
        )),
        const SizedBox(height: 24),
        const Text("WATCHTOWER UPLINK STATUS", style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey)),
        const SizedBox(height: 12),
        _buildDataRow("Live Data:", "Live"),
        _buildDataRow("Direct Data:", "14ms"),
        _buildDataRow("Signal Strength:", "98%"),
        _buildDataRow("Latency:", "12ms"),
        _buildDataRow("Encryption:", "AES-256"),
        const SizedBox(height: 24),
        const Text("RESOURCE USAGE", style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.grey)),
        const SizedBox(height: 12),
        const Text("CPU", style: TextStyle(fontSize: 10, color: Colors.grey)),
        Container(
          height: 60,
          margin: const EdgeInsets.symmetric(vertical: 4),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.cyan.withValues(alpha: 0.3)),
            borderRadius: BorderRadius.circular(8),
            gradient: LinearGradient(
              begin: Alignment.bottomCenter,
              end: Alignment.topCenter,
              colors: [Colors.cyan.withValues(alpha: 0.1), Colors.transparent]
            )
          ),
          child: Center(child: Icon(Icons.show_chart, color: Colors.cyan, size: 24)), 
        ),
        const SizedBox(height: 8),
        const Text("Memory", style: TextStyle(fontSize: 10, color: Colors.grey)),
        Container(
          height: 60,
          margin: const EdgeInsets.symmetric(vertical: 4),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.purple.withValues(alpha: 0.3)),
            borderRadius: BorderRadius.circular(8),
             gradient: LinearGradient(
              begin: Alignment.bottomCenter,
              end: Alignment.topCenter,
              colors: [Colors.purple.withValues(alpha: 0.1), Colors.transparent]
            )
          ),
          child: Center(child: Icon(Icons.align_vertical_bottom_rounded, color: Colors.purple, size: 24)),
        ),
      ],
    );
  }

  Widget _buildDataRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
          Text(value, style: const TextStyle(fontSize: 12, color: Colors.white, fontFamily: "monospace")),
        ],
      ),
    );
  }

  Widget _buildModernInputArea() {
     return Container(
       padding: const EdgeInsets.all(16),
       child: Column(
         children: [
            Row(
              children: [
                _buildPill("Summarise"),
                const SizedBox(width: 8),
                _buildPill("Next steps"),
                const SizedBox(width: 8),
                _buildPill("Debug"),
              ],
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _chatController,
              onSubmitted: (_) => _sendMessage(),
              style: const TextStyle(color: Colors.white, fontFamily: "Inter"),
              decoration: InputDecoration(
                hintText: "Issue command...",
                hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.3)),
                filled: true,
                fillColor: const Color(0xFF1E1424),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: Colors.purple.withValues(alpha: 0.3)),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                suffixIcon: InkWell(
                  onTap: _sendMessage,
                  child: Container(
                    margin: const EdgeInsets.all(6),
                    width: 40,
                    decoration: BoxDecoration(
                      color: kColorPrimary,
                      borderRadius: BorderRadius.circular(8)
                    ),
                    child: const Icon(Icons.send_rounded, color: Colors.white, size: 18),
                  ),
                ),
              ),
            ),
         ],
       ),
     );
  }
  
  Widget _buildPill(String text) {
    return GestureDetector(
      onTap: () {
         _chatController.text = text;
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
        ),
        child: Text(text, style: const TextStyle(fontSize: 11, color: Colors.white70)),
      ),
    );
  }

  Widget _buildBottomNav(int activeTab) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 20),
      color: Colors.black.withValues(alpha: 0.8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _NavIcon(
            icon: Icons.dashboard_outlined,
            active: activeTab == 0,
            tooltip: "Dashboard",
            onTap: () => ref.read(activeTabProvider.notifier).state = 0,
          ),
          _NavIcon(
            icon: Icons.chat_bubble_outline,
            active: activeTab == 1,
            tooltip: "Comms Link",
            onTap: () => ref.read(activeTabProvider.notifier).state = 1,
          ),
        ],
      ),
    );
  }
}

// -----------------------------------------------------------------------------
// SUB-WIDGETS
// -----------------------------------------------------------------------------

class _LinkBadge extends StatelessWidget {
  final String status;
  const _LinkBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final online = status == "ONLINE";
    final color = online ? Colors.green : Colors.red;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color, width: 0.5),
      ),
      child: Row(
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 8),
          Text(status,
              style: TextStyle(
                  color: color, fontSize: 10, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

class _VariantCard extends StatefulWidget {
  final String name;
  final IconData icon;
  final Color color;
  const _VariantCard(
      {required this.name, required this.icon, required this.color});

  @override
  State<_VariantCard> createState() => _VariantCardState();
}

class _VariantCardState extends State<_VariantCard>
    with SingleTickerProviderStateMixin {
  bool _isHovered = false;
  late AnimationController _animController;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 200),
    );
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() {
        _isHovered = true;
        _animController.forward();
      }),
      onExit: (_) => setState(() {
        _isHovered = false;
        _animController.reverse();
      }),
      child: GestureDetector(
        onTapDown: (_) => _animController.forward(),
        onTapUp: (_) => _animController.reverse(),
        onTapCancel: () => _animController.reverse(),
        child: ScaleTransition(
          scale: Tween<double>(begin: 1.0, end: 1.05).animate(
            CurvedAnimation(parent: _animController, curve: Curves.easeOut),
          ),
          child: Semantics(
            label: "Variant: ${widget.name}",
            button: true,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              decoration: BoxDecoration(
                color: _isHovered
                    ? widget.color.withValues(alpha: 0.12)
                    : Colors.white.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: _isHovered
                      ? widget.color.withValues(alpha: 0.6)
                      : widget.color.withValues(alpha: 0.3),
                  width: _isHovered ? 1.5 : 1.0,
                ),
                boxShadow: [
                  if (_isHovered)
                    BoxShadow(
                      color: widget.color.withValues(alpha: 0.25),
                      blurRadius: 15,
                      spreadRadius: 2,
                    ),
                ],
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(widget.icon,
                      color: _isHovered ? widget.color : widget.color.withValues(alpha: 0.8),
                      size: 26), // Reduced size
                  const SizedBox(height: 6),
                  Text(
                    widget.name.toUpperCase(),
                    style: TextStyle(
                      fontFamily: "Outfit",
                      fontWeight: FontWeight.bold,
                      fontSize: 11, // Reduced size
                      color: _isHovered ? Colors.white : Colors.white.withValues(alpha: 0.8),
                      letterSpacing: 1.2,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}



class _ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const _ChatBubble({required this.message});

  String _hhmm(DateTime dt) {
    final h = dt.hour.toString().padLeft(2, '0');
    final m = dt.minute.toString().padLeft(2, '0');
    return '$h:$m';
  }

  @override
  Widget build(BuildContext context) {
    if (message.state == MessageState.failed) {
      return Align(
        alignment: Alignment.centerRight,
        child: Container(
          constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.85),
          child: SystemAlertPanel(text: message.text.replaceFirst("Error: ", "")),
        ),
      );
    }
    
    final rhea = message.role == "rhea";
    final accent = rhea ? kColorSecondary : kColorPrimary;

    final statusText = switch (message.state) {
      MessageState.sending => "SENDING",
      MessageState.failed => "FAILED",
      _ => "",
    };

    final metaColor = message.state == MessageState.failed
        ? Colors.redAccent.withValues(alpha: 0.9)
        : Colors.white.withValues(alpha: 0.55);

    return Align(
      alignment: rhea ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: 14),
        constraints:
            BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
        child: GestureDetector(
          onLongPress: () {
            Clipboard.setData(ClipboardData(text: message.text));
            HapticFeedback.lightImpact();
          },
          child: CornerBrackets(
            color: accent,
            child: HudPanel(
              accent: accent,
              padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
              child: Column(
                crossAxisAlignment:
                    rhea ? CrossAxisAlignment.start : CrossAxisAlignment.end,
                children: [
                  Row(
                    mainAxisAlignment:
                        rhea ? MainAxisAlignment.start : MainAxisAlignment.end,
                    children: [
                      if (rhea)
                        Icon(Icons.memory,
                            size: 14, color: accent.withValues(alpha: 0.95)),
                      if (rhea) const SizedBox(width: 8),
                      Text(
                        rhea ? "RHEA" : "YOU",
                        style: TextStyle(
                          fontSize: 10,
                          letterSpacing: 1.2,
                          fontWeight: FontWeight.bold,
                          color: accent.withValues(alpha: 0.95),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        _hhmm(message.ts),
                        style: TextStyle(
                            fontSize: 10,
                            letterSpacing: 0.8,
                            color: Colors.white.withValues(alpha: 0.45)),
                      ),
                      if (statusText.isNotEmpty) ...[
                        const SizedBox(width: 10),
                        Text(
                          statusText,
                          style: TextStyle(
                              fontSize: 10, letterSpacing: 1.0, color: metaColor),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (rhea)
                    CyberneticTypingEffect(
                      text: message.text,
                      // Only auto-play if message is less than 5 seconds old
                      autoPlay: DateTime.now().difference(message.ts).inSeconds < 5,
                      builder: (context, displayText) => MarkdownBody(
                        data: displayText,
                        styleSheet: MarkdownStyleSheet(
                          p: const TextStyle(
                              fontSize: 14, height: 1.45, color: Colors.white),
                          code: TextStyle(
                              backgroundColor: Colors.white.withValues(alpha: 0.1),
                              fontFamily: 'monospace',
                              fontSize: 13),
                          codeblockDecoration: BoxDecoration(
                            color: Colors.black45,
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                      ),
                    )
                  else
                    MarkdownBody(
                      data: message.text,
                      styleSheet: MarkdownStyleSheet(
                        p: const TextStyle(
                            fontSize: 14, height: 1.45, color: Colors.white),
                        code: TextStyle(
                            backgroundColor: Colors.white.withValues(alpha: 0.1),
                            fontFamily: 'monospace',
                            fontSize: 13),
                        codeblockDecoration: BoxDecoration(
                          color: Colors.black45,
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _NavIcon extends StatelessWidget {
  final IconData icon;
  final bool active;
  final String tooltip;
  final VoidCallback onTap;
  const _NavIcon(
      {required this.icon,
      required this.active,
      required this.onTap,
      this.tooltip = ""});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      tooltip: tooltip,
      icon: Icon(icon,
          color: active ? kColorPrimary : Colors.white24, size: 28),
      onPressed: onTap,
    );
  }
}

class HudPanel extends StatelessWidget {
  final Widget child;
  final Color accent;
  final EdgeInsets padding;
  final BorderRadius radius;

  const HudPanel({
    super.key,
    required this.child,
    required this.accent,
    this.padding = const EdgeInsets.all(14),
    this.radius = const BorderRadius.all(Radius.circular(18)),
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: radius,
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 14, sigmaY: 14),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: kColorSurface,
            borderRadius: radius,
            border: Border.all(
                color: accent.withValues(alpha: 0.28), width: 0.9),
            boxShadow: [
              BoxShadow(
                color: accent.withValues(alpha: 0.16),
                blurRadius: 22,
                spreadRadius: 1,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}

class CornerBrackets extends StatelessWidget {
  final Widget child;
  final Color color;

  const CornerBrackets({super.key, required this.child, required this.color});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _CornerBracketPainter(color: color.withValues(alpha: 0.85)),
      child: child,
    );
  }
}

class _CornerBracketPainter extends CustomPainter {
  final Color color;
  const _CornerBracketPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final p = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2;

    const double len = 10;
    const double inset = 6;

    // top left
    canvas.drawLine(
        const Offset(inset, inset), const Offset(inset + len, inset), p);
    canvas.drawLine(
        const Offset(inset, inset), const Offset(inset, inset + len), p);

    // top right
    canvas.drawLine(Offset(size.width - inset, inset),
        Offset(size.width - inset - len, inset), p);
    canvas.drawLine(Offset(size.width - inset, inset),
        Offset(size.width - inset, inset + len), p);

    // bottom left
    canvas.drawLine(Offset(inset, size.height - inset),
        Offset(inset + len, size.height - inset), p);
    canvas.drawLine(Offset(inset, size.height - inset),
        Offset(inset, size.height - inset - len), p);

    // bottom right
    canvas.drawLine(
      Offset(size.width - inset, size.height - inset),
      Offset(size.width - inset - len, size.height - inset),
      p,
    );
    canvas.drawLine(
      Offset(size.width - inset, size.height - inset),
      Offset(size.width - inset, size.height - inset - len),
      p,
    );
  }

  @override
  bool shouldRepaint(covariant _CornerBracketPainter oldDelegate) =>
      oldDelegate.color != color;
}

class HudGridBackground extends StatelessWidget {
  const HudGridBackground({super.key});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _HudGridPainter(),
      child: const SizedBox.expand(),
    );
  }
}

class _HudGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withValues(alpha: 0.035)
      ..strokeWidth = 1;

    const double step = 42;

    for (double x = 0; x <= size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y <= size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }

    final vignette = Paint()
      ..shader = RadialGradient(
        colors: [
          Colors.transparent,
          Colors.black.withValues(alpha: 0.45),
        ],
        radius: 1.0,
        center: Alignment.center,
      ).createShader(Offset.zero & size);

    canvas.drawRect(Offset.zero & size, vignette);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _TypingIndicator extends StatefulWidget {
  final Color accent;
  const _TypingIndicator({required this.accent});

  @override
  State<_TypingIndicator> createState() => _TypingIndicatorState();
}

class _TypingIndicatorState extends State<_TypingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1200))
      ..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return HudPanel(
      accent: widget.accent,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _Dot(controller: _controller, delay: 0.0, color: widget.accent),
          const SizedBox(width: 6),
          _Dot(controller: _controller, delay: 0.2, color: widget.accent),
          const SizedBox(width: 6),
          _Dot(controller: _controller, delay: 0.4, color: widget.accent),
        ],
      ),
    );
  }
}






class _Dot extends StatelessWidget {
  final AnimationController controller;
  final double delay;
  final Color color;

  const _Dot(
      {required this.controller, required this.delay, required this.color});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        final tick = (controller.value + delay) % 1.0;
        final op = tick < 0.5 ? tick * 2 : (1.0 - tick) * 2;

        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.5 + 0.5 * op),
            shape: BoxShape.circle,
          ),
        );
      },
    );
  }
}