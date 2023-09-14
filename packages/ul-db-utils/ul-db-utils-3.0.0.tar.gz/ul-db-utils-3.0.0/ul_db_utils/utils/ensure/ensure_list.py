from typing import Any, List, Callable, Optional


def ensure_list(some: List[Any], inner_ensure: Optional[Callable[[Any], Any]] = None) -> List[Any]:
    assert isinstance(some, list), f'{type(some).__name__} given'
    if inner_ensure is None:
        return some
    for item in some:
        inner_ensure(item)
    return some
