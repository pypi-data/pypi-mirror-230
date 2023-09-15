from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, Awaitable, ParamSpec

if TYPE_CHECKING:
    from typing import Callable, Optional


P = ParamSpec("P")
R = TypeVar("R", Awaitable[bool], bool)


class ValidatorError:
    def __init__(self, condition: str, error_message: str) -> None:
        self.condition = condition
        self.error_message = error_message

    def __eq__(self, other: object) -> bool:
        if (
            isinstance(other, ValidatorError)
            and self.condition == other.condition
            and self.error_message == other.error_message
        ):
            return True
        return False

    def __hash__(self):
        return hash((self.condition, self.error_message))

    def __str__(self) -> str:
        return f"ValidatorError(condition='{self.condition}', error_message='{self.error_message}')"  # noqa

    def __repr__(self) -> str:
        return f"ValidatorError(condition='{self.condition}', error_message='{self.error_message}')"  # noqa


class _BaseSubvalidator(ABC, Generic[P, R]):
    @property
    @abstractmethod
    def name(self) -> str:
        """Not Implemented"""

    @property
    @abstractmethod
    def message_if_fails(self) -> str:
        """Not Implemented"""

    @property
    @abstractmethod
    def callable(self) -> Callable[P, R]:
        """Not Implemented"""

    @property
    @abstractmethod
    def args(self):
        """Not Implemented"""

    @property
    @abstractmethod
    def kwargs(self):
        """Not Implemented"""


class BaseSubvalidator(_BaseSubvalidator[P, R]):
    _callable: Callable[P, R]

    def __init__(
        self,
        name: str,
        message_if_fails: str,
        callable: Callable[P, R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        self._name = name
        self._message_if_fails = message_if_fails
        self._callable = callable
        self._args = args
        self._kwargs = kwargs

    @property
    def name(self) -> str:
        return self._name

    @property
    def message_if_fails(self) -> str:
        return self._message_if_fails

    @property
    def callable(self) -> Callable[P, R]:
        return self._callable

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs

    def _return_result(
        self, is_condition_valid: bool
    ) -> Optional[ValidatorError]:
        if is_condition_valid is False:
            return ValidatorError(self._name, self._message_if_fails)
        return None
