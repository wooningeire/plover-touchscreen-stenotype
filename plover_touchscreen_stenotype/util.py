from PyQt5.QtCore import (
    QObject,
    QTimer,
    pyqtSignal,
    pyqtBoundSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
)
from PyQt5.QtGui import (
    QScreen,
)

from functools import partial
from dataclasses import dataclass
from typing import TypeVar, Generic, Any, Callable, Iterable, cast


class UseDpi(QObject):
    """Composable that handles DPI-responsivity."""

    change = pyqtSignal()
    change_logical = pyqtSignal()

    def __init__(self, widget: QWidget):
        super().__init__(widget)

        self.__widget = widget
        self.__current_screen = widget.screen()

        self.__current_screen.physicalDotsPerInchChanged.connect(self.__on_screen_physcial_dpi_change)
        self.__current_screen.logicalDotsPerInchChanged.connect(self.__on_screen_logical_dpi_change)
        # `widget.window().windowHandle()` may initially be None on Linux
        QTimer.singleShot(0,
            lambda: widget.window().windowHandle().screenChanged.connect(self.__on_screen_change)
        )

    def cm(self, cm: float) -> int:
        """Converts cm to px using the current physical DPI."""
        return round(cm * self.__widget.screen().physicalDotsPerInch() / 2.54)

    def dp(self, dp: float) -> int:
        """Converts dp to px using the current physical DPI. (Defines dp as the length of a pixel on a 96 dpi screen.)"""
        return round(dp * self.__widget.screen().physicalDotsPerInch() / 96)

    def pt(self, pt: float) -> int:
        """Converts pt to px using the current logical DPI."""
        return round(pt * self.__widget.screen().logicalDotsPerInch() / 72)
    
    def px_to_cm(self, px: int) -> float:
        return px * 2.54 / self.__widget.screen().physicalDotsPerInch()

    def __on_screen_change(self, screen: QScreen):
        self.__current_screen.physicalDotsPerInchChanged.disconnect(self.__on_screen_physcial_dpi_change)
        self.__current_screen.logicalDotsPerInchChanged.disconnect(self.__on_screen_logical_dpi_change)

        self.__current_screen = screen
        screen.physicalDotsPerInchChanged.connect(self.__on_screen_physcial_dpi_change)
        screen.logicalDotsPerInchChanged.connect(self.__on_screen_logical_dpi_change)

        self.change.emit()
        self.change_logical.emit()

    def __on_screen_physcial_dpi_change(self, dpi: float):
        self.change.emit()

    def __on_screen_logical_dpi_change(self, dpi: float):
        self.change_logical.emit()


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


FONT_FAMILY = "Atkinson Hyperlegible, Segoe UI, Ubuntu"

KEY_STYLESHEET = """
KeyWidget[matched="true"] {
    background: #6f9f86;
    color: #fff;
    border: 1px solid;
    border-color: #2a6361 #2a6361 #1f5153 #2a6361;
}

KeyWidget[touched="true"] {
    background: #41796a;
}
"""


KeyColumnsTuple = tuple[
    tuple[
        tuple[list[str], str, "int | None", "str | None"]
    ]
]
KeyGridTuple = tuple[
    tuple[
        list[str],
        str,
        "tuple[int, int] | tuple[int, int, int, int]",
        "str | None",
    ]
]
SizeTuple = tuple[Ref[float]]

@dataclass
class LayoutDescriptor:
    MAIN_ROWS_STAGGERED_LEFT: KeyColumnsTuple
    MAIN_ROWS_STAGGERED_RIGHT: KeyColumnsTuple
    col_widths_staggered_left: SizeTuple
    col_widths_staggered_right: SizeTuple
    col_offsets_staggered_left: SizeTuple
    col_offsets_staggered_right: SizeTuple
    row_heights_staggered_left: SizeTuple
    row_heights_staggered_right: SizeTuple
    TALLEST_COLUMN_INDEX_LEFT: float
    TALLEST_COLUMN_INDEX_RIGHT: float

    N_INDEX_COLS_LEFT: float
    N_INDEX_COLS_RIGHT: float

    MAIN_ROWS_GRID: KeyGridTuple
    row_heights_grid: SizeTuple
    col_widths_grid: SizeTuple
    ASTERISK_COLUMN_INDEX_GRID: float

    VOWEL_ROW_KEYS_LEFT: KeyGridTuple
    VOWEL_ROW_KEYS_RIGHT: KeyGridTuple
    vowel_set_widths: SizeTuple
    vowel_set_heights: SizeTuple
    vowel_set_offset: Ref[float]

    LOW_ROW: float