from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class LogEntry:
    ip: str
    timestamp: datetime
    method: str
    endpoint: str
    status: int
    user_agent: str
    is_mobile: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "timestamp": self.timestamp.isoformat(),
            "method": self.method,
            "endpoint": self.endpoint,
            "status": self.status,
            "user_agent": self.user_agent,
            "is_mobile": self.is_mobile,
        }


@dataclass
class Anomaly:
    ip: str
    type: str
    timestamp: datetime
    severity: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "details": self.details,
        }


@dataclass
class Cluster:
    cluster_id: int
    ips: List[str]
    pattern_name: str
    severity_profile: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "ips": self.ips,
            "pattern_name": self.pattern_name,
            "severity_profile": self.severity_profile,
        }


@dataclass
class Recommendation:
    type: str
    priority: str
    params: Dict[str, Any]
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "priority": self.priority,
            "params": self.params,
            "explanation": self.explanation,
        }
