from plover.gui_qt.utils import ToolBar

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
)
from PyQt5.QtGui import (
    QFont,
    QMouseEvent,
)


from typing import Callable

from ..util import UseDpi, on, watch, FONT_FAMILY

class FramelessControls(QWidget):
    def __init__(self, on_mouse_press: Callable[[QMouseEvent], None], toolbar: ToolBar, parent: QWidget=None):
        super().__init__(parent)

        self.__setup_ui(on_mouse_press, toolbar)

    def __setup_ui(self, on_mouse_press: Callable[[QMouseEvent], None], toolbar: ToolBar):
        dpi = UseDpi(self)

        layout = QVBoxLayout()
        
        dragger = QPushButton("✥")
        dragger.mousePressEvent = on_mouse_press
        

        @watch(dpi.change)
        def set_dragger_size():
            dragger.setFixedWidth(dpi.dp(48))

            dragger_font = QFont(FONT_FAMILY)
            dragger_font.setPixelSize(dpi.dp(48 / 1.5))
            dragger.setFont(dragger_font)

        layout.addWidget(dragger)
        layout.addWidget(toolbar)

        layout.setAlignment(dragger, Qt.AlignHCenter)
        layout.setAlignment(toolbar, Qt.AlignHCenter)

        self.setLayout(layout)
        