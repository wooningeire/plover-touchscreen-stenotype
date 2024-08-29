from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QSpacerItem,
    QLayout,
)

from ..lib.reactivity import Ref, watch_many
from ..widgets.composables.UseDpi import UseDpi


class DisplayAlignmentLayout(QGridLayout):
    def __init__(self, left_right_width_diff: Ref[float], dpi: UseDpi, parent: "QWidget | None"=None):
        super().__init__(parent)

        self.setColumnStretch(0, 0)
        self.setColumnStretch(1, 1)
        self.setColumnStretch(2, 0)
        
        self.addItem(QSpacerItem(0, 0), 0, 0)
        self.addItem(QSpacerItem(0, 0), 0, 2)
        
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        @watch_many(left_right_width_diff.change)
        def resize_display_alignment():
            self.setColumnMinimumWidth(0, dpi.cm(max(0, left_right_width_diff.value)))
            self.setColumnMinimumWidth(2, dpi.cm(max(0, -left_right_width_diff.value)))

    def addLayout(self, layout: QLayout):
        super(DisplayAlignmentLayout, self).addLayout(layout, 0, 1)