from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .models import Anomaly, LogEntry
from .detector import AuthAnalyzer, EndpointEnumerator, SpikeDetector


class BenchmarkEngine:
    def __init__(self) -> None:
        self.detectors = [SpikeDetector(), AuthAnalyzer(), EndpointEnumerator()]

    def run(self) -> Dict[str, Any]:
        scenarios = self._build_scenarios()
        baseline_results = []
        model_results = []

        for scenario in scenarios:
            synthetic_logs, expected = self._generate_scenario(scenario)
            model_anomalies = self._detect(synthetic_logs)
            baseline = self._fail2ban_like(synthetic_logs)

            model_metrics = self._score(expected, model_anomalies)
            baseline_metrics = self._score(expected, baseline)

            model_results.append({
                "scenario": scenario["name"],
                "expected": expected,
                "detected": [a.to_dict() for a in model_anomalies],
                "metrics": model_metrics,
            })
            baseline_results.append({
                "scenario": scenario["name"],
                "metrics": baseline_metrics,
            })

        overall = self._summarize(model_results, baseline_results)
        return {
            "scenarios": model_results,
            "baseline": baseline_results,
            "summary": overall,
        }

    def _build_scenarios(self) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        return [
            {
                "name": "Spikes mobiles haute fréquence",
                "ip": "203.0.113.21",
                "pattern": "spike",
                "duration": 60,
                "requests": 120,
                "endpoint": "/api/mobiles/data",
                "status": 200,
                "user_agent": "Mozilla/5.0 (Android; Mobile)",
            },
            {
                "name": "Bruteforce /login",
                "ip": "198.51.100.24",
                "pattern": "bruteforce",
                "duration": 120,
                "requests": 18,
                "endpoint": "/login",
                "status": 401,
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile",
            },
            {
                "name": "Enumeration d'API",
                "ip": "10.0.0.99",
                "pattern": "enumeration",
                "duration": 90,
                "requests": 30,
                "endpoint": "/api/v1/item/",
                "status": 200,
                "user_agent": "curl/7.85.0",
            },
            {
                "name": "Scanner multiroute",
                "ip": "203.0.113.95",
                "pattern": "enumeration",
                "duration": 150,
                "requests": 45,
                "endpoint": "/api/v2/resource/",
                "status": 200,
                "user_agent": "python-requests/2.31.0",
            },
            {
                "name": "Flood 500 errors",
                "ip": "192.0.2.37",
                "pattern": "spike",
                "duration": 80,
                "requests": 90,
                "endpoint": "/api/v1/checkout",
                "status": 500,
                "user_agent": "Mozilla/5.0 (Linux; Android 13) Mobile",
            },
            {
                "name": "Brower legitimate",
                "ip": "198.51.100.200",
                "pattern": "legitimate",
                "duration": 240,
                "requests": 24,
                "endpoint": "/api/profile",
                "status": 200,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            },
            {
                "name": "Rapid 401 login probe",
                "ip": "203.0.113.229",
                "pattern": "bruteforce",
                "duration": 90,
                "requests": 22,
                "endpoint": "/auth",
                "status": 401,
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Mobile",
            },
            {
                "name": "Stealth scanner variation",
                "ip": "10.0.0.147",
                "pattern": "enumeration",
                "duration": 200,
                "requests": 42,
                "endpoint": "/api/search?q=",
                "status": 200,
                "user_agent": "curl/7.92.0",
            },
            {
                "name": "Normal Mobile Browse",
                "ip": "192.0.2.99",
                "pattern": "legitimate",
                "duration": 180,
                "requests": 18,
                "endpoint": "/api/dashboard",
                "status": 200,
                "user_agent": "Mozilla/5.0 (Android; Mobile)",
            },
        ]

    def _generate_scenario(self, scenario: Dict[str, Any]) -> Any:
        synthetic: List[LogEntry] = []
        expected_types = []
        ip = scenario["ip"]
        start = datetime.utcnow()
        if scenario["pattern"] == "spike":
            expected_types = ["spike"]
        elif scenario["pattern"] == "bruteforce":
            expected_types = ["bruteforce"]
        elif scenario["pattern"] == "enumeration":
            expected_types = ["enumeration"]
        else:
            expected_types = []

        for idx in range(scenario["requests"]):
            timestamp = start + timedelta(seconds=idx * max(1, scenario["duration"] // max(1, scenario["requests"])))
            endpoint = scenario["endpoint"]
            if scenario["pattern"] == "enumeration":
                endpoint = f"{endpoint}{idx}"
            synthetic.append(
                LogEntry(
                    ip=ip,
                    timestamp=timestamp,
                    method="GET",
                    endpoint=endpoint,
                    status=scenario["status"],
                    user_agent=scenario["user_agent"],
                    is_mobile="Mobile" in scenario["user_agent"] or "Android" in scenario["user_agent"],
                )
            )
        return synthetic, {"ip": ip, "expected_types": expected_types}

    def _detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        anomalies: List[Anomaly] = []
        for detector in self.detectors:
            anomalies.extend(detector.detect(logs))
        return anomalies

    def _fail2ban_like(self, logs: List[LogEntry]) -> List[Anomaly]:
        results: List[Anomaly] = []
        ip_history: Dict[str, List[LogEntry]] = defaultdict(list)
        for log in logs:
            ip_history[log.ip].append(log)

        for ip, entries in ip_history.items():
            auth_errors = [log for log in entries if log.endpoint.split("?")[0] in {"/login", "/auth", "/signin"} and log.status == 401]
            if len(auth_errors) >= 7:
                results.append(
                    Anomaly(
                        ip=ip,
                        type="bruteforce",
                        timestamp=min(log.timestamp for log in auth_errors),
                        severity="HIGH",
                        details={"failed_attempts": len(auth_errors), "baseline": "fail2ban"},
                    )
                )
            time_sorted = sorted(entries, key=lambda log: log.timestamp)
            window_start = time_sorted[0].timestamp
            count = 0
            for entry in time_sorted:
                if (entry.timestamp - window_start).total_seconds() <= 60:
                    count += 1
                else:
                    window_start = entry.timestamp
                    count = 1
                if count >= 80:
                    results.append(
                        Anomaly(
                            ip=ip,
                            type="spike",
                            timestamp=entry.timestamp,
                            severity="MEDIUM",
                            details={"peak_rps": count, "baseline": "fail2ban"},
                        )
                    )
                    break
        return results

    def _score(self, expected: Dict[str, Any], anomalies: List[Anomaly]) -> Dict[str, Any]:
        truth_types = set(expected["expected_types"])
        detected_types = set(anomaly.type for anomaly in anomalies if anomaly.ip == expected["ip"])
        tp = len(truth_types & detected_types)
        fp = len(detected_types - truth_types)
        fn = len(truth_types - detected_types)
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, tp + fn)
        f1 = 2 * precision * recall / max(1e-6, precision + recall)
        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
        }

    def _summarize(self, model_results: List[Dict[str, Any]], baseline_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        def average(metrics_list):
            precision = sum(item["metrics"]["precision"] for item in metrics_list) / max(1, len(metrics_list))
            recall = sum(item["metrics"]["recall"] for item in metrics_list) / max(1, len(metrics_list))
            f1 = sum(item["metrics"]["f1_score"] for item in metrics_list) / max(1, len(metrics_list))
            return {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1, 3),
            }

        model_avg = average(model_results)
        baseline_avg = average(baseline_results)
        return {
            "model_average": model_avg,
            "baseline_average": baseline_avg,
            "improvement": {
                "precision": round(model_avg["precision"] - baseline_avg["precision"], 3),
                "recall": round(model_avg["recall"] - baseline_avg["recall"], 3),
                "f1_score": round(model_avg["f1_score"] - baseline_avg["f1_score"], 3),
            },
        }
