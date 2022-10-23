from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from plover_onscreen_stenotype.Main import Main
else:
    Main = object


from plover_onscreen_stenotype.widgets.KeyWidget import KeyWidget
from plover_onscreen_stenotype.widgets.build_keyboard import build_staggered


class KeyboardWidget(QWidget):
    end_stroke = pyqtSignal(set)  #set[str]
    after_touch_event = pyqtSignal()

    dpi_change = pyqtSignal()

    #region Overrides

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._current_stroke_keys: set[str] = set()
        self._key_widgets: list[KeyWidget] = []

        self.__setup_ui()


    def event(self, event: QEvent) -> bool:
        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.after_touch_event.emit()

        touched_key_widgets = self._find_touched_key_widgets(event.touchPoints())

        if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
            self._current_stroke_keys.update(
                key
                for key_widget in touched_key_widgets
                for key in key_widget.values
            )

        elif event.type() == QEvent.TouchEnd:
            # This also filters out empty strokes (Plover accepts them and will insert extra spaces)
            if self._current_stroke_keys and all(touch.state() == Qt.TouchPointReleased for touch in event.touchPoints()):
                self.end_stroke.emit(self._current_stroke_keys)
                self._current_stroke_keys = set()
        

        self._update_key_widget_styles(touched_key_widgets)

        return True

    #endregion

    def __setup_ui(self):
        self.setLayout(build_staggered(self, self._key_widgets))


        self.setStyleSheet("""
KeyWidget[matched="true"] {
    background: #6f9f86;
    color: #fff;
    border: 1px solid;
    border-color: #2a6361 #2a6361 #1f5153 #2a6361;
}

KeyWidget[touched="true"] {
    background: #41796a;
}
""")

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
        
        self.screen().physicalDotsPerInchChanged.connect(lambda _dpi: self.__handle_dpi_change())
        # `self.window().windowHandle()` may initially be None on Linux
        QTimer.singleShot(0,
            lambda: self.window().windowHandle().screenChanged.connect(lambda _screen: self.__handle_dpi_change())
        )


    def __handle_dpi_change(self):
        # self.main_rows_layout.invalidate()
        # self.vowel_row_layout.invalidate()
        # self.layout().invalidate()

        self.dpi_change.emit()

        # self.window().setMinimumSize(self.window().sizeHint()) # Needed in order to use QWidget.resize
        # cast(Main, self.window()).resize_from_center(0, 0)
        


    def _find_touched_key_widgets(self, touch_points: list[QTouchEvent.TouchPoint]):
        touched_key_widgets: list[KeyWidget] = []
        for touch in touch_points:
            if touch.state() == Qt.TouchPointReleased: continue

            key_widget = self.childAt(touch.pos().toPoint())
            if not key_widget: continue

            touched_key_widgets.append(key_widget)

        return touched_key_widgets

    def _update_key_widget_styles(self, touched_key_widgets: list):
        touched_key_widgets: list[KeyWidget] = touched_key_widgets
    
        for key_widget in self._key_widgets:
            old_touched, old_matched = key_widget.touched, key_widget.matched

            if key_widget in touched_key_widgets:
                key_widget.touched = True
                key_widget.matched = True

            elif all(key in self._current_stroke_keys for key in key_widget.values):
                key_widget.touched = False
                key_widget.matched = True

            else:
                key_widget.touched = False
                key_widget.matched = False


            if (old_touched, old_matched) != (key_widget.touched, key_widget.matched):
                # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                # self.style().unpolish(key_widget)
                self.style().polish(key_widget)

    def px(self, cm: float) -> int:
        return round(cm * self.screen().physicalDotsPerInch() / 2.54)
