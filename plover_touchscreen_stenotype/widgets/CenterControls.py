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

from .DisplayAlignmentLayout import DisplayAlignmentLayout
from ..lib.reactivity import Ref, watch
from ..lib.UseDpi import UseDpi
from ..lib.constants import FONT_FAMILY

class CenterControls(QWidget):
    def __init__(self, on_mouse_press: Callable[[QMouseEvent], None], toolbar: ToolBar, right_left_width_diff: Ref[float], parent: QWidget=None):
        super().__init__(parent)

        self.__setup_ui(on_mouse_press, toolbar, right_left_width_diff)

    def __setup_ui(self, on_mouse_press: Callable[[QMouseEvent], None], toolbar: ToolBar, right_left_width_diff: Ref[float]):
        dpi = UseDpi(self)


        controls_layout = QVBoxLayout()
        
        dragger = QPushButton("✥")
        dragger.mousePressEvent = on_mouse_press
        
        @watch(dpi.change)
        def set_dragger_size():
            dragger.setFixedWidth(dpi.dp(48))

            dragger_font = QFont(FONT_FAMILY)
            dragger_font.setPixelSize(dpi.dp(48 / 1.5))
            dragger.setFont(dragger_font)

        controls_layout.addWidget(dragger)
        controls_layout.addWidget(toolbar)

        controls_layout.setAlignment(dragger, Qt.AlignHCenter)
        controls_layout.setAlignment(toolbar, Qt.AlignHCenter)


        display_alignment_layout = DisplayAlignmentLayout(right_left_width_diff)
        display_alignment_layout.addLayout(controls_layout, 0, 0)
        self.setLayout(display_alignment_layout)
        