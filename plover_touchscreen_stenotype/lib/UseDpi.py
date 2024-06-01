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