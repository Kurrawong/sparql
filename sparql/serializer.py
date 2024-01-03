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
            if i != 0 and i + 1 != len(value_logicals):
                self._result += " && "
            self._value_logical(value_logical)

    def _conditional_or_expression(self, conditional_or_expression: Tree):
        conditional_and_expressions = list(filter(lambda x: x.data == "conditional_and_expression", conditional_or_expression.children))
        for i,  conditional_and_expression in enumerate(conditional_and_expressions):
            if i != 0 and i + 1 != len(conditional_and_expressions):
                self._result += " || "
            self._conditional_and_expression(conditional_and_expression)

    def _expression(self, expression: Tree):
        conditional_or_expression = expression.children[0]
        self._conditional_or_expression(conditional_or_expression)

    def _select_clause_expression_as_var(self, expression_as_var: Tree):
        expression = expression_as_var.children[0]
        self._result += "("
        self._expression(expression)
        as_str = expression_as_var.children[1].value
        var = get_var(expression_as_var.children[2])
        self._result += f" {as_str} {var})\n"

    def _select_clause_var_or_expression(self, select_clause_var_or_expression: Tree):
        value = select_clause_var_or_expression.children[0]
        if value.data == "var":
            self._result += f"{get_var(value)} "
        elif value.data == "select_clause_expression_as_var":
            self._select_clause_expression_as_var(value)
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

    def _var_or_term(self, var_or_term: Tree):
        value = var_or_term.children[0]
        if value.data == "var":
            self._result += f"{'\t' * self._indent}{get_var(value)} "
        elif value.data == "graph_term":
            raise NotImplementedError
        else:
            raise ValueError(f"Unexpected var_or_term value type: {value.data}")

    def _verb_simple(self, verb_simple: Tree):
        var = verb_simple.children[0]
        self._result += f"{get_var(var)} "

    def _triples_node_path(self, triples_node_path: Tree):
        value = triples_node_path.children[0]
        if value.data == "collection_path":
            raise NotImplementedError
        elif value.data == "blank_node_property_list_path":
            raise NotImplementedError
        else:
            raise ValueError(f"Unexpected triples_node_path value type: {value.data}")

    def _graph_node_path(self, graph_node_path: Tree):
        value = graph_node_path.children[0]
        if value.data == "var_or_term":
            self._var_or_term(value)
        elif value.data == "triples_node_path":
            self._triples_node_path(value)
        else:
            raise ValueError(f"Unexpected graph_node_path value type: {value.data}")

    def _object_path(self, object_path: Tree):
        graph_node_path = object_path.children[0]
        self._graph_node_path(graph_node_path)

    def _object_list_path(self, object_list_path: Tree):
        object_path = object_list_path.children[0]
        self._object_path(object_path)

        object_list_path_others = list(filter(lambda x: x.data == "object_list_path_other", object_list_path.children))
        for object_path_other in object_list_path_others:
            self._result += ", "
            self._object_path(object_path_other)

    def _path_mod(self, path_mod: Tree):
        symbol = path_mod.children[0].value
        self._result += symbol

    def _path_one_in_property_set(self, path_one_in_property_set: Tree):
        if len(path_one_in_property_set.children) == 2:
            self._result += "^"
            value = path_one_in_property_set.children[1]
        else:
            value = path_one_in_property_set.children[0]

        if isinstance(value, Tree):
            self._result += get_iri(value)
        else:
            self._result += "a"

    def _path_negated_property_set(self, path_negated_property_set: Tree):
        path_one_in_property_sets = list(filter(lambda x: x.data == "path_one_in_property_set", path_negated_property_set.children))
        if len(path_one_in_property_sets) == 1:
            self._path_one_in_property_set(path_one_in_property_sets[0])
        else:
            self._result += "("
            for i, path_one_in_property in enumerate(path_one_in_property_sets):
                if i + 1 != len(path_one_in_property_sets):
                    self._result += "|"
                self._path_one_in_property_set(path_one_in_property)

            self._result += ")"

    def _path_primary(self, path_primary: Tree):
        value = path_primary.children[0]
        if isinstance(value, Token):
            if value.type == "A":
                self._result += "a"
        elif isinstance(value, Tree):
            if value.data == "iri":
                self._result += get_iri(value)
            elif value.data == "path_negated_property_set":
                self._path_negated_property_set(value)
            elif value.data == "path":
                self._result += "("
                self._path(value)
                self._result += ")"
        else:
            raise ValueError(f"Unexpected path_primary value type: {type(value)}")

    def _path_elt(self, path_elt: Tree):
        path_primary = path_elt.children[0]
        self._path_primary(path_primary)

        if len(path_elt.children) == 2:
            path_mod = path_elt.children[1]
            self._path_mod(path_mod)

        if len(path_elt.children) > 2:
            raise ValueError(f"Unexpected path_elt children size: {len(path_elt.children)}")

    def _path_elt_or_inverse(self, path_elt_or_inverse: Tree):
        if len(path_elt_or_inverse.children) == 1:
            path_elt = path_elt_or_inverse.children[0]
            self._path_elt(path_elt)
        elif len(path_elt_or_inverse.children) == 2:
            self._result += "^"
            path_elt = path_elt_or_inverse.children[1]
            self._path_elt(path_elt)
        else:
            raise ValueError(f"Unexpected path_elt_or_inverse children size: {len(path_elt_or_inverse.children)}")

    def _path_sequence(self, path_sequence: Tree):
        path_elt_or_inverses = list(filter(lambda x: x.data == "path_elt_or_inverse", path_sequence.children))
        for i, path_elt_or_inverse_elt in enumerate(path_elt_or_inverses):
            if i != 0 and i + 1 != len(path_elt_or_inverses):
                self._result += "/"
            self._path_elt_or_inverse(path_elt_or_inverse_elt)

    def _path_alternative(self, path_alternative: Tree):
        path_sequences = list(filter(lambda x: x.data == "path_sequence", path_alternative.children))
        for i, path_sequence in enumerate(path_sequences):
            if i != 0 and i + 1 != len(path_sequences):
                self._result += "|"
            self._path_sequence(path_sequence)

    def _path(self, path: Tree):
        path_alternative = path.children[0]
        self._path_alternative(path_alternative)

    def _verb_path(self, verb_path: Tree):
        path = verb_path.children[0]
        self._path(path)

    def _collection(self, collection: Tree):
        graph_nodes = list(filter(lambda x: x.data == "graph_node", collection.children))
        self._result += "("

        for graph_node in graph_nodes:
            self._graph_node(graph_node)

        self._result += ")"

    def _property_list_not_empty(self, property_list_not_empty: Tree):
        raise NotImplementedError

    def _blank_node_property_list(self, blank_node_property_list: Tree):
        self._result += "["
        value = blank_node_property_list.children[0]
        self._property_list_not_empty(value)
        self._result += "]"

    def _triples_node(self, triples_node: Tree):
        value = triples_node.children[0]
        if value.data == "collection":
            self._collection(value)
        elif value.data == "blank_node_property_list":
            self._blank_node_property_list(value)
        else:
            raise ValueError(f"Unexpected triples_node value type: {value.data}")

    def _graph_node(self, graph_node: Tree):
        value = graph_node.children[0]
        if value.data == "var_or_term":
            self._var_or_term(value)
        elif value.data == "triples_node":
            self._triples_node(value)
        else:
            raise ValueError(f"Unexpected graph_node value type: {value.data}")

    def _object(self, obj: Tree):
        graph_node = obj.children[0]
        self._graph_node(graph_node)

    def _object_list(self, object_list):
        objects = list(filter(lambda x: x.data == "object", object_list.children))
        for i, obj in enumerate(objects):
            if i != 0 and i + 1 != len(objects):
                self._result += ", "
            self._object(obj)

    def _property_list_path_not_empty_rest(self, property_list_path_not_empty_rest: Tree):
        first_value = property_list_path_not_empty_rest.children[0]
        if first_value.data == "verb_path":
            self._verb_path(first_value)
        elif first_value.data == "verb_simple":
            self._verb_simple(first_value)
        else:
            raise ValueError(f"Unexpected property_list_path_not_empty_rest value type: {first_value.data}")

        object_list = property_list_path_not_empty_rest.children[1]
        self._object_list(object_list)

    def _property_list_path_not_empty_other(self, property_list_path_not_empty_other: Tree):
        self._result += ";\n"

        if property_list_path_not_empty_other.children:
            property_list_path_not_empty_rest = property_list_path_not_empty_other.children[0]
            self._property_list_path_not_empty_rest(property_list_path_not_empty_rest)

    def _property_list_path_not_empty(self, property_list_path_not_empty: Tree):
        first_value = property_list_path_not_empty.children[0]
        if first_value.data == "verb_path":
            self._verb_path(first_value)
        elif first_value.data == "verb_simple":
            self._verb_simple(first_value)
        else:
            raise ValueError(f"Unexpected first_value value type: {first_value.data}")

        object_list_path = property_list_path_not_empty.children[1]
        self._object_list_path(object_list_path)

        property_list_path_not_empty_others = list(filter(lambda x: x.data == "property_list_path_not_empty_other", property_list_path_not_empty.children))
        for property_list_not_empty_other in property_list_path_not_empty_others:
            self._property_list_path_not_empty_other(property_list_not_empty_other)

    def _property_list_path(self, property_list_path: Tree):
        raise NotImplementedError

    def _triples_same_subject_path(self, triples_same_subject_path: Tree):
        first_value = triples_same_subject_path.children[0]
        second_value = triples_same_subject_path.children[1]
        if first_value.data == "var_or_term":
            self._var_or_term(first_value)
            self._property_list_path_not_empty(second_value)
        elif first_value.data == "triples_node_path":
            self._triples_node_path(first_value)
            self._property_list_path(second_value)
        else:
            raise ValueError(f"Unexpected first value value type: {first_value.data}")

    def _triples_block(self, triples_block: Tree):
        triples_same_subject_path = triples_block.children[0]
        self._triples_same_subject_path(triples_same_subject_path)

        if len(triples_block.children) > 1:
            self._result += " .\n"
            second_triples_block = triples_block.children[1]
            self._triples_block(second_triples_block)

    def _optional_graph_pattern(self, optional_graph_pattern: Tree):
        optional_str = optional_graph_pattern.children[0].value
        self._result += f"{optional_str} "

        group_graph_pattern = optional_graph_pattern.children[1]
        self._group_graph_pattern(group_graph_pattern)

    def _inline_data(self, inline_data: Tree):
        values_str = inline_data.children[0]
        self._result += f"{values_str} "
        data_block = inline_data.children[1]
        self._data_block(data_block)
        self._result += "\n"

    def _graph_pattern_not_triples(self, graph_pattern_not_triples: Tree):
        value = graph_pattern_not_triples.children[0]
        if value.data == "group_or_union_graph_pattern":
            raise NotImplementedError
        elif value.data == "optional_graph_pattern":
            self._optional_graph_pattern(value)
        elif value.data == "minus_graph_pattern":
            raise NotImplementedError
        elif value.data == "graph_graph_pattern":
            raise NotImplementedError
        elif value.data == "service_graph_pattern":
            raise NotImplementedError
        elif value.data == "filter":
            raise NotImplementedError
        elif value.data == "bind":
            raise NotImplementedError
        elif value.data == "inline_data":
            self._inline_data(value)
        else:
            raise ValueError(f"Unexpected graph_pattern_not_triples value type: {value.data}")

    def _group_graph_pattern_sub_other(self, group_graph_pattern_sub_other: Tree):
        self._result += "\n"
        for child in group_graph_pattern_sub_other.children:
            if isinstance(child, Tree):
                if child.data == "graph_pattern_not_triples":
                    self._graph_pattern_not_triples(child)
                elif child.data == "triples_block":
                    self._triples_block(child)
            elif isinstance(child, Token):
                if child.type == "DOT":
                    self._result += " .\n"
            else:
                raise TypeError(f"Unexpected child type: {type(child)}")

    def _group_graph_pattern_sub(self, group_graph_pattern_sub: Tree):
        for child in group_graph_pattern_sub.children:
            if child.data == "triples_block":
                self._triples_block(child)
            elif child.data == "group_graph_pattern_sub_other":
                self._group_graph_pattern_sub_other(child)
            else:
                raise ValueError(f"Unexpected group_graph_pattern_sub_other value type: {child.data}")

    def _group_graph_pattern(self, group_graph_pattern: Tree):
        self._result += "{\n"

        value = group_graph_pattern.children[0]
        if value.data == "sub_select":
            raise NotImplementedError
        elif value.data == "group_graph_pattern_sub":
            self._group_graph_pattern_sub(value)
        else:
            raise ValueError(f"Unexpected group_graph_pattern value type: {value.data}")

        self._result += "\n}\n"

    def _where_clause(self, where_clause: Tree):
        if len(where_clause.children) == 2:
            where_str = where_clause.children[0].value
            group_graph_pattern = where_clause.children[1]
            self._result += f"{where_str} "
        elif len(where_clause.children) == 1:
            group_graph_pattern = where_clause.children[0]
        else:
            raise ValueError(f"Unexpected where_clause children count: {len(where_clause.children)}")

        self._indent += 1
        self._group_graph_pattern(group_graph_pattern)
        self._indent -= 1

    def _select_query(self, select_query: Tree):
        select_clause = select_query.children[0]
        self._select_clause(select_clause)
        dataset_clauses = list(filter(lambda x: x.data == "dataset_clause", select_query.children))
        for dataset_clause in dataset_clauses:
            self._dataset_clause(dataset_clause)

        where_clause = list(filter(lambda x: x.data == "where_clause", select_query.children))[0]
        self._where_clause(where_clause)

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
