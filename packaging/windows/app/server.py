"""Local web UI over the unchanged CleanYourTV scripts (stdlib only)."""
import configparser
import hashlib
import hmac
import ipaddress
import json
import mimetypes
import os
import re
import secrets
import socket
import subprocess
import sys
import threading
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[3]
WEB = ROOT / "web" if getattr(sys, "frozen", False) else Path(__file__).resolve().parent / "web"
PY = ROOT / "tools" / "venv" / "Scripts" / "python.exe"
APK = ROOT / "launcher" / ("tvhome.apk" if getattr(sys, "frozen", False) else "app/build/outputs/apk/release/app-release.apk")
URL_FILE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CleanYourTV" / "url.txt"
STATE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CleanYourTV" / "state.json"
POWERSHELL = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"


def load_state():
    try:
        value = json.loads(STATE.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state), encoding="utf-8")


def installer_language():
    ini = configparser.ConfigParser()
    ini.read(ROOT / "cleanyourtv.ini", encoding="utf-8")
    value = ini.get("Settings", "Lang", fallback="ms")
    return value if value in ("ms", "en") else "ms"


def examples():
    items = []
    for folder in sorted((ROOT / "examples").iterdir()):
        path = folder / "debloat.txt"
        if not path.is_file():
            continue
        try:
            info = json.loads((folder / "tv.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            info = {}
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        packages, comments = [], []
        for line in text.splitlines():
            package, _, comment = line.partition("#")
            if package.strip():
                packages.append({"package": package.strip(), "comment": "\n".join(comments + ([comment.strip()] if comment else []))})
                comments = []
            elif line.strip().startswith("#"):
                comments.append(comment.strip())
            else:
                comments = []
        items.append({"name": folder.name, "tv": info.get("tv", folder.name), "brand": info.get("brand", "?"),
                      "header": text[:600], "packages": packages})
    return items


def matches(item, props):
    words = {props.get(k, "").strip().lower() for k in ("ro.product.model", "ro.product.device")}
    hay = (item["tv"] + " " + item["header"]).lower()
    return any(len(w) >= 3 and re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", hay) for w in words)


def tv_ip(value):
    address = ipaddress.IPv4Address(value)
    if address.is_loopback or address.is_unspecified or address.is_multicast or str(address) == "255.255.255.255":
        raise ValueError("IP")
    return str(address)


def port_open(ip):
    try:
        with socket.create_connection((ip, 5555), timeout=0.5):
            return True
    except OSError:
        return False


def discover():
    command = "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.AddressState -eq 'Preferred' } | ForEach-Object { '{0}/{1}' -f $_.IPAddress, $_.PrefixLength }"
    result = subprocess.run([str(POWERSHELL), "-NoProfile", "-Command", command], capture_output=True, text=True, timeout=15)
    own, networks = set(), set()
    for line in result.stdout.splitlines():
        try:
            interface = ipaddress.IPv4Interface(line.strip())
            tv_ip(str(interface.ip))
        except ValueError:
            continue
        if interface.ip.is_private:
            own.add(str(interface.ip))
            # The adapter's own subnet, but never more than the /24 around this PC.
            networks.add(interface.network if interface.network.prefixlen >= 24 else interface.ip.exploded + "/24")
    targets = sorted({str(ip) for network in networks for ip in ipaddress.IPv4Network(network, strict=False).hosts()} - own)
    with ThreadPoolExecutor(max_workers=64) as pool:
        return [{"ip": ip, "port": 5555} for ip, opened in zip(targets, pool.map(port_open, targets)) if opened]


def summary(output):
    # Count script output, never infer success from the selected list or the exit code.
    lines = output.splitlines()
    return {"disabled": sum(bool(re.search(r"new state:\s*disabled", line)) for line in lines),
            "enabled": sum(bool(re.search(r"new state:\s*enabled", line)) for line in lines),
            "skipped": len(set(re.findall(r"Skipping\s+([\w.]+):", output))),
            "absent": sum(bool(re.search(r"not installed|unknown package|does not exist", line, re.I)) for line in lines)}


class App:
    def __init__(self):
        self.token = secrets.token_urlsafe(32)
        self.state = load_state()
        self.items = examples()
        self.props = {}
        self.connected = None
        self.jobs = {}
        self.lock = threading.Lock()
        self.process = None
        self.closing = False
        self.server = None

    def start(self, operation, body):
        if not self.lock.acquire(blocking=False):
            raise ValueError("BUSY")
        try:
            if self.closing:
                raise ValueError("BUSY")
            ip = tv_ip(body.get("ip", "")) if operation != "discover" else None
            item = None
            if operation in ("disable", "restore", "launcher") and ip != self.connected:
                raise ValueError("CONNECT_FIRST")
            if operation in ("disable", "restore"):
                item = next((entry for entry in self.items if entry["name"] == body.get("list")), None)
                if item is None:
                    raise ValueError("LIST")
            if operation == "launcher" and body.get("homeKey") and "xiaomi" not in (self.props.get("ro.product.manufacturer", "") + self.props.get("ro.product.brand", "")).lower():
                raise ValueError("INPUT")
            job = {"id": secrets.token_hex(16), "operation": operation, "ip": ip, "list": item["name"] if item else None,
                   "restore": body.get("restore") is True or operation == "restore", "output": "", "done": False}
            self.jobs.clear()
            self.jobs[job["id"]] = job
            threading.Thread(target=self.work, args=(job, ip, item, body), daemon=True).start()
            return {"jobId": job["id"]}
        except Exception:
            self.lock.release()
            raise

    def run(self, command, ip, job, timeout=None):
        env = dict(os.environ, TV_HOST=ip, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1")
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace")
        self.process = process
        timer = threading.Timer(timeout, process.kill) if timeout else None
        if timer:
            timer.start()
        try:
            for line in process.stdout:
                job["output"] += line
            return process.wait()
        finally:
            if timer:
                timer.cancel()
            process.stdout.close()
            self.process = None

    def work(self, job, ip, item, body):
        operation = job["operation"]
        try:
            if operation == "discover":
                job["candidates"] = discover()
                job["code"] = 0
                return
            if operation == "connect":
                self.connected = None
                self.props = {}
                if not port_open(ip):
                    job.update(code=1, error="PORT_CLOSED")
                    return
                job["code"] = self.run([str(PY), "-I", str(ROOT / "tools/tv.py"), "--probe"], ip, job, timeout=120)
                if job["code"] != 0:
                    job["error"] = "PROBE"
                    return
                self.props = dict(line.split(" = ", 1) for line in job["output"].splitlines() if " = " in line)
                if not self.props.get("ro.product.model"):
                    job.update(code=1, error="PROBE")
                    return
                self.connected = ip
                self.state["ip"] = ip
                save_state(self.state)
                job["device"] = {key: self.props.get(key, "?") for key in ("ro.product.model", "ro.product.manufacturer", "ro.product.brand", "ro.build.version.release")}
                job["matched"] = [entry["name"] for entry in self.items if matches(entry, self.props)]
                job["lastList"] = self.state.get("lists", {}).get(ip)
                return
            command = [str(POWERSHELL), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
            if operation == "launcher":
                command += [str(ROOT / "launcher/build-and-install.ps1"), "-TvHost", ip, "-Apk", str(APK)]
                if body.get("keepHome") is True:
                    command += ["-StockLauncher", "none"]
                if body.get("homeKey") is True:
                    command += ["-HomeKeyService"]
            else:
                path = ROOT / "examples" / item["name"] / "debloat.txt"
                command += [str(ROOT / "tools" / (operation + ".ps1")), "-TvHost", ip, str(path)]
            job["code"] = self.run(command, ip, job)
            if operation == "disable":
                tag = re.sub(r"[^A-Za-z0-9.-]", "_", ip)
                digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
                if (Path.home() / ".cleanyourtv" / f"recovery-{tag}-{digest}.json").is_file():
                    self.state.setdefault("lists", {})[ip] = item["name"]
                    save_state(self.state)
            job["summary"] = summary(job["output"])
            job["unknownHome"] = operation == "launcher" and job["code"] != 0 and bool(re.search(
                r"which\s+is\s+not\s+a\s+stock\s+launcher\s+this\s+script\s+knows", job["output"]))
        except (OSError, ValueError, subprocess.SubprocessError):
            job.update(code=1, error="SCRIPT")
        finally:
            job["done"] = True
            self.lock.release()

    def close(self):
        self.closing = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
        if self.server:
            self.server.shutdown()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def send(self, status, value, content_type="application/json; charset=utf-8"):
        data = json.dumps(value).encode() if isinstance(value, (dict, list)) else value
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Security-Policy", "default-src 'self'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def allowed(self):
        port = self.server.server_port
        hosts = (f"127.0.0.1:{port}", f"localhost:{port}")
        return self.headers.get("Host") in hosts and self.headers.get("Origin") in (None, *("http://" + host for host in hosts))

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {"error": "FORBIDDEN"})
        app = self.server.app
        path = urlsplit(self.path).path
        if path == "/api/state":
            return self.send(200, {"language": installer_language(), "ip": app.state.get("ip", ""), "lists": app.items,
                                   "device": {key: app.props.get(key, "?") for key in ("ro.product.model", "ro.product.manufacturer", "ro.product.brand", "ro.build.version.release")},
                                   "job": next((dict(job) for job in app.jobs.values()
                                                if not job["done"] or job["operation"] in ("disable", "restore", "launcher")), None)})
        if path.startswith("/api/jobs/"):
            job = app.jobs.get(path.rsplit("/", 1)[-1])
            return self.send(200, dict(job)) if job else self.send(404, {"error": "JOB"})
        file = (WEB / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
        if not file.is_relative_to(WEB.resolve()) or not file.is_file():
            return self.send(404, {"error": "NOT_FOUND"})
        data = file.read_bytes()
        if file.name == "index.html":
            data = data.replace(b"{{CLEANYOURTV_TOKEN}}", app.token.encode())
        content_type = "text/javascript" if file.suffix == ".js" else mimetypes.guess_type(str(file))[0] or "application/octet-stream"
        self.send(200, data, content_type)

    def do_POST(self):
        app = self.server.app
        if not self.allowed() or not hmac.compare_digest(self.headers.get("x-cleanyourtv-token", "").encode(), app.token.encode()) or self.headers.get_content_type() != "application/json":
            return self.send(403, {"error": "FORBIDDEN"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 <= size <= 65536:
                raise ValueError("INPUT")
            body = json.loads(self.rfile.read(size) or b"{}")
            if not isinstance(body, dict):
                raise ValueError("INPUT")
            operation = urlsplit(self.path).path.removeprefix("/api/")
            if operation == "exit":
                if app.lock.locked():
                    raise ValueError("BUSY")
                self.send(200, {"closed": True})
                threading.Thread(target=app.close, daemon=True).start()
            elif operation in ("discover", "connect", "disable", "restore", "launcher"):
                self.send(202, app.start(operation, body))
            else:
                self.send(404, {"error": "NOT_FOUND"})
        except (ValueError, TypeError):
            self.send(400, {"error": "INPUT"})


def make_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.app = App()
    server.app.server = server
    return server


def single_instance():
    """One CleanYourTV at a time, so two copies can never run scripts against the same TV at once."""
    import ctypes
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, "Local\CleanYourTV")
    return handle if handle and kernel32.GetLastError() != 183 else None  # ERROR_ALREADY_EXISTS


def main():
    mutex = single_instance()
    if mutex is None:
        # Already running: show that window's page instead of starting a second server.
        try:
            webbrowser.open(URL_FILE.read_text(encoding="utf-8").strip())
        except OSError:
            pass
        return
    server = make_server()
    url = f"http://127.0.0.1:{server.server_port}/"
    print("CleanYourTV: " + url, flush=True)
    URL_FILE.parent.mkdir(parents=True, exist_ok=True)
    URL_FILE.write_text(url, encoding="utf-8")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.app.closing = True
        if server.app.process:
            server.app.process.terminate()
        server.server_close()


if __name__ == "__main__":
    main()
