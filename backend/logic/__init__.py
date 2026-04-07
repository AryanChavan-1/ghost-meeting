"""
logic — Ghost Meeting AI & Logic Package (Person 3: Shreya)

Exports the KeywordScanner (from scanner) and the summarize functions
(from summarizer) so they can be cleanly imported by the FastAPI server.

Usage:
    from logic.scanner import KeywordScanner, Snippet
    from logic.summarizer import summarize_snippet, summarize_meeting
"""

from importlib import import_module

# Dynamic imports to handle the parenthesized filenames
_scanner_mod = import_module(".scanner(Shreya)", package=__name__)
_summarizer_mod = import_module(".summarizer(Shreya)", package=__name__)

# Re-export public API
KeywordScanner = _scanner_mod.KeywordScanner
Snippet = _scanner_mod.Snippet
summarize_snippet = _summarizer_mod.summarize_snippet
summarize_meeting = _summarizer_mod.summarize_meeting

__all__ = [
    "KeywordScanner",
    "Snippet",
    "summarize_snippet",
    "summarize_meeting",
]
