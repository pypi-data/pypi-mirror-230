from collections import defaultdict
from typing import Callable, Any, Dict, Generic, TypeVar


class Listener:
    def __init__(self) -> None:
        self._listeners: Dict[str, Any] = defaultdict(list)
        super().__init__()

    def set_value(self, attr: str, val: Any) -> None:
        """Abstracts __setitem__, __setattr__"""

    def _trigger(self, attr: str) -> None:
        if not hasattr(self, "_listeners"):
            # This is necessary, as this class will be subclassed by dataclasses
            # dataclasses will use __setattr__ before calling __post_init__
            return
        for callback in self._listeners[attr]:
            callback()

    def _set(self, attr: str, val: Any) -> None:
        """Each time an attribute is set, check whether it is being watched,
        and if so, run the associated functions."""
        self.set_value(attr, val)
        self._trigger(attr)

    def add_listener(self, attr: str, callback: Callable[[], Any]) -> None:
        """Add a listener to the specified attribute. Each time the value of
        the attribute changes, the specified callback function(s) is called.
        """
        self._listeners[attr].append(callback)


class ClassWithListener(Listener):
    def set_value(self, attr: str, val: Any) -> None:
        super().__setattr__(attr, val)

    def __setattr__(self, attr: str, val: Any) -> None:
        self._set(attr, val)


T = TypeVar("T")


class ListenerWrap(Listener, Generic[T]):
    """Wrapper around an object to listen to."""

    def __init__(self, obj: T) -> None:
        super().__init__()
        self._target = obj

    def set_value(self, attr: str, val: Any) -> None:
        setattr(self._target, attr, val)

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._target, attr)

    def __eq__(self, other: Any) -> bool:
        return bool(self._target == other)

    @property
    def target(self) -> T:
        return self._target

    @target.setter
    def target(self, value: T) -> None:
        self._target = value
        self._trigger_all()

    def _trigger_all(self) -> None:
        for callbacks in self._listeners.values():
            for callback in callbacks:
                callback()
