from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtProperty,
)
from PyQt5.QtWidgets import (
    QWidget,
    QToolButton,
    QSizePolicy,
    QVBoxLayout,
    QLabel,
)
from PyQt5.QtGui import (
    QFont,
)

from plover.steno import Stroke

from .composables.UseDpi import UseDpi
from ..lib.reactivity import Ref, watch, watch_many
from ..lib.constants import FONT_FAMILY
from ..lib.util import child, empty_stroke, not_none, render


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
        self.__key_label: "KeyLabel | None" = None

        touched_key_widgets = touched_key_widgets or Ref(set())
        current_stroke = current_stroke or Ref(empty_stroke())
        dpi = dpi or UseDpi(self)


        @watch_many(touched_key_widgets.change, current_stroke.change, parent=self)
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


            if (old_touched, old_matched) == (self.touched, self.matched): return
            # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
            # self.style().unpolish(key_widget)
            not_none(self.style()).polish(self)


        key_label: "KeyLabel | None" = None

        @render(self, QVBoxLayout(self))
        def render_widget(widget: QWidget, _: QVBoxLayout):
            @child(self, KeyLabel())
            def render_label(label: KeyLabel, _: None):
                nonlocal key_label
                key_label = label

                label.setAlignment(Qt.AlignCenter)

                if isinstance(label_maybe_ref, str):
                    label_text: str = label_maybe_ref
                    label.setText(label_text)
                else:
                    label_ref: Ref[str] = label_maybe_ref
                    @watch(label_ref.change, parent=label)
                    def set_label():
                        label.setText(label_ref.value)

                return ()

            return ()

        self.__key_label = not_none(key_label)


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

        if self.__key_label is None: return
        self.__key_label.highlighted = matched or self.matched_soft

    @pyqtProperty(bool)
    def matched_soft(self):
        return self.__matched_soft
    
    @matched_soft.setter
    def matched_soft(self, matched_soft: bool):
        self.__matched_soft = matched_soft

        if self.__key_label is None: return
        self.__key_label.highlighted = matched_soft or self.matched


class KeyLabel(QLabel):
    def __init__(self, parent: "QWidget | None"=None):
        super().__init__(parent)

        dpi = UseDpi(self)

        self.__highlighted = False

        @watch(dpi.change, parent=self)
        def set_font():
            self.setFont(QFont(FONT_FAMILY, dpi.dp(8)))

    @pyqtProperty(bool)
    def highlighted(self):
        return self.__highlighted

    @highlighted.setter
    def highlighted(self, highlighted: bool):
        old_highlighted = self.__highlighted

        self.__highlighted = highlighted
        if old_highlighted != highlighted:
            not_none(self.style()).polish(self)