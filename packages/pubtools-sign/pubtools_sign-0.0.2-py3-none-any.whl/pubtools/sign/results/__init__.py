from __future__ import annotations

from abc import ABC, abstractmethod
import dataclasses

from .clearsign import ClearSignResult  # noqa: F401
from .containersign import ContainerSignResult  # noqa: F401


@dataclasses.dataclass()
class SignerResults(ABC):
    """SignerResults abstract class."""

    @abstractmethod
    def to_dict(self: SignerResults):
        """Return dict representation of SignerResults."""
        ...  # pragma: no cover
