"""Error panel widget — renders compilation errors / warnings."""

from textual.widgets import Static
from textual.reactive import reactive


class ErrorPanel(Static):
    """Shows errors and warnings from compilation."""

    errors: reactive[list] = reactive([])

    def watch_errors(self, errors: list) -> None:
        if not errors:
            self.update('[green]✓ No errors[/]')
        else:
            items = '\n'.join(f'[red]✗ {e}[/]' for e in errors)
            self.update(f'[bold red]Errors ({len(errors)}):[/]\n{items}')
