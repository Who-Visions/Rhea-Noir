# Task Plan: Installing Stitch API Skills

## Goal
Install and configure the Stitch API skills (`design-md` and `react-components`) to enable advanced design-to-code capabilities for Rhea/Antigravity.

## Phases

### Phase 1: Preparation
- [x] Update `task.md` with new objective.

### Phase 2: Installation
- [ ] Clone `stitch-skills` repo to temporary directory.
- [ ] Inspect repository structure.
- [ ] Install `design-md` skill to `.agent/skills/`.
- [ ] Install `react-components` skill to `.agent/skills/`.

### Phase 3: Configuration (If needed)
- [ ] Verify `SKILL.md` contents.
- [ ] Install any dependencies (if scripts require them).

### Phase 4: Verification
- [ ] List installed skills to confirm availability.
- [ ] Simple test of `design-md` (if applicable without full context).

### Phase 5: Verification
- [x] Launch app on Windows (`flutter run -d windows`).
- [x] Verify visual effects manually.

### Phase 6: Stitch Skill Validation
- [x] Analyze Rhea Mobile Command (`main.dart`) using `design-md` principles.
- [x] Synthesize `DESIGN.md` for proper Rhea styling.
- [x] Verify `DESIGN.md` follows semantic naming conventions.

### Phase 7: Rhea Design CLI
- [x] Create `rhea_cli.py` using `rich`.
- [x] Integrate File Planning (`task_plan.md` viewer/editor).
- [x] Integrate Flutter Design workflow (`design-md` + `flutter run`).
### Phase 7: Rhea Design CLI
- [x] Create `rhea_cli.py` using `rich`.
- [x] Integrate File Planning (`task_plan.md` viewer/editor).
- [x] Integrate Flutter Design workflow (`design-md` + `flutter run`).
- [x] Verify CLI interactivity.

### Phase 8: Elevation & Refactoring
- [x] Implement `void.frag` shader.
- [x] Add Google Fonts & Shaders to `pubspec.yaml`.
- [x] Implement `VoidBackground` (Shader-based).
- [x] Implement `GlitchText` (Cybernetic Header).
- [x] Refactor widgets into `lib/widgets/` for cleanliness.

### Phase 9: Dashboard Redesign (Full Screen)
- [x] Remove `ListView` scrolling.
- [x] Implement Dense Grid Layout (Variants + Assets).
- [x] Optimize sized for "Cybernetic Density" (reduce oversized elements).
- [x] Verify "No Scroll" on standard window size.

### Phase 10: Chat UI Overhaul (3-Pane)
- [x] Implement 3-Column Layout (Sidebar, Main Chat, Diagnostics).
- [x] **Left Panel**: Projects, Groups, History list.
- [x] **Center Panel**: "Command Log" style chat, floating input, action pills.
- [x] **Right Panel**: System Diagnostics (Uplink, Graphs, Active Units).
- [x] **Aesthetics**: Match "Deep Purple/Cyan" #1A0B2E palette from reference.of `design-md` (if applicable without full context).
