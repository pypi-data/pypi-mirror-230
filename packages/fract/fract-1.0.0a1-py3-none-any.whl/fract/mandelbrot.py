from math import ceil
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Optional

import png

from fract.process_instruction import ProcessInstruction
from fract.process_planner import ProcessPlanner
from fract.segment import Segment
from fract.segment_planner import SegmentPlanner


def calculate(
    instructions: Iterator[ProcessInstruction],
    max_processes: int,
) -> None:
    with Pool(processes=max_processes) as pool:
        pool.map_async(
            calculate_segment,
            instructions,
        )

        pool.close()
        pool.join()


def calculate_segment(i: ProcessInstruction) -> None:
    """
    Generates a temporary iteration count file for a row segment.
    """

    with open(i["result_path"], "wb") as f:
        for px in range(i["min_x"], i["max_x"]):
            viewport_x_percent = px / i["render_width"]

            c = complex(
                i["plane_min_x"] + viewport_x_percent * i["plane_width"],
                i["plane_y"],
            )

            iterations = count_iterations(
                c,
                i["max_iterations"],
            )

            f.write(iterations.to_bytes(i["result_byte_length"]))


def count_iterations(
    c: complex,
    maximum: int,
) -> int:
    """
    Counts and returns the iterations for a complex number.
    """

    count = 0
    z = c

    while count < maximum and (z * z.conjugate()).real < 4:
        z = (z * z) + c
        count += 1

    return count


def iterations_to_pixels(
    max_iterations: int,
    result_byte_length: int,
    segments: Iterator[Segment],
) -> Iterator[list[int]]:
    current_y: Optional[int] = None
    colors: list[int] = []

    for segment in segments:
        if current_y != segment["y"]:
            if current_y is not None:
                yield colors
                colors = []

            current_y = segment["y"]

        with open(segment["path"], "rb") as f:
            while read_bytes := f.read(result_byte_length):
                iteration_count = int.from_bytes(read_bytes)

                if iteration_count < max_iterations:
                    colors.extend([255, 255, 255])
                else:
                    colors.extend([0, 0, 0])

    yield colors


def render(
    width: int,
    height: int,
    path: Path,
    max_iterations: int = 500,
    max_processes: Optional[int] = None,
    x: float = -0.65,
    y: float = 0,
    zoom: float = 3.0,
) -> None:
    """
    Renders the Mandelbrot Set to a PNG file.
    """

    max_processes = cpu_count() - 1 if max_processes is None else max_processes

    # Give each thread enough to keep busy for at least a few seconds. If
    # segments are too small then threads will spend more time starting/stopping
    # than working. This value works on my laptop, so nyah.
    max_segment_width = 100_000

    plot_height = zoom * (height / width)
    result_byte_length = ceil(max_iterations.bit_length() / 8.0)

    with TemporaryDirectory() as temp_dir:
        working_directory = Path(temp_dir)

        segment_planner = SegmentPlanner(
            max_segment_width,
            height,
            width,
            working_directory,
        )

        process_planner = ProcessPlanner(
            max_iterations,
            plot_height,
            zoom,
            x - (zoom / 2),
            y - (plot_height / 2),
            height,
            width,
            result_byte_length,
            segment_planner.make(),
        )

        calculate(
            process_planner.make(),
            max_processes=max_processes,
        )

        with open(path, "wb") as f:
            writer = png.Writer(
                width,
                height,
                greyscale=False,
            )

            writer.write(
                f,
                iterations_to_pixels(
                    max_iterations,
                    result_byte_length,
                    segment_planner.make(),
                ),
            )
