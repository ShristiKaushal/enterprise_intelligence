"""
Provider factory — returns the correct AIProvider based on configuration.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from app.extraction.base import AIProvider
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_provider_instance: Optional[AIProvider] = None


def get_provider(override: Optional[str] = None) -> AIProvider:
    """
    Return the configured AI provider instance.
    Singletons are cached per provider type.
    """
    global _provider_instance

    provider_name = override or settings.AI_PROVIDER

    # Check if we need to create or recreate
    if _provider_instance is None or (
        override and _provider_instance.name != provider_name
    ):
        _provider_instance = _create_provider(provider_name)

    return _provider_instance


def _create_provider(name: str) -> AIProvider:
    name = name.lower().strip()

    if name == "gemini":
        if not settings.GEMINI_API_KEY:
            logger.warning(
                "GEMINI_API_KEY not set — falling back to MockProvider",
                requested_provider="gemini",
            )
            from app.extraction.mock_provider import MockProvider
            return MockProvider()
        from app.extraction.gemini_provider import GeminiProvider
        logger.info("Using GeminiProvider", model=settings.GEMINI_MODEL)
        return GeminiProvider()

    elif name == "openai":
        if not settings.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set — falling back to MockProvider")
            from app.extraction.mock_provider import MockProvider
            return MockProvider()
        from app.extraction.openai_provider import OpenAIProvider
        logger.info("Using OpenAIProvider", model=settings.OPENAI_MODEL)
        return OpenAIProvider()

    elif name == "mock":
        from app.extraction.mock_provider import MockProvider
        logger.info("Using MockProvider (deterministic mode)")
        return MockProvider()

    else:
        logger.warning(
            f"Unknown AI provider '{name}' — falling back to MockProvider",
        )
        from app.extraction.mock_provider import MockProvider
        return MockProvider()


def reset_provider() -> None:
    """Reset the cached provider (useful for testing)."""
    global _provider_instance
    _provider_instance = None
