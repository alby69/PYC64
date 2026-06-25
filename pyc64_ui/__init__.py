"""PYC64 UI — TUI editor for Python-to-C64 compilation.

Architecture:
  pyc64_ui/controller.py   ← pure orchestration, no UI imports
  pyc64_ui/widgets/        ← reusable display components
  pyc64_ui/screens/        ← Textual screens (editor, output, about)
  pyc64_ui/app.py          ← Textual app entry point

Downstream:
  pyc64c/                  ← compiler core (untouched)
"""
