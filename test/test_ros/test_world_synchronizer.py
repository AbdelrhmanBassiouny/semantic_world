import os
import time
import unittest

import sqlalchemy
from ormatic.utils import drop_database
from sqlalchemy import select
from sqlalchemy.orm import Session

from semantic_world.adapters.ros.world_synchronizer import (
    StateSynchronizer,
    ModelReloadSynchronizer,
    ModelSynchronizer,
)
from semantic_world.adapters.urdf import URDFParser
from semantic_world.datastructures.prefixed_name import PrefixedName
from semantic_world.orm.ormatic_interface import Base, WorldMappingDAO
from semantic_world.testing import rclpy_node
from semantic_world.utils import get_semantic_world_directory_root
from semantic_world.world import World
from semantic_world.world_description.connections import (
    Connection6DoF,
)
from semantic_world.world_description.world_entity import Body


def create_dummy_world():
    w = World()
    b1 = Body(name=PrefixedName("b1"))
    b2 = Body(name=PrefixedName("b2"))
    with w.modify_world():
        w.add_kinematic_structure_entity(b1)
        w.add_kinematic_structure_entity(b2)
        w.add_connection(Connection6DoF(b1, b2, _world=w))
    return w


def test_state_synchronization(rclpy_node):

    w1 = create_dummy_world()
    w2 = create_dummy_world()

    synchronizer_1 = StateSynchronizer(
        node=rclpy_node,
        world=w1,
    )
    synchronizer_2 = StateSynchronizer(
        node=rclpy_node,
        world=w2,
    )

    # Allow time for publishers/subscribers to connect on unique topics
    time.sleep(0.2)

    w1.state.data[0, 0] = 1.0
    w1.notify_state_change()
    time.sleep(0.2)
    assert w1.state.data[0, 0] == 1.0
    assert w1.state.data[0, 0] == w2.state.data[0, 0]

    synchronizer_1.close()
    synchronizer_2.close()


def test_model_reload(rclpy_node):

    engine = sqlalchemy.create_engine(
        "sqlite+pysqlite:///file::memory:?cache=shared",
        connect_args={"check_same_thread": False, "uri": True},
    )
    drop_database(engine)
    Base.metadata.create_all(engine)
    session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
    session1 = session_maker()
    session2 = session_maker()

    w1 = create_dummy_world()
    w2 = World()

    synchronizer_1 = ModelReloadSynchronizer(
        rclpy_node,
        w1,
        session=session1,
    )
    synchronizer_2 = ModelReloadSynchronizer(
        rclpy_node,
        w2,
        session=session2,
    )

    synchronizer_1.publish_reload_model()
    time.sleep(1.0)
    assert len(w2.kinematic_structure_entities) == 2

    query = session1.scalars(select(WorldMappingDAO)).all()
    assert len(query) == 1
    assert w2.get_kinematic_structure_entity_by_name("b2")

    synchronizer_1.close()
    synchronizer_2.close()


def test_model_synchronization_body_only(rclpy_node):

    w1 = World(name="w1")
    w2 = World(name="w2")

    synchronizer_1 = ModelSynchronizer(
        node=rclpy_node,
        world=w1,
    )
    synchronizer_2 = ModelSynchronizer(
        node=rclpy_node,
        world=w2,
    )

    with w1.modify_world():
        new_body = Body(name=PrefixedName("b3"))
        w1.add_kinematic_structure_entity(new_body)
        assert len(w1.kinematic_structure_entities) == 1

    time.sleep(0.2)
    assert len(w1.kinematic_structure_entities) == 1
    assert len(w2.kinematic_structure_entities) == 1

    assert w2.get_kinematic_structure_entity_by_name("b3")

    synchronizer_1.close()
    synchronizer_2.close()


