from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QSpacerItem,
)

from ..lib.reactivity import Ref, watch_many


class DisplayAlignmentLayout(QGridLayout):
    def __init__(self, right_left_width_diff: Ref[float], parent: QWidget=None):
        super().__init__(parent)

        self.setColumnStretch(0, 1)
        self.setColumnStretch(1, 0)
        
        self.addItem(QSpacerItem(0, 0), 0, 1)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        @watch_many(right_left_width_diff.change)
        def resize_display_alignment():
            self.setColumnMinimumWidth(1, int(right_left_width_diff.value))
            # dpi.cm(self.__settings.key_width) * cos(radians(self.__settings.main_rows_angle)))