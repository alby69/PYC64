"""Listing viewer widget — renders annotated 6502 assembly listing."""

from textual.widgets import Static
from textual.reactive import reactive


class ListingView(Static):
    """Displays compiler listing (addr | bytes | mnemonic | operands)."""

    entries: reactive[list] = reactive([])

    def watch_entries(self, entries: list) -> None:
        self.update(self._fmt(entries))

    @staticmethod
    def _fmt(entries: list) -> str:
        lines = []
        for e in entries:
            addr = e.get('addr', 0)
            bs = ' '.join(f'{b:02X}' for b in e.get('bytes', []))
            pad = f'{bs:<20s}'
            if e.get('isLabel'):
                lines.append(f'{addr:04X}  {pad}  {e.get("labelName","")}:')
            elif e.get('isData'):
                lines.append(f'{addr:04X}  {pad}  .byte {e.get("op","")}')
            elif e.get('fixup'):
                lines.append(f'{addr:04X}  {pad}  {e.get("mnem",""):6s} {e.get("op","")}  [fix]')
            elif bs:
                lines.append(f'{addr:04X}  {pad}  {e.get("mnem",""):6s} {e.get("op","")}')
        return '\n'.join(lines)