def test_model_synchronization_creation_only(rclpy_node):

    w1 = World(name="w1")
    w2 = World(name="w2")

    synchronizer_1 = ModelSynchronizer(
        node=rclpy_node,
        world=w1,
    )
    synchronizer_2 = ModelSynchronizer(
        node=rclpy_node,
        world=w2,
    )

    with w1.modify_world():
        b2 = Body(name=PrefixedName("b2"))
        w1.add_kinematic_structure_entity(b2)

        new_body = Body(name=PrefixedName("b3"))
        w1.add_kinematic_structure_entity(new_body)

        c = Connection6DoF(b2, new_body, _world=w1)
        w1.add_connection(c)
    time.sleep(0.1)
    assert len(w1.kinematic_structure_entities) == 2
    assert len(w2.kinematic_structure_entities) == 2
    assert len(w1.connections) == 1
    assert len(w2.connections) == 1

    synchronizer_1.close()
    synchronizer_2.close()


def test_model_synchronization_merge_full_world(rclpy_node):

    w1 = World(name="w1")
    w2 = World(name="w2")

    synchronizer_1 = ModelSynchronizer(
        node=rclpy_node,
        world=w1,
    )
    synchronizer_2 = ModelSynchronizer(
        node=rclpy_node,
        world=w2,
    )

    pr2_world = URDFParser.from_file(
        os.path.join(
            get_semantic_world_directory_root(os.getcwd()),
            "resources",
            "urdf",
            "pr2_kinematic_tree.urdf",
        )
    ).parse()

    with w1.modify_world():
        new_body = Body(name=PrefixedName("b3"))
        w1.add_kinematic_structure_entity(new_body)

    w1.merge_world(pr2_world)

    def wait_for_sync(timeout=3.0, interval=0.05):
        start = time.time()
        while time.time() - start < timeout:
            body_names_1 = [body.name for body in w1.kinematic_structure_entities]
            body_names_2 = [body.name for body in w2.kinematic_structure_entities]
            if body_names_1 == body_names_2:
                return body_names_1, body_names_2
            time.sleep(interval)

        body_names_1 = [body.name for body in w1.kinematic_structure_entities]
        body_names_2 = [body.name for body in w2.kinematic_structure_entities]
        return body_names_1, body_names_2

    body_names_1, body_names_2 = wait_for_sync()

    assert body_names_1 == body_names_2
    assert len(w1.kinematic_structure_entities) == len(w2.kinematic_structure_entities)

    w1_connection_names = [c.name for c in w1.connections]
    w2_connection_names = [c.name for c in w2.connections]
    assert w1_connection_names == w2_connection_names
    assert len(w1.connections) == len(w2.connections)
    assert len(w2.degrees_of_freedom) == len(w1.degrees_of_freedom)

    synchronizer_1.close()
    synchronizer_2.close()


def test_callback_pausing(rclpy_node):

    w1 = World(name="w1")
    w2 = World(name="w2")

    model_synchronizer_1 = ModelSynchronizer(node=rclpy_node, world=w1)
    model_synchronizer_2 = ModelSynchronizer(node=rclpy_node, world=w2)
    state_synchronizer_1 = StateSynchronizer(node=rclpy_node, world=w1)
    state_synchronizer_2 = StateSynchronizer(node=rclpy_node, world=w2)

    model_synchronizer_2.pause()
    state_synchronizer_2.pause()
    assert model_synchronizer_2._is_paused
    assert state_synchronizer_2._is_paused

    with w1.modify_world():
        b2 = Body(name=PrefixedName("b2"))
        w1.add_kinematic_structure_entity(b2)

        new_body = Body(name=PrefixedName("b3"))
        w1.add_kinematic_structure_entity(new_body)

        c = Connection6DoF(b2, new_body, _world=w1)
        w1.add_connection(c)

    time.sleep(0.1)
    assert len(model_synchronizer_2.missed_messages) == 1
    assert len(w1.kinematic_structure_entities) == 2
    assert len(w2.kinematic_structure_entities) == 0
    assert len(w1.connections) == 1
    assert len(w2.connections) == 0

    state_synchronizer_2.resume()
    model_synchronizer_2.resume()
    state_synchronizer_2.apply_missed_messages()
    model_synchronizer_2.apply_missed_messages()

    time.sleep(0.1)
    assert len(w1.kinematic_structure_entities) == 2
    assert len(w2.kinematic_structure_entities) == 2
    assert len(w1.connections) == 1
    assert len(w2.connections) == 1


if __name__ == "__main__":
    unittest.main()
