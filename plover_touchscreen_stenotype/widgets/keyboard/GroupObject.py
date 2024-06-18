from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    QPointF,
)
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
)

from plover.steno import Stroke
import plover.log

from typing import cast


from ..KeyWidget import KeyWidget
from .KeyGroupWidget import KeyGroupWidget, set_group_transforms
from ...lib.keyboard_layout.LayoutDescriptor import Group, KeyGroup, LayoutDescriptor
from ...lib.reactivity import Ref, on
from ..composables.UseDpi import UseDpi
from ...lib.util import not_none, Point


class GroupObject(QObject):
    displacement_this_stroke_change = pyqtSignal(KeyGroupWidget, object)
    last_displacement_change = pyqtSignal(KeyGroupWidget, object)

    def __init__(
        self,
        group: "LayoutDescriptor | Group",
        scene: QGraphicsScene,
        view: QGraphicsView,
        *,
        touched_key_widgets: Ref[set[KeyWidget]],
        current_stroke: Ref[Stroke],
        parent_group_displacement_this_stroke: Ref[Point]=Ref(Point(0, 0)),
        parent_group_displacement: Ref[Point]=Ref(Point(0, 0)),
        dpi: UseDpi,
    ):
        super().__init__()

        items: list[QGraphicsItem] = []
        self.__group_objects: list[GroupObject] = [self]
        self.__key_group_widgets: list[KeyGroupWidget] = []

        key_group_displacements_this_stroke: dict[KeyGroupWidget, Point] = {}
        absolute_group_displacement_this_stroke = Ref(Point(0, 0))
        absolute_group_displacement = Ref(Point(0, 0))

        def reset_position():
            nonlocal key_group_displacements_this_stroke
            
            key_group_displacements_this_stroke = {}
            absolute_group_displacement_this_stroke.value = Point(0, 0)
            absolute_group_displacement.value = Point(0, 0)
        self.reset_position = reset_position


        use_adaptive_transform = isinstance(group, Group) and group.adaptive_transform
        child_displacement_this_stroke = absolute_group_displacement_this_stroke if use_adaptive_transform else parent_group_displacement_this_stroke
        child_displacement = absolute_group_displacement if use_adaptive_transform else parent_group_displacement

        def handle_displacement_this_stroke_update(key_group_widget: KeyGroupWidget, displacement: "Point | None"):
            self.displacement_this_stroke_change.emit(key_group_widget, displacement)

            if displacement is not None:
                key_group_displacements_this_stroke[key_group_widget] = displacement
                return

            if key_group_widget in key_group_displacements_this_stroke:
                del key_group_displacements_this_stroke[key_group_widget]

        def handle_last_displacement_update(key_group_widget: KeyGroupWidget, displacement: Point):
            self.last_displacement_change.emit(key_group_widget, displacement)

            key_group_last_displacements[key_group_widget] = displacement

        @on(current_stroke.change)
        def on_stroke_reset():
            nonlocal key_group_displacements_this_stroke
            nonlocal key_group_last_displacements

            if current_stroke.value: return

            if not use_adaptive_transform or len(key_group_displacements_this_stroke) == 0:
                return
            
            avg_displacement_this_stroke = sum((displacement for displacement in key_group_displacements_this_stroke.values()), Point(0, 0)) / len(key_group_displacements_this_stroke)
            avg_displacement = sum((
                displacement + key_group_displacements_this_stroke[key_group_widget]
                    if key_group_widget in key_group_displacements_this_stroke
                    else displacement + avg_displacement_this_stroke
                for key_group_widget, displacement in key_group_last_displacements.items()
            ), Point(0, 0)) / len(key_group_last_displacements)

            # transform = self.__item_group.deviceTransform(view.viewportTransform())
            # inverse_transform = transform.inverted()[0]
            # local_avg_displacement = inverse_transform.map(avg_displacement.to_qpointf() + transform.map(QPointF(0, 0)))

            absolute_group_displacement_this_stroke.value = avg_displacement_this_stroke
            absolute_group_displacement.value = avg_displacement

            key_group_displacements_this_stroke = {}


        for subgroup in group.elements:
            if isinstance(subgroup, Group):
                group_object = GroupObject(subgroup, scene, view,
                    touched_key_widgets=touched_key_widgets,
                    current_stroke=current_stroke,
                    parent_group_displacement_this_stroke=child_displacement_this_stroke,
                    parent_group_displacement=child_displacement,
                    dpi=dpi,
                )

                @on(group_object.displacement_this_stroke_change)
                def update_displacement(key_group_widget: KeyGroupWidget, displacement: "Point | None"):
                    handle_displacement_this_stroke_update(key_group_widget, displacement)

                @on(group_object.last_displacement_change)
                def update_displacement(key_group_widget: KeyGroupWidget, displacement: Point):
                    handle_last_displacement_update(key_group_widget, displacement)


                items.append(group_object.item_group)
                self.__group_objects.extend(group_object.group_objects)
                self.__key_group_widgets.extend(group_object.key_group_widgets)
            elif isinstance(subgroup, KeyGroup):
                key_group_widget = KeyGroupWidget(subgroup, scene, view,
                    touched_key_widgets=touched_key_widgets,
                    current_stroke=current_stroke,
                    avg_group_displacement_this_stroke=child_displacement_this_stroke,
                    avg_group_displacement=child_displacement,
                    dpi=dpi,
                )

                @on(key_group_widget.displacement_this_stroke_change)
                def update_displacement(key_group_widget: KeyGroupWidget, displacement: "Point | None"):
                    handle_displacement_this_stroke_update(key_group_widget, displacement)

                @on(key_group_widget.last_displacement_change)
                def update_displacement(key_group_widget: KeyGroupWidget, displacement: Point):
                    handle_last_displacement_update(key_group_widget, displacement)

                items.append(key_group_widget.proxy)
                self.__key_group_widgets.append(key_group_widget)

        self.__item_group = not_none(scene.createItemGroup(items))

        key_group_last_displacements = {
            key_group_widget: Point(0, 0)
            for key_group_widget in self.__key_group_widgets
        }

        if isinstance(group, Group):
            set_group_transforms(self.__item_group, group, [], displacement=Ref(Point(0, 0)), dpi=dpi)

    @property
    def item_group(self):
        return self.__item_group
    
    @property
    def key_group_widgets(self):
        return self.__key_group_widgets
    
    @property
    def group_objects(self):
        return self.__group_objects