from typing import Iterator

from twixt.types import Function
from twixt.utilities import lerp


class Transition:
    def __init__(
        self,
        start: float,
        end: float,
        function: Function,
        frames: int,
    ) -> None:
        if frames < 2:
            msg = f"Transitions require at least two frames ({frames})"
            raise ValueError(msg)

        self._end = end
        self._frames = frames
        self._function = function
        self._start = start

    @property
    def frames(self) -> int:
        return self._frames

    def step(self, frame: int) -> float:
        if frame <= 0:
            return self._start

        if frame >= self._frames:
            return self._end

        normal_frame = frame / (self._frames - 1)
        normal = self._function(normal_frame)

        value = lerp(
            self._start,
            self._end,
            normal,
        )

        return value

    @property
    def steps(self) -> Iterator[float]:
        for frame in range(self._frames):
            yield self.step(frame)
