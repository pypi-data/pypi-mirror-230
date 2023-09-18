from bendy import CubicBezier

from twixt.types import Function


def curve(
    cb: CubicBezier,
    resolution: int = 100,
) -> Function:
    def transform(n: float) -> float:
        estimations = cb.estimate_y(
            n,
            resolution=resolution,
        )

        # We intentionally take only the first estimation. We shouldn't be
        # passing curves that have multiple values for any given frame.
        return next(estimations)

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
