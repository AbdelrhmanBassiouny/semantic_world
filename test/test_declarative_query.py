from semantic_world import FixedConnection, PrismaticConnection
from semantic_world.views.views import Handle


class Var:
    def __init__(self, name: str):
        self.name = name

    def __getattr__(self, item):
        return Attr(self, item)

class Attr:
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    def __eq__(self, other):
        return Eq(self, other)

    def __repr__(self):
        return f"{self.obj}.{self.attr}"

class Eq:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __and__(self, other):
        return And(self, other)

    def __repr__(self):
        return f"({self.left} == {self.right})"

class And:
    def __init__(self, *conds):
        self.conds = conds

    def __and__(self, other):
        return And(*self.conds, other)

    def __repr__(self):
        return " and ".join(map(str, self.conds))


FC: FixedConnection = Var("FC")
PC: PrismaticConnection = Var("PC")
H: Handle = Var("H")
condition = (FC.child == H.body) & (FC.parent == PC.child)
