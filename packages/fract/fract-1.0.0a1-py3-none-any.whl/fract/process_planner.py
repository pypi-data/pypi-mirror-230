from typing import Iterator

from fract.process_instruction import ProcessInstruction
from fract.segment import Segment


class ProcessPlanner:
    def __init__(
        self,
        max_iterations: int,
        plane_height: float,
        plane_width: float,
        plane_min_x: float,
        plane_min_y: float,
        render_height: int,
        render_width: int,
        result_byte_length: int,
        segments: Iterator[Segment],
    ) -> None:
        self._result_byte_length = result_byte_length
        self._segments = segments
        self._max_iterations = max_iterations
        self._render_height = render_height
        self._render_width = render_width

        self._plane_width = plane_width

        self._plane_height = plane_height

        self._plane_min_x = plane_min_x
        self._plane_min_y = plane_min_y

    def make(self) -> Iterator[ProcessInstruction]:
        for segment in self._segments:
            viewport_y_percent = segment["y"] / self._render_height
            plane_y = self._plane_min_y + viewport_y_percent * self._plane_height

            yield ProcessInstruction(
                min_x=segment["min_x"],
                max_iterations=self._max_iterations,
                max_x=segment["max_x"],
                plane_min_x=self._plane_min_x,
                plane_width=self._plane_width,
                plane_y=plane_y,
                render_width=self._render_width,
                result_byte_length=self._result_byte_length,
                result_path=segment["path"],
            )
