from PyQt5.QtCore import (
    QEvent,
    QPoint,
    Qt,
    QTimer,
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QWidget,
    QLayout,
    QGraphicsProxyWidget,
    QGraphicsScene,
)
from PyQt5.QtGui import (
    QMouseEvent,
    QTransform,
    QResizeEvent,
)


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

from .KeyWidget import KeyWidget
from ..lib.constants import KEY_STYLESHEET

class RotatableKeyContainer(QGraphicsView):
    """
    `QGraphicsView` used to transform a group of `KeyWidget`s. Provides additional styling and access to key positions
    """

    @staticmethod
    def of_layout(layout: QLayout, align_left: bool, angle: float, parent: QWidget = None) -> "RotatableKeyContainer":
        scene = QGraphicsScene(parent)

        widget = QWidget()
        widget.setStyleSheet(KEY_STYLESHEET)
        widget.setAttribute(Qt.WA_TranslucentBackground) # Gives this container a transparent background
        widget.setLayout(layout)

        proxy = scene.addWidget(widget)

        container = RotatableKeyContainer(widget, proxy, align_left, angle, scene, parent)

        return container

    def __init__(self, widget: QWidget, proxy: QGraphicsProxyWidget, align_left: bool, angle: float, *args):
        super().__init__(*args)

        self.__widget = widget
        self.__proxy = proxy

        self.__align_left = align_left
        self.__angle = angle

        self.__setup_ui()

    def __setup_ui(self):
        # self.setAttribute(Qt.WA_AcceptTouchEvents)

        # Disable scrolling and hide scrollbars
        self.__h_scrollbar = h_scrollbar = self.horizontalScrollBar()
        self.__v_scrollbar = v_scrollbar = self.verticalScrollBar()

        h_scrollbar.setEnabled(False)
        v_scrollbar.setEnabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Scroll to the bottom of the container (bottom-align the key groups)
        QTimer.singleShot(0, self.__rescroll)

        # Clear default styling
        self.setStyleSheet("background: #00000000; border: none;")

    """ def event(self, event: QEvent):
        if not isinstance(event, QTouchEvent):
            return super().event(event)

        if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
            screen_coords = event.touchPoints()[0].pos().toPoint()
            widget_coords = self.__proxy.deviceTransform(self.viewportTransform()).inverted()[0].map(screen_coords)
            key_widget: KeyWidget = self.__widget.childAt(widget_coords)

        elif event.type() == QEvent.TouchEnd:
            pass

        return True """

    def key_widget_at_point(self, window_coords: QPoint) -> KeyWidget:
        # Convert screen coords to container widget coords, which can then be used to retrieve the key widget

        # Undo the widget's translation
        widget_translation = QTransform()
        widget_translation.translate(self.pos().x(), self.pos().y())
        view_coords = widget_translation.inverted()[0].map(window_coords)

        widget_coords = self.__proxy.deviceTransform(self.viewportTransform()).inverted()[0].map(view_coords)

        return self.__widget.childAt(widget_coords)

    def __rescroll(self):
        self.scroll_to_bottom()
        self.scroll_to_horizontal_edge()

    def scroll_to_bottom(self):
        self.__v_scrollbar.setValue(self.__v_scrollbar.maximum())

    def scroll_to_horizontal_edge(self):
        if self.__align_left:
            self.__h_scrollbar.setValue(self.__h_scrollbar.maximum())
        else:
            self.__h_scrollbar.setValue(self.__h_scrollbar.minimum())


    def update_size(self):
        self.__update_widget_size_and_position()
        QTimer.singleShot(0, self.__update_own_size)
        # self.__update_own_size()

    def __update_widget_size_and_position(self):
        widget = self.__widget
        layout = self.__widget.layout()

        for i in range(layout.count()):
            if child_layout := layout.itemAt(i).layout():
                child_layout.invalidate()

        # Constrains the widget to the size of its layout
        widget.setMaximumSize(layout.sizeHint())

        if self.__align_left:
            self.__proxy.setPos(0, -self.__widget.geometry().height())
            self.__proxy.setTransformOriginPoint(self.__widget.rect().bottomLeft())
        else:
            self.__proxy.setPos(-self.__widget.geometry().width(), -self.__widget.geometry().height())
            self.__proxy.setTransformOriginPoint(self.__widget.rect().bottomRight())

        self.__proxy.setRotation(self.__angle)

    def __update_own_size(self):
        scene = self.scene()

        scene.setSceneRect(scene.itemsBoundingRect())
        self.setMaximumSize(scene.sceneRect().size().toSize())

        QTimer.singleShot(0, self.__rescroll)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.scroll_to_horizontal_edge()
        return super().resizeEvent(event)
    

    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, value: float):
        self.__angle = value
        self.update_size()
