from __future__ import annotations
import dataclasses

from typing import List, ClassVar
from typing_extensions import Self

from ..results.operation_result import OperationResult


@dataclasses.dataclass
class ContainerSignResult(OperationResult):
    """ContainerOperationResult model."""

    ResultType: ClassVar[OperationResult]
    signed_claims: List[str]
    signing_key: str

    def to_dict(self: Self):
        """Return dict representation of ContainerOperationResult."""
        return {"signed_claims": self.signed_claims, "signing_key": self.signing_key}
