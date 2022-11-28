from PyQt5.QtCore import (
    QEvent,
   	QPoint,
    Qt,
)
from PyQt5.QtWidgets import (
    QGraphicsView,
	QWidget,
	QGraphicsProxyWidget,
)
from PyQt5.QtGui import (
	QTouchEvent,
)


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .KeyboardWidget import KeyboardWidget
else:
    KeyboardWidget = object

from .KeyWidget import KeyWidget


class RotatableKeyContainer(QGraphicsView):
	"""
	`QGraphicsView` used to transform a group of `KeyWidget`s. Provides additional styling and access to key positions
	"""

	def __init__(self, widget: QWidget, proxy: QGraphicsProxyWidget, *args):
		super().__init__(*args)

		self.__widget = widget
		self.__proxy = proxy

		self.__setup_ui()

	def __setup_ui(self):
		# self.setAttribute(Qt.WA_AcceptTouchEvents)

		# Disable scrolling
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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

	def key_widget_at_point(self, screen_coords: QPoint) -> KeyWidget:
		# Convert screen coords to container widget coords, which can then be used to retrieve the key widget
		widget_coords = self.__proxy.deviceTransform(self.viewportTransform()).inverted()[0].map(screen_coords)
		return self.__widget.childAt(widget_coords)
