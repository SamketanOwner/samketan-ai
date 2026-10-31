"""Provider-neutral, bounded research gateway for Samketan AI.

Providers are injected and explicitly registered. This module does not scrape,
make network calls, expose secrets, or assume that a lead is verified.
"""
from dataclasses import dataclass, field
from typing import Callable, Mapping
from urllib.parse import urlparse


@dataclass(frozen=True)
class ResearchEvidence:
    title: str
    source_url: str
    excerpt: str = ""

    def is_valid(self) -> bool:
        url = urlparse(self.source_url)
        return url.scheme == "https" and bool(url.hostname) and bool(self.title.strip())


@dataclass(frozen=True)
class LeadCandidate:
    company: str
    region: str
    evidence: tuple[ResearchEvidence, ...] = field(default_factory=tuple)
    decision_maker: str = ""
    business_email: str = ""
    status: str = "candidate"

    @property
    def evidence_backed(self) -> bool:
        return bool(self.evidence) and all(item.is_valid() for item in self.evidence)


class ResearchGateway:
    """Calls an explicitly registered provider, with a result-count ceiling."""

    def __init__(self, max_results: int = 25):
        if not 1 <= max_results <= 100:
            raise ValueError("max_results must be between 1 and 100")
        self.max_results = max_results
        self._providers: dict[str, Callable[[str, int], list[LeadCandidate]]] = {}

    def register(self, name: str, provider: Callable[[str, int], list[LeadCandidate]]) -> None:
        if not name or not name.isidentifier() or name in self._providers:
            raise ValueError("Provider name must be unique and a valid identifier")
        self._providers[name] = provider

    def discover(self, provider_name: str, query: str, limit: int = 10) -> list[LeadCandidate]:
        if provider_name not in self._providers:
            raise ValueError("Unknown provider")
        if not query.strip() or not 1 <= limit <= self.max_results:
            raise ValueError("Invalid query or result limit")
        records = self._providers[provider_name](query, limit)
        if not isinstance(records, list) or any(not isinstance(x, LeadCandidate) for x in records):
            raise TypeError("Provider returned invalid lead records")
        return records[:limit]
