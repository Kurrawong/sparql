import shutil
from pathlib import Path

from rdflib import RDF, Graph, Namespace, URIRef
from rdflib.collection import Collection

MF = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#")
QT = Namespace("http://www.w3.org/2001/sw/DataAccess/tests/test-query#")
UT = Namespace("http://www.w3.org/2009/sparql/tests/test-update#")

skip_paths = [
    "sparql/sparql11/http-rdf-update/manifest.ttl",
    "sparql/sparql11/basic-update/manifest.ttl",
    "sparql/sparql11/update-silent/manifest.ttl",
    "sparql/sparql11/service-description/manifest.ttl",
    "sparql/sparql11/protocol/manifest.ttl",
    "sparql/sparql12/grouping/manifest.ttl",
]

target_path = Path("test")
path = Path("sparql")


def func(path: Path):
    for item in path.iterdir():
        local_manifest_path = "/".join(item.parts)

        if item.is_file() and (
            local_manifest_path == "sparql/sparql11/update-silent/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/add/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/copy/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/move/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/drop/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/clear/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/delete/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/delete-data/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/delete-insert/manifest.ttl"
            or local_manifest_path == "sparql/sparql11/delete-where/manifest.ttl"
        ):
            graph = Graph()
            graph.parse(item)

            manifest = graph.value(predicate=RDF.type, object=MF.Manifest)
            entries = graph.value(manifest, MF.entries)
            entries_collection = Collection(graph, entries)
            for entry in entries_collection:
                test_type = graph.value(entry, RDF.type)

                if (
                    test_type == MF.NegativeSyntaxTest11
                    or test_type == MF.NegativeSyntaxTest
                    or test_type == MF.NegativeUpdateSyntaxTest11
                ):
                    continue

                action = graph.value(entry, MF.action)
                query = graph.value(action, UT.request)
                if query is None:
                    query = action

                file = Path(str(query).replace("file:///", "/"))
                target_file = target_path / Path("/".join(item.parts[:-1])) / file.name
                shutil.copy(file, target_file)
        elif item.is_file() and local_manifest_path not in skip_paths:
            if item.name == "manifest.ttl":
                graph = Graph()
                try:
                    graph.parse(item)
                except Exception as err:
                    raise RuntimeError(f"Failed to parse file {item}") from err

                manifest = graph.value(predicate=RDF.type, object=MF.Manifest)
                entries = graph.value(manifest, MF.entries)
                entries_collection = Collection(graph, entries)
                for entry in entries_collection:
                    test_type = graph.value(entry, RDF.type)

                    if (
                        test_type == MF.NegativeSyntaxTest11
                        or test_type == MF.NegativeSyntaxTest
                        or test_type == MF.NegativeUpdateSyntaxTest11
                    ):
                        continue

                    action = graph.value(entry, MF.action)
                    query = graph.value(action, QT.query)

                    if query is None:
                        if (
                            action is not None
                            and isinstance(action, URIRef)
                            and (
                                str(action).endswith(".rq")
                                or str(action).endswith(".ru")
                            )
                        ):
                            query = action

                        if query is None:
                            raise RuntimeError(
                                f"Query file is None for manifest file {entry}"
                            )

                    file = Path(str(query).replace("file:///", "/"))
                    target_file = (
                        target_path / Path("/".join(item.parts[:-1])) / file.name
                    )
                    shutil.copy(file, target_file)

        elif item.is_dir():
            (target_path / item).mkdir(parents=True, exist_ok=True)
            func(item)


if __name__ == "__main__":
    func(path)
