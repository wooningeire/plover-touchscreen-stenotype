from plover.gui_qt.tool import Tool
# from plover.gui_qt import Engine
from plover.engine import StenoEngine
from plover.steno import Stroke

from PyQt5.QtCore import (
    Qt,
    QEvent,
    QSize,
    QPoint,
    pyqtSignal,
    pyqtProperty,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QToolButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QFont,
    QTouchEvent,
    QScreen,
)

import ctypes
from ctypes.wintypes import HWND
import win32con

from typing import cast


class Main(Tool):
    #region Overrides

    TITLE = "On-screen stenotype"
    ICON = ""
    ROLE = "onscreen_stenotype"

    def __init__(self, engine: StenoEngine):
        super().__init__(engine)

        self.engine = engine
        self.__last_stroke_from_widget = False
        """Whether the last emitted stroke originated from the on-screen stenotype"""
        self.__last_stroke_keys: set[str] | None = None
        self.__last_stroke_engine_enabled = False

        self.__setup_ui()

        engine.signal_stroked.connect(self._on_stroked)

    #endregion

    def __setup_ui(self):
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        # self.setAttribute(Qt.WA_ShowWithoutActivating)
        # self.setFocusPolicy(Qt.NoFocus)

        # https://stackoverflow.com/questions/71084136/how-to-set-focus-to-the-old-window-on-button-click-in-pyqt5-python
        # self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # For some reason, this has to be called before KeyboardWidget is created. Other attributes must also be
        # set before this, otherwise the window will steal focus again
        self.__prevent_window_focus()


        self.last_stroke_label = last_stroke_label = QLabel(self)
        last_stroke_label.setFont(QFont("Atkinson Hyperlegible", 24))
        last_stroke_label.setText("…")

        stenotype = KeyboardWidget(self)
        stenotype.end_stroke.connect(self._on_stenotype_input)

        self.layout = layout = QGridLayout(self)
        layout.addWidget(last_stroke_label, 0, 0, Qt.AlignBottom | Qt.AlignRight)
        layout.addWidget(stenotype, 0, 0, Qt.AlignVCenter)
        self.setLayout(layout)


        self.setWindowOpacity(0.9375)


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
        self.__last_stroke_engine_enabled = self.engine.output
        self.engine.output = True

        self.__last_stroke_from_widget = True
        self.__last_stroke_keys = stroke_keys
        self.engine._machine._notify(list(stroke_keys))

        # Wait until `stroked` hook is dispatched to reset `self.engine.output`, since it must be True for Suggestions to be shown

        # TODO The current implementation is not infallible because the `stroked` handler does not verify that the stroke it
        # received is the same stroke sent from this method. Multiple strokes may also be sent before the handler is called
        # (use deque to resolve this)

    def _on_stroked(self, stroke: Stroke):
        # if not self.__last_stroke_from_widget: return
        if not self.__last_stroke_from_widget or self.__last_stroke_keys != set(stroke.keys()): return

        self.last_stroke_label.setText(stroke.rtfcre or "…")
        self.engine.output = self.__last_stroke_engine_enabled
        
        self.__last_stroke_from_widget = False
        self.__last_stroke_keys = None

    def resize_from_center(self, width: int, height: int):
        try:
            rect = self.geometry()
            old_size = self.size()

            # In practice, the new size will be constrained to the minimum size, so it is not necessarily the given size
            new_size = QSize(
                max(self.minimumWidth(), width),
                max(self.minimumHeight(), height),
            )
            
            # Do not use QSize.__sub__ because it does not accept negative/zero values
            x_diff = new_size.width() - old_size.width()
            y_diff = new_size.height() - old_size.height()


            rect.moveTopLeft(QPoint(rect.left() - x_diff // 2, rect.top() - y_diff // 2))
            rect.setSize(new_size)
            
            self.setGeometry(rect)

        except Exception as error:
            self.last_stroke_label.setText(str(error))
        



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

    # in centimeters
    _KEY_SIZE_NUM_BAR = 0.96890420899
    _KEY_SIZE = 1.8
    _COMPOUND_KEY_SIZE = 0.91507619738
    _REDUCED_KEY_SIZE = _KEY_SIZE - _COMPOUND_KEY_SIZE / 2

    _ROW_HEIGHTS = (
        _KEY_SIZE_NUM_BAR,
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # top row
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # bottom row
    )

    _COL_WIDTHS = (
        _KEY_SIZE,
    ) * 3 + (
        _REDUCED_KEY_SIZE,  # H-, R-
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE * 2 + _KEY_SIZE * 2.5,  # *
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # -F, -R
    ) + (
        _KEY_SIZE,
    ) * 2 + (
        _REDUCED_KEY_SIZE,  # -T, -S
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # -D, -Z
    )

    VOWEL_SET_WIDTHS = (
        _REDUCED_KEY_SIZE,
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,
    )

    _KEY_OFFSETS = (
        0,
        _KEY_SIZE * 0.75,
        _KEY_SIZE * 0.75,
        0,
    )

    end_stroke = pyqtSignal(set)  #set[str]
    after_touch_event = pyqtSignal()

    #region Overrides

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.current_stroke_keys: set[str] = set()
        self.key_widgets: list[KeyWidget] = []

        self.__setup_ui()


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

    def __setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addLayout(self.__build_main_rows_layout())
        layout.addSpacing(self.__px(self._KEY_SIZE))
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
    
        
        self.screen().physicalDotsPerInchChanged.connect(lambda _dpi: self.__resize_dpi_responsive_widgets())
        self.window().windowHandle().screenChanged.connect(lambda _screen: self.__resize_dpi_responsive_widgets())


    # TODO it is not well indicated that this function and the next mutate key_widgets
    def __build_main_rows_layout(self):
        self.main_rows_layout = layout = QGridLayout()
        for (values, label, grid_position) in KeyboardWidget.MAIN_ROWS_KEYS:
            key_widget = KeyWidget(values, label, self)
            self.key_widgets.append(key_widget)

            layout.addWidget(key_widget, *grid_position)

        layout.setSpacing(0)

        for i, size_cm in enumerate(KeyboardWidget._ROW_HEIGHTS):
            layout.setRowMinimumHeight(i, self.__px(size_cm))
            layout.setRowStretch(i, 0)

        for i, size_cm in enumerate(KeyboardWidget._COL_WIDTHS):
            layout.setColumnMinimumWidth(i, self.__px(size_cm))
            layout.setColumnStretch(i, 0)

        layout.setColumnStretch(5, 1)  # * key


        return layout

    def __build_vowel_row_layout(self):
        self.vowel_row_layout = layout = QHBoxLayout()

        layout.setSpacing(0)

        def add_vowel_set(vowel_key_descriptors):
            for ((values, label), width) in zip(vowel_key_descriptors, KeyboardWidget.VOWEL_SET_WIDTHS):
                key_widget = KeyWidget(values, label, self)
                self.key_widgets.append(key_widget)
                key_widget.setFixedSize(self.__px(width), self.__px(self._KEY_SIZE))

                layout.addWidget(key_widget)

        
        layout.addSpacing(self.__px(self._KEY_SIZE) * 3)
        add_vowel_set(KeyboardWidget.VOWEL_ROW_KEYS_LEFT)
        layout.addStretch(1)
        add_vowel_set(KeyboardWidget.VOWEL_ROW_KEYS_RIGHT)
        layout.addSpacing(self.__px(self._KEY_SIZE) * 4)

        return layout


    def __resize_dpi_responsive_widgets(self):
        for i, size_cm in enumerate(KeyboardWidget._ROW_HEIGHTS):
            self.main_rows_layout.setRowMinimumHeight(i, self.__px(size_cm))

        for i, size_cm in enumerate(KeyboardWidget._COL_WIDTHS):
            self.main_rows_layout.setColumnMinimumWidth(i, self.__px(size_cm))


        self.layout().itemAt(1).spacerItem().changeSize(0, self.__px(KeyboardWidget._KEY_SIZE))


        for i, size_cm in zip(
            range(self.vowel_row_layout.count()),
            (KeyboardWidget._KEY_SIZE * 3,) + KeyboardWidget.VOWEL_SET_WIDTHS
                    + (0,) + KeyboardWidget.VOWEL_SET_WIDTHS
                    + (KeyboardWidget._KEY_SIZE * 4,),
        ):
            item = self.vowel_row_layout.itemAt(i)

            if widget := item.widget():
                widget.setMinimumSize(self.__px(size_cm), self.__px(KeyboardWidget._KEY_SIZE))
            elif spacer_item := item.spacerItem():
                spacer_item.changeSize(self.__px(size_cm), 0)

        self.main_rows_layout.invalidate()
        self.vowel_row_layout.invalidate()
        self.layout().invalidate()

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
    
        for key_widget in self.key_widgets:
            old_touched, old_matched = key_widget.touched, key_widget.matched

            if key_widget in touched_key_widgets:
                key_widget.touched = True
                key_widget.matched = True

            elif all(key in self.current_stroke_keys for key in key_widget.values):
                key_widget.touched = False
                key_widget.matched = True

            else:
                key_widget.touched = False
                key_widget.matched = False


            if (old_touched, old_matched) != (key_widget.touched, key_widget.matched):
                # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                # self.style().unpolish(key_widget)
                self.style().polish(key_widget)

    def __px(self, cm: float) -> int:
        return round(cm * self.screen().physicalDotsPerInch() / 2.54)


class KeyWidget(QToolButton):
    #region Overrides

    def __init__(self, values: list[str], label: str, parent: QWidget = None):
        # super().__init__(label, parent)
        super().__init__(parent)

        self.values = values

        self.__touched = False
        self.__matched = False

        self.__setup_ui(label)

    def event(self, event: QEvent):
        # Prevents automatic button highlighting
        if event.type() == QEvent.HoverEnter:
            self.setAttribute(Qt.WA_UnderMouse, False)

        return super().event(event)

    #endregion

    def __setup_ui(self, label):
        self.setText(label)

        if label:
            self.setFont(QFont("Atkinson Hyperlegible", 16))


        # self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)


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
