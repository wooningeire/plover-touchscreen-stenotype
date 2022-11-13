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
	stroke_preview_change = pyqtSignal()
	key_width_change = pyqtSignal(float)
	
	def __init__(self):
		super().__init__()

		self.__key_layout = KeyLayout.STAGGERED

		self.__stroke_preview_stroke = True
		self.__stroke_preview_translation = True

		self.__key_width = 2

	@property
	def key_layout(self):
		return self.__key_layout

	@key_layout.setter
	def key_layout(self, value: KeyLayout):
		self.__key_layout = value
		self.key_layout_change.emit(value)

	@property
	def stroke_preview_stroke(self):
		return self.__stroke_preview_stroke

	@stroke_preview_stroke.setter
	def stroke_preview_stroke(self, value: bool):
		self.__stroke_preview_stroke = value
		self.stroke_preview_change.emit()

	@property
	def stroke_preview_translation(self):
		return self.__stroke_preview_translation

	@stroke_preview_translation.setter
	def stroke_preview_translation(self, value: bool):
		self.__stroke_preview_translation = value
		self.stroke_preview_change.emit()

	@property
	def stroke_preview_full(self):
		return self.stroke_preview_stroke and self.stroke_preview_translation

	@property
	def stroke_preview_visible(self):
		return self.stroke_preview_stroke or self.stroke_preview_translation


	@property
	def key_width(self):
		return self.__key_width
	
	@key_width.setter
	def key_width(self, value: float):
		self.__key_width = value
		self.key_width_change.emit(value)
