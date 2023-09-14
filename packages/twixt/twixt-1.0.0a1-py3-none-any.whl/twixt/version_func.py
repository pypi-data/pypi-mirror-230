from importlib.resources import files


def version() -> str:
    """
    Gets the package version.
    """

    file = files("twixt") / "VERSION"
    return file.read_text().strip()
