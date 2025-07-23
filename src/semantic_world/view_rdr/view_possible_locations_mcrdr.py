from ripple_down_rules.datastructures.case import Case, create_case
from .view_possible_locations_mcrdr_defs import *


attribute_name = 'possible_locations'
conclusion_type = (Type[View],)
mutually_exclusive = False
name = 'possible_locations'
case_type = View
case_name = 'view'


def classify(case: View, **kwargs) -> Generator[Type[View], None, None]:
    if not isinstance(case, Case):
        case = create_case(case, max_recursion_idx=3)

    if conditions_169119401358620755610132125806000007134(case):
        yield from conclusion_169119401358620755610132125806000007134(case)
    raise StopIteration
