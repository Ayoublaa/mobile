from collections import defaultdict
from dataclasses import asdict
from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import DBSCAN, KMeans

from .models import Anomaly, Cluster, LogEntry


class AbuseClusterer:
    def __init__(self, algorithm: str = "kmeans", n_clusters: int = 4) -> None:
        self.algorithm = algorithm
        self.n_clusters = n_clusters

    def _feature_vector(self, values: Dict[str, float]) -> List[float]:
        return [
            values.get("req_per_minute", 0.0),
            values.get("unique_endpoints_count", 0.0),
            values.get("error_rate_401", 0.0),
            values.get("is_mobile_ratio", 0.0),
            values.get("endpoint_variance", 0.0),
        ]

    def cluster(self, logs: List[LogEntry], anomalies: List[Anomaly]) -> List[Cluster]:
        grouped: Dict[str, Dict[str, object]] = defaultdict(lambda: {
            "count": 0,
            "start": None,
            "end": None,
            "endpoints": set(),
            "mobile": 0,
            "status_401": 0,
        })
        for log in logs:
            entry = grouped[log.ip]
            entry["count"] += 1
            entry["start"] = log.timestamp if entry["start"] is None else min(entry["start"], log.timestamp)
            entry["end"] = log.timestamp if entry["end"] is None else max(entry["end"], log.timestamp)
            entry["endpoints"].add(log.endpoint.split("?")[0])
            entry["mobile"] += int(log.is_mobile)
            entry["status_401"] += int(log.status == 401)

        features: List[List[float]] = []
        ips: List[str] = []
        summary: Dict[str, Dict[str, float]] = {}
        for ip, entry in grouped.items():
            duration = max((entry["end"] - entry["start"]).total_seconds(), 60)
            req_per_minute = entry["count"] / (duration / 60)
            unique_endpoints_count = len(entry["endpoints"])
            error_rate_401 = entry["status_401"] / entry["count"] if entry["count"] else 0.0
            is_mobile_ratio = entry["mobile"] / entry["count"] if entry["count"] else 0.0
            endpoint_variance = float(unique_endpoints_count) / max(1, len(entry["endpoints"]))
            features.append(self._feature_vector({
                "req_per_minute": req_per_minute,
                "unique_endpoints_count": unique_endpoints_count,
                "error_rate_401": error_rate_401,
                "is_mobile_ratio": is_mobile_ratio,
                "endpoint_variance": endpoint_variance,
            }))
            ips.append(ip)
            summary[ip] = {
                "req_per_minute": req_per_minute,
                "unique_endpoints_count": unique_endpoints_count,
                "error_rate_401": error_rate_401,
                "is_mobile_ratio": is_mobile_ratio,
                "endpoint_variance": endpoint_variance,
            }

        if not features:
            return []

        X = np.array(features)
        labels = self._fit_predict(X)
        clusters: Dict[int, List[str]] = defaultdict(list)
        for ip, label in zip(ips, labels):
            clusters[label].append(ip)

        cluster_results: List[Cluster] = []
        for label, ip_list in clusters.items():
            cluster_id = int(label) if label >= 0 else -1
            profile = self._classify_pattern(ip_list, summary)
            cluster_results.append(
                Cluster(
                    cluster_id=cluster_id,
                    ips=ip_list,
                    pattern_name=profile[0],
                    severity_profile=profile[1],
                )
            )
        return cluster_results

    def _fit_predict(self, X: np.ndarray) -> np.ndarray:
        if self.algorithm == "dbscan":
            model = DBSCAN(eps=0.75, min_samples=3)
            return model.fit_predict(X)
        model = KMeans(n_clusters=min(self.n_clusters, len(X)), random_state=42)
        return model.fit_predict(X)

    def _classify_pattern(self, ips: List[str], summary: Dict[str, Dict[str, float]]) -> Tuple[str, str]:
        if any(summary[ip]["req_per_minute"] > 80 for ip in ips):
            return "Bot_Scraper", "HIGH"
        if any(summary[ip]["error_rate_401"] > 0.3 for ip in ips):
            return "Bruteforcer", "CRITICAL"
        if any(summary[ip]["unique_endpoints_count"] > 20 for ip in ips):
            return "API_Scanner", "HIGH"
        return "Legitimate_Traffic", "LOW"
