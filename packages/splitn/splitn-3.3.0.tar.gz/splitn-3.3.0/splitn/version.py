from os import path

def get_version_from_pyproject_file(
    pyproject_path: str
) -> str | None:
    if not path.exists(pyproject_path):
        return None
    with open(pyproject_path) as pyproject_file:
        for line in pyproject_file:
            if line.startswith("version"):
                return line.split("=")[1].replace("\"", "")

__version__ = get_version_from_pyproject_file("pyproject.toml")