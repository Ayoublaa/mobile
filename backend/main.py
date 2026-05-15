import logging
import os
import re
import smtplib
import sqlite3
from collections import defaultdict
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, List, Optional, Set

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .advanced_analytics import BehavioralProfiler, IsolationForestDetector
from .benchmark import BenchmarkEngine
from .detector import AuthAnalyzer, EndpointEnumerator, SpikeDetector
from .models import Anomaly, Cluster, LogEntry, Recommendation
from .recommender import RecommendationEngine
from .clustering import AbuseClusterer
from .parser import parse_express_log, parse_nginx_log, parse_spring_log


# Logging structuré pour la production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("mobile_api_misuse_detector")

app = FastAPI(title="Mobile API Misuse Detector")

storage: Dict[str, List[dict]] = {
    "logs": [],
    "detections": [],
    "clusters": [],
    "recommendations": [],
}
connected_clients: Set[WebSocket] = set()

DATABASE_PATH = "misuse_detector.db"

EMAIL_ALERTS_ENABLED = True

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO").split(",") if os.getenv("EMAIL_TO") else []

EMAIL_ALERT_THRESHOLD = 1

def _send_email_alert(subject: str, body: str) -> bool:
    logger.info("Tentative d'envoi d'alerte email: %s", subject)
    if not EMAIL_ALERTS_ENABLED or not EMAIL_TO:
        logger.info("Alertes email désactivées ou pas de destinataire")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)
    msg.set_content(body)

    try:
        if SMTP_PORT == 465:
            smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
            smtp.ehlo()
            if SMTP_USERNAME and SMTP_PASSWORD:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        else:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            smtp.ehlo()
            if SMTP_USERNAME and SMTP_PASSWORD:
                smtp.starttls()
                smtp.ehlo()
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

        with smtp:
            smtp.send_message(msg)
        logger.info("Email alert envoyé à %s", EMAIL_TO)
        _log_alert(subject, "Sent", ", ".join(EMAIL_TO))
        return True
    except Exception as exc:
        logger.error("Échec de l'envoi de l'alerte email : %s", exc)
        _log_alert(subject, "Failed", ", ".join(EMAIL_TO))
        return False


def _alert_on_anomalies(logs: List[LogEntry], anomalies: List[Anomaly]) -> Optional[Dict[str, str]]:
    is_active = _get_setting("security_active", "true") == "true"
    threshold = int(_get_setting("email_alert_threshold", "1"))

    if not EMAIL_ALERTS_ENABLED or not is_active or len(anomalies) < threshold:
        return None

    top_ips = defaultdict(int)
    top_types = defaultdict(int)
    for anomaly in anomalies:
        top_ips[anomaly.ip] += 1
        top_types[anomaly.type] += 1

    subject = f"Alerte Mobile API Misuse: {len(anomalies)} anomalies détectées"
    body_lines = [
        f"Nombre total de logs analysés : {len(logs)}",
        f"Anomalies détectées : {len(anomalies)}",
        "",
        "Top IPs :",
    ]
    for ip, count in sorted(top_ips.items(), key=lambda item: item[1], reverse=True)[:5]:
        body_lines.append(f"- {ip}: {count}")

    body_lines.append("")
    body_lines.append("Top types d'anomalies :")
    for anomaly_type, count in sorted(top_types.items(), key=lambda item: item[1], reverse=True)[:5]:
        body_lines.append(f"- {anomaly_type}: {count}")

    body_lines.append("")
    body_lines.append("Paramètres de seuils :")
    body_lines.append(f"- Seuil d'alerte : {threshold} anomalies")

    success = _send_email_alert(subject, "\n".join(body_lines))
    if success:
        return {"stage": "alert", "message": f"Email d'alerte envoyé à {', '.join(EMAIL_TO)}."}
    return {"stage": "alert-failed", "message": "Échec de l'envoi de l'alerte email."}


