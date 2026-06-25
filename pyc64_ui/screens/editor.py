"""Main editor screen — code editor with output tabs.

Decoupled: screen only handles layout and user input.
Compilation is delegated to pyc64_ui.controller (zero UI imports).
"""

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, TextArea, TabbedContent, TabPane, Static
from textual.containers import Horizontal, Vertical
from textual.binding import Binding

from pyc64_ui.widgets.hex_viewer import HexViewer
from pyc64_ui.widgets.listing_view import ListingView
from pyc64_ui.widgets.error_panel import ErrorPanel
from pyc64_ui.controller import compile_source_text


class EditorScreen(Screen):
    """Main screen: code editor on left, output tabs on right."""

    BINDINGS = [
        Binding('ctrl+s', 'save_compile', 'Save+Compile'),
        Binding('ctrl+o', 'open_file', 'Open'),
        Binding('ctrl+q', 'quit', 'Quit'),
    ]

    def __init__(self, filepath=None):
        super().__init__()
        self.current_path = Path(filepath) if filepath else None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id='editor-panel'):
                yield Static('[bold]Source (.c64)[/]', id='source-label')
                yield TextArea('', id='editor', language='python')
            with Vertical(id='output-panel'):
                with TabbedContent(id='tabs'):
                    with TabPane('BASIC', id='basic'):
                        yield Static('(compile to see BASIC output)', id='basic-text')
                    with TabPane('Listing', id='listing'):
                        yield ListingView(id='listing-view')
                    with TabPane('Hex', id='hex'):
                        yield HexViewer(id='hex-view')
                yield ErrorPanel(id='errors')
        yield Footer()

    def on_mount(self) -> None:
        editor = self.query_one('#editor', TextArea)
        if self.current_path and self.current_path.exists():
            editor.text = self.current_path.read_text()
            self._update_title()
            self.set_timer(0.05, self.action_compile)
        else:
            editor.text = (
                'score: byte = 0\n'
                '\n'
                'def main():\n'
                '    clear_screen()\n'
                '    while True:\n'
                '        print "SCORE: "\n'
                '        print score\n'
                '        wait_frames(1)\n'
            )

    def action_compile(self) -> None:
        source = self.query_one('#editor', TextArea).text
        result = compile_source_text(source)

        err_panel = self.query_one('#errors', ErrorPanel)
        err_panel.errors = result.errors

        if not result.ok:
            return

        # BASIC tab
        self.query_one('#basic-text', Static).update(
            result.basic_code or '(no BASIC output)'
        )

        # Listing tab
        lv = self.query_one('#listing-view', ListingView)
        lv.entries = result.listing

        # Hex tab
        hw = self.query_one('#hex-view', HexViewer)
        hw.data = result.prg or b''

    def _update_title(self) -> None:
        name = self.current_path.name if self.current_path else 'untitled.c64'
        self.query_one('#source-label', Static).update(f'[bold]{name}[/]')

    def action_save_compile(self) -> None:
        if self.current_path:
            self.current_path.write_text(self.query_one('#editor', TextArea).text)
        else:
            self._save_as()
            return
        self.action_compile()

    def _save_as(self) -> None:
        from textual.screen import ModalScreen
        from textual.widgets import Input, Label
        from textual.containers import Vertical

        class SaveAsScreen(ModalScreen):
            def compose(self):
                yield Vertical(
                    Label('[bold]Save as[/]'),
                    Input(placeholder='filename.c64'),
                    id='dialog',
                )

            def on_input_submitted(self, event):
                path = Path(event.value.strip())
                self.dismiss(path)

        def on_save(path):
            if path:
                self.current_path = path
                path.write_text(self.query_one('#editor', TextArea).text)
                self._update_title()
                self.action_compile()

        self.app.push_screen(SaveAsScreen(), on_save)

    def action_open_file(self) -> None:
        from textual.screen import ModalScreen
        from textual.widgets import Input, Label
        from textual.containers import Vertical

        class FileOpenScreen(ModalScreen):
            def compose(self):
                yield Vertical(
                    Label('[bold]Open file[/]'),
                    Input(placeholder='Path to .c64 source file'),
                    id='dialog',
                )

            def on_input_submitted(self, event):
                path = Path(event.value.strip())
                if path.exists():
                    self.dismiss(path)
                else:
                    self.notify(f'File not found: {path}', severity='error')

        def on_open(path):
            if path:
                self.current_path = path
                editor = self.query_one('#editor', TextArea)
                editor.text = path.read_text()
                self._update_title()
                self.action_compile()

        self.app.push_screen(FileOpenScreen(), on_open)

    def action_quit(self) -> None:
        self.app.exit()
