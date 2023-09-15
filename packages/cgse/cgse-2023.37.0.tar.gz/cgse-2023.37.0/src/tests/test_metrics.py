import rich
from prometheus_client import Gauge

from egse.metrics import define_metrics


def test_define_metrics():

    metrics = define_metrics("TCS-HK")

    rich.print(f"{len(metrics)=}")
    rich.print(f"Metrics keys: {sorted(metrics.keys())}")

    assert 'GTCS_TRP1_PID_TS' in metrics.keys()
    assert isinstance(metrics["GTCS_TRP1_PID_TS"], Gauge)

    assert 'GTCS_TASK_IS_RUNNING' in metrics.keys()
    assert isinstance(metrics["GTCS_TASK_IS_RUNNING"], Gauge)


def test_define_metrics_per_dashboard():

    # metrics = define_metrics("OGSE", dashboard="GOGSE_MON")
    #
    # rich.print(f"{len(metrics)=}")
    # rich.print(f"Metrics keys: {sorted(metrics.keys())}")

    # metrics = define_metrics("TCS-HK", dashboard="TCS_SYS_MON")
    #
    # rich.print(f"{len(metrics)=}")
    # rich.print(f"Metrics keys: {sorted(metrics.keys())}")

    # metrics = define_metrics("TCS-HK", dashboard="*")
    #
    # rich.print(f"{len(metrics)=}")
    # rich.print(f"Metrics keys: {sorted(metrics.keys())}")

    # metrics = define_metrics("SYN-HK", dashboard="SYN_MON")
    #
    # rich.print(f"{len(metrics)=}")
    # rich.print(f"Metrics keys: {sorted(metrics.keys())}")

    metrics = define_metrics("TCS-HK", dashboard="*")

    rich.print(f"{len(metrics)=}")
    # rich.print(f"Metrics keys: {sorted(metrics.keys())}")
    rich.print(f"Metrics keys: {metrics.keys()}")
