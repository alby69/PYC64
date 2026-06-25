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

ROOT = Path('/app/source') if Path('/app/source').exists() else Path.cwd()


class EditorScreen(Screen):
    """Main screen: code editor on left, output tabs on right."""

    BINDINGS = [
        Binding('ctrl+s', 'save_compile', 'Save+Compile'),
        Binding('ctrl+o', 'browse_files', 'Browse'),
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
                '        print("SCORE: ")\n'
                '        print(score)\n'
                '        wait_frames(1)\n'
            )

    def action_compile(self) -> None:
        self._compile_and_save_outputs()

    def _update_title(self) -> None:
        name = self.current_path.name if self.current_path else 'untitled.c64'
        self.query_one('#source-label', Static).update(f'[bold]{name}[/]')

    def _save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.query_one('#editor', TextArea).text)
        self.current_path = path
        self._update_title()

    # ── File Browser integration ──

    def action_browse_files(self) -> None:
        """Browse all project files: sources, BASIC, ASM, PRG."""
        from pyc64_ui.screens.file_browser import FileBrowser

        def on_pick(result):
            if result is None:
                return
            action, path = result
            if action == 'open':
                if path.suffix == '.prg':
                    self.notify('PRG files are binaries — run in emulator')
                    return
                self.current_path = path
                self.query_one('#editor', TextArea).text = path.read_text()
                self._update_title()
                self.action_compile()

        self.app.push_screen(FileBrowser(current_mode='c64'), on_pick)

    # ── Save + Compile ──

    def action_save_compile(self) -> None:
        if self.current_path:
            self._save(self.current_path)
        else:
            self._save_as()
            return
        self._compile_and_save_outputs()

    def _compile_and_save_outputs(self) -> None:
        """Compile, update UI tabs, and save BASIC/PRG to output/."""
        source = self.query_one('#editor', TextArea).text
        result = compile_source_text(source)

        err_panel = self.query_one('#errors', ErrorPanel)
        err_panel.errors = result.errors

        if not result.ok:
            return

        # Update output tabs
        self.query_one('#basic-text', Static).update(
            result.basic_code or '(no BASIC output)'
        )
        lv = self.query_one('#listing-view', ListingView)
        lv.entries = result.listing
        hw = self.query_one('#hex-view', HexViewer)
        hw.data = result.prg or b''

        # Save generated files to output/{basic,prg}/
        base = self.current_path.stem if self.current_path else 'untitled'
        if result.basic_code:
            p = ROOT / f'output/basic/{base}.bas'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(result.basic_code)
        if result.prg:
            p = ROOT / f'output/prg/{base}.prg'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(result.prg)

    def _save_as(self) -> None:
        from textual.screen import ModalScreen
        from textual.widgets import Input, Label, Button
        from textual.containers import Vertical, Horizontal as H

        class SaveAsScreen(ModalScreen):
            DEFAULT_CSS = """
            SaveAsScreen { align: center middle; }
            #save-dialog { width: 50; height: 10; border: thick $primary; }
            Input { margin: 1 2; }
            Button { margin: 0 1; }
            """

            def compose(self):
                with Vertical(id='save-dialog'):
                    yield Label('[bold]Save as[/]')
                    yield Input(placeholder='filename.c64')
                    with H():
                        yield Button('Save', variant='primary', id='save-btn')
                        yield Button('Cancel', id='cancel-btn')

            def on_input_submitted(self, event):
                self._do_save(event.value.strip())

            def on_button_pressed(self, event):
                if event.button.id == 'save-btn':
                    inp = self.query_one(Input)
                    self._do_save(inp.value.strip())
                elif event.button.id == 'cancel-btn':
                    self.dismiss(None)

            def _do_save(self, name):
                if not name:
                    self.notify('Enter a filename', severity='error')
                    return
                if '.' not in name:
                    name += '.c64'
                self.dismiss(ROOT / name)

        def on_save(path):
            if path:
                self._save(path)
                self._compile_and_save_outputs()

        self.app.push_screen(SaveAsScreen(), on_save)

    def action_quit(self) -> None:
        self.app.exit()
