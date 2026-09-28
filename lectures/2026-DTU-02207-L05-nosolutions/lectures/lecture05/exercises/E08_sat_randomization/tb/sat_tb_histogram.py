from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_histogram(values, filename):
    figure, axis = plt.subplots()
    counts = Counter(values)
    value_min = min(values)
    value_max = max(values)
    bar_width = 0.8
    if len(counts) > 1:
        sorted_values = sorted(counts)
        bar_width = min(10, min(right - left for left, right in zip(sorted_values, sorted_values[1:])) * 0.8)  # noqa: B905
    axis.bar(counts.keys(), counts.values(), width=bar_width)
    axis.set_xlabel("Value")
    axis.set_ylabel("Number of times it occurred")
    tick_step = next(step for step in (1, 2, 5, 10, 25, 50) if step >= max(1, (value_max - value_min) // 6))
    tick_start = value_min // tick_step * tick_step
    tick_end = (value_max + tick_step - 1) // tick_step * tick_step
    axis.set_xticks(range(tick_start, tick_end + 1, tick_step))
    axis.set_xlim(value_min - bar_width, value_max + bar_width)
    output_path = Path(__file__).parent / "sim_build" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path)
    plt.close(figure)
