from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Pattern

from src.infrastructure.monitoring.logger import logger


@dataclass
class ModerationResult:
    sanitized_text: str
    flagged: bool
    reason: str | None = None


class ContentRejectedError(Exception):
    def __init__(self, reason: str, sanitized_text: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.sanitized_text = sanitized_text


class ContentFilter:
    """Примитивная фильтрация сообщений от нецензурной лексики и запрещённого контента."""

    def __init__(self, banned_terms: Iterable[str] | None = None) -> None:
        self.banned_terms = tuple(sorted(set(banned_terms or []), key=len, reverse=True))
        self._pattern: Pattern[str] | None = None
        if self.banned_terms:
            escaped = [re.escape(term) for term in self.banned_terms]
            self._pattern = re.compile(rf"\b({'|'.join(escaped)})\b", re.IGNORECASE)

    def evaluate(self, text: str, *, context: dict | None = None) -> ModerationResult:
        if not text or not self._pattern:
            return ModerationResult(sanitized_text=text, flagged=False)

        matches = list(self._pattern.finditer(text))
        if not matches:
            return ModerationResult(sanitized_text=text, flagged=False)

        sanitized = self._pattern.sub(lambda match: "*" * len(match.group(0)), text)
        reason = "Message contains prohibited language"

        logger.security(
            "chat_message_blocked",
            user_id=(context or {}).get("user_id"),
            ip_address=(context or {}).get("ip_address"),
            reason=reason,
            sanitized=sanitized,
            context=context or {},
        )

        return ModerationResult(sanitized_text=sanitized, flagged=True, reason=reason)

    def enforce(self, text: str, *, context: dict | None = None) -> str:
        result = self.evaluate(text, context=context)
        if result.flagged:
            raise ContentRejectedError(result.reason or "Message rejected", result.sanitized_text)
        return text


default_banned_terms = [
    "черт",
    "блять",
    "сука",
    "пизд",
    "fuck",
    "shit",
]

default_content_filter = ContentFilter(default_banned_terms)



