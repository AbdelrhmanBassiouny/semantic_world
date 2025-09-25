import pytest
from entity_query_language import symbolic_mode, From, let, entity, an, in_, not_

from semantic_world.datastructures.prefixed_name import PrefixedName
from semantic_world.spatial_types import TransformationMatrix
from semantic_world.views.factories import (
    HandleFactory,
    DoorFactory,
    Direction,
    DoubleDoorFactory,
)
from semantic_world.views.views import Door
from semantic_world.world_description.world_entity import Body

@pytest.fixture
def double_door_world():
    door_factory = DoorFactory(
        name=PrefixedName("door"),
        handle_factory=HandleFactory(name=PrefixedName("handle")),
        handle_direction=Direction.Y,
    )
    door_transform = TransformationMatrix.from_xyz_rpy(y=-0.5)

    door_factory2 = DoorFactory(
        name=PrefixedName("door2"),
        handle_factory=HandleFactory(name=PrefixedName("handle2")),
        handle_direction=Direction.NEGATIVE_Y,
    )
    door_transform2 = TransformationMatrix.from_xyz_rpy(y=0.5)

    door_factories = [door_factory, door_factory2]
    door_transforms = [door_transform, door_transform2]

    factory = DoubleDoorFactory(
        name=PrefixedName("double_door"),
        door_factories=door_factories,
        door_transforms=door_transforms,
    )
    world = factory.create()
    return world

def test_query_for_bodies_that_does_not_belong_to_doors(double_door_world):
    world = double_door_world
    with symbolic_mode():
        all_entryways = Door(From(world.views))
        door_bodies = all_entryways.bodies
        other_body = let(type_=Body, domain=world.bodies_with_enabled_collision)
        bodies_without_excluded_bodies_query = an(
            entity(other_body, not_(in_(other_body, door_bodies)))
        )
        q = an(entity(door_bodies))

    result = list(q.evaluate())

    filtered_bodies = list(bodies_without_excluded_bodies_query.evaluate())
    expected_bodies = [world.get_body_by_name("double_door")]
    assert filtered_bodies == expected_bodies