async def _handle_background_alerts(logs: List[LogEntry], anomalies: List[Anomaly]):
    alert_event = _alert_on_anomalies(logs, anomalies)
    if alert_event:
        await _broadcast_update(alert_event)


def _init_db() -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            timestamp TEXT,
            method TEXT,
            endpoint TEXT,
            status INTEGER,
            user_agent TEXT,
            is_mobile INTEGER
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            status TEXT,
            recipient TEXT,
            timestamp TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    # Default settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('email_alert_threshold', '1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('security_active', 'true')")
    conn.commit()
    conn.close()


def _get_setting(key: str, default: str) -> str:
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default


def _set_setting(key: str, value: str) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


def _log_alert(subject: str, status: str, recipient: str) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alerts (subject, status, recipient, timestamp) VALUES (?, ?, ?, ?)",
        (subject, status, recipient, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def _save_logs(log_entries: List[LogEntry]) -> None:
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO logs (ip, timestamp, method, endpoint, status, user_agent, is_mobile) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (
                entry.ip,
                entry.timestamp.isoformat(),
                entry.method,
                entry.endpoint,
                entry.status,
                entry.user_agent,
                int(entry.is_mobile),
            )
            for entry in log_entries
        ],
    )
    conn.commit()
    conn.close()


class DetectionQuery(BaseModel):
    ip: Optional[str] = None
    type: Optional[str] = None
    severity: Optional[str] = None
    page: int = 1
    size: int = 50


def _parse_log_file(uploaded_file: UploadFile) -> List[LogEntry]:
    content = uploaded_file.file.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()
    if not lines:
        raise ValueError("Le fichier est vide ou le format n'est pas supporté.")

    file_path = Path("uploaded.log")
    with file_path.open("w", encoding="utf-8", errors="ignore") as temp_fd:
        temp_fd.write(content)

    parsers = [parse_nginx_log, parse_express_log, parse_spring_log]
    raw_rows: List[dict] = []
    for parser in parsers:
        try:
            raw_rows = parser(str(file_path))
            if raw_rows:
                break
        except Exception:
            continue

    if not raw_rows:
        raise ValueError("Aucun parser n'a pu interpréter le fichier de log fourni.")

    log_entries: List[LogEntry] = []
    for row in raw_rows:
        try:
            log_entries.append(
                LogEntry(
                    ip=row["ip"],
                    timestamp=row["timestamp"],
                    method=row["method"],
                    endpoint=row["endpoint"],
                    status=int(row["status"]),
                    user_agent=row["user_agent"],
                    is_mobile=bool(row["is_mobile"]),
                )
            )
        except Exception as exc:
            logger.warning("Ignorer une ligne mal formée: %s", exc)
    return log_entries


