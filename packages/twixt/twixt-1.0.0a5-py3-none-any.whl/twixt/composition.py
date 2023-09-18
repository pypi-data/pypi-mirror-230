from typing import Generic, Iterator

from twixt.composed_step import ComposedStep
from twixt.transition import Transition
from twixt.types import TKey


class Composition(Generic[TKey]):
    """
    A composition of multiple transitions.

    Arguments:
        lead_in: Frames to step before starting any transitions.
        lead_out: Frames to step after all transitions have completed.
    """

    def __init__(
        self,
        lead_in: int = 0,
        lead_out: int = 0,
    ) -> None:
        self._frames = 0
        self._lead_in = lead_in
        self._lead_out = lead_out
        self._offsets: dict[TKey, int] = {}
        self._transitions: dict[TKey, Transition] = {}

    def add(
        self,
        key: TKey,
        transition: Transition,
        offset: int = 0,
    ) -> None:
        if key in self._transitions:
            raise ValueError(f'Transition "{key}" already exists')

        self._offsets[key] = offset
        self._transitions[key] = transition

        self._frames = max(self._frames, transition.frames + offset)

    @property
    def steps(self) -> Iterator[ComposedStep[TKey]]:
        for frame in range(self._lead_in + self._frames + self._lead_out):
            progress: dict[TKey, float] = {}

            for key, transition in self._transitions.items():
                transition_frame = frame - self._offsets[key] - self._lead_in
                progress[key] = transition.step(transition_frame)

            yield ComposedStep(
                frame=frame,
                progress=progress,
            )
