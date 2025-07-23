from semantic_world.world_entity import Body, EnvironmentView, View
from ripple_down_rules.datastructures.tracked_object import TrackedObjectMixin, X
from ripple_down_rules import *


def conditions_169119401358620755610132125806000007134(case) -> bool:
    def conditions_for_view_possible_locations_of_type_view(case: View) -> bool:
        """Get conditions on whether it's possible to conclude a value for View.possible_locations  of type View."""
        return any(has(type(case), Body, recursive=True))
    return conditions_for_view_possible_locations_of_type_view(case)


def conclusion_169119401358620755610132125806000007134(case) -> Generator[Type[View], None, None]:
    def view_possible_locations_of_type_view(case: View) -> Generator[Type[View], None, None]:
        """Get possible value(s) for View.possible_locations  of type View."""
        Location = X
        yield from (loc for loc, _ in has(Location, type(case), recursive=True)
                    if isA(loc, EnvironmentView))
    yield from view_possible_locations_of_type_view(case)


