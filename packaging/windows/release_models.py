"""Writes the "Semak model TV anda" section of the Windows release notes (BM) from examples/*/tv.json.

Usage: python packaging/windows/release_models.py [out.md]   (stdout when no file is given)
Paste the output before "### Gambar" in the release notes, then: gh release edit <tag> --notes-file <notes>.
Box, stick and projector groups are guessed from words in the "tv" cell.
"""
import json, glob, re, sys, pathlib
repo = pathlib.Path(__file__).resolve().parents[2]
rows = [json.load(open(f, encoding="utf-8")) for f in glob.glob(str(repo / "examples/*/tv.json"))]
cell = lambda s: s.replace("|", "\|").strip()
def os_cell(d):
    o = cell(d.get("readme_os") or d["os"])
    return o + " 🔥" if "fire os" in o.lower() else o
def kind(d):
    t = d["tv"]
    if re.search(r"dongle", t, re.I): return "box"
    if re.search(r"projector", t, re.I): return "proj"
    if re.search(r"\bstick\b|\bbox\b|chromecast|streamer|streaming|shield|stream tv|stream 4k|freebox player", t + " " + d["brand"], re.I): return "box"
    return "tv"
key = lambda d: d["tv"].lower()
def details(title, items, brand_col):
    head = "| Jenama | Model | Sistem |\n|---|---|---|\n" if brand_col else "| Model | Sistem |\n|---|---|\n"
    body = "".join((f"| {cell(d['brand'])} " if brand_col else "") + f"| {cell(d['tv'])} | {os_cell(d)} |\n" for d in sorted(items, key=key))
    return f"<details>\n<summary><b>{title}</b> ({len(items)})</summary>\n\n{head}{body}\n</details>\n"
box = [d for d in rows if kind(d) == "box"]; proj = [d for d in rows if kind(d) == "proj"]; tv = [d for d in rows if kind(d) == "tv"]
brands = {}
for d in tv: brands.setdefault(d["brand"], []).append(d)
big = sorted((b for b in brands if len(brands[b]) >= 2), key=lambda b: (-len(brands[b]), b.lower()))
small = [d for b in brands if len(brands[b]) < 2 for d in brands[b]]
nb = len({d["brand"] for d in rows})
s = f"""### 📺 Semak model TV anda sebelum muat turun
Senarai buang bloatware sudah diuji untuk **{len(rows)} model daripada {nb} jenama**. Klik nama jenama untuk membuka senarainya, atau tekan **Ctrl+F** dan taip nama model anda (contohnya `SWTV`, `Mi Box`, `55C`).

- **Di mana nama model?** Pada TV: Tetapan → Sistem (atau Pilihan Peranti) → Perihal → Model. Ia juga ada pada pelekat di belakang TV atau box.
- **Model anda tiada?** Senarai untuk jenama atau platform yang sama selalunya sesuai. Semua perubahan boleh dikembalikan dengan "Pulihkan TV".
- 🔥 **Fire TV / Fire OS:** buang bloatware sahaja. Fire OS tidak membenarkan launcher lain menjadi Home.
- **Chromecast, Google TV Streamer dan sesetengah box Google TV:** port 5555 mungkin hanya terbuka selepas *Wireless debugging* dipasangkan (pair) sekali menggunakan adb biasa.

{details("📦 Android TV box & stick", box, True)}
{details("📽️ Projektor", proj, True)}
**📺 TV mengikut jenama**

""" + "\n".join(details(b, brands[b], False) for b in big) + "\n" + details("Jenama lain", small, True)
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(s, encoding="utf-8")
else:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(s)
