from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSlider,
    QDoubleSpinBox,
)
from PyQt5.QtGui import (
    QResizeEvent,
)

from functools import wraps
from typing import Callable, Any

from ..lib.reactivity import on


def block_signals(fn: Callable[[Any], None]):
    @wraps(fn)
    def wrapper(self: "FloatSlider", *args):
        old_signals_blocked = self.blockSignals(True) # Prevent `valueChanged` from being fired
        fn(self, *args)
        self.blockSignals(old_signals_blocked)

    return wrapper


class FloatSlider(QSlider):
    """Slider that supports float values."""
    # Implemented by having a QSlider that can be dragged to every pixel value in its range. From there, the slider
    # values from Qt can be mapped to values in the range [0, 1]

    input = pyqtSignal(float)
    """Emitted when the user changes the value of this widget"""

    IDENTITY = lambda value: value

    def __init__(self,
        value: float=0,
        convert_in: Callable[[float], float]=IDENTITY,
        convert_out: Callable[[float], float]=IDENTITY,
        min: float=0,
        max: float=1,
        orientation: Qt.Orientation=Qt.Horizontal,
        parent: QWidget=None,
    ):
        super().__init__(orientation, parent)

        self.__convert_in = convert_in
        self.__convert_out = convert_out

        self.__min_value = self.__convert_in(min)
        self.__max_value = self.__convert_in(max)
        self.__current_value = self.__convert_in(value)

        self.__setup_ui()

    def __setup_ui(self):
        self.__update_slider_position()

        @on(self.valueChanged)
        def notify(internal_value: float):
            self.input.emit(self.__convert_out(self.__value_at(internal_value / self.__internal_max)))
        

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.setMinimum(0)
        self.setMaximum(self.__internal_max)

        self.__update_slider_position()

        return super().resizeEvent(event)

    @block_signals
    def setMaximum(self, maximum: int) -> None:
        # setMaximum can emit `valueChanged` when value > maximum
        return super().setMaximum(maximum)

    @block_signals
    def setValue(self, value: int) -> None:
        return super().setValue(value)


    def __set_progress(self, progress: float):
        self.setValue(round(progress * self.__internal_max))

    def __progress_at(self, value: float):
        return (value - self.__min_value) / (self.__max_value - self.__min_value)

    def __value_at(self, progress: float):
        return progress * (self.__max_value - self.__min_value) + self.__min_value

    def __update_slider_position(self):
        self.__set_progress(self.__progress_at(self.__current_value))

    @property
    def __internal_max(self):
        """Qt's maximum value of the QSlider. (= the number of pixels it can be dragged to)"""

        if self.orientation() == Qt.Horizontal:
            return self.size().width()
        else:
            return self.size().height()

    @property
    def current_value(self):
        return self.__convert_out(self.__current_value)
    
    @current_value.setter
    def current_value(self, value: float):
        self.__current_value = self.__convert_in(value)
        self.__update_slider_position()

    @property
    def max(self):
        return self.__max_value

    @max.setter
    def max(self, value: float):
        self.__max_value = self.__convert_in(value)
        self.__update_slider_position()


class FloatEntry(QDoubleSpinBox):
    # Main purpose of this class is to define an alternative method for `setValue` that does not emit `valueChanged`

    input = pyqtSignal(float)
    """Emitted when the user changes the value of this widget"""

    def __init__(self,
        value: float=0,
        min: float=0,
        max: float=1,
        spin_step: float=0.1,
        parent: QWidget=None,
    ):
        super().__init__(parent)
        self.__setup_ui(value, min, max, spin_step)

    def __setup_ui(self, value: float, min: float, max: float, spin_step: float):
        self.setMinimum(min)
        self.setMaximum(max)
        self.setSingleStep(spin_step)
        self.current_value = value

        @on(self.valueChanged)
        def notify(value: float):
            self.input.emit(value)

    @property
    def current_value(self):
        return self.value()

    @current_value.setter
    def current_value(self, value: float):
        old_signals_blocked = self.blockSignals(True) # Prevent `valueChanged` from being fired
        self.setValue(value)
        self.blockSignals(old_signals_blocked)
