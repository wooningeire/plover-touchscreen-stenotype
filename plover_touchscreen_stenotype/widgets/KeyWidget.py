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


from ..lib.reactivity import Ref, watch
from ..lib.constants import FONT_FAMILY


class KeyWidget(QToolButton):
    #region Overrides

    def __init__(self, values: list[str], label_maybe_ref: "str | Ref[str]", parent: QWidget=None):
        # super().__init__(label, parent)
        super().__init__(parent)

        self.values = values

        self.__touched = False
        self.__matched = False

        self.__setup_ui(label_maybe_ref)

    def event(self, event: QEvent):
        # Prevents automatic button highlighting
        if event.type() == QEvent.HoverEnter:
            self.setAttribute(Qt.WA_UnderMouse, False)

        return super().event(event)

    #endregion

    def __setup_ui(self, label_maybe_ref: "str | Ref[str]"):
        self.setFont(QFont(FONT_FAMILY, 16))

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