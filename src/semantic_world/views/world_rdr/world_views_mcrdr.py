from ripple_down_rules.datastructures.case import Case, create_case
from ripple_down_rules.utils import make_set
from ripple_down_rules.datastructures.enums import Stop
from typing_extensions import Optional, Set
from .world_views_mcrdr_defs import *


attribute_name = 'views'
conclusion_type = (Drawer, Container, Handle, Fridge, set, Apple, list, Stop, Pear, Cabinet, Door,)
mutually_exclusive = False


def classify(case: World, **kwargs) -> Set[Union[Drawer, Container, Handle, Fridge, Apple, Stop, Pear, Cabinet, Door]]:
    if not isinstance(case, Case):
        case = create_case(case, max_recursion_idx=3)
    conclusions = set()

    if conditions_90574698325129464513441443063592862114(case):
        conclusions.update(make_set(conclusion_90574698325129464513441443063592862114(case)))

    if conditions_14920098271685635920637692283091167284(case):
        conclusions.update(make_set(conclusion_14920098271685635920637692283091167284(case)))

    if conditions_331345798360792447350644865254855982739(case):
        conclusions.update(make_set(conclusion_331345798360792447350644865254855982739(case)))

    if conditions_35528769484583703815352905256802298589(case):
        conclusions.update(make_set(conclusion_35528769484583703815352905256802298589(case)))

    if conditions_59112619694893607910753808758642808601(case):
        conclusions.update(make_set(conclusion_59112619694893607910753808758642808601(case)))

    if conditions_10840634078579061471470540436169882059(case):
        conclusions.update(make_set(conclusion_10840634078579061471470540436169882059(case)))

    if conditions_52105527190495248524986346719357133983(case):

        if conditions_64835036784308343494726080812549537103(case):
            pass
        else:
            conclusions.update(make_set(conclusion_52105527190495248524986346719357133983(case)))

    if conditions_280872513725872974386672859756490030634(case):
        conclusions.update(make_set(conclusion_280872513725872974386672859756490030634(case)))

    if conditions_334264492049883475267158922414742648081(case):

        if conditions_235169144625684529188900168101056825155(case):
            pass
        else:
            conclusions.update(make_set(conclusion_334264492049883475267158922414742648081(case)))

    if conditions_162443579946168380181368054170910504965(case):
        conclusions.update(make_set(conclusion_162443579946168380181368054170910504965(case)))
    return conclusions
