from pathlib import Path
from typing import TypedDict


class Segment(TypedDict):
    """
    A line segment to be rendered in an independent process.
    """

    max_x: int
    min_x: int
    path: Path
    y: int
