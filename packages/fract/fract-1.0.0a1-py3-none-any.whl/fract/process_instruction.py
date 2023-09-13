from pathlib import Path
from typing import TypedDict


class ProcessInstruction(TypedDict):
    min_x: int
    max_iterations: int
    max_x: int
    plane_min_x: float
    plane_width: float
    plane_y: float
    render_width: int
    result_byte_length: int
    result_path: Path
