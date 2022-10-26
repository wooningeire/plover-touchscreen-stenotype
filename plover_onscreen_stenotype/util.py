from PyQt5.QtCore import (
    QObject,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
)
from PyQt5.QtGui import (
    QScreen,
)


class UseDpi(QObject):
    """Composable that handles DPI-responsivity."""

    change = pyqtSignal()

    def __init__(self, widget: QWidget):
        super().__init__(widget)

        self.__widget = widget
        self.__current_screen = widget.screen()

        self.__current_screen.physicalDotsPerInchChanged.connect(self.__on_screen_change)
        # `widget.window().windowHandle()` may initially be None on Linux
        QTimer.singleShot(0,
            lambda: widget.window().windowHandle().screenChanged.connect(self.__on_screen_change)
        )

    def px(self, cm: float) -> int:
        return round(cm * self.__widget.screen().physicalDotsPerInch() / 2.54)

    def pt(self) -> float:
        ...

    def __on_screen_change(self, screen: QScreen):
        self.__current_screen.physicalDotsPerInchChanged.disconnect(self.__on_screen_change)

        self.__current_screen = screen
        screen.physicalDotsPerInchChanged.connect(self.__on_screen_change)

        self.change.emit()
