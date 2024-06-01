from PyQt5.QtCore import (
    QObject,
    QTimer,
    pyqtSignal,
    pyqtBoundSignal,
)

from functools import partial
from typing import TypeVar, Generic, Any, Callable, Iterable, cast


T = TypeVar("T")
class RefAttr(Generic[T]):
    """Descriptor for one shallow reactive value."""

    def __init__(self, expected_type: type[T]):
        # self.signal = pyqtSignal(expected_type)
        pass

    def __set_name__(self, owner_class: type, attr_name: str):
        self.__ref_name = f"{attr_name}_ref"
        # self.__signal_name = f"{attr_name}_change"

    def __get__(self, instance: Any, owner_class: type) -> T:
        if instance is None:
            return self
        return cast(Ref[T], getattr(instance, self.__ref_name)).value

    def __set__(self, instance: Any, value: T):
        if not hasattr(instance, self.__ref_name):
            setattr(instance, self.__ref_name, Ref(value))
        else:
            cast(Ref[T], getattr(instance, self.__ref_name)).value = value

        # setattr(instance, self.__private_attr_name, value)
        # cast(pyqtBoundSignal, getattr(instance, self.__signal_name)).emit(value)

    def ref_getter(self) -> "_RefGetter[T]":
        return _RefGetter()


class _RefGetter(Generic[T]):
    def __set_name__(self, owner_class: type, attr_name: str):
        self.__private_attr_name = f"__{owner_class.__name__}_{attr_name}"

    def __get__(self, instance: Any, owner_class: type) -> "Ref[T]":
        if instance is None:
            return self
        return getattr(instance, self.__private_attr_name)

    def __set__(self, instance: Any, value: "Ref[T]"):
        setattr(instance, self.__private_attr_name, value)


class Ref(QObject, Generic[T]):
    change = pyqtSignal(object) # T

    def __init__(self, value: T):
        super().__init__()
        self.__value = value

    @property
    def value(self) -> T:
        return self.__value

    @value.setter
    def value(self, value: T):
        self.__value = value
        self.change.emit(value)

    def set(self, value: T):
        """Alias for `value` setter"""
        # so values can be set from lambdas
        self.value = value


def _create_computed(handler: Callable[[], T]):
    ref = Ref(handler())

    def recompute_value():
        # Blocking signals prevents a computed ref from recalculating multiple times due to simulataneous changes
        if ref.signalsBlocked(): return

        ref.value = handler()

        ref.blockSignals(True)
        QTimer.singleShot(0, lambda: ref.blockSignals(False))

    return ref, recompute_value


def computed(handler: Callable[[], T], *dependency_refs: Ref[T]):
    ref, recompute = _create_computed(handler)
    for dependency in dependency_refs:
        dependency.change.connect(recompute)

    return ref


def computed_on_signal(handler: Callable[[], T], dependency_signal: pyqtBoundSignal):
    ref, recompute = _create_computed(handler)
    _connect(dependency_signal, recompute, parent=ref)

    return ref


# TODO mix between synchrony and asynchrony below may lead to inconsistent/unexpected behavior

def _connect(signal: pyqtBoundSignal, handler: Callable[..., None], parent: "QObject | None"=None):
    # Disconnecting using `connection` instead of `handler` allows errors to be caught properly when attempting to
    # disconnect after the signal parents have been destroyed (why?)
    connection = signal.connect(handler)

    if parent is not None:
        @on(parent.destroyed)
        def disconnect():
            # try-except might not be ideal
            try:
                signal.disconnect(connection)
            except TypeError:
                pass

    return handler


def _connect_many(signals: Iterable[pyqtBoundSignal], handler: Callable[..., None], parent: "QObject | None"=None):
    # Blocking prevents handler from firing multiple times due to simulataneous changes
    # Handler is contained in QTimer.singleShot callback so that all watched signals will have been run
    # TODO ^ not guaranteed? (eg, if one watcher is invoked because of another)
    waiting = False

    def call_later(*args: Any):
        nonlocal waiting

        if waiting: return

        waiting = True
        QTimer.singleShot(0, call_and_unblock)

    def call_and_unblock():
        nonlocal waiting

        handler()
        waiting = False


    connections = tuple(signal.connect(call_later) for signal in signals)

    if parent is not None:
        @on(parent.destroyed)
        def disconnect_all():
            for signal, connection in zip(signals, connections):
                try:
                    signal.disconnect(connection)
                except TypeError:
                    pass

    return handler


def on(signal: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Connects a function to a signal.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from the signal.
    """

    return partial(_connect, signal, parent=parent)


def on_many(*signals: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Connects a function to an arbitrary number of signals.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from all given signals.
    """

    return partial(_connect_many, signals, parent=parent)


def watch(signal: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Calls a function immediately and connects it to a signal.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from the signal.
    """

    def run_and_connect(handler: Callable[..., None]):
        handler()
        return _connect(signal, handler, parent=parent)

    return run_and_connect


def watch_many(*signals: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Calls a function immediately and connects it to an arbitrary number of signals.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from all given signals.
    """

    def run_and_connect(handler: Callable[..., None]):
        handler()
        return _connect_many(signals, handler, parent=parent)

    return run_and_connect