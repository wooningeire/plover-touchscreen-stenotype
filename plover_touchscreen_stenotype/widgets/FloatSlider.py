from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSlider,
)
from PyQt5.QtGui import (
    QResizeEvent,
)

from typing import Callable

from ..util import on

class FloatSlider(QSlider):
    input = pyqtSignal(float)

    IDENTITY = lambda x: x

    def __init__(self,
        value: float=0,
        convert_in: Callable[[float], float]=IDENTITY,
        convert_out: Callable[[float], float]=IDENTITY,
        min: float=0,
        max: float=1,
        parent: QWidget=None,
    ):
        super().__init__(Qt.Horizontal, parent)

        self.__current_value = value
        self.convert_in = convert_in
        self.convert_out = convert_out
        self.min_value = min
        self.__max_value = max

        self.__setup_ui()

    def __setup_ui(self):
        self.__update_slider_position()

        @on(self.sliderMoved)
        def notify(internal_value: float):
            self.input.emit(self.convert_out(self.__value_at(internal_value / self.__internal_max)))
        

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.setMinimum(0)
        self.setMaximum(event.size().width())

        self.__update_slider_position()

        return super().resizeEvent(event)


    def __set_progress(self, progress: float):
        self.setValue(round(progress * self.__internal_max))

    def __progress_at(self, value: float):
        return (value - self.min_value) / (self.__max_value - self.min_value)

    def __value_at(self, progress: float):
        return progress * (self.__max_value - self.min_value) + self.min_value

    def __update_slider_position(self):
        self.__set_progress(self.__progress_at(self.__current_value))

    @property
    def __internal_max(self):
        return self.size().width()

    @property
    def current_value(self):
        return self.__current_value
    
    @current_value.setter
    def current_value(self, value: float):
        self.__current_value = value
        self.__update_slider_position()

    @property
    def max(self):
        return self.__max_value

    @max.setter
    def max(self, value: float):
        self.__max_value = value
        self.__update_slider_position()
