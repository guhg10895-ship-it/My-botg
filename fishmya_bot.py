#!/usr/bin/env python3
"""
FishMya Game - WebSocket Route Auto Scanner + Exploit Finder
Author: GHOST
Version: 11.0 - Auto Route Scanner
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

# ==================== SCANNER STATE ====================
scanner_state = {
    'scanning': False,
    'scan_results': [],
    'found_routes': {},
    'coin_routes': [],
    'repeatable_routes': [],
    'total_found': 0,
    'scan_complete': False
}

# ==================== ROUTES TO TEST ====================
# ဒီ route တွေကို auto test လုပ်မယ်
TEST_ROUTES = [
    # Claim routes
    {"route": "claimItemOnline", "data": {"package": 1}},
    {"route": "claimItemOnline", "data": {"package": 2}},
    {"route": "claimItemOnline", "data": {"package": 3}},
    {"route": "claimItemOnline", "data": {"package": 4}},
    {"route": "claimItemOnline", "data": {"package": 5}},
    {"route": "claimItemOnline", "data": {"package": 6}},
    {"route": "claimItemOnline", "data": {"package": 7}},
    {"route": "claimItemOnline", "data": {"package": 8}},
    {"route": "claimItemOnline", "data": {"package": 9}},
    {"route": "claimItemOnline", "data": {"package": 10}},
    
    # Daily rewards
    {"route": "claimDaily", "data": {}},
    {"route": "claimDailyReward", "data": {}},
    {"route": "dailyClaim", "data": {}},
    {"route": "claimLogin", "data": {}},
    {"route": "loginReward", "data": {}},
    {"route": "dailyBonus", "data": {}},
    {"route": "checkin", "data": {}},
    {"route": "dailyCheckin", "data": {}},
    
    # Gift routes
    {"route": "claimGift", "data": {}},
    {"route": "openGift", "data": {}},
    {"route": "receiveGift", "data": {}},
    {"route": "giftBox", "data": {}},
    {"route": "openBox", "data": {}},
    {"route": "claimBox", "data": {}},
    
    # Reward routes
    {"route": "claimReward", "data": {}},
    {"route": "getReward", "data": {}},
    {"route": "receiveReward", "data": {}},
    {"route": "claimBonus", "data": {}},
    {"route": "getBonus", "data": {}},
    {"route": "bonusReward", "data": {}},
    
    # Lucky wheel
    {"route": "spinLucky", "data": {}},
    {"route": "luckySpin", "data": {}},
    {"route": "spinWheel", "data": {}},
    {"route": "wheelSpin", "data": {}},
    
    # Item routes
    {"route": "claimItem", "data": {}},
    {"route": "useItem", "data": {"type": 1}},
    {"route": "useItem", "data": {"type": 2}},
    {"route": "useItem", "data": {"type": 3}},
    {"route": "useItem", "data": {"type": 4}},
    {"route": "useItem", "data": {"type": 5}},
    {"route": "useItem", "data": {"type": 6}},
    
    # Mission routes
    {"route": "claimMission", "data": {}},
    {"route": "missionReward", "data": {}},
    {"route": "completeMission", "data": {}},
    {"route": "taskReward", "data": {}},
    {"route": "claimTask", "data": {}},
    {"route": "questReward", "data": {}},
    
    # Level routes
    {"route": "levelReward", "data": {}},
    {"route": "levelUpReward", "data": {}},
    {"route": "claimLevel", "data": {}},
    
    # Event routes
    {"route": "eventReward", "data": {}},
    {"route": "claimEvent", "data": {}},
    {"route": "eventBonus", "data": {}},
    
    # Online rewards
    {"route": "onlineReward", "data": {}},
    {"route": "onlineBonus", "data": {}},
    {"route": "timeReward", "data": {}},
    {"route": "hourlyReward", "data": {}},
    
    # Fish routes
    {"route": "catchFish", "data": {}},
    {"route": "fishReward", "data": {}},
    {"route": "claimFish", "data": {}},
    
    # Exchange routes
    {"route": "exchange", "data": {}},
    {"route": "exchangeItem", "data": {}},
    {"route": "convert", "data": {}},
    
    # Other
    {"route": "getBalance", "data": {}},
    {"route": "refreshCash", "data": {}},
    {"route": "syncCash", "data": {}},
    {"route": "updateCash", "data": {}},
    {"route": "reloadCash", "data": {}},
]

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

# ==================== ROUTE SCANNER ====================
def extract_coin_from_message(decoded: Dict) -> int:
    """Extract coin amount from any WebSocket message"""
    if not decoded:
        return 0
    
    coin_keys = [
        'cash', 'coin', 'coins', 'gold', 'golds', 'reward', 'rewards',
        'amount', 'changeCash', 'newCash', 'balance', 'bonus', 'gift',
        'point', 'points', 'money', 'currency', 'diamond', 'diamonds',
        'gem', 'gems', 'totalCash', 'addCash', 'earnCash', 'winCash'
    ]
    
    def search(obj, depth=0):
        if depth > 10:
            return 0
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_lower = key.lower()
                if any(k in key_lower for k in coin_keys):
                    if isinstance(value, (int, float)) and value > 0:
                        return int(value)
                    elif isinstance(value, str) and value.isdigit() and int(value) > 0:
                        return int(value)
                result = search(value, depth + 1)
                if result > 0:
                    return result
        elif isinstance(obj, list):
            for item in obj:
                result = search(item, depth + 1)
                if result > 0:
                    return result
        return 0
    
    return search(decoded)

def scan_routes_sync(chat_id: str):
    """Scan all routes for coin rewards"""
    global scanner_state
    
    scanner_state['scanning'] = True
    scanner_state['scan_results'] = []
    scanner_state['found_routes'] = {}
    scanner_state['coin_routes'] = []
    scanner_state['repeatable_routes'] = []
    scanner_state['scan_complete'] = False
    
    logger.info(f"🔍 Starting route scan: {len(TEST_ROUTES)} routes to test")
    
    # Connect WebSocket
    try:
        ws = websocket.create_connection(
            WS_URL,
            sslopt={"cert_reqs": ssl.CERT_NONE},
            header=[f"{k}: {v}" for k, v in WS_HEADERS.items()],
            timeout=30
        )
        
        # Login
        login_payload = {
            "route": "mytelLogin",
            "data": {"accessToken": GAME_ACCESS_TOKEN, "language": "my"},
            "msgId": 1
        }
        ws.send(msgpack.packb(login_payload, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
        
        # Wait for login
        ws.settimeout(10)
        login_ok = False
        for _ in range(10):
            try:
                m = ws.recv()
                d = msgpack.unpackb(m, raw=False)
                if d.get("msgId") == 1 and d.get("data", {}).get("ok"):
                    login_ok = True
                    balance = d.get("data", {}).get("cash", 0)
                    logger.info(f"✅ Login OK! Balance: {balance:,}")
                    asyncio.run(send_telegram(chat_id, f"✅ *Login OK!*\n💰 Balance: {balance:,}\n\n🔍 Starting route scan..."))
                    break
            except:
                break
        
        if not login_ok:
            logger.error("❌ Login failed during scan")
            asyncio.run(send_telegram(chat_id, "❌ *Login Failed!*"))
            ws.close()
            scanner_state['scanning'] = False
            return
        
        # Enter room
        ws.send(msgpack.packb({"route": "play", "data": {"roomId": 1}, "msgId": 2}, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
        time.sleep(1)
        
        # Test each route
        msg_id = 1000
        
        for i, test_route in enumerate(TEST_ROUTES):
            route_name = test_route['route']
            route_data = test_route['data']
            
            # Send test route
            ws.send(msgpack.packb({
                "route": route_name,
                "data": route_data,
                "msgId": msg_id
            }, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
            
            # Wait for response
            ws.settimeout(1.0)
            coins_found = 0
            response_received = False
            
            try:
                while True:
                    m = ws.recv()
                    d = msgpack.unpackb(m, raw=False)
                    
                    # Check if response to our message
                    if d.get("msgId") == msg_id:
                        response_received = True
                        coins_found = extract_coin_from_message(d)
                        if coins_found > 0:
                            break
                    
                    # Check for cash updates
                    if d.get("route") == "reloadCash":
                        change = d.get("data", {}).get("changeCash", 0)
                        if change > 0:
                            coins_found = change
                            break
                    
                    # Check other coin routes
                    coins = extract_coin_from_message(d)
                    if coins > 0 and response_received:
                        coins_found = coins
                        break
            
            except websocket.WebSocketTimeoutException:
                pass
            except:
                pass
            
            msg_id += 1
            
            if coins_found > 0:
                result = {
                    'route': route_name,
                    'data': route_data,
                    'coin_amount': coins_found,
                    'msg_id': msg_id - 1
                }
                scanner_state['scan_results'].append(result)
                scanner_state['coin_routes'].append(result)
                
                logger.info(f"✅ [{i+1}/{len(TEST_ROUTES)}] {route_name} - {coins_found} coins!")
                
                # Test repeatability
                ws.send(msgpack.packb({
                    "route": route_name,
                    "data": route_data,
                    "msgId": msg_id
                }, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
                
                ws.settimeout(1.0)
                repeat_coins = 0
                try:
                    while True:
                        m = ws.recv()
                        d = msgpack.unpackb(m, raw=False)
                        
                        if d.get("msgId") == msg_id:
                            repeat_coins = extract_coin_from_message(d)
                            if repeat_coins > 0:
                                break
                        
                        if d.get("route") == "reloadCash":
                            change = d.get("data", {}).get("changeCash", 0)
                            if change > 0:
                                repeat_coins = change
                                break
                
                except:
                    pass
                
                msg_id += 1
                
                if repeat_coins > 0:
                    result['repeatable'] = True
                    scanner_state['repeatable_routes'].append(result)
                    logger.info(f"🔄 REPEATABLE: {route_name} - {repeat_coins} coins again!")
                else:
                    result['repeatable'] = False
            else:
                logger.debug(f"❌ [{i+1}/{len(TEST_ROUTES)}] {route_name} - No coins")
            
            time.sleep(0.1)
        
        ws.close()
        
        # Generate report
        scanner_state['scan_complete'] = True
        scanner_state['total_found'] = len(scanner_state['coin_routes'])
        
        # Send report
        report = (
            f"📊 *Route Scan Complete!*\n\n"
            f"🔍 Routes Tested: {len(TEST_ROUTES)}\n"
            f"✅ Coin Routes Found: {len(scanner_state['coin_routes'])}\n"
            f"🔄 Repeatable: {len(scanner_state['repeatable_routes'])}\n"
        )
        
        if scanner_state['repeatable_routes']:
            report += "\n🎯 *REPEATABLE ROUTES (JACKPOT!):*\n"
            for r in scanner_state['repeatable_routes'][:10]:
                report += f"📍 `{r['route']}` - {r['coin_amount']:,} coins\n"
        
        if scanner_state['coin_routes']:
            report += "\n✅ *ALL COIN ROUTES:*\n"
            for r in scanner_state['coin_routes'][:20]:
                report += f"📍 `{r['route']}` - {r['coin_amount']:,} coins\n"
        
        asyncio.run(send_telegram(chat_id, report))
        
        # Auto-exploit repeatable routes
        if scanner_state['repeatable_routes']:
            asyncio.run(send_telegram(chat_id, "⛏️ *Starting Auto-Exploit on repeatable routes...*"))
            exploit_repeatable_routes(chat_id, scanner_state['repeatable_routes'])
    
    except Exception as e:
        logger.error(f"Scan error: {e}")
        scanner_state['scan_complete'] = True
        asyncio.run(send_telegram(chat_id, f"❌ *Scan Error:* {str(e)}"))
    
    scanner_state['scanning'] = False

def exploit_repeatable_routes(chat_id: str, routes: List[Dict], times: int = 100):
    """Exploit repeatable routes for coins"""
    global scanner_state
    
    total_claimed = 0
    
    try:
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
        
        ws.settimeout(5)
        for _ in range(10):
            m = ws.recv()
            d = msgpack.unpackb(m, raw=False)
            if d.get("msgId") == 1:
                break
        
        # Enter room
        ws.send(msgpack.packb({"route": "play", "data": {"roomId": 1}, "msgId": 2}, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
        time.sleep(1)
        
        msg_id = 5000
        
        for route_info in routes:
            route_name = route_info['route']
            route_data = route_info['data']
            
            logger.info(f"⛏️ Exploiting {route_name}...")
            
            for i in range(times):
                ws.send(msgpack.packb({
                    "route": route_name,
                    "data": route_data,
                    "msgId": msg_id
                }, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
                
                ws.settimeout(1.0)
                try:
                    while True:
                        m = ws.recv()
                        d = msgpack.unpackb(m, raw=False)
                        
                        if d.get("route") == "reloadCash":
                            change = d.get("data", {}).get("changeCash", 0)
                            if change > 0:
                                total_claimed += change
                                scanner_state['total_found'] += change
                                logger.info(f"💰 +{change:,} (Total: {total_claimed:,})")
                                break
                        
                        if d.get("msgId") == msg_id:
                            coins = extract_coin_from_message(d)
                            if coins > 0:
                                total_claimed += coins
                                scanner_state['total_found'] += coins
                                logger.info(f"💰 +{coins:,} (Total: {total_claimed:,})")
                            break
                
                except:
                    break
                
                msg_id += 1
                
                if i % 20 == 0 and i > 0:
                    asyncio.run(send_telegram(
                        chat_id,
                        f"📈 *Exploit Progress*\n"
                        f"📍 Route: `{route_name}`\n"
                        f"📦 Claims: {i}\n"
                        f"💰 Total Gained: {total_claimed:,}"
                    ))
                
                time.sleep(0.01)
        
        ws.close()
        
        asyncio.run(send_telegram(
            chat_id,
            f"✅ *Exploit Complete!*\n\n"
            f"💰 Total Claimed: {total_claimed:,} coins"
        ))
    
    except Exception as e:
        logger.error(f"Exploit error: {e}")
        asyncio.run(send_telegram(chat_id, f"❌ *Exploit Error:* {str(e)}"))

# ==================== COMMANDS ====================
async def process_command(chat_id: str, command: str):
    """Process commands"""
    command = command.lower().strip()
    
    if command in ['/start', '/help', '1']:
        help_text = (
            "🔍 *FishMya Route Auto Scanner*\n\n"
            "ဒီ bot က game ရဲ့ WebSocket routes တွေကို auto scan လုပ်ပြီး:\n"
            "1️⃣ Coin ပေးတဲ့ routes တွေ ရှာမယ်\n"
            "2️⃣ Repeatable routes တွေ့ရင် auto exploit လုပ်မယ်\n"
            "3️⃣ နောက်ထပ် နည်းလမ်းအသစ်တွေ ရှာမယ်\n\n"
            "📋 *Commands:*\n"
            "🔹 `/scan` - Route scan စတင်ရန်\n"
            "🔹 `/exploit` - တွေ့ထားတဲ့ routes တွေကို exploit လုပ်ရန်\n"
            "🔹 `/status` - Scan status ကြည့်ရန်\n"
            "🔹 `/stop` - ရပ်ရန်\n\n"
            "⚡ *Powered by GHOST AI*"
        )
        await send_telegram(chat_id, help_text)
    
    elif command in ['/scan', '/search', '/mine']:
        if scanner_state['scanning']:
            await send_telegram(chat_id, "⚠️ *Scan already running!*")
            return
        
        await send_telegram(chat_id, "🔍 *Starting Route Scan...*\n\nTesting routes for coin rewards...")
        
        # Run scan in thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, scan_routes_sync, chat_id)
    
    elif command in ['/exploit', '/claim']:
        if scanner_state['repeatable_routes']:
            await send_telegram(chat_id, "⛏️ *Starting Auto-Exploit...*")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, exploit_repeatable_routes, chat_id, scanner_state['repeatable_routes'], 100)
        else:
            await send_telegram(chat_id, "❌ No repeatable routes found. Run /scan first.")
    
    elif command in ['/status', '/info']:
        status = "🟢 Scanning" if scanner_state['scanning'] else "🔴 Idle"
        await send_telegram(
            chat_id,
            f"📊 *Scanner Status*\n\n"
            f"State: {status}\n"
            f"✅ Routes Found: {len(scanner_state['coin_routes'])}\n"
            f"🔄 Repeatable: {len(scanner_state['repeatable_routes'])}\n"
            f"💰 Total Found: {scanner_state['total_found']:,}\n"
            f"📋 Scan Complete: {'Yes' if scanner_state['scan_complete'] else 'No'}"
        )
    
    elif command in ['/stop', '/end']:
        scanner_state['scanning'] = False
        await send_telegram(chat_id, "🛑 *Scanner Stopped!*")

# ==================== MAIN ====================
async def main():
    global last_update_id
    
    print("\n" + "=" * 60)
    print("🔍 FishMya Route Auto Scanner")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Token: {'✅ Set' if GAME_ACCESS_TOKEN else '❌ Not set'}")
    print(f"📡 WS: {WS_URL}")
    print(f"📋 Routes to Test: {len(TEST_ROUTES)}")
    print("=" * 60 + "\n")
    
    logger.info("🤖 Bot polling...")
    logger.info("💡 Send /scan to start route scanning!")
    
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
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
