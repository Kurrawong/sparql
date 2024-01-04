grammar = r"""query_unit: query

query: prologue ( select_query | construct_query ) values_clause

prologue: ( base_decl | prefix_decl )*

base_decl: base iriref

base: BASE

prefix_decl: prefix pname_ns iriref

pname_ns: PNAME_NS

prefix: PREFIX

construct_query: /CONSTRUCT/i ( construct_construct_template | construct_triples_template )

construct_construct_template: construct_template dataset_clause* where_clause solution_modifier

construct_triples_template: dataset_clause* /WHERE/i "{" triples_template? "}" solution_modifier

construct_template: "{" construct_triples? "}"

construct_triples: triples_same_subject ( "." construct_triples? )?

triples_same_subject: var_or_term property_list_not_empty | triples_node property_list

property_list: property_list_not_empty?

triples_template: triples_same_subject ( "." triples_template? )?

select_query: select_clause dataset_clause* where_clause solution_modifier

dataset_clause: /FROM/i ( default_graph_clause | named_graph_clause )

default_graph_clause: source_selector

named_graph_clause: /NAMED/i source_selector

source_selector: iri

where_clause: /WHERE/i? group_graph_pattern

solution_modifier: group_clause? having_clause? order_clause? limit_offset_clauses?

group_clause: /GROUP/i? /BY/i group_condition+

group_condition: built_in_call | function_call | group_condition_expression_as_var | var

group_condition_expression_as_var: "(" expression ( /AS/i var )? ")"

having_clause: /HAVING/i having_condition+

having_condition: constraint

order_clause: /ORDER/i /BY/i order_condition

order_condition: ( ( /ASC/i | /DESC/i ) bracketted_expression )
                 | ( constraint | var )

limit_offset_clauses: limit_clause offset_clause? | offset_clause limit_clause?

limit_clause: /LIMIT/i INTEGER

offset_clause: /OFFSET/i INTEGER

sub_select: select_clause where_clause solution_modifier values_clause

select_clause: /SELECT/i ( /DISTINCT/i | /REDUCED/i )? ( select_clause_var_or_expression+ | ASTERIX )

select_clause_var_or_expression: var | select_clause_expression_as_var

select_clause_expression_as_var: "(" expression /AS/i var ")"

expression: conditional_or_expression

conditional_or_expression: conditional_and_expression ( "||" conditional_and_expression )*

conditional_and_expression: value_logical ( "&&" value_logical )*

value_logical: relational_expression

relational_expression: numeric_expression ( "=" numeric_expression | "!=" numeric_expression | "<" numeric_expression | ">" numeric_expression "<=" numeric_expression | ">=" numeric_expression | /IN/i expression_list | /NOT/i /IN/i expression_list )?

numeric_expression: additive_expression

additive_expression: multiplicative_expression ( "+" multiplicative_expression | "-" multiplicative_expression | ( numeric_literal_positive | numeric_literal_negative ) ( ( "*" unary_expression ) | ( "/" unary_expression ) )* )*

multiplicative_expression: unary_expression ( "*" unary_expression | "/" unary_expression )*

unary_expression: "!" primary_expression
                  | "+" primary_expression 
                  | "-" primary_expression
                  | primary_expression

primary_expression: bracketted_expression | built_in_call | iri_or_function | rdf_literal | numeric_literal | boolean_literal | var

bracketted_expression: "(" expression ")"

built_in_call: aggregate
               | /STR/i "(" expression ")"
               | /LANG/i "(" expression ")"
               | /LANGMATCHES/i "(" expression ")"
               | /DATATYPE/i "(" expression ")"
               | /BOUND/i "(" expression ")"
               | /IRI/i "(" expression ")"
               | /URI/i "(" expression ")"
               | /BNODE/i ( "(" expression ")" | NIL )
               | /RAND/i NIL
               | /ABS/i "(" expression ")"
               | /CEIL/i "(" expression ")"
               | /FLOOR/i "(" expression ")"
               | /ROUND/i "(" expression ")"
               | /CONCAT/i expression_list
               | substring_expression
               | /STRLEN/i "(" expression ")"
               | str_replace_expression
               | /UCASE/i "(" expression ")"
               | /LCASE/i "(" expression ")"
               | /ENCODE_FOR_URI/i "(" expression ")"
               | /CONTAINS/i "(" expression "," expression ")"
               | /STRSTARTS/i "(" expression "," expression ")"
               | /STRENDS/i "(" expression "," expression ")"
               | /STRBEFORE/i "(" expression "," expression ")"
               | /STRAFTER/i "(" expression "," expression ")"
               | /YEAR/i "(" expression ")"
               | /MONTH/i "(" expression ")"
               | /DAY/i "(" expression ")"
               | /HOURS/i "(" expression ")"
               | /MINUTES/i "(" expression ")"
               | /SECONDS/i "(" expression ")"
               | /TIMEZONE/i "(" expression ")"
               | /TZ/i "(" expression ")"
               | /NOW/i NIL
               | /UUID/i NIL
               | /STRUUID/ NIL
               | /MD5/i "(" expression ")"
               | /SHA1/i "(" expression ")"
               | /SHA256/i "(" expression ")"
               | /SHA384/i "(" expression ")"
               | /SHA512/i "(" expression ")"
               | /COALESCE/i expression_list
               | /IF/i "(" expression "," expression "," expression ")"
               | /STRLANG/i "(" expression "," expression ")"
               | /STRDTZ/i "(" expression "," expression ")"
               | /sameTerm/i "(" expression "," expression ")"
               | /isIRI/i "(" expression ")"
               | /isURI/i "(" expression ")"
               | /isBLANK/i "(" expression ")"
               | /isLITERAL/i "(" expression ")"
               | /isNUMERIC/i "(" expression ")"
               | regex_expression
               | exists_func
               | not_exists_func

substring_expression: /SUBSTR/i "(" expression "," expression ( "," expression )? ")"

str_replace_expression: /REPLACE/i "(" expression "," expression "," expression ( "," expression )? ")"

regex_expression: /REGEX/i "(" expression "," expression ( "," expression )? ")"

exists_func: /EXISTS/i group_graph_pattern

not_exists_func: /NOT/i /EXISTS/i group_graph_pattern

group_graph_pattern: "{" ( sub_select | group_graph_pattern_sub ) "}"

group_graph_pattern_sub: triples_block? group_graph_pattern_sub_other*

group_graph_pattern_sub_other: graph_pattern_not_triples DOT? triples_block?

# We don't want to parse the dot token, leave as an inline char instead of a terminal.
triples_block: triples_same_subject_path ( "." triples_block? )?

graph_pattern_not_triples: group_or_union_graph_pattern | optional_graph_pattern | minus_graph_pattern | graph_graph_pattern | service_graph_pattern | filter | bind | inline_data

group_or_union_graph_pattern: group_graph_pattern ( /UNION/i group_graph_pattern )*

optional_graph_pattern: /OPTIONAL/i group_graph_pattern

minus_graph_pattern: /MINUS/i group_graph_pattern

graph_graph_pattern: /GRAPH/i var_or_iri group_graph_pattern

service_graph_pattern: /SERVICE/i /SILENT/i? var_or_iri group_graph_pattern

filter: /FILTER/i constraint

constraint: bracketted_expression | built_in_call | function_call

function_call: iri arg_list

bind: /BIND/i "(" expression /AS/i var ")"

inline_data: /VALUES/i data_block

object_list: object ( "," object )*

object: graph_node

triples_same_subject_path: var_or_term property_list_path_not_empty | triples_node_path property_list_path

property_list_path: property_list_path_not_empty?

property_list_path_not_empty: ( verb_path | verb_simple ) object_list_path property_list_path_not_empty_other*

property_list_path_not_empty_other: ";" property_list_path_not_empty_rest?

property_list_path_not_empty_rest: ( verb_path | verb_simple ) object_list

verb_path: path

verb_simple: var

object_list_path: object_path object_list_path_other*

object_list_path_other: "," object_path

object_path: graph_node_path

collection: "(" graph_node+ ")"

blank_node_property_list: "[" property_list_not_empty "]"

property_list_not_empty: verb_object_list ( ";" ( verb_object_list )? )*

verb_object_list: verb object_list

verb: var_or_iri | A

graph_node: var_or_term | triples_node

triples_node: collection | blank_node_property_list

path: path_alternative

path_alternative: path_sequence ( "|" path_sequence )*

path_sequence: path_elt_or_inverse ( "/" path_elt_or_inverse )*

path_elt_or_inverse: path_elt | CARET path_elt

path_elt: path_primary path_mod?

path_mod: "?" | "*" | "+"

path_primary: iri | A | "!" path_negated_property_set | "(" path ")"

path_negated_property_set: path_one_in_property_set | "(" ( path_one_in_property_set ( "|" path_one_in_property_set )* )? ")"

path_one_in_property_set: iri | A | CARET ( iri | A )

expression_list: NIL | "(" expression ( "," expression )* ")"

values_clause: ( /VALUES/i data_block )?

data_block: inline_data_one_var | inline_data_full

inline_data_one_var: var left_curly_brace data_block_value* right_curly_brace

inline_data_full: ( NIL | left_parenthesis var* right_parenthesis ) left_curly_brace ( left_parenthesis data_block_value* right_parenthesis | NIL )* right_curly_brace

data_block_value: iri | rdf_literal | numeric_literal | boolean_literal | undef

left_curly_brace: LEFT_CURLY_BRACE

right_curly_brace: RIGHT_CURLY_BRACE

left_parenthesis: LEFT_PARENTHESIS

right_parenthesis: RIGHT_PARENTHESIS

string: STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 | ESCAPED_STRING

iri: iriref | prefixed_name

iriref: IRIREF

rdf_literal: string ( langtag | datatype )?

datatype: ("^^" iri )

langtag: LANGTAG

boolean_literal: true | false

undef: UNDEF

true: TRUE

false: FALSE

numeric_literal: numeric_literal_unsigned | numeric_literal_positive | numeric_literal_negative

numeric_literal_unsigned: INTEGER | DECIMAL | DOUBLE

numeric_literal_positive: INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE

numeric_literal_negative: INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE

graph_node_path: var_or_term | triples_node_path

var_or_term: var | graph_term

var_or_iri: var | iri

var: VAR1 | VAR2

graph_term: iri | rdf_literal | numeric_literal | boolean_literal | blank_node | NIL

prefixed_name: PNAME_LN | PNAME_NS

triples_node_path: collection_path | blank_node_property_list_path

collection_path: "(" graph_node_path+ ")"

blank_node_property_list_path: "[" property_list_path_not_empty "]"

aggregate: /COUNT/i LEFT_PARENTHESIS DISTINCT? ( ASTERIX | expression ) RIGHT_PARENTHESIS
           | /SUM/i "(" /DISTINCT/i? expression ")"
           | /MIN/i "(" /DISTINCT/i? expression ")"
           | /MAX/i "(" /DISTINCT/i expression ")"
           | /AVG/i "(" /DISTINCT/i expression ")"
           | /SAMPLE/i "(" /DISTINCT/i expression ")"
           | /GROUP_CONCAT/i "(" /DISTINCT/i? expression ( ";" /SEPARATOR/i "=" string )? ")"

iri_or_function: iri arg_list?

arg_list: NIL | "(" /DISTINCT/i? expression ( "," expression )* ")"

blank_node: BLANK_NODE_LABEL | ANON

#
# Productions for terminals:
#

CARET: "^"

DOT: "."

A: "a"

ASTERIX: "*"

DISTINCT: /DISTINCT/i

UNDEF: "UNDEF"

BASE: /BASE/i

BLANK_NODE_LABEL: "_:" ( PN_CHARS_U | /[0-9]/ ) ((PN_CHARS|".")* PN_CHARS)?

PREFIX: /PREFIX/i

TRUE: "true"

FALSE: "false"

LEFT_PARENTHESIS: "("

RIGHT_PARENTHESIS: ")"

LEFT_CURLY_BRACE: "{"

RIGHT_CURLY_BRACE: "}"

IRIREF: "<" (/[^<>"{}|^`\\\x00-\x20]/)* ">"

LANGTAG: "@" /[a-zA-Z]/+ ("-" /[a-zA-Z0-9]/+)*

INTEGER: /[0-9]/+

INTEGER_POSITIVE: "+" INTEGER

DECIMAL_POSITIVE: "+" DECIMAL

DOUBLE_POSITIVE: "+" DOUBLE

INTEGER_NEGATIVE: "-" INTEGER

DECIMAL_NEGATIVE: "-" DECIMAL

DOUBLE_NEGATIVE: "-" DOUBLE

DECIMAL: /[0-9]/* "." /[0-9]/+

DOUBLE: /[0-9]/+ "." /[0-9]/* EXPONENT | "." (/[0-9]/)+ EXPONENT | (/[0-9]/+) EXPONENT

EXPONENT: /[eE]/ /[+-]/? /[0-9]/+

VAR1: "?" VARNAME

VAR2: "$" VARNAME

VARNAME: ( PN_CHARS_U | /[0-9]/ ) ( PN_CHARS_U | /[0-9]/ | "\u00B7" | /[\u0300-\u036F]/ | /[\u203F-\u2040]/ )*

STRING_LITERAL1: "'" ( (/[^\x27\\x5C\u000A\u000D]/) | ECHAR )* "'"

STRING_LITERAL2: "\"" ( (/[^\x22\\x5C\u000A\u000D]/) | ECHAR )* "\""

STRING_LITERAL_LONG1: "'''" ( ( "'" | "'" )? ( /[^'\\]/ | ECHAR ) )* "'''"

STRING_LITERAL_LONG2: "\"\"\"" ( ( "\"" | "\"" )? ( /[^"\\]/ | ECHAR ) )* "\"\"\""

ECHAR: "\\" /[tbnrf\"']/

PNAME_LN: PNAME_NS PN_LOCAL

PNAME_NS: PN_PREFIX? ":"

PN_CHARS_U: PN_CHARS_BASE | "_"

PN_CHARS_BASE: /[A-Z]/ | /[a-z]/ 
                | /[\u00C0-\u00D6]/ 
                | /[\u00D8-\u00F6]/ 
                | /[\u00F8-\u02FF]/ 
                | /[\u0370-\u037D]/ 
                | /[\u037F-\u1FFF]/ 
                | /[\u200C-\u200D]/ 
                | /[\u2070-\u218F]/ 
                | /[\u2C00-\u2FEF]/ 
                | /[\u3001-\uD7FF]/
                | /[\uF900-\uFDCF]/
                | /[\uFDF0-\uFFFD]/
                | /[\u10000-\uEFFFF]/

PN_CHARS: PN_CHARS_U | "-" | /[0-9]/ | "\u00B7" | /[\u0300-\u036F]/ | /[\u203F-\u2040]/

PN_PREFIX: PN_CHARS_BASE ((PN_CHARS|".")* PN_CHARS)?

PN_LOCAL: (PN_CHARS_U | ":" | /[0-9]/ | PLX ) ((PN_CHARS | "." | ":" | PLX)* (PN_CHARS | ":" | PLX) )?

PLX: PERCENT | PN_LOCAL_ESC

NIL: "(" WS* ")"

WS: "\u0020" | "\u0009" | "\u000D" | "\u000A"

ANON: "[" WS* "]"

PERCENT: "%" HEX HEX

HEX: /[0-9]/ | /[A-F]/ | /[a-f]/

PN_LOCAL_ESC: "\\" ( "_" | "~" | "." | "-" | "!" | "$" | "&" | "'" | "(" | ")" | "*" | "+" | "," | ";" | "=" | "/" | "?" | "#" | "@" | "%" )

COMMENT: "#" /[^\n]/*

%ignore /[ \t\n]/+ | COMMENT

%import common.ESCAPED_STRING
"""
