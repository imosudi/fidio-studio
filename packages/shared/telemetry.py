import time
from typing import Dict, Tuple, Any


class MetricsRegistry:
    """Lightweight Prometheus metrics collector for Fídíò platform metrics."""

    def __init__(self):
        self._counters: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], int] = {}
        self._histograms: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], list] = {}

    def inc_counter(self, name: str, labels: Dict[str, str] = None, value: int = 1):
        label_key = tuple(sorted((labels or {}).items()))
        key = (name, label_key)
        self._counters[key] = self._counters.get(key, 0) + value

    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        label_key = tuple(sorted((labels or {}).items()))
        key = (name, label_key)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)

    def generate_prometheus_text(self) -> str:
        """Render metrics in standard Prometheus text format."""
        lines = []

        # Export Counters
        for (name, labels), count in sorted(self._counters.items()):
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            label_formatted = f"{{{label_str}}}" if label_str else ""
            lines.append(f"{name}{label_formatted} {count}")

        # Export Histograms (Count & Sum)
        for (name, labels), values in sorted(self._histograms.items()):
            label_str = ",".join(f'{k}="{v}"' for k, v in labels)
            label_formatted = f"{{{label_str}}}" if label_str else ""
            count = len(values)
            total_sum = sum(values)
            lines.append(f"{name}_count{label_formatted} {count}")
            lines.append(f"{name}_sum{label_formatted} {total_sum:.4f}")

        return "\n".join(lines) + "\n"


metrics = MetricsRegistry()
