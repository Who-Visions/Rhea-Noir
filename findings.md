# Findings Log

## Research & Discoveries

### Connection to Rhea Server
- **Discovery**: Mobile app connects to `localhost:8081` (Rhea Server) via `localhost:8000` (Bridge).
- **Impact**: Any changes to server logic (searching, memory) are immediately available to the app once specialized UI displays them.

### Flutter Animation Controller
- **Constraint**: `AnimationController` needs `SingleTickerProviderStateMixin`.
- **Solution**: Widgets like `_VariantCard` and `_CyberneticTypingEffect` must be StatefulWidgets to manage their own controllers.

## Errors & Fixes

### Build Lock (LNK1168)
- **Error**: `fatal error LNK1168: cannot open ... rhea_mobile_command.exe for writing`.
- **Cause**: The application is already running and holding a lock on the executable.
- **Fix**: Kill `rhea_mobile_command.exe` before rebuilding.
