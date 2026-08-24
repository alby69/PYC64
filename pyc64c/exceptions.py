"""Exception hierarchy for PYC64 compiler components."""

from typing import Optional


class PYC64Error(Exception):
    """Base exception for all PYC64 compiler errors."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        phase: Optional[str] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col
        self.phase = phase or "engine"
        self.source_file = source_file

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "line": self.line,
            "col": self.col,
            "phase": self.phase,
            "source_file": self.source_file,
        }

    def __str__(self) -> str:
        loc = ""
        if self.line is not None:
            loc = f" at line {self.line}"
            if self.col is not None:
                loc += f", col {self.col}"
        phase_str = f"[{self.phase.upper()}] " if self.phase else ""
        return f"{phase_str}{self.message}{loc}"


class LexerError(PYC64Error):
    """Raised when tokenization fails."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            line=line,
            col=col,
            phase="lexer",
            source_file=source_file,
        )


class ParseError(PYC64Error):
    """Raised when parsing fails."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            line=line,
            col=col,
            phase="parser",
            source_file=source_file,
        )


class SemanticError(PYC64Error):
    """Raised during semantic analysis and type checking."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            line=line,
            col=col,
            phase="semantic",
            source_file=source_file,
        )


class CodegenError(PYC64Error):
    """Raised during intermediate/assembly code generation."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            line=line,
            col=col,
            phase="codegen",
            source_file=source_file,
        )


class FixupError(PYC64Error):
    """Raised during assembly resolution / label fixup."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            line=line,
            col=col,
            phase="fixup",
            source_file=source_file,
        )


class SimulationError(PYC64Error):
    """Raised during 6502 simulation."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        col: Optional[int] = None,
        source_file: Optional[str] = None,
    ):
        super().__init__(
            message=message,
            line=line,
            col=col,
            phase="simulation",
            source_file=source_file,
        )
