from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Awaitable
from pycsi.utils.BaseSubValidator import P, BaseSubvalidator

if TYPE_CHECKING:
    from typing import Optional
    from pycsi.utils.BaseSubValidator import ValidatorError


class BaseAsyncSubvalidator(BaseSubvalidator[P, Awaitable[bool]]):
    @abstractmethod
    async def run(self) -> Optional[ValidatorError]:
        """Not implemented"""


class AsyncSubvalidator(BaseAsyncSubvalidator):
    async def run(self) -> Optional[ValidatorError]:
        is_condition_valid = await self._callable(*self._args, **self._kwargs)
        return self._return_result(is_condition_valid)
