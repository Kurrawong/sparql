grammar = r"""query_unit: query

query: prologue values_clause

prologue: ( base_decl | prefix_decl )*

base_decl: base iriref

base: BASE

prefix_decl: prefix pname_ns iriref

pname_ns: PNAME_NS

prefix: PREFIX

# select_query: select_clause dataset_clause* where_clause solution_modifier
# 
# select_clause: /SELECT/i ( /DISTINCT/i | /REDUCED/i )? ( ( var | ( "(" expression /AS/i var ")" ) )+ | "*" )
# 
# expression: conditional_or_expression
# 
# conditional_or_expression: conditional_and_expression ( "||" conditional_and_expression )*
# 
# conditional_and_expression: value_logical ( "&&" value_logical )*
# 
# value_logical: relational_expression
# 
# relational_expression: numeric_expression ( "=" numeric_expression | "!=" numeric_expression | "<" numeric_expression | ">" numeric_expression "<=" numeric_expression | ">=" numeric_expression | /IN/i expression_list | /NOT/i /IN/i expression_list )?
# 
# numeric_expression: additive_expression
# 
# additive_expression: multiplicative_expression ( "+" multiplicative_expression | "-" multiplicative_expression | ( numeric_literal_positive | numeric_literal_negative ) ( ( "*" unary_expression ) | ( "/" unary_expression ) )* )*
# 
# expression_list: NIL | "(" expression ( "," expression )* ")"

values_clause: ( /VALUES/i data_block )?

data_block: inline_data_one_var | inline_data_full

inline_data_one_var: var left_curly_brace data_block_value* right_curly_brace

inline_data_full: ( NIL | left_parenthesis var* right_parenthesis ) left_curly_brace ( left_parenthesis data_block_value* right_parenthesis | NIL )* right_curly_brace

data_block_value: iri | rdf_literal | numeric_literal | boolean_literal | undef

left_curly_brace: LEFT_CURLY_BRACE

right_curly_brace: RIGHT_CURLY_BRACE

left_parenthesis: LEFT_PARENTHESIS

right_parenthesis: RIGHT_PARENTHESIS

string: STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2

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

var: VAR1 | VAR2

prefixed_name: PNAME_LN | PNAME_NS

#
# Productions for terminals:
#

UNDEF: "UNDEF"

BASE: /BASE/i

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

PERCENT: "%" HEX HEX

HEX: /[0-9]/ | /[A-F]/ | /[a-f]/

PN_LOCAL_ESC: "\\" ( "_" | "~" | "." | "-" | "!" | "$" | "&" | "'" | "(" | ")" | "*" | "+" | "," | ";" | "=" | "/" | "?" | "#" | "@" | "%" )

%ignore /[ \t\n]/+ | COMMENT

COMMENT: "#" /[^\n]/*
"""