def _build_stats(logs: List[LogEntry], anomalies: List[Anomaly]) -> Dict[str, object]:
    total_logs = len(logs)
    unique_ips = len({log.ip for log in logs})
    total_anomalies = len(anomalies)
    abuse_rate = round((total_anomalies / max(1, total_logs)) * 100, 2)
    top_ips = [
        {"ip": ip, "count": count}
        for ip, count in sorted(
            ((ip, sum(1 for log in logs if log.ip == ip)) for ip in {log.ip for log in logs}),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
    ]
    endpoint_counts = defaultdict(int)
    status_counts = defaultdict(int)
    status_group_counts = defaultdict(int)
    endpoint_status = defaultdict(lambda: defaultdict(int))
    mobile_count = 0
    for log in logs:
        endpoint = log.endpoint.split("?")[0]
        endpoint_counts[endpoint] += 1
        status_counts[str(log.status)] += 1
        status_group = f"{log.status // 100}xx"
        status_group_counts[status_group] += 1
        endpoint_status[endpoint][status_group] += 1
        mobile_count += int(log.is_mobile)

    attack_timeline = defaultdict(int)
    for anomaly in anomalies:
        key = anomaly.timestamp.strftime("%Y-%m-%dT%H:00:00")
        attack_timeline[key] += 1

    top_endpoints = [
        {"endpoint": endpoint, "count": count}
        for endpoint, count in sorted(endpoint_counts.items(), key=lambda item: item[1], reverse=True)[:8]
    ]
    status_groups = ["2xx", "3xx", "4xx", "5xx"]
    heatmap_rows = [
        {
            "endpoint": item["endpoint"],
            "values": [endpoint_status[item["endpoint"]].get(group, 0) for group in status_groups],
        }
        for item in top_endpoints
    ]
    error_rate = round(((status_group_counts.get("4xx", 0) + status_group_counts.get("5xx", 0)) / max(1, total_logs)) * 100, 2)
    auth_401_rate = round((status_counts.get("401", 0) / max(1, total_logs)) * 100, 2)

    return {
        "total_logs_processed": total_logs,
        "abuse_rate": abuse_rate,
        "top_ips": top_ips,
        "attack_timeline": [{"timestamp": k, "count": v} for k, v in sorted(attack_timeline.items())],
        "unique_ips": unique_ips,
        "top_endpoints": top_endpoints,
        "status_distribution": [{"status": status, "count": count} for status, count in sorted(status_counts.items())],
        "mobile_ratio": round((mobile_count / max(1, total_logs)) * 100, 2),
        "heatmap": {"groups": status_groups, "rows": heatmap_rows},
        "risk_profile": [
            {"label": "Anomalies", "value": min(100, total_anomalies * 3)},
            {"label": "Usage mobile", "value": round((mobile_count / max(1, total_logs)) * 100, 2)},
            {"label": "Taux d'erreur", "value": error_rate},
            {"label": "401 authentifications", "value": auth_401_rate},
            {"label": "Endpoints ciblés", "value": min(100, len(top_endpoints) * 12)},
        ],
    }


def _filter_detections(query: DetectionQuery) -> List[Dict[str, object]]:
    detections = storage["detections"]
    if query.ip:
        detections = [d for d in detections if d["ip"] == query.ip]
    if query.type:
        detections = [d for d in detections if d["type"] == query.type]
    if query.severity:
        detections = [d for d in detections if d["severity"] == query.severity]
    start = (query.page - 1) * query.size
    end = start + query.size
    return detections[start:end]


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    raise ValueError("Horodatage de log invalide")


def _parse_log_entry(raw: Dict[str, object]) -> LogEntry:
    return LogEntry(
        ip=str(raw["ip"]),
        timestamp=_parse_timestamp(raw["timestamp"]),
        method=str(raw["method"]),
        endpoint=str(raw["endpoint"]),
        status=int(raw["status"]),
        user_agent=str(raw["user_agent"]),
        is_mobile=bool(raw["is_mobile"]),
    )


def _parse_anomaly(raw: Dict[str, object]) -> Anomaly:
    return Anomaly(
        ip=str(raw["ip"]),
        type=str(raw["type"]),
        timestamp=_parse_timestamp(raw["timestamp"]),
        severity=str(raw["severity"]),
        details=dict(raw.get("details", {})),
    )


def _build_cluster_details(logs: List[LogEntry], clusters: List[Cluster]) -> List[Dict[str, object]]:
    ip_stats = {}
    for log in logs:
        entry = ip_stats.setdefault(log.ip, {"count": 0, "endpoints": set(), "status_401": 0, "mobile": 0, "first_seen": log.timestamp})
        entry["count"] += 1
        entry["endpoints"].add(log.endpoint.split("?")[0])
        entry["status_401"] += int(log.status == 401)
        entry["mobile"] += int(log.is_mobile)
        entry["first_seen"] = min(entry["first_seen"], log.timestamp)

    details: List[Dict[str, object]] = []
    for cluster in clusters:
        metrics = [ip_stats[ip] for ip in cluster.ips if ip in ip_stats]
        if not metrics:
            continue
        average_req = round(sum(item["count"] for item in metrics) / max(1, len(metrics)), 2)
        average_endpoints = round(sum(len(item["endpoints"]) for item in metrics) / max(1, len(metrics)), 2)
        average_401 = round(sum(item["status_401"] for item in metrics) / max(1, len(metrics)), 2)
        avg_mobile = round(sum(item["mobile"] for item in metrics) / max(1, len(metrics)), 2)
        details.append(
            {
                "cluster_id": cluster.cluster_id,
                "pattern_name": cluster.pattern_name,
                "severity_profile": cluster.severity_profile,
                "ips": cluster.ips,
                "avg_requests": average_req,
                "avg_endpoints": average_endpoints,
                "avg_401_errors": average_401,
                "avg_mobile_hits": avg_mobile,
            }
        )
    return details


@app.on_event("startup")
def startup_event() -> None:
    _init_db()
    logger.info("Backend démarré et base SQLite initialisée.")


@app.post("/upload-log")
async def upload_log(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> JSONResponse:
    try:
        log_entries = _parse_log_file(file)
    except ValueError as exc:
        logger.error("Erreur parsing : %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    if not log_entries:
        raise HTTPException(status_code=422, detail="Aucune entrée de log valide trouvée.")

    await _broadcast_update({"stage": "parsed", "message": f"{len(log_entries)} entrées de log importées."})

    spike_detector = SpikeDetector()
    auth_analyzer = AuthAnalyzer()
    enumerator = EndpointEnumerator()
    isolation_detector = IsolationForestDetector()

    anomalies = spike_detector.detect(log_entries)
    anomalies.extend(auth_analyzer.detect(log_entries))
    anomalies.extend(enumerator.detect(log_entries))
    anomalies.extend(isolation_detector.detect(log_entries))

    await _broadcast_update({"stage": "detected", "message": f"{len(anomalies)} anomalies détectées."})
    logger.info("Déclenchement de la vérification des alertes (Background)")
    background_tasks.add_task(_handle_background_alerts, log_entries, anomalies)
    
    logger.info("Début du clustering")
    clusterer = AbuseClusterer()
    clusters = clusterer.cluster(log_entries, anomalies)

    recommender = RecommendationEngine()
    recommendations = []
    for cluster in clusters:
        recs = recommender.recommend(cluster)
        recommendations.extend(recs)

    storage["logs"].extend([entry.to_dict() for entry in log_entries])
    storage["detections"].extend([anomaly.to_dict() for anomaly in anomalies])
    storage["clusters"] = [cluster.to_dict() for cluster in clusters]
    storage["recommendations"] = [rec.to_dict() for rec in recommendations]

    _save_logs(log_entries)

    stats = _build_stats(log_entries, anomalies)
    result = {
        "detections": storage["detections"],
        "clusters": storage["clusters"],
        "recommendations": storage["recommendations"],
        "stats": stats,
        "behavioral_profiles": BehavioralProfiler().profile(log_entries, [cluster.to_dict() for cluster in clusters]),
    }
    logger.info("Fichier log traité : %s entrées, %s anomalies détectées", len(log_entries), len(anomalies))
    await _broadcast_update({"stage": "completed", "message": "Traitement des logs terminé."})
    logger.info("Fin du traitement upload_log")
    return JSONResponse(status_code=200, content=result)


@app.get("/detections")
async def get_detections(
    ip: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
) -> JSONResponse:
    query = DetectionQuery(ip=ip, type=type, severity=severity, page=page, size=size)
    data = _filter_detections(query)
    return JSONResponse(content={"detections": data, "page": page, "size": size})


@app.get("/clusters")
async def get_clusters() -> JSONResponse:
    clusters = storage["clusters"]
    total_ips = len({log["ip"] for log in storage["logs"]})
    abuse_rate = round((len(storage["detections"]) / max(1, len(storage["logs"]))) * 100, 2)
    summary = {"total_ips": total_ips, "abuse_rate": abuse_rate}
    return JSONResponse(content={"clusters": clusters, "summary": summary})


@app.get("/recommendations")
async def get_recommendations() -> JSONResponse:
    recs = storage["recommendations"]
    by_cluster: Dict[int, List[Dict[str, object]]] = defaultdict(list)
    recommender = RecommendationEngine()
    for cluster in storage["clusters"]:
        cluster_recs = recommender.recommend(Cluster(**cluster))
        by_cluster[cluster["cluster_id"]] = [rec.to_dict() for rec in cluster_recs]
    return JSONResponse(content={"recommendations": recs, "by_cluster": by_cluster})


@app.get("/stats")
async def get_stats() -> JSONResponse:
    log_objects = [_parse_log_entry(log) for log in storage["logs"]]
    anomaly_objects = [_parse_anomaly(det) for det in storage["detections"]]
    stats = _build_stats(log_objects, anomaly_objects)
    cluster_objects = [Cluster(**cluster) for cluster in storage["clusters"]]
    return JSONResponse(
        content={
            "stats": stats,
            "clusters": _build_cluster_details(log_objects, cluster_objects),
            "recommendations": storage["recommendations"],
            "detections": storage["detections"],
        }
    )


@app.get("/benchmark")
async def get_benchmark() -> JSONResponse:
    benchmark = BenchmarkEngine().run()
    return JSONResponse(content=benchmark)


@app.post("/alert/test-email")
async def test_email_alert() -> JSONResponse:
    if not EMAIL_ALERTS_ENABLED:
        raise HTTPException(status_code=400, detail="Les alertes email sont désactivées. Activez EMAIL_ALERTS_ENABLED=true.")
    if not EMAIL_TO:
        raise HTTPException(status_code=400, detail="Aucune adresse email de destination configurée dans EMAIL_TO.")

    success = _send_email_alert(
        "Test d'alerte Mobile API Misuse Detector",
        "Ceci est un test d'alerte email pour le Mobile API Misuse Detector. Si vous recevez ce message, la configuration SMTP fonctionne.",
    )
    if success:
        await _broadcast_update({"stage": "alert", "message": "Test d'alerte email envoyé."})
        return JSONResponse(content={"detail": "Email de test envoyé."})

    await _broadcast_update({"stage": "alert-failed", "message": "Échec de l'envoi du test d'alerte email."})
    raise HTTPException(status_code=500, detail="Impossible d'envoyer l'email de test.")


@app.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket) -> None:
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.discard(websocket)


@app.get("/alerts/history")
async def get_alerts_history() -> JSONResponse:
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject, status, recipient, timestamp FROM alerts ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        history = [
            {"id": r[0], "subject": r[1], "status": r[2], "recipient": r[3], "timestamp": r[4]}
            for r in rows
        ]
        return JSONResponse(content={"history": history})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class SettingsUpdate(BaseModel):
    email_alert_threshold: Optional[int] = None
    security_active: Optional[bool] = None


@app.get("/settings")
async def get_settings() -> JSONResponse:
    return JSONResponse(
        content={
            "email_alert_threshold": int(_get_setting("email_alert_threshold", "1")),
            "security_active": _get_setting("security_active", "true") == "true",
        }
    )


@app.post("/settings")
async def update_settings(update: SettingsUpdate) -> JSONResponse:
    if update.email_alert_threshold is not None:
        _set_setting("email_alert_threshold", str(update.email_alert_threshold))
    if update.security_active is not None:
        _set_setting("security_active", "true" if update.security_active else "false")
    
    return JSONResponse(content={"status": "updated"})


async def _broadcast_update(message: Dict[str, object]) -> None:
    disconnected = []
    for client in connected_clients:
        try:
            await client.send_json(message)
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        connected_clients.discard(client)
