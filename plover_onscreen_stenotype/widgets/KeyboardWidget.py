from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
    QSpacerItem,
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


class KeyboardWidget(QWidget):
    TOP_ROW = 2
    LOW_ROW = 4
    TOP_COMPOUND_ROW = 1
    LOW_COMPOUND_ROW = 3

    _MAIN_ROWS_KEYS = (
        (
            (["#"], ""),
            (["#", "S-"], ""),
            (["S-"], "S", 3),
        ), (
            (["#"], ""),
            (["#", "T-"], ""),
            (["T-"], "T"),
            (["T-", "K-"], ""),
            (["K-"], "K"),
        ), (
            (["#"], ""),
            (["#", "P-"], ""),
            (["P-"], "P"),
            (["P-", "W-"], ""),
            (["W-"], "W"),
        ), (
            (["#"], ""),
            (["#", "H-"], ""),
            (["H-"], "H"),
            (["H-", "R-"], ""),
            (["R-"], "R"),
        ), (
            (["#"], ""),
            (["#", "H-", "*"], ""),
            (["H-", "*"], ""),
            (["H-", "R-", "*"], ""),
            (["R-", "*"], ""),
        ), (
            (["#"], "#"),
            (["#", "*"], ""),
            (["*"], "*", 3),
        ), (
            (["#"], ""),
            (["#", "*", "-F"], ""),
            (["*", "-F"], ""),
            (["*", "-F", "-R"], ""),
            (["*", "-R"], ""),
        ), (
            (["#"], ""),
            (["#", "-F"], ""),
            (["-F"], "F"),
            (["-F", "-R"], ""),
            (["-R"], "R"),
        ), (
            (["#"], ""),
            (["#", "-P"], ""),
            (["-P"], "P"),
            (["-P", "-B"], ""),
            (["-B"], "B"),
        ), (
            (["#"], ""),
            (["#", "-L"], ""),
            (["-L"], "L"),
            (["-L", "-G"], ""),
            (["-G"], "G"),
        ), (
            (["#"], ""),
            (["#", "-T"], ""),
            (["-T"], "T"),
            (["-T", "-S"], ""),
            (["-S"], "S"),
        ), (
            (["#"], ""),
            (["#", "-T", "-D"], ""),
            (["-T", "-D"], ""),
            (["-T", "-S", "-D", "-Z"], ""),
            (["-S", "-Z"], ""),
        ), (
            (["#"], ""),
            (["#", "-D"], ""),
            (["-D"], "D"),
            (["-D", "-Z"], ""),
            (["-Z"], "Z"),
        ),
    )

    # # [keys], (row, column, rowSpan, columnSpan)
    # MAIN_ROWS_KEYS = (
    #     (["#"], "#", (0, 0, 1, -1)),
    #     (["S-"], "S", (TOP_ROW, 0, 3, 1)),
    #     (["T-"], "T", (TOP_ROW, 1)),
    #     (["K-"], "K", (LOW_ROW, 1)),
    #     (["P-"], "P", (TOP_ROW, 2)),
    #     (["W-"], "W", (LOW_ROW, 2)),
    #     (["H-"], "H", (TOP_ROW, 3)),
    #     (["R-"], "R", (LOW_ROW, 3)),
    #     (["H-", "*"], "", (TOP_ROW, 4)),
    #     (["R-", "*"], "", (LOW_ROW, 4)),
    #     (["*"], "*", (TOP_ROW, 5, 3, 1)),
    #     (["*", "-F"], "", (TOP_ROW, 6)),
    #     (["*", "-R"], "", (LOW_ROW, 6)),
    #     (["-F"], "F", (TOP_ROW, 7)),
    #     (["-R"], "R", (LOW_ROW, 7)),
    #     (["-P"], "P", (TOP_ROW, 8)),
    #     (["-B"], "B", (LOW_ROW, 8)),
    #     (["-L"], "L", (TOP_ROW, 9)),
    #     (["-G"], "G", (LOW_ROW, 9)),
    #     (["-T"], "T", (TOP_ROW, 10)),
    #     (["-S"], "S", (LOW_ROW, 10)),
    #     (["-T", "-D"], "", (TOP_ROW, 11)),
    #     (["-S", "-Z"], "", (LOW_ROW, 11)),
    #     (["-D"], "D", (TOP_ROW, 12)),
    #     (["-Z"], "Z", (LOW_ROW, 12)),

    #     (["#", "S-"], "", (TOP_COMPOUND_ROW, 0)),
    #     (["#", "T-"], "", (TOP_COMPOUND_ROW, 1)),
    #     (["#", "P-"], "", (TOP_COMPOUND_ROW, 2)),
    #     (["#", "H-"], "", (TOP_COMPOUND_ROW, 3)),
    #     (["#", "H-", "*"], "", (TOP_COMPOUND_ROW, 4)),
    #     (["#", "*"], "", (TOP_COMPOUND_ROW, 5)),
    #     (["#", "*", "-F"], "", (TOP_COMPOUND_ROW, 6)),
    #     (["#", "-F"], "", (TOP_COMPOUND_ROW, 7)),
    #     (["#", "-P"], "", (TOP_COMPOUND_ROW, 8)),
    #     (["#", "-L"], "", (TOP_COMPOUND_ROW, 9)),
    #     (["#", "-T"], "", (TOP_COMPOUND_ROW, 10)),
    #     (["#", "-T", "-D"], "", (TOP_COMPOUND_ROW, 11)),
    #     (["#", "-D"], "", (TOP_COMPOUND_ROW, 12)),

    #     (["T-", "K-"], "", (LOW_COMPOUND_ROW, 1)),
    #     (["P-", "W-"], "", (LOW_COMPOUND_ROW, 2)),
    #     (["H-", "R-"], "", (LOW_COMPOUND_ROW, 3)),
    #     (["H-", "R-", "*"], "", (LOW_COMPOUND_ROW, 4)),
    #     (["*", "-R", "-F"], "", (LOW_COMPOUND_ROW, 6)),
    #     (["-F", "-R"], "", (LOW_COMPOUND_ROW, 7)),
    #     (["-P", "-B"], "", (LOW_COMPOUND_ROW, 8)),
    #     (["-L", "-G"], "", (LOW_COMPOUND_ROW, 9)),
    #     (["-T", "-S"], "", (LOW_COMPOUND_ROW, 10)),
    #     (["-T", "-S", "-D", "-Z"], "", (LOW_COMPOUND_ROW, 11)),
    #     (["-D", "-Z"], "", (LOW_COMPOUND_ROW, 12)),
    # )

    _VOWEL_ROW_KEYS_LEFT = (
        (["A-"], "A"),
        (["A-", "O-"], ""),
        (["O-"], "O"),
    )

    _VOWEL_ROW_KEYS_RIGHT = (
        (["-E"], "E"),
        (["-E", "-U"], ""),
        (["-U"], "U"),
    )

    # in centimeters
    _KEY_SIZE_NUM_BAR = 0.96890420899
    _KEY_SIZE = 1.8
    _COMPOUND_KEY_SIZE = 0.91507619738
    _REDUCED_KEY_SIZE = _KEY_SIZE - _COMPOUND_KEY_SIZE / 2

    _PINKY_STRETCH = _KEY_SIZE * 0.125

    _ROW_HEIGHTS = (
        _KEY_SIZE_NUM_BAR,
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # top row
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # bottom row
    )

    _COL_WIDTHS = (
        _KEY_SIZE + _PINKY_STRETCH,
    ) + (
        _KEY_SIZE,
    ) * 2 + (
        _REDUCED_KEY_SIZE,  # H-, R-
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE * 2 + _KEY_SIZE * 2.5,  # *
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # -F, -R
    ) + (
        _KEY_SIZE,
    ) * 2 + (
        _REDUCED_KEY_SIZE + _PINKY_STRETCH,  # -T, -S
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,  # -D, -Z
    )

    _VOWEL_SET_WIDTHS = (
        _REDUCED_KEY_SIZE,
        _COMPOUND_KEY_SIZE,
        _REDUCED_KEY_SIZE,
    )

    _ROWS_GAP = _KEY_SIZE * 0.85

    _COL_OFFSETS = (
        0,  # S-
        _KEY_SIZE * 0.35, # T-, K-
        _KEY_SIZE * 0.6, # P-, W-
        0, # H-, R-
    ) + (
        0,
    ) * 3 + (
        0,  # -F, -R
        _KEY_SIZE * 0.6,  # -P, -B
        _KEY_SIZE * 0.35,  # -L, -G
        0,  # -T, -S
        0,
        0, # -D, -Z
    )


    _ASTERISK_COLUMN_INDEX = 5
    

    end_stroke = pyqtSignal(set)  #set[str]
    after_touch_event = pyqtSignal()

    dpi_change = pyqtSignal()

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
        layout.addSpacerItem(QSpacerItem(
            0,
            self.__px(KeyboardWidget._ROWS_GAP),
            QSizePolicy.Preferred,
            QSizePolicy.Expanding
        ))
        layout.addLayout(self.__build_vowel_row_layout())
        
        layout.setSpacing(0)

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
    
        
        self.screen().physicalDotsPerInchChanged.connect(lambda _dpi: self.__handle_dpi_change())
        self.window().windowHandle().screenChanged.connect(lambda _screen: self.__handle_dpi_change())


    # TODO it is not well indicated that this function and the next mutate key_widgets
    def __build_main_rows_layout(self):
        # Parameter defaults on inner functions are used to create closures

        self.main_rows_layout = layout = QHBoxLayout()
        for i, (column, col_width_cm, col_offset_cm) in enumerate(zip(
            KeyboardWidget._MAIN_ROWS_KEYS,
            KeyboardWidget._COL_WIDTHS,
            KeyboardWidget._COL_OFFSETS,
        )):
            column_layout = QVBoxLayout()
            column_layout.addStretch(1)

            row_pos = 0

            for values, label, *rest in column:
                row_span = rest[0] if rest else 1
                row_heights_cm = KeyboardWidget._ROW_HEIGHTS[row_pos:row_pos + row_span]

                key_widget = KeyWidget(values, label, self)
                self.key_widgets.append(key_widget)


                if i == KeyboardWidget._ASTERISK_COLUMN_INDEX:
                    def resize(
                        key_widget: KeyWidget=key_widget,
                        col_width_cm: float=col_width_cm,
                        row_heights_cm: tuple[float]=row_heights_cm,
                    ):
                        key_widget.setMinimumWidth(self.__px(col_width_cm))
                        key_widget.setFixedHeight(sum(self.__px(height) for height in row_heights_cm))

                        # Defer setting the minimum width to later; setting it immediately causes it to shrink to this size initially
                        QTimer.singleShot(0, lambda: key_widget.setMinimumWidth(0))
                        
                else:
                    def resize(
                        key_widget: KeyWidget=key_widget,
                        col_width_cm: float=col_width_cm,
                        row_heights_cm: tuple[float]=row_heights_cm,
                    ):
                        key_widget.setFixedSize(self.__px(col_width_cm), sum(self.__px(height) for height in row_heights_cm))

                resize()
                self.dpi_change.connect(resize)


                column_layout.addWidget(key_widget)

                row_pos += row_span
                
            
            column_layout.addSpacing(self.__px(col_offset_cm))

            column_spacer = column_layout.itemAt(column_layout.count() - 1).spacerItem()
            def resize_column_spacing(
                column_spacer: QSpacerItem=column_spacer,
                col_offset_cm: float=col_offset_cm,
            ):
                column_spacer.changeSize(0, self.__px(col_offset_cm))
            self.dpi_change.connect(resize_column_spacing)

            
            layout.addLayout(column_layout)

            # if i in (0, 9): # S- and -L, -G
            #     layout.addSpacing(self.__px(KeyboardWidget._PINKY_STRETCH))
            if i == KeyboardWidget._ASTERISK_COLUMN_INDEX:
                layout.setStretchFactor(column_layout, 1)


        # def resize_asterisk_column():
        #     asterisk_column = layout.itemAt(KeyboardWidget._ASTERISK_COLUMN_INDEX).layout()
        #     for item in (asterisk_column.itemAt(i) for i in range(asterisk_column.count())):
        #         if not (widget := item.widget()): continue
        #         widget.setMinimumWidth(0)

        # QTimer.singleShot(0, resize_asterisk_column)
            

        layout.setSpacing(0)

        # self.main_rows_layout = layout = QGridLayout()
        # for (values, label, grid_position) in KeyboardWidget.MAIN_ROWS_KEYS:
        #     key_widget = KeyWidget(values, label, self)
        #     self.key_widgets.append(key_widget)

        #     layout.addWidget(key_widget, *grid_position)

        # for i, size_cm in enumerate(KeyboardWidget._ROW_HEIGHTS):
        #     layout.setRowMinimumHeight(i, self.__px(size_cm))
        #     layout.setRowStretch(i, 0)

        # for i, size_cm in enumerate(KeyboardWidget._COL_WIDTHS):
        #     layout.setColumnMinimumWidth(i, self.__px(size_cm))
        #     layout.setColumnStretch(i, 0)

        # layout.setColumnStretch(5, 1)  # * key


        return layout

    def __build_vowel_row_layout(self):
        # Parameter defaults on inner functions are used to create closures

        self.vowel_row_layout = layout = QHBoxLayout()

        layout.setSpacing(0)

        def add_vowel_set(vowel_key_descriptors):
            for ((values, label), width) in zip(vowel_key_descriptors, KeyboardWidget._VOWEL_SET_WIDTHS):
                key_widget = KeyWidget(values, label, self)
                self.key_widgets.append(key_widget)


                def resize(
                    key_widget: KeyWidget=key_widget,
                    width: float=width,
                ):
                    key_widget.setFixedSize(self.__px(width), self.__px(KeyboardWidget._KEY_SIZE))

                resize()
                self.dpi_change.connect(resize)


                layout.addWidget(key_widget)

        
        layout.addSpacing(self.__px(KeyboardWidget._KEY_SIZE) * 3 + self.__px(KeyboardWidget._PINKY_STRETCH))
        add_vowel_set(KeyboardWidget._VOWEL_ROW_KEYS_LEFT)
        layout.addStretch(1)
        add_vowel_set(KeyboardWidget._VOWEL_ROW_KEYS_RIGHT)
        layout.addSpacing(self.__px(KeyboardWidget._KEY_SIZE) * 4 + self.__px(KeyboardWidget._PINKY_STRETCH))

        def resize_spacing():
            layout.itemAt(0).spacerItem().changeSize(self.__px(KeyboardWidget._KEY_SIZE) * 3 + self.__px(KeyboardWidget._PINKY_STRETCH), 0)
            layout.itemAt(layout.count() - 1).spacerItem().changeSize(self.__px(KeyboardWidget._KEY_SIZE) * 4 + self.__px(KeyboardWidget._PINKY_STRETCH), 0)
        self.dpi_change.connect(resize_spacing)


        return layout


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
