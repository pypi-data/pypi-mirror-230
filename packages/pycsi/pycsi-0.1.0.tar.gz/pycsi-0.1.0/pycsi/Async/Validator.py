from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
from pycsi.utils.BaseValidator import BaseValidator
from pycsi.Async.Subvalidator import AsyncSubvalidator

if TYPE_CHECKING:
    from pycsi.Sync.Subvalidator import Subvalidator
    from pycsi.utils.BaseSubValidator import ValidatorError


class BaseAsyncValidator(BaseValidator):
    @property
    @abstractmethod
    def callable_list(self) -> list[Subvalidator | AsyncSubvalidator]:
        """Not implemented yet"""

    @abstractmethod
    def add(
        self, callable_validator: Subvalidator | AsyncSubvalidator
    ) -> None:
        """Not implemented yet"""

    @abstractmethod
    async def run(self) -> None:
        """Not implemented yet"""


class AsyncValidator(BaseAsyncValidator):
    _callable_list: list[Subvalidator | AsyncSubvalidator]
    _unvalidated_set: set[ValidatorError]

    def __init__(self) -> None:
        self._callable_list = []
        self._unvalidated_set = set()

    @property
    def callable_list(self) -> list[Subvalidator | AsyncSubvalidator]:
        return self._callable_list

    @property
    def unvalidated_set(self) -> set[ValidatorError]:
        return self._unvalidated_set

    def add(
        self, callable_validator: Subvalidator | AsyncSubvalidator
    ) -> None:
        self._callable_list.append(callable_validator)

    def clear(self) -> None:
        self._callable_list.clear()

    async def run(self) -> None:
        self._unvalidated_set.clear()
        for subvalidator in self._callable_list:
            await self._run_subvalidator(subvalidator)

    async def _run_subvalidator(
        self, subvalidator: Subvalidator | AsyncSubvalidator
    ) -> None:
        if isinstance(subvalidator, AsyncSubvalidator):
            await self._run_async_validators(subvalidator)
        else:
            self._run_sync_validators(subvalidator)

    async def _run_async_validators(
        self, subvalidator: AsyncSubvalidator
    ) -> None:
        result = await subvalidator.run()
        self._add_to_unvalidated_set_if_error(result)
