import numpy as np
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from sklearn.ensemble import IsolationForest

from .models import Anomaly, LogEntry


class IsolationForestDetector:
    def __init__(self, contamination: float = 0.1, random_state: int = 42) -> None:
        self.contamination = contamination
        self.random_state = random_state

    def detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        if len(logs) < 5:
            return []

        ip_metrics = self._group_metrics(logs)
        if len(ip_metrics) < 3:
            return []

        features = []
        ordered_ips = []
        for ip, metrics in ip_metrics.items():
            features.append(
                [
                    metrics["req_per_minute"],
                    metrics["unique_endpoints"],
                    metrics["error_rate_401"],
                    metrics["error_rate_5xx"],
                    metrics["mobile_ratio"],
                    metrics["method_variance"],
                ]
            )
            ordered_ips.append(ip)

        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
        )
        labels = model.fit_predict(np.array(features))

        anomalies: List[Anomaly] = []
        for ip, label in zip(ordered_ips, labels):
            if label == -1:
                metrics = ip_metrics[ip]
                anomalies.append(
                    Anomaly(
                        ip=ip,
                        type="behavioral_outlier",
                        timestamp=metrics["first_seen"],
                        severity="HIGH",
                        details={
                            "req_per_minute": round(metrics["req_per_minute"], 2),
                            "unique_endpoints": metrics["unique_endpoints"],
                            "error_rate_401": round(metrics["error_rate_401"], 3),
                            "error_rate_5xx": round(metrics["error_rate_5xx"], 3),
                            "mobile_ratio": round(metrics["mobile_ratio"], 3),
                            "method_variance": round(metrics["method_variance"], 3),
                        },
                    )
                )
        return anomalies

    def _group_metrics(self, logs: List[LogEntry]) -> Dict[str, Dict[str, float]]:
        groups: Dict[str, Dict[str, object]] = defaultdict(lambda: {
            "count": 0,
            "user_agents": set(),
            "endpoints": set(),
            "methods": set(),
            "status_401": 0,
            "status_5xx": 0,
            "mobile": 0,
            "first_seen": None,
            "timestamps": [],
        })

        for log in logs:
            entry = groups[log.ip]
            entry["count"] += 1
            entry["user_agents"].add(log.user_agent)
            entry["endpoints"].add(log.endpoint.split("?")[0])
            entry["methods"].add(log.method)
            entry["status_401"] += int(log.status == 401)
            entry["status_5xx"] += int(500 <= log.status < 600)
            entry["mobile"] += int(log.is_mobile)
            entry["timestamps"].append(log.timestamp)
            if entry["first_seen"] is None or log.timestamp < entry["first_seen"]:
                entry["first_seen"] = log.timestamp

        summary: Dict[str, Dict[str, float]] = {}
        for ip, entry in groups.items():
            duration = max(
                (max(entry["timestamps"]) - min(entry["timestamps"])).total_seconds(),
                60,
            )
            summary[ip] = {
                "req_per_minute": entry["count"] / (duration / 60),
                "unique_endpoints": float(len(entry["endpoints"])),
                "error_rate_401": entry["status_401"] / max(1, entry["count"]),
                "error_rate_5xx": entry["status_5xx"] / max(1, entry["count"]),
                "mobile_ratio": entry["mobile"] / max(1, entry["count"]),
                "method_variance": float(len(entry["methods"])) / max(1, entry["count"]),
                "first_seen": entry["first_seen"] or datetime.utcnow(),
            }
        return summary


class BehavioralProfiler:
    def profile(self, logs: List[LogEntry], clusters: List[dict]) -> List[Dict[str, object]]:
        ip_metrics = self._group_metrics(logs)
        profiles: List[Dict[str, object]] = []

        for cluster in clusters:
            metrics = [ip_metrics.get(ip) for ip in cluster.get("ips", []) if ip in ip_metrics]
            if not metrics:
                continue
            average = {
                "avg_req_per_minute": round(sum(item["req_per_minute"] for item in metrics) / len(metrics), 2),
                "avg_unique_endpoints": round(sum(item["unique_endpoints"] for item in metrics) / len(metrics), 2),
                "avg_error_rate_401": round(sum(item["error_rate_401"] for item in metrics) / len(metrics), 3),
                "avg_mobile_ratio": round(sum(item["mobile_ratio"] for item in metrics) / len(metrics), 3),
            }
            profiles.append(
                {
                    "cluster_id": cluster["cluster_id"],
                    "pattern_name": cluster["pattern_name"],
                    "severity_profile": cluster["severity_profile"],
                    **average,
                }
            )
        return profiles

    def _group_metrics(self, logs: List[LogEntry]) -> Dict[str, Dict[str, float]]:
        return IsolationForestDetector()._group_metrics(logs)
