from bendy import CubicBezier

from twixt.types import Function


def curve(cb: CubicBezier) -> Function:
    def transform(n: float) -> float:
        return next(iter(cb.estimate_y(n)))

    return transform


def elastic() -> Function:
    cb = CubicBezier(
        (0, 0),
        (0.25, -0.45),
        (0.75, 1.45),
        (1, 1),
    )

    return curve(cb)


def linear() -> Function:
    def transform(n: float) -> float:
        return n

    return transform
