from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING
from pycsi.utils.BaseSubValidator import P, BaseSubvalidator

if TYPE_CHECKING:
    from typing import Optional
    from pycsi.utils.BaseSubValidator import ValidatorError


class BaseSyncSubvalidator(BaseSubvalidator[P, bool]):
    @abstractmethod
    def run(self) -> Optional[ValidatorError]:
        """Not implemented"""


class Subvalidator(BaseSyncSubvalidator):
    def run(self) -> Optional[ValidatorError]:
        is_condition_valid = self._callable(*self._args, **self._kwargs)
        return self._return_result(is_condition_valid)
