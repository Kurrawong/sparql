from lark import Tree
from lark.visitors import Visitor_Recursive


class SparqlSerializer(Visitor_Recursive):
    def __init__(self):
        self._result = ""
        super().__init__()
        self._indent = 0

    @property
    def result(self):
        return self._result

    def base(self, node: Tree):
        self._result += "BASE "

    def prefix(self, node: Tree):
        self._result += "PREFIX "

    def pname_ns(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def iriref(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def prefixed_name(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def values_clause(self, node: Tree):
        self._result += "VALUES "

    def var(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def left_curly_brace(self, node: Tree):
        self._result += " {\n"
        self._indent += 1

    def right_curly_brace(self, node: Tree):
        self._result += "\n} "
        self._indent -= 1

    def left_parenthesis(self, node: Tree):
        self._result += "("

    def right_parenthesis(self, node: Tree):
        self._result += ")"

    def string(self, node: Tree):
        self._result += node.children[0].value

    def langtag(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def datatype(self, node: Tree):
        self._result += "^^"

    def undef(self, node: Tree):
        self._result += "UNDEF "

    def numeric_literal(self, node: Tree):
        self._result += f"{node.children[0].children[0].value} "

    def boolean_literal(self, node: Tree):
        self._result += f"{node.children[0].children[0].value} "
