from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
from pycsi.utils.BaseValidator import BaseValidator

if TYPE_CHECKING:
    from pycsi.Sync.Subvalidator import Subvalidator
    from pycsi.utils.BaseSubValidator import ValidatorError


class BaseSyncValidator(BaseValidator):
    @property
    @abstractmethod
    def callable_list(self) -> list[Subvalidator]:
        """Not implemented yet"""

    @abstractmethod
    def add(self, callable_validator: Subvalidator) -> None:
        """Not implemented yet"""

    @abstractmethod
    def run(self) -> None:
        """Not implemented yet"""


class Validator(BaseSyncValidator):
    _callable_list: list[Subvalidator]
    _unvalidated_set: set[ValidatorError]

    def __init__(self) -> None:
        self._callable_list = []
        self._unvalidated_set = set()

    @property
    def callable_list(self) -> list[Subvalidator]:
        return self._callable_list

    @property
    def unvalidated_set(self) -> set[ValidatorError]:
        return self._unvalidated_set

    def add(self, callable_validator: Subvalidator) -> None:
        self._callable_list.append(callable_validator)

    def clear(self) -> None:
        self._callable_list.clear()

    def run(self) -> None:
        self._unvalidated_set.clear()
        for subvalidator in self._callable_list:
            self._run_sync_validators(subvalidator)
