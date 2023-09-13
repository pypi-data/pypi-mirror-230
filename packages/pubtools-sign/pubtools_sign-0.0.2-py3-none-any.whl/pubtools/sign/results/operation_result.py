from __future__ import annotations

from abc import ABC, abstractmethod
import dataclasses


@dataclasses.dataclass()
class OperationResult(ABC):
    """OperationResult abstract class."""

    @abstractmethod
    def to_dict(self: OperationResult):
        """Return dict representation of OperationResult."""
        ...  # pragma: no cover
