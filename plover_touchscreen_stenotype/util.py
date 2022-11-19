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

from functools import wraps
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
class RefAttr(QObject, Generic[T]):
    """Descriptor for one shallow reactive value."""

    change = pyqtSignal() # T

    def __init__(self, value: T):
        self.__value = value

    def __get__(self, instance: Any, owner: Any) -> T:
        return self.__value

    def __set__(self, instance: Any, value: T):
        self.__value = value
        self.change.emit(value)


def on(signal: pyqtBoundSignal):
    """Decorator factory. Connects a function to a signal."""

    def run_and_connect(handler: Callable[..., None]):
        signal.connect(handler)
        return handler

    return run_and_connect

def watch(signal: pyqtBoundSignal, *args, **kwargs):
    """Decorator factory. Calls a function immediately and connects it to a signal."""

    def run_and_connect(handler: Callable[..., None]):
        handler(*args, **kwargs)
        signal.connect(handler)
        return handler

    return run_and_connect


def watch_many(*signals: pyqtBoundSignal):
    """Decorator factory. Calls a function immediately and connects it to an arbitrary number of signals."""

    def run_and_connect(handler: Callable[..., None]):
        handler()
        for signal in signals:
            signal.connect(handler)
        return handler

    return run_and_connect


FONT_FAMILY = "Atkinson Hyperlegible, Segoe UI, Ubuntu"