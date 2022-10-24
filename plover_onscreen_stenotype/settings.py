from PyQt5.QtCore import (
	QObject,
	pyqtSignal,
)

from enum import Enum, auto


class KeyboardLayout(Enum):
	STAGGERED = auto()
	GRID = auto()


class Settings(QObject):
	keyboard_layout_change = pyqtSignal(KeyboardLayout)
	
	def __init__(self):
		super().__init__()

		self.__keyboard_layout = KeyboardLayout.STAGGERED

	@property
	def keyboard_layout(self):
		return self.__keyboard_layout

	@keyboard_layout.setter
	def keyboard_layout(self, value: KeyboardLayout):
		self.__keyboard_layout = value
		self.keyboard_layout_change.emit(value)
