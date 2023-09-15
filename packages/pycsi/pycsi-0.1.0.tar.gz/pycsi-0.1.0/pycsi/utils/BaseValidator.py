from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycsi.Sync.Subvalidator import Subvalidator
    from pycsi.utils.BaseSubValidator import ValidatorError


class BaseValidator(ABC):
    _unvalidated_set: set[ValidatorError]

    @property
    @abstractmethod
    def unvalidated_set(self) -> set[ValidatorError]:
        """Not implemented yet"""

    @abstractmethod
    def clear(self) -> None:
        """Not implemented yet"""

    def _run_sync_validators(self, subvalidator: Subvalidator) -> None:
        result = subvalidator.run()
        self._add_to_unvalidated_set_if_error(result)

    def _add_to_unvalidated_set_if_error(
        self, result: ValidatorError | None
    ) -> None:
        if result:
            self._unvalidated_set.add(result)
