from pathlib import Path
from typing import Iterator

from fract.segment import Segment


class SegmentPlanner:
    def __init__(
        self,
        max_segment_length: int,
        render_height: int,
        render_width: int,
        working_directory: Path,
    ) -> None:
        self._max_segment_length = max_segment_length
        self._render_height = render_height
        self._render_width = render_width
        self._working_directory = working_directory

    def make(self) -> Iterator[Segment]:
        for y in range(self._render_height):
            x = 0
            remaining = self._render_width

            while remaining > 0:
                segment_length = (
                    self._max_segment_length
                    if remaining >= self._max_segment_length
                    else remaining
                )

                yield Segment(
                    max_x=x + segment_length,
                    min_x=x,
                    path=self._working_directory / f"{y}x{x}",
                    y=y,
                )

                remaining -= segment_length
                x += segment_length
