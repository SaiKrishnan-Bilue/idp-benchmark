from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Table:
    rows: list[list[str]]
    row_count: int
    column_count: int


@dataclass
class KVPair:
    key: str
    value: str
    confidence: float


@dataclass
class ProviderResult:
    provider: str
    document: str
    pages: int
    latency_ms: float
    raw_text: str
    tables: list[Table] = field(default_factory=list)
    kv_pairs: list[KVPair] = field(default_factory=list)
    error: str | None = None


class BaseProvider(ABC):
    name: str

    @abstractmethod
    def analyze(self, document_path: str) -> ProviderResult:
        """Send a document through the provider and return structured results."""
        ...

    @abstractmethod
    def verify(self) -> bool:
        """Check that credentials and connectivity are working."""
        ...
