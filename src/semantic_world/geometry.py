from __future__ import annotations

import itertools
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import Optional, List, Iterator

from random_events.variable import Continuous
from typing_extensions import Self

import trimesh
from random_events.interval import SimpleInterval, Bound
from random_events.product_algebra import SimpleEvent, Event

from .spatial_types import TransformationMatrix, Point3
from .spatial_types.spatial_types import Expression
from .utils import IDGenerator

id_generator = IDGenerator()

@dataclass
class Color:
    """
    Dataclass for storing rgba_color as an RGBA value.
    The values are stored as floats between 0 and 1.
    The default rgba_color is white.
    """
    R: float = 1
    """
    Red value of the color.
    """

    G: float = 1
    """
    Green value of the color.
    """

    B: float = 1
    """
    Blue value of the color.
    """

    A: float = 1
    """
    Opacity of the color.
    """

@dataclass
class Scale:
    """
    Dataclass for storing the scale of geometric objects.
    """

    x: float = 1.
    """
    The scale in the x direction.
    """

    y: float = 1.
    """
    The scale in the y direction.
    """

    z: float = 1.
    """
    The scale in the z direction.
    """

@dataclass
class Shape(ABC):
    """
    Base class for all shapes in the world.
    """
    origin: TransformationMatrix

@dataclass
class Mesh(Shape):
    """
    A mesh shape.
    """

    filename: str = ""
    """
    Filename of the mesh.
    """

    scale: Scale = field(default_factory=Scale)
    """
    Scale of the mesh.
    """

    @cached_property
    def mesh(self) -> trimesh.Trimesh:
        """
        The mesh object.
        """
        return trimesh.load_mesh(self.filename)

    def as_bounding_box(self) -> BoundingBox:
        """
        Returns the bounding box of the mesh.
        """
        return BoundingBox.from_mesh(self.mesh)


@dataclass
class Primitive(Shape):
    """
    A primitive shape.
    """
    color: Color = field(default_factory=Color)


@dataclass
class Sphere(Primitive):
    """
    A sphere shape.
    """

    radius: float = 0.5
    """
    Radius of the sphere.
    """


@dataclass
class Cylinder(Primitive):
    """
    A cylinder shape.
    """
    width: float = 0.5
    height: float = 0.5


@dataclass
class Box(Primitive):
    """
    A box shape. Pivot point is at the center of the box.
    """
    scale: Scale = field(default_factory=Scale)

    def as_bounding_box(self) -> BoundingBox:
        """
        Returns the bounding box of the box.
        """
        return BoundingBox(-self.scale.x / 2, -self.scale.y / 2, -self.scale.z / 2,
                           self.scale.x / 2, self.scale.y / 2, self.scale.z / 2)

class SpatialVariables(Enum):
    x = Continuous("x")
    y = Continuous("y")
    z = Continuous("z")

