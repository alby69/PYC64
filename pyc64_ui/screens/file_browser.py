"""File browser modal — browse, open, delete project files.

Directories (relative to project root):
  .             → .c64 sources
  output/basic/ → .bas generated BASIC
  output/asm/   → .asm assembly sources
  output/prg/   → .prg compiled binaries
"""

from pathlib import Path
from datetime import datetime

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static, ListView, ListItem, Label, Footer
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual import log


_root = Path('/app/source') if Path('/app/source').exists() else Path.cwd()

DIRS = {
    'c64': _root,
    'bas': _root / 'output/basic',
    'asm': _root / 'output/asm',
    'prg': _root / 'output/prg',
}

EXT_LABEL = {
    'c64': 'Sources (.c64)',
    'bas': 'BASIC (.bas)',
    'asm': 'Assembly (.asm)',
    'prg': 'Binary (.prg)',
}

EXT_PAT = {
    'c64': '*.c64',
    'bas': '*.bas',
    'asm': '*.asm',
    'prg': '*.prg',
}

MODE_TAB = ['c64', 'bas', 'asm', 'prg']


class FileBrowser(ModalScreen):
    """Modal file browser — categorized by type."""

    DEFAULT_CSS = """
    FileBrowser {
        align: center middle;
    }
    #browser-box {
        width: 70;
        height: 80%;
        border: thick $primary;
        background: $surface;
    }
    #browser-title {
        padding: 1 2;
        background: $primary-background;
        text-style: bold;
    }
    #browser-tabs {
        height: 3;
    }
    .tab-btn {
        width: 1fr;
        height: 3;
        padding: 0 1;
        text-align: center;
    }
    .tab-btn.active {
        text-style: bold;
        color: $primary;
    }
    #file-list {
        height: 1fr;
        margin: 1 0;
    }
    #browser-footer {
        height: 3;
        padding: 0 1;
        background: $primary-background;
    }
    ListItem {
        padding: 0 2;
    }
    ListItem > Label {
        width: 1fr;
    }
    .file-name {
        color: $text;
    }
    .file-detail {
        color: $text-muted;
        text-align: right;
    }
    """

    BINDINGS = [
        Binding('escape', 'dismiss', 'Close'),
        Binding('enter', 'select', 'Open'),
        Binding('delete', 'delete', 'Del'),
        Binding('right', 'next_tab', 'Next'),
        Binding('left', 'prev_tab', 'Prev'),
    ]

    def __init__(self, current_mode='c64'):
        super().__init__()
        self.mode = current_mode if current_mode in MODE_TAB else 'c64'

    def compose(self) -> ComposeResult:
        with Vertical(id='browser-box'):
            yield Static('[bold]File Browser[/]', id='browser-title')
            with Horizontal(id='browser-tabs'):
                for m in MODE_TAB:
                    yield Static(EXT_LABEL[m], classes='tab-btn')
            yield ListView(id='file-list')
            yield Static('', id='browser-footer')
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        dir_path = DIRS[self.mode]
        if self.mode != 'c64':
            dir_path.mkdir(parents=True, exist_ok=True)
        files = sorted(dir_path.glob(EXT_PAT[self.mode]))
        lv = self.query_one('#file-list', ListView)
        lv.clear()
        if not files:
            lv.append(ListItem(Label('[dim italic]  (no files)[/]')))
        for f in files:
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            label = Label(
                f'[bold]{f.name}[/]  [dim]{_fmt_size(size)}  {mtime}[/]'
            )
            lv.append(ListItem(label))
        self._update_tabs()
        self._update_footer()

    def _update_tabs(self) -> None:
        for i, m in enumerate(MODE_TAB):
            btn = self.query('.tab-btn').nodes[i]
            btn.set_class(m == self.mode, 'active')
            count = len(list(DIRS[m].glob(EXT_PAT[m]))) if DIRS[m].exists() else 0
            btn.update(f'{EXT_LABEL[m]} ({count})')

    def _update_footer(self) -> None:
        path = DIRS[self.mode] / '...'
        self.query_one('#browser-footer', Static).update(
            f'[dim]{DIRS[self.mode]}[/]'
        )

    def action_select(self) -> None:
        lv = self.query_one('#file-list', ListView)
        item = lv.highlighted_child
        if item is None:
            return
        label = item.query(Label).first()
        text = label.renderable if hasattr(label, 'renderable') else str(label)
        fname = text.split('[')[2].split(']')[0] if '[' in text else ''
        if not fname or fname == '(no files)':
            return
        path = DIRS[self.mode] / fname
        if path.exists():
            self.dismiss(('open', path))

    def action_delete(self) -> None:
        lv = self.query_one('#file-list', ListView)
        item = lv.highlighted_child
        if item is None:
            return
        label = item.query(Label).first()
        text = label.renderable if hasattr(label, 'renderable') else str(label)
        fname = text.split('[')[2].split(']')[0] if '[' in text else ''
        if not fname or fname == '(no files)':
            return
        path = DIRS[self.mode] / fname
        if path.exists():
            path.unlink()
            self._refresh()
            self.notify(f'Deleted: {fname}')

    def action_next_tab(self) -> None:
        idx = MODE_TAB.index(self.mode)
        self.mode = MODE_TAB[(idx + 1) % len(MODE_TAB)]
        self._refresh()

    def action_prev_tab(self) -> None:
        idx = MODE_TAB.index(self.mode)
        self.mode = MODE_TAB[(idx - 1) % len(MODE_TAB)]
        self._refresh()


def _fmt_size(n: int) -> str:
    if n < 1024:
        return f'{n}B'
    return f'{n/1024:.1f}K'
