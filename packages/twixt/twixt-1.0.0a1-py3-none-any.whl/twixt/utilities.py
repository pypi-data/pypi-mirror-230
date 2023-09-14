def lerp(
    start: float,
    end: float,
    percent: float,
) -> float:
    """
    Calculates the value `percent` between `start` and `end` inclusive.
    """

    return start + percent * (end - start)
