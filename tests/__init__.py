from pathlib import Path

TEST_DIR = Path(__file__).parent


def content_from_data_directory(data_directory: str) -> list[str]:
    source_path = TEST_DIR / "data" / data_directory
    file_paths = list(source_path.glob("*.rq"))

    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            yield file_path, content
