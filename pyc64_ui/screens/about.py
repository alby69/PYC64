"""About screen — project info and key bindings."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Markdown
from textual.containers import Vertical
from textual.binding import Binding


ABOUT_TEXT = """# PYC64 — Python-to-C64 Cross-Compiler & 6502 Assembler

**v0.1.0** — Pure Python toolkit per lo sviluppo Commodore 64.

## Key Bindings

| Key | Action |
|-----|--------|
| `Ctrl+S` | Compila |
| `Ctrl+O` | Apri file |
| `Ctrl+Q` | Esci |
| `F1` | Questo help |

## Pipeline

```
Source (.c64) → Lexer → Parser → CodeGen → PRG (.prg)
                                      └→ BASIC (.bas)
```

## Componenti

- **pyc64c/** — compilatore Python→6502 core
- **asm6502.py** — assembler 6502 standalone dual-pass
- **run_c64.py** — CLI per compilazione

## Licenza

GNU GPL v3 — © Leonardo Boselli
"""


class AboutScreen(Screen):
    """Help / about screen."""

    BINDINGS = [
        Binding('escape', 'dismiss', 'Back'),
        Binding('f1', 'dismiss', 'Close'),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(Markdown(ABOUT_TEXT), id='about-content')
        yield Footer()
