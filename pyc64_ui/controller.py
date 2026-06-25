"""Controller — pure orchestration between UI and compiler.

Zero UI imports.  One job: take source text, run the pipeline,
return structured results.  The UI only calls compile_source()
and renders whatever comes back.
"""

from dataclasses import dataclass, field
from typing import Optional
from pyc64c.compiler import compile_to_prg, compile_source


@dataclass
class CompileResult:
    ok: bool = False
    prg: Optional[bytes] = None
    prg_size: int = 0
    basic_code: str = ''
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    listing: list = field(default_factory=list)
    labels: dict = field(default_factory=dict)
    hex_lines: list = field(default_factory=list)


def hex_dump(data: bytes, addr: int = 0x0801, width: int = 16) -> list:
    """Return list of (offset, hex_str, ascii_str) tuples."""
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_str = ' '.join(f'{b:02X}' for b in chunk)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append((addr + i, hex_str, ascii_str))
    return lines


def compile_source_text(source: str, filename: str = 'untitled') -> CompileResult:
    """Run full pyc64c pipeline.  Returns CompileResult."""
    res = CompileResult()

    prg, cres = compile_to_prg(source)
    if cres.lex_errors:
        res.errors = [f'Lexer [{e.get("line","?")}:{e.get("col","?")}]: {e["msg"]}'
                      for e in cres.lex_errors]
        return res
    if cres.parse_errors:
        res.errors = [f'Parser [{e.get("line","?")}:{e.get("col","?")}]: {e["msg"]}'
                      for e in cres.parse_errors]
        return res

    if prg is None:
        if cres.builder and cres.builder.fixup_errs:
            res.errors = [f'Fixup: {e}' for e in cres.builder.fixup_errs]
        else:
            res.errors.append('Compilation failed: no PRG produced')
        return res

    res.ok = True
    res.prg = prg
    res.prg_size = len(prg)
    res.basic_code = getattr(cres, 'basic_code', '')

    # Extract listing and labels from builder if available
    builder = getattr(cres, 'builder', None)
    if builder:
        res.listing = getattr(builder.e, 'listing', [])
        res.labels = getattr(builder.e, 'labels', {})

    res.hex_lines = hex_dump(prg)

    return res


def compile_source_basic(source: str) -> str:
    """BASIC-only pipeline.  Returns BASIC source string."""
    cres = compile_source(source)
    return getattr(cres, 'basic_code', '')
