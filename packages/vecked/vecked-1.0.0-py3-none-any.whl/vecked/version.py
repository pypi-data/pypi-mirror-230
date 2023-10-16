from importlib.resources import files


def get_version() -> str:
    """
    Gets the package version.
    """

    file = files("vecked") / "VERSION"
    return file.read_text().strip()
