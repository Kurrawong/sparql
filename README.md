# SPARQL Parser and Serializer

## Issues

### property path alternative symbol getting matched with prefixed_name

File: [tests/data/sparql_spec_examples/9.2_property_path_alternatives.rq](tests/data/sparql_spec_examples/9.2_property_path_alternatives.rq)

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

select *
where { :book1 dc:title|rdfs:label ?displayString }
```

Currently, the grammar is matching `dc:title|rdfs:label` as **one** `prefixed_name` under one `path_sequence` branch. Coincidentally, this roundtrips the tests correctly and passes, but it's not entirely correct.

Instead of being captured as one `prefixed_name`, it should be 2 prefixed names under 2 separate `path_sequence` branches.

Removing the last regex `/[\u10000-\uEFFFF]/` in `PN_CHARS_BASE` allows the `prefixed_name` to be matched correctly as 2 prefixed names but this then breaks other tests. The suspicion is that somehow `/[\u10000-\uEFFFF]/` is matching the `|` character. 

Will need to study the grammar further to ensure there are no other errors and figure out what is going on. It could also be possible that the rule is being interpreted differently under Lark/Python and by chance, the tests are passing.

**Update**: Removing the last regex rule no longer breaks the tests. Keeping it commented out for now.

**Update**: Keeping it commented out fails other tests from the SPARQL 1.1 Syntax Query test suite. Uncommenting for now.
