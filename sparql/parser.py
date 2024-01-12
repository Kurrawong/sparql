from pathlib import Path

from lark import Lark

grammar_path = current_dir = Path(__file__).parent / "grammar.lark"

with open(grammar_path, "r", encoding="utf-8") as file:
    grammar = file.read()
    sparql_parser = Lark(grammar, start="query_unit")
    sparql_update_parser = Lark(grammar, start="update_unit")
