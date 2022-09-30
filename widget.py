from plover.gui_qt.tool import Tool
# from plover.gui_qt import Engine
from plover.engine import StenoEngine
from plover.steno import Stroke

from PyQt5.QtCore import (
    Qt,
    QEvent,
    QPointF,
    pyqtSignal,
    pyqtProperty,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QFont,
    QTouchEvent,
)

import ctypes
from ctypes.wintypes import HWND
import win32con


class Main(Tool):
    #region Overrides

    TITLE = "On-screen stenotype"
    ICON = ""
    ROLE = "onscreen_stenotype"

    def __init__(self, engine: StenoEngine):
        super().__init__(engine)

        self.engine = engine

        self.last_stroke_label = last_stroke_label = QLabel(self)
        last_stroke_label.setFont(QFont("Atkinson Hyperlegible", 24))
        last_stroke_label.setText("…")

        stenotype = KeyboardWidget(self)
        stenotype.end_stroke.connect(self._on_stenotype_input)

        self.layout = layout = QGridLayout(self)
        layout.addWidget(last_stroke_label, 0, 0, Qt.AlignBottom | Qt.AlignRight)
        layout.addWidget(stenotype, 0, 0, Qt.AlignVCenter)
        self.setLayout(layout)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.NoFocus)

        # https://stackoverflow.com/questions/71084136/how-to-set-focus-to-the-old-window-on-button-click-in-pyqt5-python
        # self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.__prevent_window_focus()


        self.setWindowOpacity(0.9375)

        engine.signal_stroked.connect(self._on_stroked)


    #endregion

    # https://stackoverflow.com/questions/24582525/how-to-show-clickable-qframe-without-loosing-focus-from-main-window
    # https://stackoverflow.com/questions/68276479/how-to-use-setwindowlongptr-hwnd-gwl-exstyle-ws-ex-noactivate

    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
    def __prevent_window_focus(self):
        """
        Prevents the stenotype window from taking focus from other programs when the keys are touched. Currently, this
        is an alternative to the nonfunctional Qt window flag `Qt.WindowDoesNotAcceptFocus` and Unix-only attribute
        `Qt.WA_X11DoNotAcceptFocus`. This function is currently designed for Windows only.

        See https://bugreports.qt.io/browse/QTBUG-36230, https://forum.qt.io/topic/82493/the-windowdoesnotacceptfocus-flag-is-making-me-thirsty/7 for bug information.
        """

        window_handle = HWND(int(self.winId()))

        user32 = ctypes.windll.user32
        user32.SetWindowLongPtrW(
            window_handle,
            win32con.GWL_EXSTYLE,
            user32.GetWindowLongPtrW(window_handle, win32con.GWL_EXSTYLE) | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_APPWINDOW,
        )

    def _on_stenotype_input(self, stroke_keys: set[str]):
        # Temporarily enable steno output
        engine_already_enabled = self.engine.output
        self.engine.output = True

        self.engine._machine._notify(list(stroke_keys))

        self.engine.output = engine_already_enabled

    def _on_stroked(self, stroke: Stroke):
        self.last_stroke_label.setText(stroke.rtfcre or "…")


