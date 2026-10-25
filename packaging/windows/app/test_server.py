"""Offline checks: no test connects to ADB or invokes a TV script."""
import hashlib
import http.client
import json
import tempfile
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import server


class WebTests(unittest.TestCase):
    def setUp(self):
        build = Path(__file__).resolve().parents[1] / "build"
        build.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=build)
        self.state_patch = patch.object(server, "STATE", Path(self.temp.name) / "state.json")
        self.state_patch.start()
        self.httpd = server.make_server()
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.app = self.httpd.app

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
        self.state_patch.stop()
        self.temp.cleanup()

    def request(self, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        values = {"Content-Type": "application/json", "x-cleanyourtv-token": self.app.token}
        values.update(headers or {})
        connection.request("GET" if body is None else "POST", path, None if body is None else json.dumps(body), values)
        response = connection.getresponse()
        status, data = response.status, response.read()
        connection.close()
        return status, data

    def wait_job(self, operation, body):
        job_id = self.app.start(operation, body)["jobId"]
        for _ in range(100):
            job = self.app.jobs[job_id]
            if job["done"]:
                return job
            time.sleep(0.01)
        self.fail("job did not finish")

    def test_static_state_languages_and_security(self):
        status, page = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(self.app.token.encode(), page)
        self.assertNotIn(b"{{CLEANYOURTV_TOKEN}}", page)
        for path in ("/css/tokens.css", "/css/app.css", "/css/windows.css", "/fonts/PlusJakartaSans.woff2", "/js/app.js", "/js/screens/setup.js"):
            self.assertEqual(self.request(path)[0], 200, path)
        languages = [json.loads(self.request(f"/i18n/{code}.json")[1]) for code in ("ms", "en")]
        self.assertEqual(languages[0].keys(), languages[1].keys())
        state = json.loads(self.request("/api/state")[1])
        self.assertTrue(state["lists"])
        self.assertEqual(self.request("/../server.py")[0], 404)
        self.assertEqual(self.request("/", headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.request("/api/state", headers={"Origin": "https://evil.example"})[0], 403)
        for headers in ({"x-cleanyourtv-token": ""}, {"x-cleanyourtv-token": "wrong"}, {"x-cleanyourtv-token": "\xff"},
                        {"Origin": "https://evil.example"}, {"Content-Type": "text/plain"}, {"Host": "evil.example"}):
            self.assertEqual(self.request("/api/discover", {}, headers)[0], 403)
        with patch.object(server, "discover", return_value=[]):
            self.assertEqual(self.request("/api/discover", {})[0], 202)

    def test_probe_matching_and_restore_preselection(self):
        self.app.state = {"lists": {"192.0.2.50": "xiaomi-mi-tv-4a"}}
        def probe(command, ip, job, timeout=None):
            self.assertEqual(command[:2], [str(server.PY), "-I"])
            self.assertEqual(command[-1], "--probe")
            job["output"] = "ro.product.model = MiTV-AXSO1\nro.product.device = MiTV-AXSO1\nro.product.manufacturer = Xiaomi\nro.build.version.release = 9\n"
            return 0
        with patch.object(server, "port_open", return_value=True), patch.object(self.app, "run", side_effect=probe):
            job = self.wait_job("connect", {"ip": "192.0.2.50"})
        self.assertEqual(job["code"], 0)
        self.assertEqual(job["lastList"], "xiaomi-mi-tv-4a")
        self.assertEqual(self.app.connected, "192.0.2.50")
        self.assertTrue(server.matches({"tv": "MiTV-AXSO1", "header": ""}, self.app.props))
        self.assertFalse(server.matches({"tv": "MiTV-AXSO10", "header": ""}, self.app.props))

    def test_closed_port_and_connect_guard(self):
        with patch.object(server, "port_open", return_value=False), patch.object(self.app, "run") as run:
            job = self.wait_job("connect", {"ip": "192.0.2.50"})
            self.assertEqual(job["error"], "PORT_CLOSED")
            run.assert_not_called()
        with self.assertRaises(ValueError):
            self.app.start("disable", {"ip": "192.0.2.50", "list": self.app.items[0]["name"]})
        with self.assertRaises(ValueError):
            self.app.start("connect", {"ip": "127.0.0.1"})

    def test_script_commands_recovery_and_summary(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        self.app.state = {"lists": {ip: "previous"}}
        output = "Package com.example.one new state: disabled-user\nWARNING: Skipping com.example.two: protected\nUnknown package: com.example.three\n"
        def run(command, host, job):
            self.assertEqual(host, ip)
            self.assertIn("-ExecutionPolicy", command)
            job["output"] = output
            return 0
        with patch.object(self.app, "run", side_effect=run), patch.object(Path, "home", return_value=Path(self.temp.name)):
            job = self.wait_job("disable", {"ip": ip, "list": item["name"]})
            self.assertEqual(self.app.state["lists"][ip], "previous")
            path = server.ROOT / "examples" / item["name"] / "debloat.txt"
            digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
            recovery = Path(self.temp.name) / ".cleanyourtv" / f"recovery-{ip}-{digest}.json"
            recovery.parent.mkdir()
            recovery.write_text("{}")
            self.wait_job("disable", {"ip": ip, "list": item["name"]})
            self.assertEqual(self.app.state["lists"][ip], item["name"])
            self.wait_job("restore", {"ip": ip, "list": item["name"]})
        self.assertEqual(job["summary"], {"disabled": 1, "enabled": 0, "skipped": 1, "absent": 1})
        last = json.loads(self.request("/api/state")[1])["job"]
        self.assertTrue(last["done"])
        self.assertEqual(last["operation"], "restore")
        with self.assertRaises(ValueError):
            self.app.start("restore", {"ip": ip, "list": "../other"})

    def test_launcher_retry_is_explicit_and_apk_is_bundled(self):
        ip = self.app.connected = "192.0.2.50"
        self.app.props = {"ro.product.manufacturer": "Xiaomi"}
        calls = []
        def run(command, host, job):
            calls.append(command)
            job["output"] = "which is not a stock\nlauncher this script knows"
            return 1
        with patch.object(self.app, "run", side_effect=run):
            job = self.wait_job("launcher", {"ip": ip, "homeKey": True})
            self.assertTrue(job["unknownHome"])
            self.assertIn("-Apk", calls[0])
            self.assertIn(str(server.APK), calls[0])
            self.assertNotIn("-StockLauncher", calls[0])
            self.assertIn("-HomeKeyService", calls[0])
            self.wait_job("launcher", {"ip": ip, "keepHome": True})
            self.assertEqual(calls[1][-2:], ["-StockLauncher", "none"])

    def test_discovery_only_scans_local_24_without_own_address(self):
        with patch.object(server.subprocess, "run") as interfaces, patch.object(server, "port_open", return_value=False) as probe:
            interfaces.return_value.stdout = "192.0.2.20/24\n127.0.0.1/8\n192.0.2.20/24\n"
            self.assertEqual(server.discover(), [])
        targets = {call.args[0] for call in probe.call_args_list}
        self.assertEqual(len(targets), 253)
        self.assertNotIn("192.0.2.20", targets)
        self.assertNotIn("127.0.0.1", targets)

    def test_discovery_stays_inside_a_smaller_subnet(self):
        with patch.object(server.subprocess, "run") as interfaces, patch.object(server, "port_open", return_value=False) as probe:
            interfaces.return_value.stdout = "192.0.2.10/25\n"
            server.discover()
        targets = {call.args[0] for call in probe.call_args_list}
        self.assertEqual(len(targets), 125)
        self.assertNotIn("192.0.2.200", targets)

    def test_exit_stops_server(self):
        self.assertEqual(self.request("/api/exit", {})[0], 200)
        self.thread.join(timeout=3)
        self.assertFalse(self.thread.is_alive())

    def test_active_job_is_available_for_page_reload(self):
        entered, release = threading.Event(), threading.Event()
        def scan():
            entered.set()
            release.wait(timeout=3)
            return []
        with patch.object(server, "discover", side_effect=scan):
            job_id = self.app.start("discover", {})["jobId"]
            self.assertTrue(entered.wait(timeout=1))
            try:
                data = json.loads(self.request("/api/state")[1])
                self.assertEqual(data["job"]["id"], job_id)
                self.assertFalse(data["job"]["done"])
                self.assertEqual(self.request("/api/exit", {})[0], 400)
            finally:
                release.set()
            for _ in range(100):
                if self.app.jobs[job_id]["done"]:
                    break
                time.sleep(0.01)

    def test_output_arrives_before_the_local_process_finishes(self):
        job = {"output": ""}
        command = [sys.executable, "-u", "-c", "import time; print('first'); time.sleep(0.5); print('last')"]
        thread = threading.Thread(target=self.app.run, args=(command, "192.0.2.50", job))
        thread.start()
        for _ in range(100):
            if "first" in job["output"]:
                break
            time.sleep(0.01)
        self.assertIn("first", job["output"])
        self.assertTrue(thread.is_alive())
        thread.join(timeout=3)
        self.assertIn("last", job["output"])


if __name__ == "__main__":
    unittest.main()
