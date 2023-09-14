from bendy import CubicBezier

from twixt.types import Transform


def elastic() -> Transform:
    cb = CubicBezier(
        (0, 0),
        (0.25, -0.45),
        (0.75, 1.45),
        (1, 1),
    )

    def transform(n: float) -> float:
        return next(iter(cb.estimate_y(n)))

    return transform


def linear() -> Transform:
    def transform(n: float) -> float:
        return n

    return transform
