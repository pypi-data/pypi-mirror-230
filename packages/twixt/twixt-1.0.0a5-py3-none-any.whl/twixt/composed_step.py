from typing import Generic, TypedDict

from twixt.types import TKey


class ComposedStep(TypedDict, Generic[TKey]):
    frame: int
    progress: dict[TKey, float]
