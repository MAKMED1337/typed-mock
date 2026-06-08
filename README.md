# typed-mock

Typed mocks for Python 3.13+.

Mocks are configured from real callable references, so type checkers can see the
function or method being mocked.

## Install

```bash
pip install typed-mock
```

## Mock an object

```python
from typed_mock import FOREVER, Mocker


class Service:
    def get_user(self, user_id: int) -> str:
        return "real"


mocker = Mocker()
service = mocker.mock(Service)

mocker.when(service.get_user).return_("alice", times=FOREVER)

assert service.get_user(1) == "alice"
assert service.get_user(2) == "alice"
```

## Mock a function

```python
from typed_mock import Mocker


def price() -> int:
    return 10


with Mocker() as mocker:
    mocker.when(price).return_(99)
    assert price() == 99

assert price() == 10
```

## Return multiple values

```python
from typed_mock import Mocker


class Counter:
    def next(self) -> int:
        return 0


mocker = Mocker()
counter = mocker.mock(Counter)

mocker.when(counter.next).return_(1, 2, 3)

assert counter.next() == 1
assert counter.next() == 2
assert counter.next() == 3
```

## Match arguments

```python
from typed_mock import Mocker


class Calculator:
    def add(self, x: int, y: int) -> int:
        return x + y


mocker = Mocker()
calculator = mocker.mock(Calculator)

mocker.when(calculator.add).called_with(1, 2, return_=10)

assert calculator.add(1, 2) == 10
```

## Raise errors

```python
from typed_mock import Mocker


class Client:
    def fetch(self) -> str:
        return "ok"


class FetchError(Exception):
    pass


mocker = Mocker()
client = mocker.mock(Client)

mocker.when(client.fetch).raise_(FetchError)

client.fetch()
```

## Async functions

```python
from typed_mock import Mocker


class Api:
    async def load(self, item_id: int) -> str:
        return "real"


async def test_load() -> None:
    mocker = Mocker()
    api = mocker.mock(Api)

    mocker.when(api.load).called_with(1, return_="mocked")

    assert await api.load(1) == "mocked"
```
