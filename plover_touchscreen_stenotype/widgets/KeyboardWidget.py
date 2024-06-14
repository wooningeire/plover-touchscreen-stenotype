from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    pyqtBoundSignal,
    QPoint,
    QPointF,
    QRectF,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGraphicsView,
    QGraphicsScene,
    QGridLayout,
    QGraphicsItem,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from plover.steno import Stroke

from collections import Counter
from typing import cast, TYPE_CHECKING, Generator, Iterable
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object


from .KeyWidget import KeyWidget
from .RotatableKeyContainer import RotatableKeyContainer
from ..lib.keyboard_layout.LayoutDescriptor import Group, GroupOrganizationType, Key, KeyGroup, LayoutDescriptor, GroupOrganization, GroupOrganizationType, GroupAlignment
from ..lib.keyboard_layout.use_build_keyboard import use_build_keyboard
from ..settings import Settings
from ..lib.reactivity import Ref, RefAttr, watch, watch_many
from ..lib.UseDpi import UseDpi
from ..lib.constants import GRAPHICS_VIEW_STYLE, KEY_STYLESHEET
from ..lib.util import empty_stroke, not_none, render, child


class KeyboardWidget(QWidget):
    end_stroke = pyqtSignal(Stroke)
    current_stroke_change = pyqtSignal(Stroke)

    
    num_bar_pressed = RefAttr(bool)
    num_bar_pressed_ref = num_bar_pressed.ref_getter()


    def __init__(self, settings: Settings, left_right_width_diff: Ref[float], parent: "QWidget | None"=None):
        from ..lib.keyboard_layout.descriptors.english_stenotype_extended_custom import build_layout_descriptor

        super().__init__(parent)

        current_stroke: Stroke = empty_stroke()

        touches_to_key_widgets: dict[int, KeyWidget] = {} # keys of dict are from QTouchPoint::id
        key_widget_touch_counter: Counter[KeyWidget] = Counter()
        key_widgets: list[KeyWidget] = []

        self.num_bar_pressed = False

        self.settings = settings

        
        #region Touch handling

        def handle_touch_event(event: QTouchEvent):
            nonlocal current_stroke

            # Variables for detecting changes post-update
            had_num_bar = "#" in current_stroke.keys()

            if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
                old_stroke_length = len(current_stroke)

                for key_widget in updated_key_widgets(event.touchPoints()):
                    current_stroke += key_widget.substroke

                if len(current_stroke) > old_stroke_length and current_stroke:
                    self.current_stroke_change.emit(current_stroke)
                if not had_num_bar and "#" in current_stroke:
                    self.num_bar_pressed = True
                

            elif event.type() == QEvent.TouchEnd:
                # This also filters out empty strokes (Plover accepts them and will insert extra spaces)
                if current_stroke and all(touch.state() == Qt.TouchPointReleased for touch in event.touchPoints()):
                    self.end_stroke.emit(current_stroke)
                    current_stroke = empty_stroke()
                    touches_to_key_widgets.clear()
                    key_widget_touch_counter.clear()
                
                if had_num_bar:
                    self.num_bar_pressed = False

                
            update_key_widget_styles_and_state(key_widget_touch_counter.keys())
        self.__handle_touch_event = handle_touch_event


        def updated_key_widgets(touch_points: list[QTouchEvent.TouchPoint]) -> Generator[KeyWidget, None, None]:
            for touch in touch_points:
                if touch.state() == Qt.TouchPointStationary: continue

                if touch.id() in touches_to_key_widgets:
                    old_key_widget = touches_to_key_widgets[touch.id()]
                    key_widget_touch_counter[old_key_widget] -= 1

                    del touches_to_key_widgets[touch.id()]

                    if key_widget_touch_counter[old_key_widget] == 0:
                        del key_widget_touch_counter[old_key_widget]

                if touch.state() == Qt.TouchPointReleased: continue


                key_widget = key_widget_at(touch.pos().toPoint())
                if key_widget is None: continue


                touches_to_key_widgets[touch.id()] = key_widget
                key_widget_touch_counter[key_widget] += 1

                
                if not key_widget.matched:
                    yield key_widget


        containers: list[tuple[QWidget, QGraphicsItem]] = []
        graphics_view: QGraphicsView
        def key_widget_at(point: QPoint) -> "KeyWidget | None":
            for widget, proxy in containers:
                proxy_transform = proxy.deviceTransform(graphics_view.viewportTransform())
                widget_coords = proxy_transform.inverted()[0].map(point)

                key_widget = widget.childAt(widget_coords)
                if key_widget is not None:
                    return key_widget

            return None


        def update_key_widget_styles_and_state(touched_key_widgets: Iterable[KeyWidget]):
            stroke_has_ended = len(key_widget_touch_counter) == 0

            for key_widget in key_widgets:
                old_touched, old_matched = key_widget.touched, key_widget.matched

                if key_widget in touched_key_widgets:
                    key_widget.touched = True
                    key_widget.matched = True

                elif ((not stroke_has_ended and key_widget.matched) # optimization assumes keys will not be removed mid-stroke
                        or key_widget.substroke in current_stroke):
                    key_widget.touched = False
                    key_widget.matched = True

                else:
                    key_widget.touched = False
                    key_widget.matched = False


                if (old_touched, old_matched) != (key_widget.touched, key_widget.matched):
                    # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                    # self.style().unpolish(key_widget)
                    not_none(self.style()).polish(key_widget)

        #endregion


        #region Layout

        self.__dpi = dpi = UseDpi(self)
        layout_descriptor = build_layout_descriptor(self.settings, self)


        def build_group_elements(scene: QGraphicsScene, group: "LayoutDescriptor | Group"):
            items: list[QGraphicsItem] = []

            for subgroup in group.elements:
                if isinstance(subgroup, Group):
                    items.append(build_group(scene, subgroup))
                elif isinstance(subgroup, KeyGroup):
                    items.append(build_key_group(scene, subgroup))
                    
            return not_none(scene.createItemGroup(items))
        
        def set_group_transforms(item: QGraphicsItem, group: "Group | KeyGroup", bounding_rect_change_signals: list[pyqtBoundSignal]):
            @watch_many(group.x.change, group.y.change, *bounding_rect_change_signals, dpi.change)
            def set_group_pos():
                rect = item.boundingRect()
                item.setPos(
                    dpi.cm(group.x.value) - rect.width() * group.alignment.value[0],
                    dpi.cm(group.y.value) - rect.height() * group.alignment.value[1],
                )

            if group.angle is not None:
                @watch_many(*bounding_rect_change_signals, dpi.change)
                def set_origin_point():
                    item.setTransformOriginPoint(
                        item.boundingRect().width() * group.alignment.value[0],
                        item.boundingRect().height() * group.alignment.value[1],
                    )

                @watch(group.angle.change)
                def set_group_angle():
                    item.setRotation(group.angle.value)


        def build_group(scene: QGraphicsScene, group: Group):
            item_group = build_group_elements(scene, group)
            set_group_transforms(item_group, group, [])

            return item_group

        def build_key_group(scene: QGraphicsScene, group: KeyGroup):
            items: list[QGraphicsItem] = []

            bounding_rect_change_signals: list[pyqtBoundSignal] = []

            if group.organization.type == GroupOrganizationType.VERTICAL:
                @render(QWidget(), QVBoxLayout())
                def render_widget(widget: QWidget, _: QVBoxLayout):
                    @watch_many(group.organization.width.change, dpi.change)
                    def set_key_width():
                        widget.setFixedWidth(dpi.cm(group.organization.width.value))
                    bounding_rect_change_signals.append(group.organization.width.change)

                    for key in group.elements:
                        assert key.height is not None

                        @child(widget, KeyWidget(Stroke.from_steno(key.steno), key.label, dpi=dpi))
                        def render_widget(key_widget: KeyWidget, _: None):
                            key_widgets.append(key_widget)
                            current_key = key

                            @watch_many(current_key.height.change, dpi.change)
                            def set_height():
                                key_widget.setFixedHeight(dpi.cm(current_key.height.value))
                            bounding_rect_change_signals.append(current_key.height.change)

                            return ()
                        
                    widget.setStyleSheet(KEY_STYLESHEET)

                    proxy = not_none(scene.addWidget(widget))
                    items.append(proxy)
                    containers.append((widget, proxy))
                
                    return ()

            elif group.organization.type == GroupOrganizationType.HORIZONTAL:
                @render(QWidget(), QHBoxLayout())
                def render_widget(widget: QWidget, _: QHBoxLayout):
                    @watch_many(group.organization.height.change, dpi.change)
                    def set_key_height():
                        widget.setFixedHeight(dpi.cm(group.organization.height.value))
                    bounding_rect_change_signals.append(group.organization.height.change)

                    for key in group.elements:
                        assert key.width is not None

                        @child(widget, KeyWidget(Stroke.from_steno(key.steno), key.label, dpi=dpi))
                        def render_widget(key_widget: KeyWidget, _: None):
                            key_widgets.append(key_widget)
                            current_key = key

                            @watch_many(current_key.width.change, dpi.change)
                            def set_width():
                                key_widget.setFixedWidth(dpi.cm(current_key.width.value))
                            bounding_rect_change_signals.append(current_key.width.change)

                            return ()
                        
                    widget.setStyleSheet(KEY_STYLESHEET)

                    proxy = not_none(scene.addWidget(widget))
                    items.append(proxy)
                    containers.append((widget, proxy))
                
                    return ()
                    
            elif group.organization.type == GroupOrganizationType.GRID:
                @render(QWidget(), QGridLayout())
                def render_widget(widget: QWidget, layout: QGridLayout):
                    for i, height in enumerate(not_none(group.organization.row_heights)):
                        @watch_many(height.change, dpi.change)
                        def set_row_height():
                            layout.setRowMinimumHeight(i, dpi.cm(height.value))
                        bounding_rect_change_signals.append(height.change)

                    for i, width in enumerate(not_none(group.organization.col_widths)):
                        @watch_many(width.change, dpi.change)
                        def set_col_width():
                            layout.setColumnMinimumWidth(i, dpi.cm(width.value))
                        bounding_rect_change_signals.append(width.change)


                    for key in group.elements:
                        @child(widget, KeyWidget(Stroke.from_steno(key.steno), key.label, dpi=dpi))
                        def render_widget(key_widget: KeyWidget, _: None):
                            key_widgets.append(key_widget)
                            return key.grid_location
                        
                    widget.setStyleSheet(KEY_STYLESHEET)

                    proxy = not_none(scene.addWidget(widget))
                    items.append(proxy)
                    containers.append((widget, proxy))
                
                    return ()
                
            item_group = not_none(scene.createItemGroup(items))
            set_group_transforms(item_group, group, bounding_rect_change_signals)

            return item_group
        
        #endregion

        #region Render

        @render(self, QGridLayout())
        def render_widget(widget: QWidget, _: QGridLayout):
            scene = QGraphicsScene(self)

            @child(self, QGraphicsView(scene))
            def render_widget(view: QGraphicsView, _: None):
                nonlocal graphics_view

                view.setStyleSheet(GRAPHICS_VIEW_STYLE)
                
                item_group = build_group_elements(scene, layout_descriptor)
                rect = QRectF(item_group.boundingRect())

                # rect = QRectF(view.rect())
                # rect.moveCenter(QPointF(0, 0))

                view.setSceneRect(rect)

                graphics_view = view

                return ()
            
            return ()


        # build_keyboard, left_right_width_diff_src = use_build_keyboard(self.settings, self, dpi)

        # self.__build_keyboard = build_keyboard
        # layout, key_widgets = build_keyboard()
        # self.setLayout(layout)
        # key_widgets = key_widgets

        # @watch(left_right_width_diff_src.change)
        # def update_left_right_width_diff():
        #     left_right_width_diff.value = left_right_width_diff_src.value


        self.setStyleSheet(KEY_STYLESHEET)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #endregion


    def __rebuild_layout(self):
        # Detach listeners on the old key widgets to avoid leaking memory
        # TODO removing all listeners may become overzealous in the future
        self.__dpi.change.disconnect()

        # https://stackoverflow.com/questions/10416582/replacing-layout-on-a-qwidget-with-another-layout
        QWidget().setLayout(self.layout()) # Unparent and destroy the current layout so it can be replaced
        layout, key_widgets = self.__build_keyboard()
        self.setLayout(layout)
        key_widgets = key_widgets
        

    def event(self, event: QEvent) -> bool:
        """(override)"""

        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.__handle_touch_event(event)
        return True