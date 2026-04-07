"""
scanner.py — Keyword Scanner Module (Person 3: Shreya)

Scans a continuous stream of meeting transcript text for trigger words
and extracts contextual snippets around each match.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Snippet:
    """Represents an important snippet extracted around a trigger word."""
    trigger: str
    context: str       # The ~100-word window (50 before + trigger + 50 after)
    position: int      # Word-index of the trigger in the overall stream


class KeywordScanner:
    """
    Accepts continuous incoming text strings from the transcription layer.
    Maintains a rolling buffer of the last 200 words and scans for an
    array of configurable trigger words using regex matching.

    When a trigger is detected it extracts the 50 words before and
    50 words after the trigger to form an "Important Snippet".
    """

    DEFAULT_BUFFER_SIZE = 200
    CONTEXT_WINDOW = 50          # words before / after the trigger

    def __init__(
        self,
        trigger_words: Optional[List[str]] = None,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        context_window: int = CONTEXT_WINDOW,
    ):
        """
        Args:
            trigger_words:  List of words / phrases to watch for
                            (e.g. ["action item", "deadline", "John Doe"]).
            buffer_size:    Max number of words kept in the rolling buffer.
            context_window: Number of words to capture before & after trigger.
        """
        self.trigger_words: List[str] = trigger_words or []
        self.buffer_size = buffer_size
        self.context_window = context_window

        self._word_buffer: List[str] = []      # rolling word list
        self._total_words_seen: int = 0         # lifetime counter
        self._seen_positions: set = set()       # avoid duplicate snippets

        # Pre-compile the regex pattern for performance
        self._pattern: Optional[re.Pattern] = None
        self._compile_pattern()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_trigger_words(self, trigger_words: List[str]) -> None:
        """Replace the current trigger-word list and recompile the regex."""
        self.trigger_words = trigger_words
        self._seen_positions.clear()
        self._compile_pattern()

    def add_trigger_word(self, word: str) -> None:
        """Add a single trigger word to the list."""
        if word and word not in self.trigger_words:
            self.trigger_words.append(word)
            self._compile_pattern()

    def feed(self, text: str) -> List[Snippet]:
        """
        Feed a new chunk of transcript text into the scanner.

        Args:
            text: Raw transcript string (may be a sentence, paragraph, etc.)

        Returns:
            A list of Snippet objects for every trigger word detected in
            the *new* text.  Duplicates at the same position are suppressed.
        """
        if not text or not text.strip():
            return []

        new_words = text.split()
        if not new_words:
            return []

        # Append new words to the buffer
        self._word_buffer.extend(new_words)
        self._total_words_seen += len(new_words)

        # Scan for triggers *before* trimming so we still have full context
        snippets = self._scan_buffer()

        # Trim the buffer to maintain the rolling window
        self._trim_buffer()

        return snippets

    def reset(self) -> None:
        """Clear the buffer and all state (e.g. between meetings)."""
        self._word_buffer.clear()
        self._total_words_seen = 0
        self._seen_positions.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compile_pattern(self) -> None:
        """Build a single compiled regex that matches any trigger phrase."""
        if not self.trigger_words:
            self._pattern = None
            return

        # Escape each phrase and join with alternation; match as whole
        # words where possible.  Using IGNORECASE for resilience to
        # inconsistent transcription casing.
        escaped = [re.escape(w) for w in self.trigger_words]
        joined = "|".join(escaped)
        self._pattern = re.compile(
            rf"\b(?:{joined})\b",
            re.IGNORECASE,
        )

    def _scan_buffer(self) -> List[Snippet]:
        """Search the current word buffer for trigger-word matches."""
        if self._pattern is None:
            return []

        buffer_text = " ".join(self._word_buffer)
        snippets: List[Snippet] = []

        for match in self._pattern.finditer(buffer_text):
            # Convert the character position to a word index
            char_start = match.start()
            word_index = len(buffer_text[:char_start].split()) - 1
            if word_index < 0:
                word_index = 0

            # Compute the "global" word position across the entire stream
            # so we can deduplicate across successive feed() calls.
            buffer_offset = self._total_words_seen - len(self._word_buffer)
            global_pos = buffer_offset + word_index

            if global_pos in self._seen_positions:
                continue
            self._seen_positions.add(global_pos)

            # Extract the context window
            ctx_start = max(0, word_index - self.context_window)
            # Determine how many words the trigger phrase spans
            trigger_word_count = len(match.group().split())
            ctx_end = min(
                len(self._word_buffer),
                word_index + trigger_word_count + self.context_window,
            )
            context_words = self._word_buffer[ctx_start:ctx_end]
            context_text = " ".join(context_words)

            snippets.append(
                Snippet(
                    trigger=match.group(),
                    context=context_text,
                    position=global_pos,
                )
            )

        return snippets

    def _trim_buffer(self) -> None:
        """Keep only the last `buffer_size` words in the rolling buffer."""
        if len(self._word_buffer) > self.buffer_size:
            excess = len(self._word_buffer) - self.buffer_size
            self._word_buffer = self._word_buffer[excess:]
