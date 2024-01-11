from lark import Lark

from sparql.grammar import grammar

sparql_parser = Lark(grammar, start="query_unit")
sparql_update_parser = Lark(grammar, start="update_unit")
