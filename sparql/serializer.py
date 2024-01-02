from lark import Tree, Token
from lark.visitors import Visitor_Recursive


def get_prefixed_name(prefixed_name: Tree) -> str:
    return prefixed_name.children[0].value


def get_iriref(iriref: Tree) -> str:
    return iriref.children[0].value


def get_rdf_literal(rdf_literal: Tree) -> str:
    value = rdf_literal.children[0].children[0].value

    if len(rdf_literal.children) > 1:
        langtag_or_datatype = rdf_literal.children[1].children[0]
        if isinstance(langtag_or_datatype, Tree) and langtag_or_datatype.data == "iri":
            value += f"^^{get_iri(langtag_or_datatype)}"
        else:
            value += rdf_literal.children[1].children[0].value

    return value


def get_value(tree: Tree, memory: list[Token] = None) -> list[Token]:
    """This function walks a tree recursively and only expects a single path. Multiple paths raises a ValueError."""
    if memory is None:
        memory = []

    if isinstance(tree, Token):
        memory.append(tree)
    else:
        for child in tree.children:
            get_value(child, memory)

    return memory


def get_iri(iri: Tree) -> str:
    value = iri.children[0]
    if value.data == "iriref":
        return get_iriref(value)
    elif value.data == "prefixed_name":
        return get_prefixed_name(value)
    else:
        raise ValueError(f"Unexpected iri type: {value.data}")


def get_data_block_value(data_block_value: Tree) -> str:
    value = data_block_value.children[0]

    if value.data == "iri":
        return get_iri(value)
    elif value.data == "rdf_literal" or value.data == "numeric_literal" or value.data == "boolean_literal":
        return get_rdf_literal(value)
    elif value.data == "undef":
        return "UNDEF"
    else:
        raise ValueError(f"Unrecognized data_block_value type: {value.data}")


def get_var(var: Tree) -> str:
    return var.children[0].value


def get_vars(vars_: list[Tree]) -> str:
    result = ""
    for i, var in enumerate(vars_):
        result += get_var(var)
        if i + 1 != len(vars_):
            result += " "

    return result


