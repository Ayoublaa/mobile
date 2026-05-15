from datetime import datetime, timedelta
from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_logs"
SAMPLE_DIR.mkdir(exist_ok=True)


def _format_nginx_line(ip: str, ts: datetime, method: str, endpoint: str, status: int, ua: str) -> str:
    return f'{ip} - - [{ts.strftime("%d/%b/%Y:%H:%M:%S +0000")} ] "{method} {endpoint} HTTP/1.1" {status} 123 "-" "{ua}"\n'


def _format_express_line(ts: datetime, method: str, endpoint: str, status: int, ua: str) -> str:
    return f'[{ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}] "{method} {endpoint} HTTP/1.1" {status} - "{ua}"\n'


def _format_spring_line(ts: datetime, method: str, endpoint: str, status: int, ua: str) -> str:
    return f'[{ts.strftime("%Y-%m-%d %H:%M:%S,%f")}] INFO 12345 --- [nio-8080-exec-1] org.springframework.web.servlet.DispatcherServlet : "{method} {endpoint} HTTP/1.1" {status} 456 "{ua}"\n'


def generate_sample_logs() -> None:
    now = datetime.utcnow()
    nginx_path = SAMPLE_DIR / "nginx_sample.log"
    express_path = SAMPLE_DIR / "express_sample.log"
    spring_path = SAMPLE_DIR / "spring_sample.log"

    with nginx_path.open("w", encoding="utf-8") as nginx_file:
        burst_ip = "192.168.0.10"
        for i in range(110):
            t = now + timedelta(seconds=i % 60)
            nginx_file.write(_format_nginx_line(burst_ip, t, "GET", "/api/data", 200, "Mozilla/5.0 (Linux; Android 12) Mobile"))
        brute_ip = "203.0.113.51"
        for i in range(18):
            t = now + timedelta(seconds=5 * i)
            nginx_file.write(_format_nginx_line(brute_ip, t, "POST", "/login", 401, "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) Mobile"))
        normal_ip = "198.51.100.22"
        for i in range(8):
            t = now + timedelta(minutes=i)
            nginx_file.write(_format_nginx_line(normal_ip, t, "GET", "/api/user/profile", 200, "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X)"))

    with express_path.open("w", encoding="utf-8") as express_file:
        scan_ip = "10.0.0.99"
        for i in range(32):
            t = now + timedelta(seconds=9 * i)
            express_file.write(_format_express_line(t, "GET", f"/api/v1/resource/{i}", 200, "curl/7.64.1"))
        express_file.write(_format_express_line(now, "GET", "/api/status", 200, "Mozilla/5.0 (Android; Mobile)"))

    with spring_path.open("w", encoding="utf-8") as spring_file:
        spring_file.write(_format_spring_line(now, "POST", "/auth", 401, "Mozilla/5.0 (Android; Mobile)"))
        for i in range(5):
            t = now + timedelta(seconds=i * 12)
            spring_file.write(_format_spring_line(t, "GET", f"/api/offer/{i}", 200, "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)") )

    print(f"Échantillons générés dans {SAMPLE_DIR}")


if __name__ == "__main__":
    generate_sample_logs()
