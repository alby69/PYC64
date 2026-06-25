"""Status bar for the editor — cursor position, filename, compile status."""

from textual.widgets import Static
from textual.reactive import reactive


class EditorStatusBar(Static):
    """Bottom bar showing filename, Ln/Col, and compile status.

    Uses reactives — setting any attribute triggers auto-refresh.
    """

    cursor_pos = reactive((1, 1))
    filename = reactive('untitled.c64')
    is_modified = reactive(False)
    compile_ok = reactive(None)

    DEFAULT_CSS = """
    EditorStatusBar {
        height: 1;
        padding: 0 2;
        background: $panel;
        color: $text-muted;
    }
    """

    def render(self) -> str:
        fn = self.filename
        if self.is_modified:
            fn = f'[bold yellow]*[/] {fn}'
        line, col = self.cursor_pos
        cursor = f'[dim]Ln {line}, Col {col}[/]'
        status = ''
        if self.compile_ok is True:
            status = '[bold green]✓ OK[/]'
        elif self.compile_ok is False:
            status = '[bold red]✗ Error[/]'
        else:
            status = '[dim]·[/]'
        return f'{fn}  ·  {cursor}  ·  {status}'
