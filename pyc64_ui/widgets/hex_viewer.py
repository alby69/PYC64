"""Hex viewer widget — renders byte array as classic hex dump."""

from textual.widgets import Static
from textual.reactive import reactive


class HexViewer(Static):
    """Displays a hex dump (address | hex | ASCII)."""

    data: reactive[bytes] = reactive(b'')

    def watch_data(self, data: bytes) -> None:
        self.update(self._fmt(data))

    @staticmethod
    def _fmt(data: bytes, addr: int = 0x0801) -> str:
        lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i + 16]
            hex_str = ' '.join(f'{b:02X}' for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f'{addr + i:04X}  {hex_str:<48s}  {ascii_str}')
        return '\n'.join(lines)
