from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .fake_function import FakeFunction

PATCHED_FUNCTIONS: list['FakeFunction[..., Any]'] = []
