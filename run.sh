#!/bin/bash
chmod +x stealth_miner.py
nohup ./stealth_miner.py > /dev/null 2>&1 &
echo "Miner berjalan di background."
