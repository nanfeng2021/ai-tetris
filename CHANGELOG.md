# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- 🧪 Add frontend unit tests for web/game_optimized.js
- 🔧 Add CI/CD pipeline with GitHub Actions
- 📊 Add Grafana dashboard configurations
- 🤖 Enhance AI decision algorithm with deep learning

---

## [5.0.0] - 2026-03-31

### Added
- ✨ Client-side prediction architecture for Web version
- 🎮 Full game logic running in browser
- ⚡ `requestAnimationFrame` for smooth 60 FPS animations
- 🔄 Local validation + async sync mode

### Changed
- 🚀 Operation response: 150ms → <1ms (**150x improvement**)
- 📈 Render frame rate: 30 FPS → 60 FPS (**2x improvement**)
- 📉 API calls: Once per frame → Only on initialization (**99% reduction**)

### Fixed
- ✅ Fixed issue where blocks wouldn't auto-drop
- ✅ Fixed bug where blocks disappeared after reaching bottom
- ✅ Fixed missing bottom border on mobile layout
- ✅ Reset `dropCounter` and `lastTime` for accurate timing

### Technical
- Refactored to client-server architecture
- Implemented local game state management
- Added proper animation loop handling

---

## [4.0.0] - 2026-03-31

### Added
- 📱 Mobile-responsive design improvements
- 🎨 Enhanced CSS for better visual appearance

### Fixed
- ✅ Fixed game area layout issues on mobile devices
- ✅ Added `display: block` to eliminate canvas baseline spacing
- ✅ Optimized padding and margin for mobile screens

---

## [3.0.0] - 2026-03-31

### Added
- 🌐 Initial Web version release
- 💻 Client-side game logic implementation
- 👆 Touch gesture support for mobile
- 🎨 Modern UI with HTML5 Canvas

### Changed
- Migrated from terminal-based to web-based interface
- Improved user experience with visual feedback

---

## [2.0.0] - 2026-03-28

### Added
- 🤖 AI auto-battle mode
- 🧠 Enhanced decision-making algorithm
- 📊 Complete monitoring metrics
- 📈 Prometheus integration

### Changed
- Optimized AI evaluation depth and search algorithm
- Improved game performance and stability

---

## [1.0.0] - 2026-03-27

### Added
- 🎮 Basic game logic implementation
- 🧱 Classic Tetris gameplay (7 tetromino types)
- 🎯 10x20 game board
- ⌨️ Keyboard controls (arrow keys, space, P, R)
- 📊 Score, level, and lines tracking

### Harness Engineering
- 🔒 Guardrails (boundary checks, collision detection)
- ✅ Validators (state consistency checks)
- 📈 Monitors (Prometheus metrics definition)

### Infrastructure
- 🐳 Docker support
- 📦 requirements.txt for dependency management
- 📝 Initial documentation

---

## Version History Summary

| Version | Date | Key Feature |
|---------|------|-------------|
| 5.0.0 | 2026-03-31 | Client-side prediction architecture |
| 4.0.0 | 2026-03-31 | Mobile optimization |
| 3.0.0 | 2026-03-31 | Web version launch |
| 2.0.0 | 2026-03-28 | AI enhancement |
| 1.0.0 | 2026-03-27 | Initial release |

---

## Migration Guide

### From v4 to v5
- No breaking changes
- Performance improvements are automatic
- Recommended to clear browser cache after update

### From v3 to v4
- Mobile users will see improved layout automatically
- No action required

### From v2 to v3
- Web interface replaces terminal UI
- Update bookmarks to new web URL

---

## Contributing

When adding changes:
1. Update the `[Unreleased]` section
2. Follow the Keep a Changelog format
3. Use appropriate categories: Added, Changed, Deprecated, Removed, Fixed, Security
4. Include version number and date in release commit

For more info, see [CONTRIBUTING.md](CONTRIBUTING.md)
