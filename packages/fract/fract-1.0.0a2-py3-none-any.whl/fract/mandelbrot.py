from datetime import datetime
from math import ceil
from multiprocessing import Pool, Queue, cpu_count, current_process
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Optional

import png

from fract.logging import logger


def count_all_iterations(
    render_width: int,
    render_height: int,
    real: float,
    imaginary: float,
    real_width: float,
    max_iterations: int,
    max_processes: int,
    result_byte_length: int,
    working_directory: Path,
) -> None:
    queue: "Queue[int]" = Queue()
    start = datetime.now()

    for y in range(render_height):
        queue.put(y)

    for _ in range(max_processes):
        queue.put(-1)

    imaginary_height = real_width * (render_height / render_width)

    worker_args = (
        render_width,
        render_height,
        real_width,
        real - (real_width / 2),
        imaginary_height,
        imaginary - (imaginary_height / 2),
        max_iterations,
        queue,
        result_byte_length,
        working_directory,
    )

    logger.debug("Starting a pool of %i processes", max_processes)
    with Pool(max_processes, start_row_listener, worker_args) as pool:
        pool.close()

        logger.debug("Waiting for workers to finish...")
        pool.join()

    logger.debug(
        "Calculated all iterations in %.1f seconds",
        (datetime.now() - start).total_seconds(),
    )


def count_iterations(
    real: float,
    imaginary: float,
    maximum: int,
) -> int:
    """
    Counts the number of iterations required for the point (`real`, `imaginary`)
    to escape the Mandelbrot set, to a `maximum` iteration.
    """

    if estimate_in_mandelbrot_set(real, imaginary):
        return maximum

    count = 0

    x = 0.0
    y = 0.0

    x_squared = 0.0
    y_squared = 0.0

    x_cycle = 0.0
    y_cycle = 0.0

    period = 0

    while x_squared + y_squared <= 4.0 and count < maximum:
        y = ((2 * x) * y) + imaginary
        x = (x_squared - y_squared) + real

        x_squared = x * x
        y_squared = y * y

        if x == x_cycle and y == y_cycle:
            return maximum

        period += 1

        if period > 20:
            period = 0
            x_cycle = x
            y_cycle = y

        count += 1

    return count


def estimate_in_mandelbrot_set(
    real: float,
    imaginary: float,
) -> bool:
    """
    Estimates whether or not the point of (`real`, `imaginary`) is inside the
    Mandelbrot set's cardioid or a second-order bulb.

    `True` indicates certainty that the point is within the cardioid or a
    second-order bulb. `False` indicates uncertainty whether the point is inside
    or outside.
    """

    # Check cardioid:

    imaginary_squared = imaginary * imaginary

    real_minus_quarter = real - 0.25

    q = (real_minus_quarter * real_minus_quarter) + imaginary_squared

    if q * (q + real_minus_quarter) <= (0.25 * imaginary_squared):
        return True

    # Check bulbs:

    real_plus_one = real + 1

    return (real_plus_one * real_plus_one) + imaginary_squared <= 0.0625


def iterations_to_color_rows(
    height: int,
    max_iterations: int,
    result_byte_length: int,
    working_directory: Path,
) -> Iterator[list[int]]:
    colors: list[int] = []

    for y in range(height):
        if y > 0:
            yield colors
            colors = []

        with open(working_directory / str(y), "rb") as f:
            while read_bytes := f.read(result_byte_length):
                iteration_count = int.from_bytes(read_bytes)

                if iteration_count < max_iterations:
                    colors.extend([255, 255, 255])
                else:
                    colors.extend([0, 0, 0])

    yield colors


def render_mandelbrot(
    width: int,
    height: int,
    path: Path | str,
    max_iterations: int = 1_000,
    max_processes: Optional[int] = None,
    x: float = -0.65,
    y: float = 0,
    zoom: float = 3.0,
) -> None:
    """
    Renders the Mandelbrot set to a PNG file.
    """

    max_processes = cpu_count() - 1 if max_processes is None else max_processes
    result_byte_length = ceil(max_iterations.bit_length() / 8.0)

    with TemporaryDirectory() as temp_dir:
        working_directory = Path(temp_dir)

        count_all_iterations(
            width,
            height,
            x,
            y,
            zoom,
            max_iterations,
            max_processes,
            result_byte_length,
            working_directory,
        )

        start = datetime.now()

        with open(path, "wb") as f:
            writer = png.Writer(
                width,
                height,
                greyscale=False,
            )

            rows = iterations_to_color_rows(
                height,
                max_iterations,
                result_byte_length,
                working_directory,
            )

            writer.write(f, rows)

        logger.debug(
            "Wrote PNG in %.1f seconds",
            (datetime.now() - start).total_seconds(),
        )


def start_row_listener(
    render_width: int,
    render_height: int,
    real_width: float,
    real_min: float,
    imaginary_height: float,
    imaginary_min: float,
    max_iterations: int,
    queue: "Queue[int]",
    result_byte_length: int,
    working_directory: Path,
) -> None:
    name = current_process().name
    logger.debug("Worker process %s started", name)

    while True:
        y = queue.get()

        if y < 0:
            logger.debug("Worker process %s stopping", name)
            return

        logger.debug("Worker process %s now working on line %i", name, y)

        imaginary = imaginary_min + (y / render_height) * imaginary_height

        path = working_directory / str(y)

        with open(path, "wb") as f:
            for x in range(render_width):
                count = count_iterations(
                    real_min + (x / render_width) * real_width,
                    imaginary,
                    max_iterations,
                )

                f.write(count.to_bytes(result_byte_length))
