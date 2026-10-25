"""CleanYourTV for Windows: a small bilingual console menu over the repo's own tools.

It only calls tools/tv.py, tools/disable.ps1 and tools/restore.ps1 as they are, from the folder the
installer put them in. The embedded Python those scripts expect sits at tools/venv/Scripts/python.exe.
"""
import configparser
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
if not (ROOT / "tools").is_dir():  # running from packaging/windows in a checkout
    ROOT = ROOT.parent.parent
PY = ROOT / "tools" / "venv" / "Scripts" / "python.exe"
EXAMPLES = ROOT / "examples"
STATE = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CleanYourTV" / "state.json"
# Same as tv.py: an old console code page cannot print every character (→), so replace instead of stopping.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
POWERSHELL = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"

TEXT = {
    "ms": {
        "title": "CleanYourTV: buang bloatware Android TV melalui Wi-Fi",
        "ip_ask": "Masukkan alamat IP TV (cth. 192.168.1.50): ",
        "ip_bad": "Alamat IP itu tidak sah. Cuba lagi.",
        "ip_where": "Alamat IP TV boleh didapati di Tetapan (Settings) → Rangkaian & Internet (Network & Internet) → nama Wi-Fi anda.",
        "menu": "\nTV: {ip}\n  1  Semak sambungan TV\n  2  Buang bloatware (disable)\n  3  Pulihkan TV seperti asal (restore)\n  4  Tukar alamat IP TV\n  5  English\n  0  Keluar\nPilihan: ",
        "allow": "Jika TV memaparkan \"Benarkan penyahpepijatan USB?\" (Allow USB debugging?), tandakan \"Sentiasa benarkan daripada komputer ini\" dan pilih \"Benarkan\" menggunakan alat kawalan jauh.",
        "probe_fail": "Tidak dapat menyambung ke TV. Pastikan TV dihidupkan, disambungkan ke rangkaian Wi-Fi yang sama, dan Network debugging atau USB debugging dihidupkan.",
        "probe_ok": "Bersambung: {model} ({maker}), Android {ver}.",
        "match": "\nSenarai yang sepadan dengan TV anda:",
        "no_match": "\nTiada senarai yang sepadan dengan model ini. Pilih jenama TV anda:",
        "browse": "  B  Lihat semua jenama",
        "brands": "\nJenama TV:",
        "models": "\nModel {brand}:",
        "pick": "Nombor senarai (Enter untuk batal): ",
        "summary": "\nSenarai: {name}\n{tv}\n{n} pakej akan dimatikan (disable). Tiada apa-apa yang di-uninstall, dan semuanya boleh dipulihkan melalui menu 3.",
        "confirm": "Teruskan? (y/n): ",
        "restore_last": "Pulihkan menggunakan senarai terakhir, {name}? (y/n): ",
        "restore_pick": "Pilih senarai yang anda gunakan semasa membuang bloatware.",
        "done": "\nSelesai. Semak hasil di atas.",
        "failed": "\nBerlaku ralat (kod {code}). Baca mesej di atas. Tiada perubahan lanjut dibuat.",
        "missing": "Fail program tidak lengkap: {path}. Pasang semula CleanYourTV.",
        "enter": "\nTekan Enter untuk kembali ke menu...",
        "yes": "y",
    },
    "en": {
        "title": "CleanYourTV: remove Android TV bloatware over Wi-Fi",
        "ip_ask": "Enter the TV's IP address (e.g. 192.168.1.50): ",
        "ip_bad": "That IP address is not valid. Try again.",
        "ip_where": "The TV's IP address is under Settings → Network & Internet → your Wi-Fi name.",
        "menu": "\nTV: {ip}\n  1  Check the TV connection\n  2  Remove bloatware (disable)\n  3  Put the TV back as it was (restore)\n  4  Change the TV's IP address\n  5  Bahasa Melayu\n  0  Exit\nChoice: ",
        "allow": "If the TV shows \"Allow USB debugging?\", tick \"Always allow from this computer\" and choose \"Allow\" with the remote.",
        "probe_fail": "Could not connect to the TV. Make sure it is on, on the same Wi-Fi, and has Network debugging or USB debugging turned on.",
        "probe_ok": "Connected: {model} ({maker}), Android {ver}.",
        "match": "\nLists that match your TV:",
        "no_match": "\nNo list matches this model. Choose your TV brand:",
        "browse": "  B  Browse all brands",
        "brands": "\nTV brands:",
        "models": "\n{brand} models:",
        "pick": "List number (Enter to cancel): ",
        "summary": "\nList: {name}\n{tv}\n{n} packages will be disabled. Nothing is uninstalled, and menu 3 puts everything back.",
        "confirm": "Continue? (y/n): ",
        "restore_last": "Restore with the last list used, {name}? (y/n): ",
        "restore_pick": "Choose the list you used to remove bloatware.",
        "done": "\nDone. Check the results above.",
        "failed": "\nSomething went wrong (code {code}). Read the messages above. Nothing more was changed.",
        "missing": "Program files are incomplete: {path}. Reinstall CleanYourTV.",
        "enter": "\nPress Enter to return to the menu...",
        "yes": "y",
    },
}
lang = "ms"


def t(key, **kw):
    return TEXT[lang][key].format(**kw)


def load_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(state):
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass


def installer_language():
    ini = configparser.ConfigParser()
    ini.read(ROOT / "cleanyourtv.ini", encoding="utf-8")
    return ini.get("Settings", "Lang", fallback="ms")


