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
| `Ctrl+S` | Salva e compila |
| `Ctrl+O` | File browser (sorgenti + output) |
| `Ctrl+Q` | Esci |
| `F1` | Questo help |
| `Ctrl+←` | Restringe pannello editor |
| `Ctrl+→` | Allarga pannello editor |
| `Ctrl+↑` | Allarga pannello output (tabs) |
| `Ctrl+↓` | Allarga pannello errori |
| `Enter` | Apri file selezionato |
| `Del` | Cancella file selezionato |
| `←` `→` | Cambia categoria file |

## Pipeline

```
Source (.c64) → Lexer → Parser → CodeGen → PRG (.prg)
                                      └→ BASIC (.bas)
```

## Output directories

| Cartella | Contenuto |
|----------|-----------|
| `output/basic/` | BASIC listing generati |
| `output/asm/` | Sorgenti assembly salvati |
| `output/prg/` | Binari PRG compilati |

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
