from typing import cast

from PyQt5.QtCore import (
    pyqtSignal,
    pyqtBoundSignal,
    QPointF,
)
from PyQt5.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsView,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QLayout,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from plover.steno import Stroke
import plover.log

from ..KeyWidget import KeyWidget
from ...lib.keyboard_layout.LayoutDescriptor import Group, GroupOrganizationType, KeyGroup, Key, GroupOrganizationType, ADAPTATION_RATE, MEAN_DEVIATION_FACTOR
from ...lib.reactivity import on, on_many, watch, watch_many, Ref, computed
from ..composables.UseDpi import UseDpi
from ...lib.constants import KEY_GROUP_STYLESHEET
from ...lib.util import empty_stroke, not_none, render, child, Point


def set_group_transforms(item: QGraphicsItem, group: "Group | KeyGroup", bounding_rect_change_signals: list[pyqtBoundSignal], *, displacement: Ref[Point], dpi: UseDpi):
    @watch_many(group.x.change, group.y.change, displacement.change, *bounding_rect_change_signals, dpi.change, parent=item.parentWidget())
    def set_group_pos():
        rect = item.boundingRect()
        item.setPos(
            dpi.cm(group.x.value + displacement.value.x) - rect.width() * group.alignment.value[0],
            dpi.cm(group.y.value + displacement.value.y) - rect.height() * group.alignment.value[1],
        )

    if group.angle is not None:
        @watch_many(*bounding_rect_change_signals, dpi.change, parent=item.parentWidget())
        def set_origin_point():
            item.setTransformOriginPoint(
                item.boundingRect().width() * group.alignment.value[0],
                item.boundingRect().height() * group.alignment.value[1],
            )

        @watch(group.angle.change, parent=item.parentWidget())
        def set_group_angle():
            item.setRotation(not_none(group.angle).value)