@dataclass
class BoundingBox:
    min_x: float
    """
    The minimum x-coordinate of the bounding box.
    """

    min_y: float
    """
    The minimum y-coordinate of the bounding box.
    """

    min_z: float
    """
    The minimum z-coordinate of the bounding box.
    """

    max_x: float
    """
    The maximum x-coordinate of the bounding box.
    """

    max_y: float
    """
    The maximum y-coordinate of the bounding box.
    """

    max_z: float
    """
    The maximum z-coordinate of the bounding box.
    """

    def __hash__(self):
        # The hash should be this since comparing those via hash is checking if those are the same and not just equal
        return hash((self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z))

    @property
    def x_interval(self) -> SimpleInterval:
        """
        :return: The x interval of the bounding box.
        """
        return SimpleInterval(self.min_x, self.max_x, Bound.CLOSED, Bound.CLOSED)

    @property
    def y_interval(self) -> SimpleInterval:
        """
        :return: The y interval of the bounding box.
        """
        return SimpleInterval(self.min_y, self.max_y, Bound.CLOSED, Bound.CLOSED)

    @property
    def z_interval(self) -> SimpleInterval:
        """
        :return: The z interval of the bounding box.
        """
        return SimpleInterval(self.min_z, self.max_z, Bound.CLOSED, Bound.CLOSED)

    @property
    def simple_event(self) -> SimpleEvent:
        """
        :return: The bounding box as a random event.
        """
        return SimpleEvent({SpatialVariables.x.value: self.x_interval,
                            SpatialVariables.y.value: self.y_interval,
                            SpatialVariables.z.value: self.z_interval})

    def bloat(self, x_amount: float = 0., y_amount: float = 0, z_amount: float = 0) -> BoundingBox:
        """
        Enlarges the bounding box by a given amount in all dimensions.

        :param x_amount: The amount to adjust minimum and maximum x-coordinates
        :param y_amount: The amount to adjust minimum and maximum y-coordinates
        :param z_amount: The amount to adjust minimum and maximum z-coordinates
        :return: New enlarged bounding box
        """
        return self.__class__(self.min_x - x_amount, self.min_y - y_amount, self.min_z - z_amount,
                              self.max_x + x_amount, self.max_y + y_amount, self.max_z + z_amount)

    def contains(self, point: Point3) -> bool:
        """
        Check if the bounding box contains a point.
        """
        x, y, z = (point.x.to_np(), point.y.to_np(), point.z.to_np()) if isinstance(point.z, Expression) else (point.x, point.y, point.z)

        return self.simple_event.contains((x, y, z))

    def as_collection(self) -> BoundingBoxCollection:
        """
        Convert the bounding box to a collection of bounding boxes.

        :return: The bounding box as a collection
        """
        return BoundingBoxCollection([self])

    @classmethod
    def from_simple_event(cls, simple_event: SimpleEvent):
        """
        Create a list of bounding boxes from a simple random event.

        :param simple_event: The random event.
        :return: The list of bounding boxes.
        """
        result = []
        for x, y, z in itertools.product(simple_event[SpatialVariables.x.value].simple_sets,
                                         simple_event[SpatialVariables.y.value].simple_sets,
                                         simple_event[SpatialVariables.z.value].simple_sets):
            result.append(cls(x.lower, y.lower, z.lower, x.upper, y.upper, z.upper))
        return result

    def intersection_with(self, other: BoundingBox) -> Optional[BoundingBox]:
        """
        Compute the intersection of two bounding boxes.

        :param other: The other bounding box.
        :return: The intersection of the two bounding boxes or None if they do not intersect.
        """
        result = self.simple_event.intersection_with(other.simple_event)
        if result.is_empty():
            return None
        return self.__class__.from_simple_event(result)[0]

    def enlarge(self, min_x: float = 0., min_y: float = 0, min_z: float = 0,
                max_x: float = 0., max_y: float = 0., max_z: float = 0.):
        """
        Enlarge the axis-aligned bounding box by a given amount in-place.
        :param min_x: The amount to enlarge the minimum x-coordinate
        :param min_y: The amount to enlarge the minimum y-coordinate
        :param min_z: The amount to enlarge the minimum z-coordinate
        :param max_x: The amount to enlarge the maximum x-coordinate
        :param max_y: The amount to enlarge the maximum y-coordinate
        :param max_z: The amount to enlarge the maximum z-coordinate
        """
        self.min_x -= min_x
        self.min_y -= min_y
        self.min_z -= min_z
        self.max_x += max_x
        self.max_y += max_y
        self.max_z += max_z

    def enlarge_all(self, amount: float):
        """
        Enlarge the axis-aligned bounding box in all dimensions by a given amount in-place.

        :param amount: The amount to enlarge the bounding box
        """
        self.enlarge(amount, amount, amount,
                     amount, amount, amount)

    @classmethod
    def from_mesh(cls, mesh: trimesh.Trimesh) -> Self:
        """
        Create a bounding box from a trimesh object.
        :param mesh: The trimesh object.
        :return: The bounding box.
        """
        bounds = mesh.bounds
        return cls(bounds[0][0], bounds[0][1], bounds[0][2],
                   bounds[1][0], bounds[1][1], bounds[1][2])


@dataclass
class BoundingBoxCollection:
    """
    Dataclass for storing a collection of bounding boxes.
    """

    bounding_boxes: List[BoundingBox] = field(default_factory=list)

    def __iter__(self) -> Iterator[BoundingBox]:
        return iter(self.bounding_boxes)

    @property
    def event(self) -> Event:
        """
        :return: The bounding boxes as a random event.
        """
        return Event(*[box.simple_event for box in self.bounding_boxes])

    def merge(self, other: BoundingBoxCollection) -> BoundingBoxCollection:
        """
        Merge another bounding box collection into this one.

        :param other: The other bounding box collection.
        :return: The merged bounding box collection.
        """
        return BoundingBoxCollection(self.bounding_boxes + other.bounding_boxes)

    def bloat(self, x_amount: float = 0., y_amount: float = 0, z_amount: float = 0) -> BoundingBoxCollection:
        """
        Enlarges all bounding boxes in the collection by a given amount in all dimensions.

        :param x_amount: The amount to adjust the x-coordinates
        :param y_amount: The amount to adjust the y-coordinates
        :param z_amount: The amount to adjust the z-coordinates

        :return: The enlarged bounding box collection
        """
        return BoundingBoxCollection([box.bloat(x_amount, y_amount, z_amount) for box in self.bounding_boxes])

    @classmethod
    def from_simple_event(cls, simple_event: SimpleEvent):
        """
        Create a list of bounding boxes from a simple random event.

        :param simple_event: The random event.
        :return: The list of bounding boxes.
        """
        result = []
        for x, y, z in itertools.product(simple_event[SpatialVariables.x.value].simple_sets,
                                         simple_event[SpatialVariables.y.value].simple_sets,
                                         simple_event[SpatialVariables.z.value].simple_sets):
            result.append(BoundingBox(x.lower, y.lower, z.lower, x.upper, y.upper, z.upper))
        return result

    @classmethod
    def from_event(cls, event: Event) -> Self:
        """
        Create a list of bounding boxes from a random event.

        :param event: The random event.
        :return: The list of bounding boxes.
        """
        return cls([box for simple_event in event.simple_sets for box in cls.from_simple_event(simple_event)])
