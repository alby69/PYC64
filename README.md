# PYC64 — Python-to-C64 Cross-Compiler & TUI Editor

Compila codice **Python-like** in codice macchina nativo **Commodore 64**,
assembla codice **6502** in file `.PRG`,
modifica e compila con una **TUI** (Textual) — tutto in Python puro.

---

## Un comando Docker — tutto incluso

```bash
# Prima build (solo la prima volta)
docker compose build

# TUI + motore: editor, compilazione, BASIC/listing/hex
docker compose run --rm pyc64
```

Oppure con Make:

```bash
make build   # docker compose build
make run     # docker compose run --rm pyc64
```

---

## Altri comandi utili

```bash
# Compila test_python.c64 → output/test_python.prg
docker compose run --rm compile

# Assembla examples/hello.asm → output/hello.prg
docker compose run --rm asm

# Build immagini
docker compose build

# Pulisci output
rm -rf output/*
```

---

## TUI (Textual) — come funziona

```
┌────────── Header ───────────╮
│ ┌─ Editor ──┐ ┌─ Tabs ───┐ │
│ │ sorgente   │ │ BASIC    │ │
│ │ .c64       │ │ Listing  │ │
│ │            │ │ Hex      │ │
│ └────────────┘ └──────────┘ │
│ ┌── Error Panel ───────────┐│
│ │ ✓ No errors              ││
│ └──────────────────────────┘│
└────────── Footer ───────────┘
```

| Tasto | Azione |
|-------|--------|
| `Ctrl+S` | Salva e compila |
| `Ctrl+O` | Apri file |
| `F1` | Guida |
| `Ctrl+Q` | Esci |

---

## Componenti

| Percorso | Ruolo |
|----------|-------|
| `pyc64c/` | Compilatore Python → 6502 (lexer, parser, codegen, runtime, assembler) |
| `pyc64_ui/` | TUI Textual (editor, tabs, controller) |
| `asm6502.py` | Assembler 6502 standalone (dual-pass) |
| `Dockerfile` | Immagine con tutto pre-installato |

**Builtin:** `print`, `println`, `print_at`, `poke`, `peek`, `clear_screen`,
`border_color`, `screen_color`, `wait_frames`, `sei`, `cli`

---

## Struttura

```
pyc64c/                  # Compilatore
  compiler.py            #   Pipeline orchestrator
  lexer.py, parser.py    #   Analisi
  code_gen.py            #   Code generator AST → 6502
  code_emitter.py        #   Emitter 6502 (label, fixup)
  prg_builder.py         #   Builder PRG (BASIC stub + code + runtime)
  runtime.py             #   Runtime 6502 (print, cls, wait, mul)
  basic_gen.py           #   BASIC listing fallback
  asm6502.py             #   Assembler 6502 dual-pass
pyc64_ui/                # TUI
  app.py                 #   Entry point Textual
  controller.py          #   Orchestrazione (zero UI import)
  screens/editor.py      #   Schermata principale
  screens/about.py       #   Help
  widgets/               #   HexViewer, ListingView, ErrorPanel
examples/hello.asm       # Esempio assembly
test_python.c64          # Esempio Python-like (sprite, joystick, score)
```

---

## Licenza

GNU General Public License v3.0 — Copyright © Leonardo Boselli

Progetto realizzato con [Claude](https://claude.ai) di Anthropic · [youdev.it](https://www.youdev.it)
