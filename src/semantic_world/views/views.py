from dataclasses import dataclass, field

import numpy as np
from probabilistic_model.probabilistic_circuit.rx.helper import uniform_measure_of_event
from typing_extensions import List

from semantic_world.geometry import BoundingBox, BoundingBoxCollection
from semantic_world.spatial_types import Point3
from semantic_world.variables import SpatialVariables
from semantic_world import PrefixedName
from semantic_world.world import View, Body
from semantic_world.world_entity import EnvironmentView


@dataclass(unsafe_hash=True)
class Handle(View):
    body: Body

    def __post_init__(self):
        self.name = self.body.name


@dataclass(unsafe_hash=True)
class Container(View):
    body: Body

    def __post_init__(self):
        self.name = self.body.name


@dataclass(unsafe_hash=True)
class Table(View):
    """
    A view that represents a table.
    """

    top: Body
    """
    The body that represents the table's top surface.
    """

    def points_on_table(self, amount: int = 100) -> List[Point3]:
        """
        Get points that are on the table.

        :amount: The number of points to return.
        :returns: A list of points that are on the table.
        """
        area_of_table = BoundingBoxCollection.from_shapes(self.top.collision)
        event = area_of_table.event
        p = uniform_measure_of_event(event)
        p = p.marginal(SpatialVariables.xy)
        samples = p.sample(amount)
        z_coordinate = np.full((amount, 1), max([b.max_z for b in area_of_table]) + 0.01)
        samples = np.concatenate((samples, z_coordinate), axis=1)
        return [Point3.from_xyz(*s, reference_frame=self.top) for s in samples]

    def __post_init__(self):
        self.name = self.top.name

################################


@dataclass(unsafe_hash=True)
class Components(View):
    ...


@dataclass(unsafe_hash=True)
class Furniture(View):
    ...


#################### subclasses von Components
@dataclass(unsafe_hash=True)
class Door(Components):
    body: Body
    handle: Handle

    def __post_init__(self):
        self.name = self.body.name

@dataclass(unsafe_hash=True)
class Fridge(View):
    body: Body
    door: Door

    def __post_init__(self):
        self.name = self.body.name


@dataclass(unsafe_hash=True)
class Kitchen(EnvironmentView):
    """
    Represents a view of a kitchen.
    """
    fridges: List[Fridge] = field(default_factory=list)

    def __post_init__(self):
        if self.name is None:
            self.name = PrefixedName('kitchen', prefix='environment')


@dataclass(unsafe_hash=True)
class Drawer(Components):
    container: Container
    handle: Handle

    def __post_init__(self):
        self.name = self.container.name


############################### subclasses to Furniture
@dataclass
class Cupboard(Furniture):
    ...


############################### subclasses to Cupboard
@dataclass(unsafe_hash=True)
class Cabinet(Cupboard):
    container: Container
    drawers: list[Drawer] = field(default_factory=list, hash=False)

    def __post_init__(self):
        self.name = self.container.name


@dataclass
class Wardrobe(Cupboard):
    doors: List[Door] = field(default_factory=list)

@dataclass
class MultiBodyView(View):
    """
    A Generic View for multiple bodies.
    """
    bodies: List[Body] = field(default_factory=list, hash=False)
    views: List[View] = field(default_factory=list, hash=False)

    def add_body(self, body: Body):
        self.bodies.append(body)
        body._views.append(self)

    def add_view(self, view: View):
        self.views.append(view)
        view._views.append(self)