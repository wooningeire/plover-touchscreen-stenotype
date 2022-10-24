from PyQt5.QtCore import (
	QObject,
	pyqtSignal,
)

from enum import Enum, auto


class KeyLayout(Enum):
	STAGGERED = auto()
	GRID = auto()


class Settings(QObject):
	key_layout_change = pyqtSignal(KeyLayout)
	
	def __init__(self):
		super().__init__()

		self.__key_layout = KeyLayout.STAGGERED

	@property
	def key_layout(self):
		return self.__key_layout

	@key_layout.setter
	def key_layout(self, value: KeyLayout):
		self.__key_layout = value
		self.key_layout_change.emit(value)
