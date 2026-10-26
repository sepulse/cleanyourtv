"""Offline checks: no test connects to ADB or invokes a TV script."""
import hashlib
import http.client
import io
import json
import shutil
import subprocess
import tempfile
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import server

RESTORE_OUTPUT = "$ pm enable com.example.app\nPackage com.example.app new state: enabled\n$ pm list packages -d\n"


class WebTests(unittest.TestCase):
    def setUp(self):
        build = Path(__file__).resolve().parents[1] / "build"
        build.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=build)
        self.state_patch = patch.object(server, "STATE", Path(self.temp.name) / "localappdata/CleanYourTV/state.json")
        self.state_patch.start()
        self.history_patch = patch.object(server, "HISTORY", Path(self.temp.name) / ".cleanyourtv/windows/state.json", create=True)
        self.history_patch.start()
        self.httpd = server.make_server()
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.app = self.httpd.app

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
        self.state_patch.stop()
        self.history_patch.stop()
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
        self.app.state = {}
        output = "Package com.example.one new state: disabled-user\nWARNING: Skipping com.example.two: protected\nUnknown package: com.example.three\n"
        def run(command, host, job):
            self.assertEqual(host, ip)
            self.assertIn("-ExecutionPolicy", command)
            job["output"] = output
            return 0
        with patch.object(self.app, "run", side_effect=run), patch.object(Path, "home", return_value=Path(self.temp.name)):
            job = self.wait_job("disable", {"ip": ip, "list": item["name"]})
            self.assertNotIn(ip, self.app.state.get("lists", {}))
            path = server.ROOT / "examples" / item["name"] / "debloat.txt"
            digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
            recovery = Path(self.temp.name) / ".cleanyourtv" / f"recovery-{ip}-{digest}.json"
            recovery.parent.mkdir(exist_ok=True)
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

    def test_adb_closed_codes_command_and_reload(self):
        ip = "192.0.2.50"
        self.assertIsNone(self.app.connected)  # Checking after a restart needs no ADB connection.
        for code in (0, 1, 2):
            with self.subTest(code=code), patch.dict(server.os.environ, TV_PORT="5556"), patch.object(self.app, "run", return_value=code) as run:
                job = self.wait_job("adb-closed", {"ip": ip})
                run.assert_called_once_with([str(server.PY), "-I", str(server.ROOT / "tools/adb-closed.py"), ip, "5555"], ip, job)
                self.assertEqual(job["code"], code)
                self.assertNotIn("error", job)
                self.assertEqual(json.loads(self.request("/api/state")[1])["job"]["id"], job["id"])
        with patch.object(self.app, "run", side_effect=OSError):
            self.assertEqual(self.wait_job("adb-closed", {"ip": ip})["code"], 2)

    def test_adb_closed_endpoint_validation_and_job_lock(self):
        with patch.object(self.app, "run") as run:
            for ip in ("", "127.0.0.1", "0.0.0.0", "224.0.0.1", "255.255.255.255", "192.0.2.50:5555", "192.0.2.50;whoami"):
                self.assertEqual(self.request("/api/adb-closed", {"ip": ip})[0], 400, ip)
            self.app.lock.acquire()
            try:
                self.assertEqual(self.request("/api/adb-closed", {"ip": "192.0.2.50"})[0], 400)
            finally:
                self.app.lock.release()
            run.assert_not_called()
        finished = threading.Event()
        def run(command, ip, job):
            finished.set()
            return 0
        with patch.object(self.app, "run", side_effect=run):
            self.assertEqual(self.request("/api/adb-closed", {"ip": "192.0.2.50"})[0], 202)
            self.assertTrue(finished.wait(timeout=1))

    def test_family_checklist_uses_names_and_comments_of_active_packages(self):
        folder = Path(self.temp.name) / "examples" / "sample"
        folder.mkdir(parents=True)
        (folder / "debloat.txt").write_text(
            "# Streaming apps\ncom.netflix.ninja\ncom.google.android.youtube.tv\ncom.spotify.tv.android\n"
            "com.cbs.ott\ncom.espn.gtv\n\ncom.hulu.plus\ncom.peacock.peacockfiretv\ncom.tubitv.ott\n"
            "com.google.android.katniss\ncom.google.android.apps.mediashell\ncom.vendor.wfd\ncom.vendor.ota\n"
            "com.homwee.multiscreenshare\ncom.homwee.mmp.screenshare\n"
            "com.creative.fastscreen.tv # Miracast receiver\n"
            "# Firmware updater\ncom.vendor.firmware\n\n"
            "# com.disney.disneyplus # left enabled\n\ncom.amazon.device.metrics\ncom.vendor.telemetry\n", encoding="utf-8")
        with patch.object(server, "ROOT", Path(self.temp.name)):
            packages = server.examples()[0]["packages"]
        self.assertTrue(all(entry["family"] for entry in packages[:-2]))
        self.assertTrue(all(not entry["family"] for entry in packages[-2:]))
        self.assertNotIn("com.disney.disneyplus", [entry["package"] for entry in packages])

    def test_filtered_list_and_restore_share_exact_recovery_identity(self):
        ip = self.app.connected = "192.0.2.50"
        item = next(entry for entry in self.app.items if entry["name"] == "xiaomi-mi-tv-4a")
        keep = ["com.xiaomi.mitv.updateservice", "com.xiaomi.amazon.alexa"]
        calls = []
        def run(command, host, job):
            path = Path(command[-1])
            calls.append(path)
            self.assertEqual(host, job["ip"])
            self.assertEqual(command[-3:-1], ["-TvHost", host])
            if job["operation"] == "disable":
                self.assertIn(str(server.ROOT / "tools/disable.ps1"), command)
                self.assertEqual(path.read_text(encoding="utf-8").splitlines(),
                                 [entry["package"] for entry in item["packages"] if entry["package"] not in keep])
                digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
                recovery = Path(self.temp.name) / ".cleanyourtv" / f"recovery-{ip}-{digest}.json"
                recovery.parent.mkdir(exist_ok=True)
                recovery.write_text("{}")
            else:
                self.assertIn(str(server.ROOT / "tools/restore.ps1"), command)
                job["output"] = RESTORE_OUTPUT
            return 0
        with patch.object(self.app, "run", side_effect=run), patch.object(Path, "home", return_value=Path(self.temp.name)):
            self.assertEqual(self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": keep})["code"], 0)
            applied = calls[0]
            self.assertEqual(applied.parent, server.HISTORY.parent / "lists" / ip)
            self.assertEqual(self.app.state["appliedLists"][ip], str(applied.resolve()))
            self.assertEqual(self.app.state["lists"][ip], item["name"])
            self.app.state = server.load_state()  # A later session must restore the same file.
            self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": list(reversed(keep))})
            self.assertEqual(calls[-1], applied)
            self.wait_job("restore", {"ip": ip, "list": item["name"]})
            self.assertEqual(calls[-1], applied)
            self.assertNotIn(ip, server.load_state()["appliedLists"])
            keep.pop()
            self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": keep})
            self.assertNotEqual(calls[-1], applied)  # Do not mix recovery records for different subsets.
            other = next(entry for entry in self.app.items if entry["name"] != item["name"])
            self.wait_job("restore", {"ip": ip, "list": other["name"]})
            self.assertEqual(calls[-1], server.ROOT / "examples" / other["name"] / "debloat.txt")
            self.app.connected = "192.0.2.51"
            self.wait_job("restore", {"ip": self.app.connected, "list": item["name"]})
            self.assertEqual(calls[-1], server.ROOT / "examples" / item["name"] / "debloat.txt")

    def test_plain_list_history_blocks_a_different_path_until_restore(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        path = server.ROOT / "examples" / item["name"] / "debloat.txt"
        server.save_state({"lists": {ip: item["name"]}})  # Legacy state has no appliedLists entry.
        self.app.state = server.load_state()
        digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
        recovery = Path(self.temp.name) / ".cleanyourtv" / f"recovery-{ip}-{digest}.json"
        recovery.parent.mkdir(exist_ok=True)
        recovery.write_text("{}")
        with patch.object(self.app, "run", side_effect=lambda command, host, job: job.update(output=RESTORE_OUTPUT) or 0) as run, patch.object(Path, "home", return_value=Path(self.temp.name)):
            job = self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": [item["packages"][0]["package"]]})
            self.assertEqual(job["error"], "RESTORE_FIRST")
            run.assert_not_called()
            for body in ({"ip": ip, "list": item["name"], "keep": []}, {"ip": ip, "list": item["name"]}):
                self.wait_job("disable", body)
                self.assertEqual(run.call_args.args[0][-1], str(path))
                self.assertNotIn(ip, self.app.state.get("appliedLists", {}))
            self.wait_job("restore", {"ip": ip, "list": item["name"]})
            self.assertEqual(run.call_args.args[0][-1], str(path))
            self.assertNotIn(ip, server.load_state()["lists"])
            self.assertEqual(self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": [item["packages"][0]["package"]]})["code"], 0)

    def test_filtered_history_survives_restart_and_failed_or_unrelated_restore(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        body = {"ip": ip, "list": item["name"], "keep": [item["packages"][0]["package"]]}
        def run(command, host, job):
            digest = hashlib.sha1(str(Path(command[-1]).resolve()).encode()).hexdigest()[:8]
            recovery = Path(self.temp.name) / ".cleanyourtv" / f"recovery-{host}-{digest}.json"
            recovery.parent.mkdir(exist_ok=True)
            recovery.write_text("{}")
            return 0
        with patch.object(self.app, "run", side_effect=run), patch.object(Path, "home", return_value=Path(self.temp.name)):
            self.assertEqual(self.wait_job("disable", body)["code"], 0)
        self.app = self.httpd.app = server.App()  # Reload saved state in a fresh app.
        self.app.connected = ip
        saved = server.load_state()
        applied = Path(saved["appliedLists"][ip])
        files = list(applied.parent.iterdir())
        other = next(entry for entry in self.app.items if entry["name"] != item["name"])
        with patch.object(self.app, "run", return_value=1) as run:
            self.wait_job("restore", {"ip": ip, "list": item["name"]})
            self.assertEqual(server.load_state(), saved)
            run.return_value = 0
            self.wait_job("restore", {"ip": ip, "list": other["name"]})
            self.assertEqual(server.load_state(), saved)
            run.reset_mock()
            for change in ({"keep": []}, {"keep": [item["packages"][1]["package"]]}, {"list": other["name"], "keep": []}):
                job = self.wait_job("disable", dict(body, **change))
                self.assertEqual(job["error"], "RESTORE_FIRST")
                self.assertTrue(job["done"])
                self.assertFalse(self.app.lock.locked())
            run.assert_not_called()
            self.assertEqual(server.load_state(), saved)
            self.assertEqual(list(applied.parent.iterdir()), files)
            run.side_effect = lambda command, host, job: job.update(output=RESTORE_OUTPUT) or 0
            self.wait_job("restore", {"ip": ip, "list": item["name"]})
            self.assertNotIn(ip, server.load_state()["appliedLists"])
            self.assertEqual(self.wait_job("disable", dict(body, keep=[]))["code"], 0)

    def test_filtered_recovery_survives_removing_localappdata(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        self.app.state["ip"] = ip
        def run(command, host, job):
            path = Path(command[-1])
            digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
            recovery = Path(self.temp.name) / ".cleanyourtv" / f"recovery-{host}-{digest}.json"
            if job["operation"] == "disable":
                recovery.parent.mkdir(exist_ok=True)
                recovery.write_text("{}")
            else:
                self.assertTrue(recovery.is_file())
                self.assertTrue(path.is_file())
                job["output"] = RESTORE_OUTPUT
            return 0
        with patch.object(self.app, "run", side_effect=run), patch.object(Path, "home", return_value=Path(self.temp.name)):
            self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": [item["packages"][0]["package"]]})
        applied = Path(self.app.state["appliedLists"][ip])
        self.assertEqual(json.loads(server.STATE.read_text()), {"ip": ip})
        history = json.loads(server.HISTORY.read_text())
        self.assertEqual(set(history), {"lists", "appliedLists"})
        shutil.rmtree(server.STATE.parent)
        self.app = self.httpd.app = server.App()
        self.app.connected = ip
        self.assertNotIn("ip", self.app.state)
        self.assertEqual(self.app.state["appliedLists"][ip], str(applied.resolve()))
        with patch.object(self.app, "run", side_effect=run) as runner:
            self.assertEqual(self.wait_job("restore", {"ip": ip, "list": item["name"]})["code"], 0)
            self.assertEqual(Path(runner.call_args.args[0][-1]), applied)
        self.assertNotIn(ip, server.load_state()["appliedLists"])

    def test_zero_exit_restore_keeps_history_on_errors_or_uncertain_output(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        applied = server.HISTORY.parent / "lists" / ip / "filtered.txt"
        saved = {"lists": {ip: item["name"]}, "appliedLists": {ip: str(applied)}}
        server.save_state(saved)
        self.app.state = server.load_state()
        for output in ("", "Success\n", RESTORE_OUTPUT + "Error: unable to enable package\n",
                       RESTORE_OUTPUT + "Failure [not allowed]\n", RESTORE_OUTPUT + "java.lang.SecurityException: denied\n",
                       RESTORE_OUTPUT + "Permission Denial: cannot change settings\n",
                       RESTORE_OUTPUT + "Unknown package: com.example.app\n", RESTORE_OUTPUT + "Failed to set home\n",
                       RESTORE_OUTPUT + "/system/bin/sh: settings: not found\n",
                       RESTORE_OUTPUT + "Skipping window_animation_scale: invalid value\n"):
            with self.subTest(output=output):
                def run(command, host, job):
                    job["output"] = output
                    return 0
                with patch.object(self.app, "run", side_effect=run) as runner:
                    self.wait_job("restore", {"ip": ip, "list": item["name"]})
                    self.assertEqual(server.load_state(), saved)
                    runner.reset_mock()
                    job = self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": []})
                    self.assertEqual(job["error"], "RESTORE_FIRST")
                    runner.assert_not_called()

    def test_kept_names_are_strictly_validated_before_a_job_starts(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        with patch.object(self.app, "run") as run:
            for keep in (None, "com.netflix.ninja", {}, [None], [{}], ["com.not.in.this.list"],
                         [item["packages"][0]["package"] + "\ncom.injected.app"], ["-ExecutionPolicy"], ["../list"]):
                with self.subTest(keep=keep):
                    self.assertEqual(self.request("/api/disable", {"ip": ip, "list": item["name"], "keep": keep})[0], 400)
                    self.assertFalse(self.app.lock.locked())
            run.assert_not_called()
        self.assertFalse((server.HISTORY.parent / "lists").exists())

    def test_unclassified_aqua_streaming_apps_can_be_kept(self):
        ip = self.app.connected = "192.0.2.50"
        item = next(entry for entry in self.app.items if entry["name"] == "aqua-matrixtv-ee-50")
        keep = ["com.apple.atve.androidtv.appletv", "id.visionplus.android.atv", "com.tencent.qqlivei18n"]
        with patch.object(self.app, "run", return_value=0) as run, patch.object(Path, "home", return_value=Path(self.temp.name)):
            self.assertEqual(self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": keep})["code"], 0)
        self.assertEqual(Path(run.call_args.args[0][-1]).read_text(encoding="utf-8").splitlines(),
                         [entry["package"] for entry in item["packages"] if entry["package"] not in keep])

    @unittest.skipUnless(shutil.which("node"), "Node is needed to check the checklist UI offline")
    def test_all_apps_checklist_is_collapsed_and_shares_keep_boxes(self):
        item = next(entry for entry in self.app.items if entry["name"] == "aqua-matrixtv-ee-50")
        script = """
const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync(process.argv[1], 'utf8').split('function confirmScreen() {')[1].split('function progressScreen()')[0];
const state = { list: JSON.parse(process.argv[2]), keep: [], showAll: false, restore: false };
state.keep = state.list.packages.filter(entry => entry.family).map(entry => entry.package);
const h = (tag, attributes = {}, ...children) => ({ tag, attributes, children: children.flat(Infinity).filter(Boolean) });
const confirm = new Function('state', 'h', 'heading', 'button', 't', 'render', 'actions',
  'return function() {' + source)(state, h, () => h('h1', {}),
    (label, action, attributes) => h('button', attributes, label), key => key, () => {}, {});
const nodes = tree => typeof tree === 'object' ? [tree, ...tree.children.flatMap(nodes)] : [];
const tree = confirm();
const all = nodes(tree);
const details = all.find(node => node.tag === 'details');
assert.equal(details.attributes.open, false);
assert.equal(details.children[0].children[0], 'confirm.allApps');
const boxes = all.filter(node => node.tag === 'input');
assert.equal(boxes.length, state.list.packages.length);
assert.deepEqual(boxes.map(box => box.attributes.id), [
  ...state.list.packages.filter(entry => entry.family), ...state.list.packages.filter(entry => !entry.family),
].map(entry => 'keep-' + entry.package));
assert.deepEqual(nodes(details).filter(node => node.tag === 'input').map(box => box.attributes.id),
  state.list.packages.filter(entry => !entry.family).map(entry => 'keep-' + entry.package));
details.attributes.ontoggle({ target: { open: true } });
for (const name of ['com.apple.atve.androidtv.appletv', 'id.visionplus.android.atv', 'com.tencent.qqlivei18n']) {
  const box = boxes.find(node => node.attributes.id === 'keep-' + name);
  box.attributes.onchange({ target: { checked: true } });
  assert(state.keep.includes(name));
  assert(nodes(confirm()).find(node => node.attributes.id === box.attributes.id).attributes.checked);
  box.attributes.onchange({ target: { checked: false } });
  assert(!state.keep.includes(name));
}
assert.equal(nodes(confirm()).find(node => node.tag === 'details').attributes.open, true);
state.keep = state.list.packages.map(entry => entry.package);
assert.equal(nodes(confirm()).find(node => node.attributes.id === 'confirm-run').attributes.disabled, true);
state.restore = true;
assert(!nodes(confirm()).some(node => node.tag === 'input' || node.tag === 'details'));
state.restore = false;
state.list.packages = state.list.packages.filter(entry => !entry.family);
assert.equal(nodes(confirm()).filter(node => node.tag === 'input').length, state.list.packages.length);
"""
        result = subprocess.run([shutil.which("node"), "-e", script, str(server.WEB / "js/app.js"), json.dumps(item)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_filtered_path_is_not_remembered_without_a_recovery_record(self):
        ip = self.app.connected = "192.0.2.50"
        item = self.app.items[0]
        self.app.state = {"lists": {"192.0.2.51": "previous"}, "appliedLists": {"192.0.2.51": "previous.txt"}}
        with patch.object(self.app, "run", return_value=1) as run, patch.object(Path, "home", return_value=Path(self.temp.name)):
            self.wait_job("disable", {"ip": ip, "list": item["name"], "keep": [item["packages"][0]["package"]]})
            run.assert_called_once()
        self.assertEqual(self.app.state, {"lists": {"192.0.2.51": "previous"}, "appliedLists": {"192.0.2.51": "previous.txt"}})

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

    def test_exit_stops_server_when_response_is_broken(self):
        handler = object.__new__(server.Handler)
        handler.server = self.httpd
        handler.path = "/api/exit"
        handler.rfile = io.BytesIO(b"{}")
        handler.headers = http.client.HTTPMessage()
        for key, value in {"Host": f"127.0.0.1:{self.httpd.server_port}", "Content-Type": "application/json",
                           "Content-Length": "2", "x-cleanyourtv-token": self.app.token}.items():
            handler.headers[key] = value
        with patch.object(handler, "send", side_effect=BrokenPipeError):
            with self.assertRaises(BrokenPipeError):
                handler.do_POST()
        self.thread.join(timeout=3)
        self.assertTrue(self.app.closing)
        self.assertFalse(self.app.lock.locked())
        self.assertFalse(self.thread.is_alive())

    def test_exit_reserves_shutdown_before_async_close(self):
        with patch.object(self.app, "close"), patch.object(server, "discover") as discover:
            self.assertEqual(self.request("/api/exit", {})[0], 200)
            self.assertTrue(self.app.closing)
            self.assertFalse(self.app.lock.locked())
            for operation, body in (("discover", {}), ("connect", {"ip": "192.0.2.50"}), ("adb-closed", {"ip": "192.0.2.50"})):
                self.assertEqual(self.request("/api/" + operation, body)[0], 400)
            discover.assert_not_called()
            self.assertFalse(self.app.jobs)

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
                self.assertFalse(self.app.closing)
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
