from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtProperty,
)
from PyQt5.QtWidgets import (
    QWidget,
    QToolButton,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QFont,
)

from plover.steno import Stroke

from .composables.UseDpi import UseDpi
from ..lib.reactivity import Ref, watch, watch_many
from ..lib.constants import FONT_FAMILY
from ..lib.util import empty_stroke, not_none


class KeyWidget(QToolButton):
    #region Overrides

    def __init__(
        self,
        substroke: Stroke,
        label_maybe_ref: "str | Ref[str]",
        parent: "QWidget | None"=None,
        *,
        touched_key_widgets: "Ref[set[KeyWidget]] | None"=None,
        current_stroke: "Ref[Stroke] | None"=None,
        dpi: "UseDpi | None"=None,
    ):
        # super().__init__(label, parent)
        super().__init__(parent)

        self.substroke = substroke

        self.__touched = False
        self.__matched = False
        self.__matched_soft = False

        touched_key_widgets = touched_key_widgets or Ref(set())
        current_stroke = current_stroke or Ref(empty_stroke())
        dpi = dpi or UseDpi(self)


        @watch_many(touched_key_widgets.change, current_stroke.change)
        def update_highlight_state():
            old_touched, old_matched = self.touched, self.matched

            if self in touched_key_widgets.value:
                self.touched = True
                self.matched = True

            elif substroke in current_stroke.value:
                self.touched = False
                self.matched = True

            else:
                self.touched = False
                self.matched = False


            if (old_touched, old_matched) != (self.touched, self.matched):
                # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                # self.style().unpolish(key_widget)
                not_none(self.style()).polish(self)


        @watch(dpi.change)
        def set_font():
            self.setFont(QFont(FONT_FAMILY, dpi.dp(8)))

        if isinstance(label_maybe_ref, str):
            label: str = label_maybe_ref
            self.setText(label)
        else:
            label_ref: Ref[str] = label_maybe_ref
            @watch(label_ref.change)
            def set_label():
                self.setText(label_ref.value)


        # self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)
        

    def event(self, event: QEvent):
        # Prevents automatic button highlighting
        if event.type() == QEvent.HoverEnter:
            self.setAttribute(Qt.WA_UnderMouse, False)

        return super().event(event)

    #endregion


    @pyqtProperty(bool)
    def touched(self):
        return self.__touched

    @touched.setter
    def touched(self, touched: bool):
        self.__touched = touched

    @pyqtProperty(bool)
    def matched(self):
        return self.__matched

    @matched.setter
    def matched(self, matched: bool):
        self.__matched = matched

    @pyqtProperty(bool)
    def matched_soft(self):
        return self.__matched_soft
    
    @matched_soft.setter
    def matched_soft(self, matched_soft: bool):
        self.__matched_soft = matched_soft