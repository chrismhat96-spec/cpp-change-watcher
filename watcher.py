import hashlib, json, os, re, urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

SOURCES = {
    "MSVC what's new": "https://learn.microsoft.com/en-us/cpp/overview/what-s-new-for-msvc?view=msvc-170",
    "MSVC language conformance": "https://learn.microsoft.com/en-us/cpp/overview/visual-cpp-language-conformance?view=msvc-170",
    "MSVC conformance and behavior changes": "https://learn.microsoft.com/en-us/cpp/overview/msvc-conformance-improvements?view=msvc-170",
    "MSVC compiler versions": "https://learn.microsoft.com/en-us/cpp/overview/compiler-versions?view=msvc-170",
    "Visual Studio release notes": "https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-notes",
    "C++ standards committee papers": "https://www.open-std.org/jtc1/sc22/wg21/docs/papers/",
}
STATE = Path("state.json")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cpp-change-watcher/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", "replace")
    raw = re.sub(r"<script[\\s\\S]*?</script>|<style[\\s\\S]*?</style>", " ", raw, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\\s+", " ", unescape(text)).strip()

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def send(changes):
    key = os.environ["RESEND_API_KEY"]
    to = os.environ.get("EMAIL_TO", "chrismhat96@gmail.com")
    lines = ["C++ sources changed since the previous check.", ""]
    for name, url in changes:
        lines += [name, url, ""]
    lines += [
        "Checked: " + datetime.now(timezone.utc).isoformat(),
        "This watcher covers C++ standardization plus the MSVC compiler/toolchain you use on Windows.",
        "A documentation edit is not automatically a language or compiler behavior change.",
    ]
    payload = json.dumps({
        "from": "C++ Change Watcher <onboarding@resend.dev>",
        "to": [to],
        "subject": "C++ watcher: changes detected",
        "text": "\n".join(lines),
    }).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "cpp-change-watcher/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        print("Resend:", r.read().decode("utf-8", "replace"))

old = json.loads(STATE.read_text()) if STATE.exists() else {}
new, changes = {}, []

for name, url in SOURCES.items():
    try:
        h = digest(fetch(url))
        new[name] = {"url": url, "sha256": h}
        if name in old and old[name].get("sha256") != h:
            changes.append((name, url))
    except Exception as e:
        print(f"ERROR {name}: {e}")
        if name in old:
            new[name] = old[name]

first_run = not bool(old)
STATE.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n")

if changes and not first_run:
    send(changes)
    print("Email sent for:", ", ".join(x[0] for x in changes))
elif first_run:
    print("Baseline saved. No email on first run.")
else:
    print("No changes.")
