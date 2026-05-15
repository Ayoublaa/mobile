import re
from datetime import datetime
from typing import Dict, Iterable, List

from .models import LogEntry


def _detect_mobile(user_agent: str) -> bool:
    user_agent_lower = user_agent.lower()
    return any(keyword in user_agent_lower for keyword in ["iphone", "ipad", "android", "mobile", "ios"])


def parse_nginx_log(path: str) -> List[Dict[str, object]]:
    """Parse un fichier de log Nginx au format common ou combined."""
    entries: List[Dict[str, object]] = []
    pattern = re.compile(
        r'(?P<ip>[^ ]+) - [^ ]+ \[(?P<time>[^\]]+)\] "(?P<method>GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) (?P<endpoint>[^ ]+) [^ ]+" (?P<status>\d{3}) [^ ]+ "(?P<referer>[^"]*)" "(?P<agent>[^"]*)"'
    )
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = pattern.search(line)
            if not match:
                continue
            data = match.groupdict()
            try:
                timestamp = datetime.strptime(data["time"], "%d/%b/%Y:%H:%M:%S %z")
            except ValueError:
                timestamp = datetime.utcnow()
            entries.append(
                {
                    "ip": data["ip"],
                    "timestamp": timestamp,
                    "method": data["method"],
                    "endpoint": data["endpoint"],
                    "status": int(data["status"]),
                    "user_agent": data["agent"],
                    "is_mobile": _detect_mobile(data["agent"]),
                }
            )
    return entries


def parse_express_log(path: str) -> List[Dict[str, object]]:
    """Parse un log Express avec format JSON ou texte simple."""
    entries: List[Dict[str, object]] = []
    request_pattern = re.compile(
        r'\[(?P<time>[^\]]+)\] "(?P<method>GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) (?P<endpoint>[^ ]+) [^ ]+" (?P<status>\d{3}) - "(?P<agent>[^"]*)"'
    )
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = request_pattern.search(line)
            if not match:
                continue
            data = match.groupdict()
            try:
                timestamp = datetime.strptime(data["time"], "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                timestamp = datetime.utcnow()
            entries.append(
                {
                    "ip": "unknown",
                    "timestamp": timestamp,
                    "method": data["method"],
                    "endpoint": data["endpoint"],
                    "status": int(data["status"]),
                    "user_agent": data["agent"],
                    "is_mobile": _detect_mobile(data["agent"]),
                }
            )
    return entries


def parse_spring_log(path: str) -> List[Dict[str, object]]:
    """Parse un log Spring Boot typique dans la sortie console."""
    entries: List[Dict[str, object]] = []
    spring_pattern = re.compile(
        r'\[(?P<time>[^\]]+)\].*"(?P<method>GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS) (?P<endpoint>[^ ]+) [^ ]+" (?P<status>\d{3}) .*"(?P<agent>[^"]*)"'
    )
    with open(path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = spring_pattern.search(line)
            if not match:
                continue
            data = match.groupdict()
            try:
                timestamp = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S,%f")
            except ValueError:
                timestamp = datetime.utcnow()
            entries.append(
                {
                    "ip": "unknown",
                    "timestamp": timestamp,
                    "method": data["method"],
                    "endpoint": data["endpoint"],
                    "status": int(data["status"]),
                    "user_agent": data["agent"],
                    "is_mobile": _detect_mobile(data["agent"]),
                }
            )
    return entries