class KeyGroupWidget(QWidget):
    displacement_this_stroke_change = pyqtSignal(object, object)  # KeyGroupWidget, Point | None, Point | None,
    last_displacement_change = pyqtSignal(object, object)  # KeyGroupWidget, Point | None, Point | None,

    def __init__(
        self,
        group: KeyGroup,
        scene: QGraphicsScene,
        view: QGraphicsView,
        parent: "QWidget | None"=None,
        *,
        touched_key_widgets: Ref[set[KeyWidget]],
        current_stroke: Ref[Stroke],
        avg_group_displacement_this_stroke: Ref[Point],
        avg_group_displacement: Ref[Point],
        dpi: UseDpi,
    ):
        super().__init__(parent)


        items: list[QGraphicsItem] = []
        bounding_rect_change_signals: list[pyqtBoundSignal] = []

        key_widgets_to_keys: dict[KeyWidget, Key] = {}


        last_touch: "Ref[QTouchEvent.TouchPoint | None]" = Ref(None)
        last_touched_key_widget: "Ref[KeyWidget | None]" = Ref(None)

        displacement_active = computed(lambda: group.adaptive_transform and last_touched_key_widget.value is not None and last_touch.value is not None,
                last_touched_key_widget, last_touch)

        displacement = Ref(Point(0, 0))

        tapped_in_current_stroke = Ref(False)
        last_displacement = Ref(Point(0, 0))

        def recompute_displacement_this_stroke():
            if not displacement_active.value:
                return Point(0, 0)
            
            proxy_rect = proxy.boundingRect()

            key = key_widgets_to_keys[last_touched_key_widget.value]

            key_widget_center = not_none(last_touched_key_widget.value).geometry().center()
            proxy_inverse_transform = proxy.deviceTransform(view.viewportTransform()).translate(-proxy_rect.x(), -proxy_rect.y()).inverted()[0]
            local_touch_pos = proxy_inverse_transform.map(not_none(last_touch.value).pos())
            return Point(
                dpi.px_to_cm(local_touch_pos.x() - key_widget_center.x()),# - (key.center_offset_x.value if key.center_offset_x is not None else 0),
                dpi.px_to_cm(local_touch_pos.y() - key_widget_center.y()),# - (key.center_offset_y.value if key.center_offset_y is not None else 0),
            ) * ADAPTATION_RATE
        
        displacement_this_stroke = Ref(Point(0, 0))
        
        @on_many(last_touch.change, last_touched_key_widget.change, displacement_active.change)
        def update_displacement_this_stroke():
            displacement_this_stroke.value = recompute_displacement_this_stroke()
            emit_displacement_update()
        
        displacement = Ref(Point(0, 0))
        

        @on(avg_group_displacement.change)
        def on_stroke_reset():
            if current_stroke.value: return

            proxy_transform = proxy.deviceTransform(view.viewportTransform())
            proxy_inverse_transform = proxy_transform.inverted()[0]
            local_avg_group_displacement_this_stroke = Point.from_qpointf(proxy_inverse_transform.map(avg_group_displacement_this_stroke.value.to_qpointf() + proxy_transform.map(QPointF(0, 0))))
            local_avg_group_displacement = Point.from_qpointf(proxy_inverse_transform.map(avg_group_displacement.value.to_qpointf() + proxy_transform.map(QPointF(0, 0))))
            
            if tapped_in_current_stroke.value:
                new_displacement_centered = last_displacement.value + displacement_this_stroke.value - local_avg_group_displacement
                displacement.value = local_avg_group_displacement + new_displacement_centered * MEAN_DEVIATION_FACTOR 
            else:
                displacement.value = last_displacement.value + local_avg_group_displacement_this_stroke

            last_displacement.value = displacement.value
            tapped_in_current_stroke.value = False
            displacement_this_stroke.value = Point(0, 0)

            proxy_transform = proxy.deviceTransform(view.viewportTransform())
            absolute_last_displacement = Point.from_qpointf(proxy_transform.map(last_displacement.value.to_qpointf()) - proxy_transform.map(QPointF(0, 0)))
            self.last_displacement_change.emit(self, absolute_last_displacement)
    
        def emit_displacement_update():
            if displacement_active.value:
                proxy_transform = proxy.deviceTransform(view.viewportTransform())
                absolute_displacement_this_stroke = Point.from_qpointf(proxy_transform.map(displacement_this_stroke.value.to_qpointf()) - proxy_transform.map(QPointF(0, 0)))
                self.displacement_this_stroke_change.emit(self, absolute_displacement_this_stroke)
            else:
                self.displacement_this_stroke_change.emit(self, None)


        def notify_touch_release(touch: QTouchEvent.TouchPoint, key_widget: KeyWidget):
            tapped_in_current_stroke.value = True
            last_touch.value = touch
            last_touched_key_widget.value = key_widget
        self.notify_touch_release = notify_touch_release

        def reset_position():
            last_touch.value = None
            last_touched_key_widget.value = None

            last_displacement.value = Point(0, 0)
            displacement_this_stroke.value = Point(0, 0)
            tapped_in_current_stroke.value = False
            displacement.value = Point(0, 0)
        self.reset_position = reset_position


        def get_key_stroke(key: Key) -> Stroke:
            try:
                return Stroke.from_steno(key.steno)
            except ValueError:
                return empty_stroke()


        if group.organization.type == GroupOrganizationType.VERTICAL:
            @render(self, QVBoxLayout())
            def render_widget(widget: QWidget, _: QVBoxLayout):
                @watch_many(not_none(group.organization.width).change, dpi.change, parent=widget)
                def set_container_width():
                    widget.setFixedWidth(dpi.cm(not_none(group.organization.width).value))

                @watch_many(*(not_none(element.height).change for element in group.elements), dpi.change, parent=widget)
                def set_container_height():
                    widget.setFixedHeight(dpi.cm(sum(not_none(element.height).value for element in group.elements)))

                bounding_rect_change_signals.append(not_none(group.organization.width).change)

                for key in group.elements:
                    assert key.height is not None

                    @child(widget, KeyWidget(get_key_stroke(key), key.label, touched_key_widgets=touched_key_widgets, current_stroke=current_stroke, dpi=dpi))
                    def render_widget(key_widget: KeyWidget, _: None):
                        key_widgets_to_keys[key_widget] = key
                        current_key = key

                        @watch_many(not_none(current_key.height).change, dpi.change, parent=key_widget)
                        def set_height():
                            key_widget.setFixedHeight(dpi.cm(not_none(current_key.height).value))
                        bounding_rect_change_signals.append(not_none(current_key.height).change)

                        return ()
                return ()

        elif group.organization.type == GroupOrganizationType.HORIZONTAL:
            @render(self, QHBoxLayout())
            def render_widget(widget: QWidget, _: QHBoxLayout):
                @watch_many(not_none(group.organization.height).change, dpi.change, parent=widget)
                def set_container_height():
                    widget.setFixedHeight(dpi.cm(not_none(group.organization.height).value))

                @watch_many(*(not_none(element.width).change for element in group.elements), dpi.change, parent=widget)
                def set_container_width():
                    widget.setFixedWidth(dpi.cm(sum(not_none(element.width).value for element in group.elements)))

                bounding_rect_change_signals.append(not_none(group.organization.height).change)

                for key in group.elements:
                    assert key.width is not None

                    @child(widget, KeyWidget(get_key_stroke(key), key.label, touched_key_widgets=touched_key_widgets, current_stroke=current_stroke, dpi=dpi))
                    def render_widget(key_widget: KeyWidget, _: None):
                        key_widgets_to_keys[key_widget] = key
                        current_key = key

                        @watch_many(not_none(current_key.width).change, dpi.change, parent=key_widget)
                        def set_width():
                            key_widget.setFixedWidth(dpi.cm(not_none(current_key.width).value))
                        bounding_rect_change_signals.append(not_none(current_key.width).change)

                        return ()
                return ()
                
        elif group.organization.type == GroupOrganizationType.GRID:
            heights = not_none(group.organization.row_heights)
            widths = not_none(group.organization.col_widths)

            @render(self, QGridLayout())
            def render_widget(widget: QWidget, layout: QGridLayout):
                @watch_many(*(height.change for height in heights), dpi.change, parent=widget)
                def set_container_height():
                    widget.setFixedHeight(dpi.cm(sum(height.value for height in heights)))

                @watch_many(*(width.change for width in widths), dpi.change, parent=widget)
                def set_container_width():
                    widget.setFixedWidth(dpi.cm(sum(width.value for width in widths)))

                bounding_rect_change_signals.extend(height.change for height in heights)
                bounding_rect_change_signals.extend(width.change for width in widths)

                for key in group.elements:
                    @child(widget, KeyWidget(get_key_stroke(key), key.label, touched_key_widgets=touched_key_widgets, current_stroke=current_stroke, dpi=dpi))
                    def render_widget(key_widget: KeyWidget, _: None):
                        row_start = key.grid_location[0]
                        col_start = key.grid_location[1]
                        row_span = key.grid_location[2] if len(key.grid_location) > 2 else 1
                        col_span = key.grid_location[3] if len(key.grid_location) > 2 else 1

                        key_height = sum(heights[row_start + 1:row_start + row_span], heights[row_start])
                        key_width = sum(widths[col_start + 1:col_start + col_span], widths[col_start])

                        key_widgets_to_keys[key_widget] = key
                        @watch_many(key_height.change, key_width.change, dpi.change, parent=key_widget)
                        def set_size():
                            key_widget.setFixedSize(dpi.cm(key_width.value), dpi.cm(key_height.value))
                        return key.grid_location
                return ()
            
                    
        self.__proxy = proxy = not_none(scene.addWidget(self))
        items.append(proxy)


        set_group_transforms(self.__proxy, group, bounding_rect_change_signals, displacement=displacement, dpi=dpi)
                    
        self.setStyleSheet(KEY_GROUP_STYLESHEET)
    
    @property
    def proxy(self):
        return self.__proxy