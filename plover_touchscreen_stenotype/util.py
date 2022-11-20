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

from typing import TypeVar, Generic, Any, Callable


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

    def __init__(self, value: T, signal: pyqtBoundSignal):
        self.__value = value
        self.__signal = signal

    def __get__(self, instance: Any, owner: Any) -> T:
        return self.__value

    def __set__(self, instance: Any, value: T):
        self.__value = value
        self.__signal.emit(value)


class Ref(QObject, Generic[T]):
    change = pyqtSignal(object) # T

    def __init__(self, value: T):
        super().__init__()
        self.__value = value
        # self.value = RefAttr(value, self.change)

    @property
    def value(self) -> T:
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        self.change.emit(value)


def computed(handler: Callable[[], T], *dependency_refs: Ref[T]):
    ref: Ref[T] = Ref(handler())

    def recompute_value():
        ref.value = handler()

    for dependency in dependency_refs:
        dependency.change.connect(recompute_value)

    return ref


def on(signal: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Connects a function to a signal.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from the signal.
    """

    def run_and_connect(handler: Callable[..., None]):
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

    return run_and_connect

def watch(signal: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Calls a function immediately and connects it to a signal.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from the signal.
    """

    def run_and_connect(handler: Callable[..., None]):
        handler()
        connection = signal.connect(handler)

        if parent is not None:
            @on(parent.destroyed)
            def disconnect():
                try:
                    signal.disconnect(connection)
                except TypeError:
                    pass

        return handler

    return run_and_connect


def watch_many(*signals: pyqtBoundSignal, parent: "QObject | None"=None):
    """Decorator factory. Calls a function immediately and connects it to an arbitrary number of signals.

        :param parent: QObject that, when destroyed, will cause the handler to be disconnected from all given signals.
    """

    def run_and_connect(handler: Callable[..., None]):
        handler()
        no_arg_handler = lambda *_: handler()

        connections = tuple(signal.connect(no_arg_handler) for signal in signals)

        if parent is not None:
            @on(parent.destroyed)
            def disconnect_all():
                for signal, connection in zip(signals, connections):
                    try:
                        signal.disconnect(connection)
                    except TypeError:
                        pass

        return handler

    return run_and_connect


FONT_FAMILY = "Atkinson Hyperlegible, Segoe UI, Ubuntu"