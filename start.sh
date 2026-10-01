#!/bin/bash

echo "🚀 OPPANDA POWER SYSTEM STARTING..."

# 1. Sabse pehle zaroori libraries install karega
echo "📦 Installing Python libraries..."
pip install flask telebot requests psutil --quiet

# 2. C Binary ko compile karega (High Power Mode)
echo "⚙️ Compiling drx.c binary..."
gcc OPPANDA.c -o OPPANDA -lpthread -O3
chmod +x OPPANDA

# 3. Purane sessions ko band karega agar koi chal raha ho
echo "🧹 Cleaning old sessions..."
pkill -f m.py

# 5. Telegram Bot ko background mein start karega
echo "🤖 Starting Telegram Bot..."
nohup python3 m.py > bot_logs.txt 2>&1 &

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ SYSTEM IS NOW LIVE!"
echo "📡 API Status: Running"
echo "🤖 Bot Status: Running"
echo "📝 Logs saved in: api_logs.txt and bot_logs.txt"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
