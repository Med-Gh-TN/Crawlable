#!/bin/bash

# @file Start_Crawlable.sh
# @description Native launcher for Linux and macOS.

# 1. Guarantee execution happens in the project root
cd "$(dirname "$0")"

# 2. Provide instant visceral feedback
if command -v notify-send &> /dev/null; then
    notify-send "🦅 Crawlable AI" "Booting SOTA Engine. Web Dashboard opening shortly..." -t 3000
fi

# 3. Launch Python in the background, but save errors to a log file instead of deleting them!
nohup python main.py --headless > boot_diagnostics.log 2>&1 &