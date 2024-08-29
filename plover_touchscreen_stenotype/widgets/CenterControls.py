from plover.gui_qt.utils import ToolBar

from PyQt5.QtCore import (
    Qt,
    QSize,
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QAction,
    QToolButton,
)
from PyQt5.QtGui import (
    QFont,
    QMouseEvent,
)


from typing import Callable

from .DisplayAlignmentLayout import DisplayAlignmentLayout
from ..lib.reactivity import Ref, watch
from .composables.UseDpi import UseDpi
from ..lib.constants import FONT_FAMILY

class CenterControls(QWidget):
    def __init__(
        self,
        on_mouse_press: Callable[[QMouseEvent], None],
        settings_action: QAction,
        minimize_action: QAction,
        close_action: QAction,
        left_right_width_diff: Ref[float],
        parent: "QWidget | None"=None
    ):
        super().__init__(parent)


        dpi = UseDpi(self)


        controls_layout = QVBoxLayout()

        @watch(dpi.change)
        def set_layout_spacing():
            controls_layout.setSpacing(dpi.dp(8))

        
        dragger = QPushButton("✥")
        dragger.mousePressEvent = on_mouse_press
        
        @watch(dpi.change)
        def set_dragger_size():
            dragger.setFixedWidth(dpi.dp(48))

            dragger_font = QFont(FONT_FAMILY)
            dragger_font.setPixelSize(dpi.dp(48 / 1.5))
            dragger.setFont(dragger_font)
        

        settings_button = QToolButton()
        settings_button.setDefaultAction(settings_action)
        settings_button.setFocusPolicy(Qt.NoFocus)

        @watch(dpi.change)
        def resize_toolbar_button_size():
            settings_button.setIconSize(QSize(dpi.dp(32), dpi.dp(32)))
            

        minimize_button = QToolButton()
        minimize_button.setDefaultAction(minimize_action)
        minimize_button.setFocusPolicy(Qt.NoFocus)


        close_button = QToolButton()
        close_button.setDefaultAction(close_action)
        close_button.setFocusPolicy(Qt.NoFocus)

            
        controls_layout.addWidget(dragger, 0, Qt.AlignHCenter)
        controls_layout.addWidget(settings_button, 0, Qt.AlignHCenter)
        controls_layout.addWidget(minimize_button, 0, Qt.AlignHCenter)
        controls_layout.addWidget(close_button, 0, Qt.AlignHCenter)


        display_alignment_layout = DisplayAlignmentLayout(left_right_width_diff, dpi)
        display_alignment_layout.addLayout(controls_layout)
        self.setLayout(display_alignment_layout)
        