"""
Holocloude Prometheus Metrics Export
=====================================

Exportiert Metriken im Prometheus-Format fuer Monitoring.

Endpoints:
    /metrics - Prometheus-kompatibles Metriken-Endpoint

Features:
- Standard Prometheus Text Format
- Process Metrics (CPU, Memory, Open FDs)
- Custom Application Metrics
- Request/Response Metriken
- LLM Performance Metriken
- Emotion/Personality Metriken
- Thread-safe Counter/Gauge/Histogram

Verwendung:
    from holo_metrics import MetricsRegistry, Counter, Gauge, Histogram

    # Registry erstellen
    registry = MetricsRegistry()

    # Metriken definieren
    requests_total = Counter(
        "holo_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"]
    )
    registry.register(requests_total)

    # Metriken verwenden
    requests_total.inc({"method": "POST", "endpoint": "/api/chat", "status": "200"})

    # Exportieren
    output = registry.export()  # Prometheus text format
"""

import os
import sys
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# METRIC TYPES
# =============================================================================

class MetricType:
    """Prometheus Metric Types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """Ein einzelner Metrik-Wert mit Labels"""
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: Optional[float] = None


class Metric(ABC):
    """Basis-Klasse fuer alle Metriken"""

    def __init__(self, name: str, description: str, labels: List[str] = None) -> None:
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._lock = threading.Lock()

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def collect(self) -> List[MetricValue]:
        """Sammelt alle Werte dieser Metrik"""
        pass

    def _validate_labels(self, labels: Dict[str, str]) -> None:
        """Validiert Labels"""
        provided = set(labels.keys())
        expected = set(self.label_names)
        if provided != expected:
            raise ValueError(
                f"Label mismatch for {self.name}: "
                f"expected {expected}, got {provided}"
            )

    def _labels_key(self, labels: Dict[str, str]) -> str:
        """Erstellt einen eindeutigen Key aus Labels"""
        if not labels:
            return ""
        return "|".join(f"{k}={v}" for k, v in sorted(labels.items()))


class Counter(Metric):
    """
    Counter - Nur aufwaerts zaehlen.

    Verwendung:
        requests = Counter("http_requests_total", "Total requests", ["method"])
        requests.inc({"method": "GET"})
        requests.inc({"method": "POST"}, 5)
    """

    def __init__(self, name: str, description: str, labels: List[str] = None) -> None:
        super().__init__(name, description, labels)
        self._values: Dict[str, float] = defaultdict(float)

    @property
    def type(self) -> str:
        return MetricType.COUNTER

    def inc(self, labels: Dict[str, str] = None, value: float = 1.0) -> None:
        """Erhoeht den Counter"""
        labels = labels or {}
        if self.label_names:
            self._validate_labels(labels)

        with self._lock:
            key = self._labels_key(labels)
            self._values[key] += value

    def collect(self) -> List[MetricValue]:
        with self._lock:
            result = []
            for key, value in self._values.items():
                labels = {}
                if key:
                    for item in key.split("|"):
                        k, v = item.split("=", 1)
                        labels[k] = v
                result.append(MetricValue(value=value, labels=labels))
            return result


class Gauge(Metric):
    """
    Gauge - Kann hoch und runter gehen.

    Verwendung:
        memory = Gauge("process_memory_bytes", "Memory usage")
        memory.set({}, 1024000)
        memory.inc({}, 100)
        memory.dec({}, 50)
    """

    def __init__(self, name: str, description: str, labels: List[str] = None) -> None:
        super().__init__(name, description, labels)
        self._values: Dict[str, float] = {}

    @property
    def type(self) -> str:
        return MetricType.GAUGE

    def set(self, labels: Dict[str, str] = None, value: float = 0.0) -> None:
        """Setzt den Gauge-Wert"""
        labels = labels or {}
        if self.label_names:
            self._validate_labels(labels)

        with self._lock:
            key = self._labels_key(labels)
            self._values[key] = value

    def inc(self, labels: Dict[str, str] = None, value: float = 1.0) -> None:
        """Erhoeht den Gauge"""
        labels = labels or {}
        with self._lock:
            key = self._labels_key(labels)
            self._values[key] = self._values.get(key, 0.0) + value

    def dec(self, labels: Dict[str, str] = None, value: float = 1.0) -> None:
        """Verringert den Gauge"""
        self.inc(labels, -value)

    def set_function(self, labels: Dict[str, str], func: Callable[[], float]) -> None:
        """Setzt eine Funktion die bei collect() aufgerufen wird"""
        # Fuer dynamische Werte wie CPU-Auslastung
        pass  # Vereinfachte Implementation

    def collect(self) -> List[MetricValue]:
        with self._lock:
            result = []
            for key, value in self._values.items():
                labels = {}
                if key:
                    for item in key.split("|"):
                        k, v = item.split("=", 1)
                        labels[k] = v
                result.append(MetricValue(value=value, labels=labels))
            return result


class Histogram(Metric):
    """
    Histogram - Misst Verteilungen (z.B. Request-Zeiten).

    Verwendung:
        latency = Histogram("http_request_duration_seconds", "Request latency",
                           buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0])
        latency.observe({}, 0.042)
    """

    DEFAULT_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def __init__(self, name: str, description: str, labels: List[str] = None,
                 buckets: tuple = None) -> None:
        super().__init__(name, description, labels)
        self.buckets = buckets or self.DEFAULT_BUCKETS
        self._values: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"buckets": {b: 0 for b in self.buckets}, "sum": 0.0, "count": 0}
        )

    @property
    def type(self) -> str:
        return MetricType.HISTOGRAM

    def observe(self, labels: Dict[str, str] = None, value: float = 0.0) -> None:
        """Beobachtet einen Wert"""
        labels = labels or {}
        if self.label_names:
            self._validate_labels(labels)

        with self._lock:
            key = self._labels_key(labels)
            data = self._values[key]
            data["sum"] += value
            data["count"] += 1

            for bucket in self.buckets:
                if value <= bucket:
                    data["buckets"][bucket] += 1

    def time(self, labels: Dict[str, str] = None) -> '_HistogramTimer':
        """Context Manager zum Zeitmessen"""
        return _HistogramTimer(self, labels or {})

    def collect(self) -> List[MetricValue]:
        with self._lock:
            result = []
            for key, data in self._values.items():
                labels = {}
                if key:
                    for item in key.split("|"):
                        k, v = item.split("=", 1)
                        labels[k] = v

                # Bucket-Werte (kumulativ)
                cumulative = 0
                for bucket in sorted(self.buckets):
                    cumulative += data["buckets"][bucket]
                    bucket_labels = {**labels, "le": str(bucket)}
                    result.append(MetricValue(
                        value=cumulative,
                        labels=bucket_labels
                    ))

                # +Inf Bucket
                result.append(MetricValue(
                    value=data["count"],
                    labels={**labels, "le": "+Inf"}
                ))

                # Sum und Count
                result.append(MetricValue(
                    value=data["sum"],
                    labels={**labels, "__suffix__": "_sum"}
                ))
                result.append(MetricValue(
                    value=data["count"],
                    labels={**labels, "__suffix__": "_count"}
                ))

            return result


class _HistogramTimer:
    """Context Manager fuer Histogram.time()"""

    def __init__(self, histogram: Histogram, labels: Dict[str, str]) -> None:
        self.histogram = histogram
        self.labels = labels
        self.start: Optional[float] = None

    def __enter__(self) -> '_HistogramTimer':
        self.start = time.time()
        return self

    def __exit__(self, *args) -> None:
        duration = time.time() - self.start
        self.histogram.observe(self.labels, duration)


# =============================================================================
# METRICS REGISTRY
# =============================================================================

class MetricsRegistry:
    """
    Zentrale Registry fuer alle Metriken.

    Verwendung:
        registry = MetricsRegistry()
        registry.register(my_counter)
        registry.register(my_gauge)

        # Exportieren
        print(registry.export())
    """

    def __init__(self) -> None:
        self._metrics: Dict[str, Metric] = {}
        self._lock = threading.Lock()

    def register(self, metric: Metric) -> Metric:
        """Registriert eine Metrik"""
        with self._lock:
            if metric.name in self._metrics:
                raise ValueError(f"Metric {metric.name} already registered")
            self._metrics[metric.name] = metric
        return metric

    def unregister(self, name: str) -> None:
        """Entfernt eine Metrik"""
        with self._lock:
            if name in self._metrics:
                del self._metrics[name]

    def get(self, name: str) -> Optional[Metric]:
        """Gibt eine Metrik zurueck"""
        return self._metrics.get(name)

    def export(self) -> str:
        """Exportiert alle Metriken im Prometheus Text Format"""
        lines = []

        with self._lock:
            for name, metric in sorted(self._metrics.items()):
                # HELP und TYPE
                lines.append(f"# HELP {name} {metric.description}")
                lines.append(f"# TYPE {name} {metric.type}")

                # Werte
                for mv in metric.collect():
                    suffix = mv.labels.pop("__suffix__", "")
                    metric_name = f"{name}{suffix}"

                    if mv.labels:
                        label_str = ",".join(
                            f'{k}="{v}"' for k, v in sorted(mv.labels.items())
                        )
                        lines.append(f"{metric_name}{{{label_str}}} {mv.value}")
                    else:
                        lines.append(f"{metric_name} {mv.value}")

                lines.append("")  # Leerzeile zwischen Metriken

        return "\n".join(lines)


# =============================================================================
# PROCESS METRICS (Standard)
# =============================================================================

def collect_process_metrics(registry: MetricsRegistry):
    """Sammelt Standard-Prozess-Metriken"""

    # CPU Zeit
    cpu_user = Gauge("process_cpu_user_seconds_total", "User CPU time")
    cpu_system = Gauge("process_cpu_system_seconds_total", "System CPU time")

    # Memory
    memory_rss = Gauge("process_resident_memory_bytes", "Resident memory size")
    memory_virtual = Gauge("process_virtual_memory_bytes", "Virtual memory size")

    # File Descriptors
    open_fds = Gauge("process_open_fds", "Open file descriptors")

    # Start Time
    start_time = Gauge("process_start_time_seconds", "Start time since epoch")

    # Registrieren
    registry.register(cpu_user)
    registry.register(cpu_system)
    registry.register(memory_rss)
    registry.register(memory_virtual)
    registry.register(open_fds)
    registry.register(start_time)

    def update():
        """Updated die Prozess-Metriken"""
        try:
            import psutil
            process = psutil.Process()

            # CPU
            cpu_times = process.cpu_times()
            cpu_user.set({}, cpu_times.user)
            cpu_system.set({}, cpu_times.system)

            # Memory
            mem_info = process.memory_info()
            memory_rss.set({}, mem_info.rss)
            memory_virtual.set({}, mem_info.vms)

            # FDs
            try:
                open_fds.set({}, process.num_fds())
            except AttributeError:
                # Windows hat keine num_fds()
                pass

            # Start Time
            start_time.set({}, process.create_time())

        except ImportError:
            logger.warning("psutil not available - process metrics disabled")

    return update


# =============================================================================
# HOLOCLOUDE-SPEZIFISCHE METRIKEN
# =============================================================================

def create_holocloude_metrics(registry: MetricsRegistry) -> Dict[str, Metric]:
    """Erstellt Holocloude-spezifische Metriken"""

    metrics = {}

    # === REQUEST METRIKEN ===
    metrics["requests_total"] = Counter(
        "holo_http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"]
    )

    metrics["request_duration"] = Histogram(
        "holo_http_request_duration_seconds",
        "HTTP request duration",
        ["method", "endpoint"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
    )

    # === LLM METRIKEN ===
    metrics["llm_requests_total"] = Counter(
        "holo_llm_requests_total",
        "Total LLM requests",
        ["model", "route"]  # route: local, remote, cache
    )

    metrics["llm_tokens_total"] = Counter(
        "holo_llm_tokens_total",
        "Total tokens processed",
        ["type"]  # input, output
    )

    metrics["llm_latency"] = Histogram(
        "holo_llm_request_duration_seconds",
        "LLM request duration",
        ["model"],
        buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
    )

    metrics["llm_cache_hits"] = Counter(
        "holo_llm_cache_hits_total",
        "LLM cache hits"
    )

    # === PERSONALITY METRIKEN ===
    metrics["emotion_current"] = Gauge(
        "holo_emotion_current",
        "Current emotion intensity",
        ["emotion"]
    )

    metrics["energy_level"] = Gauge(
        "holo_energy_level",
        "Current energy level",
        ["dimension"]  # mental, physical, emotional, social, creative, spiritual
    )

    # === CONVERSATION METRIKEN ===
    metrics["conversations_total"] = Counter(
        "holo_conversations_total",
        "Total conversations"
    )

    metrics["messages_total"] = Counter(
        "holo_messages_total",
        "Total messages",
        ["direction"]  # in, out
    )

    # === SYSTEM METRIKEN ===
    metrics["uptime_seconds"] = Gauge(
        "holo_uptime_seconds",
        "Application uptime in seconds"
    )

    metrics["active_connections"] = Gauge(
        "holo_active_connections",
        "Number of active connections"
    )

    metrics["errors_total"] = Counter(
        "holo_errors_total",
        "Total errors",
        ["type", "module"]
    )

    # Alle registrieren
    for metric in metrics.values():
        registry.register(metric)

    return metrics


# =============================================================================
# GLOBAL REGISTRY & CONVENIENCE FUNCTIONS
# =============================================================================

# Globale Registry
_registry: Optional[MetricsRegistry] = None
_metrics: Dict[str, Metric] = {}
_process_update: Optional[Callable] = None


def init_metrics() -> MetricsRegistry:
    """Initialisiert das globale Metrics-System"""
    global _registry, _metrics, _process_update

    _registry = MetricsRegistry()
    _metrics = create_holocloude_metrics(_registry)
    _process_update = collect_process_metrics(_registry)

    logger.info("Metrics System initialisiert")
    return _registry


def get_registry() -> MetricsRegistry:
    """Gibt die globale Registry zurueck"""
    global _registry
    if _registry is None:
        init_metrics()
    return _registry


def get_metric(name: str) -> Optional[Metric]:
    """Gibt eine Metrik nach Namen zurueck"""
    global _metrics
    return _metrics.get(name)


def export_metrics() -> str:
    """Exportiert alle Metriken als Prometheus Text"""
    global _process_update
    if _process_update:
        _process_update()
    return get_registry().export()


# =============================================================================
# HTTP ENDPOINT
# =============================================================================

def metrics_endpoint() -> tuple:
    """
    HTTP Handler fuer /metrics Endpoint.

    Returns:
        Tuple (status_code, content_type, body)
    """
    try:
        output = export_metrics()
        return (200, "text/plain; charset=utf-8", output)
    except Exception as e:
        logger.error(f"Metrics export failed: {e}")
        return (500, "text/plain", f"Error: {e}")


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Holocloude Metrics Demo")
    parser.add_argument("--serve", action="store_true",
                        help="Startet einen einfachen Metrics-Server")
    parser.add_argument("--port", type=int, default=9090,
                        help="Port fuer den Metrics-Server")

    args = parser.parse_args()

    # Metriken initialisieren
    registry = init_metrics()

    # Demo-Daten
    get_metric("requests_total").inc({"method": "GET", "endpoint": "/api/chat", "status": "200"})
    get_metric("requests_total").inc({"method": "POST", "endpoint": "/api/chat", "status": "200"}, 5)
    get_metric("llm_requests_total").inc({"model": "qwen2.5", "route": "local"}, 10)
    get_metric("llm_cache_hits").inc({}, 3)
    get_metric("emotion_current").set({"emotion": "happy"}, 0.7)
    get_metric("emotion_current").set({"emotion": "curious"}, 0.5)
    get_metric("energy_level").set({"dimension": "mental"}, 0.8)
    get_metric("uptime_seconds").set({}, 3600)

    if args.serve:
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class MetricsHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/metrics":
                    status, content_type, body = metrics_endpoint()
                    self.send_response(status)
                    self.send_header("Content-Type", content_type)
                    self.end_headers()
                    self.wfile.write(body.encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass  # Suppress logging

        server = HTTPServer(("0.0.0.0", args.port), MetricsHandler)
        print(f"Metrics server running on http://localhost:{args.port}/metrics")
        server.serve_forever()
    else:
        # Einfach exportieren
        print(export_metrics())
