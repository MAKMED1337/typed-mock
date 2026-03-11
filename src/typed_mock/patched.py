from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:

    from collections.abc import Callable
    from types import CodeType

    from .fake_function import FakeFunction

PATCHED_FUNCTIONS: dict[int, list['tuple[Callable[..., Any], CodeType, FakeFunction[..., Any]]']] = {}
