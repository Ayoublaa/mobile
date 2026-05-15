from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List

from .models import Anomaly, LogEntry


class SpikeDetector:
    def __init__(self, threshold_rps: int = 50) -> None:
        self.threshold_rps = threshold_rps

    def detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        windows: Dict[str, List[datetime]] = defaultdict(list)
        anomalies: List[Anomaly] = []
        for log in sorted(logs, key=lambda entry: entry.timestamp):
            windows[log.ip].append(log.timestamp)
        for ip, timestamps in windows.items():
            for idx, ts in enumerate(timestamps):
                window_end = ts + timedelta(seconds=60)
                count = sum(1 for t in timestamps[idx:] if t <= window_end)
                if count >= self.threshold_rps:
                    anomalies.append(
                        Anomaly(
                            ip=ip,
                            type="spike",
                            timestamp=ts,
                            severity="HIGH" if count >= self.threshold_rps * 2 else "MEDIUM",
                            details={
                                "count": count,
                                "window_sec": 60,
                                "threshold_rps": self.threshold_rps,
                            },
                        )
                    )
                    break
        return anomalies


class AuthAnalyzer:
    def __init__(self, threshold_401: int = 10) -> None:
        self.threshold_401 = threshold_401
        self.login_endpoints = {"/login", "/auth", "/signin"}

    def detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        failed_by_ip: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        first_timestamp: Dict[str, datetime] = {}
        for log in logs:
            endpoint = log.endpoint.split("?")[0]
            if endpoint in self.login_endpoints and log.status == 401:
                failed_by_ip[log.ip][endpoint] += 1
                first_timestamp.setdefault(log.ip, log.timestamp)
        anomalies: List[Anomaly] = []
        for ip, endpoints in failed_by_ip.items():
            total_failed = sum(endpoints.values())
            if total_failed >= self.threshold_401:
                details = {
                    "endpoint": list(endpoints.keys()),
                    "failed_attempts": total_failed,
                    "breakdown": dict(endpoints),
                }
                anomalies.append(
                    Anomaly(
                        ip=ip,
                        type="bruteforce",
                        timestamp=first_timestamp.get(ip, datetime.utcnow()),
                        severity="CRITICAL",
                        details=details,
                    )
                )
        return anomalies


class EndpointEnumerator:
    def __init__(self, threshold_unique_endpoints: int = 20) -> None:
        self.threshold_unique_endpoints = threshold_unique_endpoints

    def detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        endpoints_by_ip: Dict[str, set] = defaultdict(set)
        first_timestamp: Dict[str, datetime] = {}
        for log in logs:
            normalized = log.endpoint.split("?")[0]
            endpoints_by_ip[log.ip].add(normalized)
            first_timestamp.setdefault(log.ip, log.timestamp)
        anomalies: List[Anomaly] = []
        for ip, endpoints in endpoints_by_ip.items():
            unique_count = len(endpoints)
            if unique_count >= self.threshold_unique_endpoints:
                anomalies.append(
                    Anomaly(
                        ip=ip,
                        type="enumeration",
                        timestamp=first_timestamp.get(ip, datetime.utcnow()),
                        severity="HIGH" if unique_count >= self.threshold_unique_endpoints * 2 else "MEDIUM",
                        details={
                            "unique_count": unique_count,
                            "endpoints_list": sorted(list(endpoints))[:50],
                        },
                    )
                )
        return anomalies
