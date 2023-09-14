from typing import Iterable

from twixt.logging import logger
from twixt.types import Transform
from twixt.utilities import lerp


def transition(
    start: float,
    end: float,
    count: int,
    t: Transform,
) -> Iterable[float]:
    """
    Yields `count` values between `start` and `end` via transformer `t`.
    """

    if count < 2:
        raise ValueError(f"count ({count}) must be >= 2")

    for index in range(count):
        normal_index = index / (count - 1)
        normal = t(normal_index)

        value = lerp(
            start,
            end,
            normal,
        )

        logger.info(
            "normal_index = %f, value = %f",
            normal_index,
            value,
        )

        yield value