class SparqlSerializer(Visitor_Recursive):
    def __init__(self):
        self._result = ""
        super().__init__()
        self._indent = 0

    @property
    def result(self):
        return self._result

    def _prologue(self, prologue: Tree):
        base_decls = list(filter(lambda x: x.data == "base_decl", prologue.children))
        prefix_decls = list(filter(lambda x: x.data == "prefix_decl", prologue.children))

        for base_decl in base_decls:
            self._result += f"{base_decl.children[0].children[0].value} {get_iriref(base_decl.children[1])}\n"

        for prefix_decl in prefix_decls:
            self._result += f"{prefix_decl.children[0].children[0].value} {prefix_decl.children[1].children[0].value} {get_iriref(prefix_decl.children[2])}\n"

        self._result += "\n"

    def query_unit(self, tree: Tree):
        self._query(tree.children[0])

    def _query(self, query: Tree):
        prologue = query.children[0]
        self._prologue(prologue)

        query_instance = query.children[1]
        if query_instance.data == "select_query":
            self._select_query(query_instance)

        values_clause = query.children[2]
        self._values_clause(values_clause)

    def _source_selector(self, source_selector: Tree):
        iri = source_selector.children[0]
        self._result += get_iri(iri)

    def _dataset_clause(self, dataset_clause: Tree):
        from_str = dataset_clause.children[0]
        self._result += f"{from_str} "
        graph_clause = dataset_clause.children[1]

        if graph_clause.data == "default_graph_clause":
            source_selector = graph_clause.children[0]
            self._source_selector(source_selector)
        elif graph_clause.data == "named_graph_clause":
            named_str = graph_clause.children[0].value
            self._result += f"{named_str} "
            source_selector = graph_clause.children[1]
            self._source_selector(source_selector)
        else:
            raise ValueError(f"Unexpected dataset_clause value: {graph_clause}")

        self._result += "\n"

    def _aggregate(self, aggregate: Tree):
        for child in aggregate.children:
            if isinstance(child, Token):
                self._result += f"{child.value}"
            else:
                # An expression
                self._expression(child)

    def _built_in_call(self, built_in_call: Tree):
        if len(built_in_call.children) > 1:
            raise NotImplementedError

        value = built_in_call.children[0]
        if isinstance(value, Tree) and value.data == "aggregate":
            self._aggregate(value)
        else:
            raise NotImplementedError

    def _primary_expression(self, primary_expression: Tree):
        value = primary_expression.children[0]

        if value.data == "built_in_call":
            self._built_in_call(value)
        elif value.data == "var":
            self._result += get_var(value)
        else:
            raise NotImplementedError

    def _unary_expression(self, unary_expression: Tree):
        if len(unary_expression.children) > 1:
            raise NotImplementedError

        primary_expression = unary_expression.children[0]
        self._primary_expression(primary_expression)

    def _multiplicative_expression(self, multiplicative_expression: Tree):
        unary_expression = multiplicative_expression.children[0]
        self._unary_expression(unary_expression)

        if len(multiplicative_expression.children) > 1:
            raise NotImplementedError

    def _additive_expression(self, additive_expression: Tree):
        multiplicative_expression = additive_expression.children[0]
        self._multiplicative_expression(multiplicative_expression)

        if len(additive_expression.children) > 1:
            raise NotImplementedError

    def _numeric_expression(self, numeric_expression: Tree):
        additive_expression = numeric_expression.children[0]
        self._additive_expression(additive_expression)

    def _relational_expression(self, relational_expression: Tree):
        numeric_expression = relational_expression.children[0]
        self._numeric_expression(numeric_expression)

        if len(relational_expression.children) > 1:
            raise NotImplementedError

    def _value_logical(self, value_logical: Tree):
        relational_expression = value_logical.children[0]
        self._relational_expression(relational_expression)

    def _conditional_and_expression(self, conditional_and_expression: Tree):
        value_logicals = list(filter(lambda x: x.data == "value_logical", conditional_and_expression.children))
        for i, value_logical in enumerate(value_logicals):
            self._value_logical(value_logical)
            if i + 1 != len(value_logicals):
                self._result += " && "

    def _conditional_or_expression(self, conditional_or_expression: Tree):
        conditional_and_expressions = list(filter(lambda x: x.data == "conditional_and_expression", conditional_or_expression.children))
        for i,  conditional_and_expression in enumerate(conditional_and_expressions):
            self._conditional_and_expression(conditional_and_expression)
            if i + 1 != len(conditional_and_expressions):
                self._result += " || "

    def _expression(self, expression: Tree):
        conditional_or_expression = expression.children[0]
        self._conditional_or_expression(conditional_or_expression)

    def _select_clause_var_or_expression(self, select_clause_var_or_expression: Tree):
        value = select_clause_var_or_expression.children[0]
        if value.data == "var":
            self._result += f"{get_var(value)}"
        elif value.data == "select_clause_expression":
            expression = value.children[0]
            self._result += "("
            self._expression(expression)
            as_str = value.children[1].value
            var = get_var(value.children[2])
            self._result += f" {as_str} {var})\n"

        else:
            raise ValueError(f"Unexpected select_clause_var_or_expression value: {select_clause_var_or_expression.data}")

    def _select_clause(self, select_clause: Tree):
        for child in select_clause.children:
            if isinstance(child, Token):
                self._result += f"{child.value} "

        select_clause_var_or_expressions = list(filter(lambda x: isinstance(x, Tree) and x.data == "select_clause_var_or_expression", select_clause.children))
        for i, select_clause_var_or_expression in enumerate(select_clause_var_or_expressions):
            self._select_clause_var_or_expression(select_clause_var_or_expression)
            if i + 1 != len(select_clause_var_or_expressions):
                self._result += " "

    def _select_query(self, select_query: Tree):
        select_clause = select_query.children[0]
        self._select_clause(select_clause)
        dataset_clauses = list(filter(lambda x: x.data == "dataset_clause", select_query.children))
        for dataset_clause in dataset_clauses:
            self._dataset_clause(dataset_clause)

    def _values_clause(self, values_clause: Tree):
        if values_clause.children:
            values_str = values_clause.children[0]
            self._result += f"{values_str} "

            data_block = values_clause.children[1]
            self._data_block(data_block)

    def _data_block(self, data_block: Tree):
        inline_data = data_block.children[0]
        if inline_data.data == "inline_data_one_var":
            self._inline_data_one_var(inline_data)
        elif inline_data.data == "inline_data_full":
            self._inline_data_full(inline_data)
        else:
            raise ValueError(f"Unexpected value for data_block: {inline_data.data}")

    def _data_block_value(self, data_block_values_group: list[Tree], newline: bool = False):
        self._result += f"{self._indent * '\t'}"

        if len(data_block_values_group) > 1:
            self._result += "("

        for i, data_block_value in enumerate(data_block_values_group):
            self._result += get_data_block_value(data_block_value)
            if i + 1 != len(data_block_values_group):
                self._result += " "

        if len(data_block_values_group) > 1:
            self._result += ")"

        if newline:
            self._result += "\n"

    def _inline_data_one_var(self, inline_data_one_var: Tree):
        var = inline_data_one_var.children[0]
        data_block_values = list(filter(lambda x: x.data == "data_block_value", inline_data_one_var.children))

        self._result += f"{get_var(var)} {{\n"
        self._indent += 1
        for i, data_block_value in enumerate(data_block_values):
            self._data_block_value([data_block_value], newline=True if i + 1 != len(data_block_values) else False)
        self._result += "\n}"
        self._indent -= 1

    def _inline_data_full(self, inline_data_full: Tree):
        vars_ = list(filter(lambda x: x.data == "var", inline_data_full.children))
        data_block_values = list(filter(lambda x: x.data == "data_block_value", inline_data_full.children))
        data_block_values_groups = list(zip(*(iter(data_block_values),) * len(vars_)))

        self._result += f"({get_vars(vars_)}) {{\n"
        self._indent += 1
        for i, data_block_values_group in enumerate(data_block_values_groups):
            self._data_block_value(data_block_values_group, newline=True if i + 1 != len(data_block_values) else False)
        self._result += "\n}"
        self._indent -= 1


class _SparqlSerializer(Visitor_Recursive):
    def __init__(self):
        self._result = ""
        super().__init__()
        self._indent = 0

    @property
    def result(self):
        return self._result

    def base(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def prefix(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def pname_ns(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def iriref(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def prefixed_name(self, node: Tree):
        self._result += f"{node.children[0].value} "

    def values_clause(self, node: Tree):
        self._result += f"{node.children[0].value} "

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
