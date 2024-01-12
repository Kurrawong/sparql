import re
from typing import Literal

from sparql.parser import sparql_parser, sparql_update_parser
from sparql.serializer import SparqlSerializer

ParserType = Literal["sparql", "sparql_update", "guess"]


def _contains(pattern: str, text: str) -> bool:
    return True if re.search(pattern, text, re.IGNORECASE) is not None else False


def format_string(query: str, parser_type: ParserType = "guess") -> str:
    """Parse the input string and return a formatted version of it.

    :param query: Input query string.
    :param parser_type: When the value is "guess", it naively infers the parser type based on regex-based keyword search.
    :return: Formatted query.
    """
    if parser_type == "guess":
        if (
            _contains("load", query)
            or _contains("clear", query)
            or _contains("drop", query)
            or _contains("create", query)
            or _contains("add", query)
            or _contains("move", query)
            or _contains("copy", query)
            or _contains("insert data", query)
            or _contains("insert", query)
            or _contains("delete data", query)
            or _contains("delete", query)
            or _contains("delete where", query)
            or _contains("using", query)
        ):
            _parser = sparql_update_parser
        else:
            _parser = sparql_parser
    elif parser_type == "sparql":
        _parser = sparql_parser
    elif parser_type == "sparql_update":
        _parser = sparql_update_parser
    else:
        raise ValueError(
            f"Unexpected parser type: {parser_type}. Must be one of {ParserType}"
        )

    tree = _parser.parse(query)

    sparql_serializer = SparqlSerializer()
    sparql_serializer.visit_topdown(tree)

    return sparql_serializer.result
