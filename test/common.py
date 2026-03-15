from collections.abc import Callable


def ff() -> int:
    return 5


class F:
    """F class"""

    val = 43
    lam: Callable[..., int] = lambda: 5
    func = ff

    def f(self) -> int:
        return 3

    def g(self, x: int, y: int) -> int:
        """Test docstring"""
        return x + y

    @staticmethod
    def st(x: int) -> int:
        return 4 + x

    @classmethod
    def cl(cls, x: int) -> int:
        return cls.val + x

    def mult(self, *_: object, **__: object) -> None:
        return None
