# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Talon Community repository, a comprehensive voice command set for [Talon](https://talonvoice.com/). It provides extensive voice commands for hands-free computer control, text editing, programming, and application interaction across Mac, Windows, and Linux.

## Development Commands

**Unit Testing:**

```bash
pytest                    # Run test suite
pytest test/specific_test.py  # Run specific test
```

**Integration Testing**:

- Push changes to local Talon user directory with `sync_talon_repo`.
- Wait a couple seconds for Talon to load the changes.
- Use `tail /mnt/c/Users/james/AppData/Roaming/talon/talon.log` to view recent logs (adding flags as needed to view more logs).
- Changed files will show up in logs as `DEBUG [~] c:\path\to\file`, with possible `WARNING` or `ERROR` lines shown afterwards.
- The user will need to manually test any changed functionality.

**Committing**: Always run `sync_talon_repo` after committing or pushing.

**Code Quality:**

```bash
pre-commit run           # Run all formatters and linters on staged files
pre-commit run --files file1.py file2.py  # Run on unstaged files
pre-commit run --all-files  # Run on all files
pre-commit install       # Set up git hooks
```

If pre-commit fails and changes files, rerun it.

**Tools Used:**

- Black (Python formatting)
- isort (import sorting)
- talonfmt (Talon file formatting)
- prettier (general formatting)

## Architecture

**Core Structure:**

- `core/` - Fundamental voice control functionality (editing, keys, mouse, modes, formatters)
- `apps/` - Application-specific commands (180+ apps: VSCode, browsers, terminals, etc.)
- `lang/` - Programming language support (Python, JS, Rust, Go, etc.) with shared tag system
- `tags/` - Reusable functionality modules (browser, file_manager, debugger, terminal)
- `plugin/` - Optional enhancements (mouse control, screenshots, macros, UI components)

**File Types:**

- `.talon` files: Voice command definitions and context matching
- `.py` files: Action implementations and business logic
- `.talon-list` files: Customizable word lists (alphabet, symbols, commands)

**Platform Handling:**

- macOS: Uses `app.bundle` for app identification
- Windows: Uses `app.name` and `app.exe` for reliability
- Web apps: Uses `browser.host` (requires browser extensions on some platforms)

## Key Patterns

**Voice Command Convention:**
Prefer `[object][verb]` over `[verb][object]` (e.g., "file save" not "save file")

**Context Matching:**
Commands automatically activate based on:

- Active application (`app.name`, `app.bundle`, `app.exe`)
- Programming language (`code.language`)
- Feature tags (`tag: browser`, `tag: user.file_manager`)
- Operating system (`os: windows`, `os: mac`, `os: linux`)

**Tag System:**
Modular functionality that applications can implement:

- `user.file_manager` - File operations
- `browser` - Web browsing commands
- `user.multiple_cursors` - Multi-cursor editing
- `user.debugger` - Debugging interface

**Settings Configuration:**

- `settings.talon` - Main user configuration
- Platform-specific settings files (e.g., `settings_mac.talon`)
- Machine-specific settings (e.g., `settings_jwstout_mac.talon`)

## Testing

Test stubs in `/test/stubs/` mock Talon APIs for testing outside the Talon environment. Tests focus on:

- Formatter functions
- Text processing utilities
- Command parsing logic
- Cross-platform compatibility

## Important Notes

When adding new functionality:

- Follow existing naming patterns for voice commands
- Use appropriate context matchers for platform/app targeting
- Implement shared functionality as tags when applicable
- Test across platforms when possible
- Update relevant `.talon-list` files for new vocabulary