class KeyboardWidget(QWidget):
    TOP_ROW = 2
    LOW_ROW = 4
    TOP_COMPOUND_ROW = 1
    LOW_COMPOUND_ROW = 3

    # [keys], (row, column, rowSpan, columnSpan)
    MAIN_ROWS_KEYS = (
        (["#"], "#", (0, 0, 1, -1)),
        (["S-"], "S", (TOP_ROW, 0, 3, 1)),
        (["T-"], "T", (TOP_ROW, 1)),
        (["K-"], "K", (LOW_ROW, 1)),
        (["P-"], "P", (TOP_ROW, 2)),
        (["W-"], "W", (LOW_ROW, 2)),
        (["H-"], "H", (TOP_ROW, 3)),
        (["R-"], "R", (LOW_ROW, 3)),
        (["H-", "*"], "", (TOP_ROW, 4)),
        (["R-", "*"], "", (LOW_ROW, 4)),
        (["*"], "*", (TOP_ROW, 5, 3, 1)),
        (["*", "-F"], "", (TOP_ROW, 6)),
        (["*", "-R"], "", (LOW_ROW, 6)),
        (["-F"], "F", (TOP_ROW, 7)),
        (["-R"], "R", (LOW_ROW, 7)),
        (["-P"], "P", (TOP_ROW, 8)),
        (["-B"], "B", (LOW_ROW, 8)),
        (["-L"], "L", (TOP_ROW, 9)),
        (["-G"], "G", (LOW_ROW, 9)),
        (["-T"], "T", (TOP_ROW, 10)),
        (["-S"], "S", (LOW_ROW, 10)),
        (["-T", "-D"], "", (TOP_ROW, 11)),
        (["-S", "-Z"], "", (LOW_ROW, 11)),
        (["-D"], "D", (TOP_ROW, 12)),
        (["-Z"], "Z", (LOW_ROW, 12)),

        (["#", "S-"], "", (TOP_COMPOUND_ROW, 0)),
        (["#", "T-"], "", (TOP_COMPOUND_ROW, 1)),
        (["#", "P-"], "", (TOP_COMPOUND_ROW, 2)),
        (["#", "H-"], "", (TOP_COMPOUND_ROW, 3)),
        (["#", "H-", "*"], "", (TOP_COMPOUND_ROW, 4)),
        (["#", "*"], "", (TOP_COMPOUND_ROW, 5)),
        (["#", "*", "-F"], "", (TOP_COMPOUND_ROW, 6)),
        (["#", "-F"], "", (TOP_COMPOUND_ROW, 7)),
        (["#", "-P"], "", (TOP_COMPOUND_ROW, 8)),
        (["#", "-L"], "", (TOP_COMPOUND_ROW, 9)),
        (["#", "-T"], "", (TOP_COMPOUND_ROW, 10)),
        (["#", "-T", "-D"], "", (TOP_COMPOUND_ROW, 11)),
        (["#", "-D"], "", (TOP_COMPOUND_ROW, 12)),

        (["T-", "K-"], "", (LOW_COMPOUND_ROW, 1)),
        (["P-", "W-"], "", (LOW_COMPOUND_ROW, 2)),
        (["H-", "R-"], "", (LOW_COMPOUND_ROW, 3)),
        (["H-", "R-", "*"], "", (LOW_COMPOUND_ROW, 4)),
        (["*", "-R", "-F"], "", (LOW_COMPOUND_ROW, 6)),
        (["-F", "-R"], "", (LOW_COMPOUND_ROW, 7)),
        (["-P", "-B"], "", (LOW_COMPOUND_ROW, 8)),
        (["-L", "-G"], "", (LOW_COMPOUND_ROW, 9)),
        (["-T", "-S"], "", (LOW_COMPOUND_ROW, 10)),
        (["-T", "-S", "-D", "-Z"], "", (LOW_COMPOUND_ROW, 11)),
        (["-D", "-Z"], "", (LOW_COMPOUND_ROW, 12)),
    )

    VOWEL_ROW_KEYS_LEFT = (
        (["A-"], "A"),
        (["A-", "O-"], ""),
        (["O-"], "O"),
    )

    VOWEL_ROW_KEYS_RIGHT = (
        (["-E"], "E"),
        (["-E", "-U"], ""),
        (["-U"], "U"),
    )

    KEY_SIZE_NUM_BAR = 72
    KEY_SIZE = 132
    COMPOUND_KEY_SIZE = 68
    REDUCED_KEY_SIZE = KEY_SIZE - COMPOUND_KEY_SIZE / 2

    ROW_HEIGHTS = (
        KEY_SIZE_NUM_BAR,
        COMPOUND_KEY_SIZE,
        REDUCED_KEY_SIZE,  # top row
        COMPOUND_KEY_SIZE,
        REDUCED_KEY_SIZE,  # bottom row
    )

    COL_WIDTHS = (
        KEY_SIZE,
    ) * 3 + (
        REDUCED_KEY_SIZE,  # H-, R-
        COMPOUND_KEY_SIZE,
        REDUCED_KEY_SIZE * 2 + KEY_SIZE * 2.5,  # *
        COMPOUND_KEY_SIZE,
        REDUCED_KEY_SIZE,  # -F, -R
    ) + (
        KEY_SIZE,
    ) * 2 + (
        REDUCED_KEY_SIZE,  # -T, -S
        COMPOUND_KEY_SIZE,
        REDUCED_KEY_SIZE,  # -D, -Z
    )

    VOWEL_SET_WIDTHS = (
        REDUCED_KEY_SIZE,
        COMPOUND_KEY_SIZE,
        REDUCED_KEY_SIZE,
    )

    end_stroke = pyqtSignal(set)  #set[str]
    after_touch_event = pyqtSignal()

    #region Overrides

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.key_widgets: list[KeyWidget] = []

        layout = QVBoxLayout(self)

        layout.addLayout(self.__build_main_rows_layout())
        layout.addSpacing(self.KEY_SIZE * 3/4)
        layout.addLayout(self.__build_vowel_row_layout())

        self.setLayout(layout)

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


        self.current_stroke_keys: set[str] = set()

    def event(self, event: QEvent) -> bool:
        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.after_touch_event.emit()

        touched_key_widgets = self._find_touched_key_widgets(event.touchPoints())

        if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
            self.current_stroke_keys.update(
                key
                for key_widget in touched_key_widgets
                for key in key_widget.values
            )

        elif event.type() == QEvent.TouchEnd:
            # This also filters out empty strokes (Plover accepts them and will insert extra spaces)
            if self.current_stroke_keys and all(touch.state() == Qt.TouchPointReleased for touch in event.touchPoints()):
                self.end_stroke.emit(self.current_stroke_keys)
                self.current_stroke_keys = set()
        

        self._update_key_widget_styles(touched_key_widgets)

        return True

    #endregion

    # TODO it is not well indicated that this function and the next mutate key_widgets
    def __build_main_rows_layout(self):
        layout = QGridLayout()
        for (values, label, grid_position) in KeyboardWidget.MAIN_ROWS_KEYS:
            key_widget = KeyWidget(values, label, self)
            self.key_widgets.append(key_widget)

            layout.addWidget(key_widget, *grid_position)

        layout.setSpacing(0)

        for i, size in enumerate(self.ROW_HEIGHTS):
            layout.setRowMinimumHeight(i, size)
            layout.setRowStretch(i, 0)

        for i, size in enumerate(self.COL_WIDTHS):
            layout.setColumnMinimumWidth(i, size)
            layout.setColumnStretch(i, 0)

        layout.setColumnStretch(5, 1) # * key

        return layout

    def __build_vowel_row_layout(self):
        layout = QHBoxLayout()

        layout.setSpacing(0)

        def add_vowel_set(vowel_key_descriptors):
            for ((values, label), width) in zip(vowel_key_descriptors, KeyboardWidget.VOWEL_SET_WIDTHS):
                key_widget = KeyWidget(values, label, self)
                self.key_widgets.append(key_widget)
                key_widget.setFixedSize(width, self.KEY_SIZE)

                layout.addWidget(key_widget)

        
        layout.addSpacing(self.KEY_SIZE * 3)
        add_vowel_set(KeyboardWidget.VOWEL_ROW_KEYS_LEFT)
        layout.addStretch(1)
        add_vowel_set(KeyboardWidget.VOWEL_ROW_KEYS_RIGHT)
        layout.addSpacing(self.KEY_SIZE * 4)

        return layout

    def _find_touched_key_widgets(self, touch_points: list[QTouchEvent.TouchPoint]):
        touched_key_widgets: list[KeyWidget] = []
        for touch in touch_points:
            if touch.state() == Qt.TouchPointReleased: continue

            key_widget = self._key_widget_from_point(touch.pos())
            if not key_widget: continue

            touched_key_widgets.append(key_widget)

        return touched_key_widgets

    def _key_widget_from_point(self, point: QPointF):
        for key_widget in self.key_widgets:
            if key_widget.geometry().contains(point.toPoint()):
                return key_widget

        return None

    def _update_key_widget_styles(self, touched_key_widgets: list):
        touched_key_widgets: list[KeyWidget] = touched_key_widgets
    
        for key_widget in self.key_widgets:
            if key_widget in touched_key_widgets:
                key_widget.touched = True
                key_widget.matched = True

            elif all(key in self.current_stroke_keys for key in key_widget.values):
                key_widget.touched = False
                key_widget.matched = True

            else:
                key_widget.touched = False
                key_widget.matched = False

            # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
            self.style().unpolish(key_widget)
            self.style().polish(key_widget)



class KeyWidget(QPushButton):
    #region Overrides

    def __init__(self, values: list[str], label: str, parent: QWidget = None):
        super().__init__(label, parent)

        self.values = values

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        if label:
            self.setFont(QFont("Atkinson Hyperlegible", 16))

        self.__touched = False
        self.__matched = False

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

# def command_open_window(engine: StenoEngine, arg: str):
#     new_window = Main(engine)
#     new_window.show()