def ask_ip():
    print(t("ip_where"))
    while True:
        ip = input(t("ip_ask")).strip()
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}(:\d{1,5})?", ip):
            return ip
        print(t("ip_bad"))


def run(cmd, ip, capture=False):
    env = dict(os.environ, TV_HOST=ip)
    if capture:
        p = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        print(p.stdout, end="")
        return p.returncode, p.stdout
    return subprocess.call(cmd, env=env), ""


def probe(ip):
    print(t("allow"))
    code, out = run([str(PY), "-I", str(ROOT / "tools" / "tv.py"), "--probe"], ip, capture=True)
    if code != 0:
        print(t("probe_fail"))
        return None
    props = dict(line.split(" = ", 1) for line in out.splitlines() if " = " in line)
    print(t("probe_ok", model=props.get("ro.product.model", "?"), maker=props.get("ro.product.manufacturer", "?"),
            ver=props.get("ro.build.version.release", "?")))
    return props


def examples():
    items = []
    for folder in sorted(EXAMPLES.iterdir()):
        if not (folder / "debloat.txt").is_file():
            continue
        try:
            info = json.loads((folder / "tv.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            info = {}
        items.append({"name": folder.name, "tv": info.get("tv", folder.name), "brand": info.get("brand", "?")})
    return items


def matches(items, props):
    words = {props.get(k, "").strip().lower() for k in ("ro.product.model", "ro.product.device")}
    words = {w for w in words if len(w) >= 3}
    found = []
    for item in items:
        head = (EXAMPLES / item["name"] / "debloat.txt").read_text(encoding="utf-8", errors="replace")[:600]
        hay = (item["tv"] + " " + head).lower()
        if any(re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", hay) for w in words):
            found.append(item)
    return found


def choose(options, label):
    for i, item in enumerate(options, 1):
        print(f"  {i:>3}  {label(item)}")
    pick = input(t("pick")).strip()
    if pick.isdigit() and 1 <= int(pick) <= len(options):
        return options[int(pick) - 1]
    return pick.upper() if pick.upper() == "B" else None


def pick_list(props):
    items = examples()
    found = matches(items, props) if props else []
    if found:
        print(t("match"))
        print(t("browse"))
        item = choose(found, lambda i: f"{i['tv']}  [{i['name']}]")
        if item != "B":
            return item
    elif props:
        print(t("no_match"))
    brands = sorted({i["brand"] for i in items}, key=str.lower)
    print(t("brands"))
    brand = choose(brands, str)
    if not brand or brand == "B":
        return None
    print(t("models", brand=brand))
    item = choose([i for i in items if i["brand"] == brand], lambda i: f"{i['tv']}  [{i['name']}]")
    return item if item != "B" else None


def list_path(item):
    return EXAMPLES / item["name"] / "debloat.txt"


def count_packages(path):
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return sum(1 for line in lines if line.split("#", 1)[0].strip())


def ps1(script, ip, path):
    return run([str(POWERSHELL), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                str(ROOT / "tools" / script), "-TvHost", ip, str(path)], ip)[0]


def report(code):
    print(t("done") if code == 0 else t("failed", code=code))


def debloat(ip, state):
    props = probe(ip)
    if props is None:
        return
    item = pick_list(props)
    if not item:
        return
    path = list_path(item)
    print(t("summary", name=item["name"], tv=item["tv"], n=count_packages(path)))
    if input(t("confirm")).strip().lower() != t("yes"):
        return
    code = ps1("disable.ps1", ip, path)
    # Remember the list for this TV only once disable.ps1 wrote its recovery record (tools/recovery.py
    # record_path), so a rejected list never replaces the one that still needs restoring.
    tag = re.sub(r"[^A-Za-z0-9.-]", "_", ip)
    digest = hashlib.sha1(str(path.resolve()).encode()).hexdigest()[:8]
    if (Path.home() / ".cleanyourtv" / f"recovery-{tag}-{digest}.json").is_file():
        state.setdefault("lists", {})[ip] = item["name"]
        save_state(state)
    report(code)


def restore(ip, state):
    item = None
    last = state.get("lists", {}).get(ip)
    if last and (EXAMPLES / last / "debloat.txt").is_file():
        if input(t("restore_last", name=last)).strip().lower() == t("yes"):
            item = {"name": last}
    if not item:
        print(t("restore_pick"))
        item = pick_list(None)
        if not item:
            return
    report(ps1("restore.ps1", ip, list_path(item)))


def main():
    global lang
    lang = installer_language() if installer_language() in TEXT else "ms"
    os.system("title CleanYourTV")
    for need in (PY, ROOT / "tools" / "tv.py", EXAMPLES):
        if not need.exists():
            print(t("missing", path=need))
            input(t("enter"))
            return 1
    state = load_state()
    print(t("title"))
    ip = state.get("ip") or ask_ip()
    state["ip"] = ip
    save_state(state)
    while True:
        choice = input(t("menu", ip=ip)).strip()
        if choice == "0":
            return 0
        if choice == "1":
            probe(ip)
        elif choice == "2":
            debloat(ip, state)
        elif choice == "3":
            restore(ip, state)
        elif choice == "4":
            ip = state["ip"] = ask_ip()
            save_state(state)
            continue
        elif choice == "5":
            lang = "en" if lang == "ms" else "ms"
            continue
        else:
            continue
        input(t("enter"))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
