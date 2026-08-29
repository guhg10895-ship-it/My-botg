#!/usr/bin/env python3
"""
FishMya Game - WebSocket Login + HTTP API Coin Scanner
Author: GHOST
Version: 7.0 - Login + Scan + Auto Claim
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import websockets
import msgpack
import ssl
import math

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
GAME_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ"
WS_URL = "wss://api-fishmcloud.ugame.vn:2083"
GAME_BASE_URL = "https://fishmya.ugame.vn"
PHONE_NUMBER = "959676109648"

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

# ==================== GAME STATE ====================
class GameSession:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.logged_in = False
        self.username = ""
        self.nickname = ""
        self.balance = 0
        self.start_balance = 0
        self.session_headers = {}
        self.found_endpoints = []
        self.repeatable_endpoints = []
        self.total_claimed = 0
        
game_session = GameSession()

# ==================== COIN ENDPOINTS TO SCAN ====================
POTENTIAL_ENDPOINTS = [
    # Balance/Client
    "/api/balance",
    "/api/client/balance",
    "/api/client/coins",
    "/api/client/rewards",
    "/api/user/balance",
    "/api/user/coins",
    "/api/user/rewards",
    "/api/profile/balance",
    "/api/profile/coins",
    "/api/profile/rewards",
    "/api/me",
    "/api/user/info",
    
    # Daily
    "/api/daily/claim",
    "/api/daily-reward",
    "/api/rewards/daily",
    "/api/daily-bonus",
    "/api/daily/checkin",
    "/api/checkin",
    "/api/daily/login",
    
    # Coins
    "/api/coins/claim",
    "/api/coins/collect",
    "/api/coins/reward",
    "/api/collect-coins",
    "/api/claim-coins",
    "/api/coin-reward",
    
    # Game rewards
    "/api/game/rewards",
    "/api/rewards/claim",
    "/api/rewards/collect",
    "/api/game/claim",
    "/api/game/coin-reward",
    "/api/game/reward",
    
    # Missions
    "/api/missions/complete",
    "/api/tasks/claim",
    "/api/quests/reward",
    "/api/mission-rewards",
    "/api/task-rewards",
    
    # Level
    "/api/level/reward",
    "/api/levelup/reward",
    "/api/level-bonus",
    
    # Login rewards
    "/api/login/reward",
    "/api/login-bonus",
    "/api/welcome-reward",
    "/api/login/claim",
    
    # Spin
    "/api/spin/reward",
    "/api/wheel/claim",
    "/api/lucky-spin",
    "/api/spin/claim",
    
    # Ads
    "/api/ads/reward",
    "/api/watch-ad",
    "/api/ad-rewards",
    "/api/ad/claim",
    
    # Friends
    "/api/friends/rewards",
    "/api/invite/reward",
    "/api/referral/claim",
    
    # Events
    "/api/events/rewards",
    "/api/event/claim",
    "/api/special-rewards",
    
    # Fish
    "/api/fish/catch",
    "/api/fishing/reward",
    "/api/catch-reward",
    "/api/fish/claim",
    
    # Treasure
    "/api/treasure/claim",
    "/api/chest/open",
    "/api/chest-rewards",
    
    # Achievement
    "/api/achievements/claim",
    "/api/achievement/reward",
    
    # Bonus
    "/api/bonus/claim",
    "/api/bonus-rewards",
    "/api/extra-bonus",
    
    # Hourly
    "/api/hourly/claim",
    "/api/hourly-reward",
    "/api/time-rewards",
    
    # Web
    "/api/web/claim",
    "/api/web/rewards",
    "/api/website/claim",
    "/api/web/balance",
    
    # Additional
    "/api/reward/claim",
    "/api/claim/reward",
    "/api/get-reward",
    "/api/get/balance",
    "/api/get/coins",
    "/api/get/rewards",
    "/api/refresh",
    "/api/sync",
    "/api/update/balance",
]

# ==================== UTILITY FUNCTIONS ====================
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
                    response_text = await response.text()
                    logger.error(f"Telegram failed: {response.status} - {response_text[:200]}")
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

# ==================== WEBSOCKET LOGIN ====================
async def websocket_login(chat_id: str = None) -> Dict:
    """Login via WebSocket and get session data"""
    global game_session
    
    result = {
        'success': False,
        'message': '',
        'username': '',
        'nickname': '',
        'balance': 0
    }
    
    url = f"{WS_URL}?access_token={GAME_ACCESS_TOKEN}"
    
    headers = [
        ("User-Agent", "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36"),
        ("Origin", "https://fishmya.ugame.vn"),
        ("Accept-Language", "my-MM,my;q=0.9,en-US;q=0.8,en;q=0.7"),
        ("X-Requested-With", "com.mytel.myid"),
    ]
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        if chat_id:
            await send_telegram(chat_id, "🔐 *Logging in via WebSocket...*")
        
        ws = await websockets.connect(
            url,
            additional_headers=headers,
            ssl=ssl_context,
            ping_interval=None,
            max_size=10 * 1024 * 1024
        )
        
        game_session.ws = ws
        game_session.connected = True
        
        # Send login message
        login_payload = {
            "route": "mytelLogin",
            "data": {"accessToken": GAME_ACCESS_TOKEN, "language": "my"},
            "msgId": 1
        }
        await ws.send(msgpack.packb(login_payload, use_bin_type=True))
        
        # Wait for response
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=15)
            decoded = msgpack.unpackb(response, raw=False)
            
            inner = decoded.get("data", {})
            msg_id = decoded.get("msgId", -1)
            
            if msg_id == 1 and inner.get("ok"):
                game_session.logged_in = True
                game_session.username = inner.get("username", "")
                game_session.nickname = inner.get("nickname", "User")
                game_session.balance = inner.get("cash", 0)
                game_session.start_balance = inner.get("cash", 0)
                
                result['success'] = True
                result['message'] = 'Login successful'
                result['username'] = game_session.username
                result['nickname'] = game_session.nickname
                result['balance'] = game_session.balance
                
                logger.info(f"✅ WebSocket Login OK: {game_session.nickname}, Balance: {game_session.balance}")
                
                if chat_id:
                    await send_telegram(
                        chat_id,
                        f"✅ *Login Successful!*\n\n"
                        f"👤 Nickname: {game_session.nickname}\n"
                        f"💰 Balance: {game_session.balance:,} coins\n\n"
                        f"🔍 Now scanning for coin endpoints..."
                    )
            else:
                result['message'] = f"Login failed: {inner.get('msg', 'Unknown error')}"
                logger.error(f"❌ Login failed: {inner}")
        
        except asyncio.TimeoutError:
            result['message'] = 'Login timeout'
            logger.error("❌ Login timeout")
        
        # Close WebSocket (we don't need it anymore for HTTP scanning)
        await ws.close()
        game_session.connected = False
        game_session.ws = None
        
    except Exception as e:
        result['message'] = f'WebSocket error: {str(e)}'
        logger.error(f"❌ WebSocket error: {e}")
    
    return result

# ==================== HTTP API SCANNER ====================
def extract_coin_amount(data: Any) -> int:
    """Extract coin amount from response"""
    if not data:
        return 0
    
    coin_patterns = [
        'coin', 'coins', 'coinAmount', 'coin_amount',
        'totalCoins', 'reward', 'rewards', 'amount',
        'gold', 'golds', 'point', 'points', 'balance',
        'currency', 'currencies', 'fishcoin', 'fish_coins',
        'money', 'cash', 'credit', 'credits', 'diamond',
        'diamonds', 'gem', 'gems', 'fish', 'score'
    ]
    
    def search(obj, depth=0):
        if depth > 8:
            return 0
        if isinstance(obj, dict):
            for key, value in obj.items():
                key_lower = key.lower()
                if any(p in key_lower for p in coin_patterns):
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
    
    return search(data)

async def scan_http_endpoints(chat_id: str = None) -> Dict:
    """Scan HTTP endpoints for coin rewards"""
    global game_session
    
    headers = {
        'Authorization': f'Bearer {GAME_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Origin': GAME_BASE_URL,
        'Referer': f'{GAME_BASE_URL}/',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    successful = []
    repeatable = []
    
    if chat_id:
        await send_telegram(chat_id, f"🔍 *Scanning {len(POTENTIAL_ENDPOINTS)} endpoints...*")
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for endpoint in POTENTIAL_ENDPOINTS:
            url = f"{GAME_BASE_URL}{endpoint}"
            
            result = {
                'endpoint': endpoint,
                'success': False,
                'repeatable': False,
                'coin_amount': 0
            }
            
            # Test GET
            try:
                async with session.get(url, timeout=8) as response:
                    if response.status == 200:
                        data = await response.json()
                        coins = extract_coin_amount(data)
                        if coins > 0:
                            result['success'] = True
                            result['coin_amount'] = coins
                            
                            # Test if repeatable
                            await asyncio.sleep(0.3)
                            async with session.get(url, timeout=8) as retry:
                                if retry.status == 200:
                                    retry_data = await retry.json()
                                    if extract_coin_amount(retry_data) > 0:
                                        result['repeatable'] = True
                            
                            successful.append(result)
                            logger.info(f"✅ {endpoint} - {coins} coins (Repeatable: {result['repeatable']})")
                            
                            if result['repeatable']:
                                repeatable.append(result)
                            
                            continue
            except:
                pass
            
            # Test POST
            try:
                async with session.post(url, json={}, timeout=8) as response:
                    if response.status == 200:
                        data = await response.json()
                        coins = extract_coin_amount(data)
                        if coins > 0:
                            result['success'] = True
                            result['coin_amount'] = coins
                            
                            # Test if repeatable
                            await asyncio.sleep(0.3)
                            async with session.post(url, json={}, timeout=8) as retry:
                                if retry.status == 200:
                                    retry_data = await retry.json()
                                    if extract_coin_amount(retry_data) > 0:
                                        result['repeatable'] = True
                            
                            successful.append(result)
                            logger.info(f"✅ {endpoint} - {coins} coins (Repeatable: {result['repeatable']})")
                            
                            if result['repeatable']:
                                repeatable.append(result)
            except:
                pass
            
            await asyncio.sleep(0.2)
    
    game_session.found_endpoints = successful
    game_session.repeatable_endpoints = repeatable
    
    return {
        'total_scanned': len(POTENTIAL_ENDPOINTS),
        'successful': successful,
        'repeatable': repeatable,
        'total_coins': sum(r['coin_amount'] for r in successful)
    }

async def auto_claim_loop(chat_id: str = None, times: int = 100):
    """Auto claim from repeatable endpoints"""
    global game_session
    
    headers = {
        'Authorization': f'Bearer {GAME_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Origin': GAME_BASE_URL,
        'Referer': f'{GAME_BASE_URL}/',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    total_claimed = 0
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for endpoint_info in game_session.repeatable_endpoints:
            endpoint = endpoint_info['endpoint']
            coins_per_claim = endpoint_info['coin_amount']
            
            logger.info(f"⛏️ Auto-claiming from {endpoint} - {coins_per_claim} coins/claim")
            
            if chat_id:
                await send_telegram(
                    chat_id,
                    f"⛏️ *Claiming from:* `{endpoint}`\n"
                    f"💰 Coins per claim: {coins_per_claim:,}"
                )
            
            for i in range(times):
                url = f"{GAME_BASE_URL}{endpoint}"
                
                # Try GET
                try:
                    async with session.get(url, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            coins = extract_coin_amount(data)
                            total_claimed += coins
                            await asyncio.sleep(0.1)
                            continue
                except:
                    pass
                
                # Try POST
                try:
                    async with session.post(url, json={}, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            coins = extract_coin_amount(data)
                            total_claimed += coins
                            await asyncio.sleep(0.1)
                            continue
                except:
                    pass
                
                break  # Stop if both methods fail
    
    game_session.total_claimed += total_claimed
    logger.info(f"💰 Total claimed: {total_claimed}")
    return total_claimed

# ==================== MAIN GAME SESSION ====================
async def run_coin_miner(chat_id: str):
    """Run complete coin mining session"""
    
    if chat_id:
        await send_telegram(
            chat_id,
            f"🎣 *FishMya Coin Miner Starting*\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"📱 Phone: {PHONE_NUMBER}"
        )
    
    # Step 1: Login via WebSocket
    login_result = await websocket_login(chat_id)
    
    if not login_result['success']:
        if chat_id:
            await send_telegram(
                chat_id,
                f"❌ *Login Failed!*\n\n"
                f"⚠️ {login_result['message']}\n\n"
                f"🔄 Please update ACCESS_TOKEN"
            )
        return
    
    # Step 2: Scan HTTP endpoints
    scan_result = await scan_http_endpoints(chat_id)
    
    if chat_id:
        report = (
            f"📊 *Scan Results*\n\n"
            f"📡 Endpoints Scanned: {scan_result['total_scanned']}\n"
            f"✅ Working: {len(scan_result['successful'])}\n"
            f"🔄 Repeatable: {len(scan_result['repeatable'])}\n"
            f"💰 Available: {scan_result['total_coins']:,} coins\n"
        )
        
        if scan_result['repeatable']:
            report += "\n🎯 *JACKPOT Endpoints (Can claim multiple times!):*\n"
            for r in scan_result['repeatable'][:10]:
                report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,} coins/claim\n"
        
        await send_telegram(chat_id, report)
    
    # Step 3: Auto claim from repeatable endpoints
    if scan_result['repeatable']:
        if chat_id:
            await send_telegram(
                chat_id,
                f"⛏️ *Starting Auto-Claim!*\n\n"
                f"🔄 Claiming from {len(scan_result['repeatable'])} endpoints..."
            )
        
        claimed = await auto_claim_loop(chat_id, times=100)
        
        if chat_id:
            await send_telegram(
                chat_id,
                f"✅ *Auto-Claim Complete!*\n\n"
                f"💰 Total Claimed: {claimed:,} coins\n"
                f"📊 Start Balance: {login_result['balance']:,}\n"
                f"💎 Estimated New Balance: {login_result['balance'] + claimed:,}"
            )
    else:
        if chat_id:
            await send_telegram(
                chat_id,
                f"❌ *No Repeatable Endpoints Found*\n\n"
                f"Try again later or update token."
            )

# ==================== COMMAND HANDLER ====================
async def process_command(chat_id: str, command: str):
    """Process user commands"""
    command = command.lower().strip()
    
    if command in ['/start', '/help']:
        help_text = (
            "🎣 *FishMya Coin Miner Bot*\n\n"
            "👋 မင်္ဂလာပါ! ဒီ bot က:\n"
            "1️⃣ WebSocket ကနေ login ဝင်မယ်\n"
            "2️⃣ Client API တွေကို scan လုပ်မယ်\n"
            "3️⃣ Coin ရနိုင်တဲ့ endpoints တွေ့ရင် auto claim လုပ်မယ်\n\n"
            "📋 *Commands:*\n"
            "🔹 `/mine` - Coin mining စတင်ရန်\n"
            "🔹 `/scan` - Endpoints scan လုပ်ရန်\n"
            "🔹 `/claim` - Auto claim လုပ်ရန်\n"
            "🔹 `/balance` - Balance ကြည့်ရန်\n"
            "🔹 `/status` - Bot status\n\n"
            "⚡ *Powered by GHOST AI*"
        )
        await send_telegram(chat_id, help_text)
    
    elif command in ['/mine', '/start', '/play']:
        await run_coin_miner(chat_id)
    
    elif command in ['/scan']:
        # Login first
        login_result = await websocket_login(chat_id)
        
        if login_result['success']:
            scan_result = await scan_http_endpoints(chat_id)
            
            report = (
                f"📊 *Scan Results*\n\n"
                f"📡 Scanned: {scan_result['total_scanned']}\n"
                f"✅ Working: {len(scan_result['successful'])}\n"
                f"🔄 Repeatable: {len(scan_result['repeatable'])}\n"
                f"💰 Available: {scan_result['total_coins']:,}\n"
            )
            
            if scan_result['repeatable']:
                report += "\n🎯 *Repeatable:*\n"
                for r in scan_result['repeatable'][:10]:
                    report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,}\n"
            
            await send_telegram(chat_id, report)
    
    elif command in ['/claim']:
        if game_session.repeatable_endpoints:
            claimed = await auto_claim_loop(chat_id, times=50)
            await send_telegram(chat_id, f"✅ *Claimed:* {claimed:,} coins")
        else:
            await send_telegram(chat_id, "❌ No repeatable endpoints found. Run /scan first.")
    
    elif command in ['/balance', '/check']:
        login_result = await websocket_login(chat_id)
        
        if login_result['success']:
            await send_telegram(
                chat_id,
                f"💰 *Balance:* {login_result['balance']:,} coins\n"
                f"👤 Player: {login_result['nickname']}\n"
                f"📱 Phone: {PHONE_NUMBER}"
            )
    
    elif command in ['/status', '/info']:
        await send_telegram(
            chat_id,
            f"📊 *Bot Status*\n\n"
            f"🎮 Game: FishMya\n"
            f"📡 Server: Online\n"
            f"🔑 Token: Active ✅\n"
            f"💰 Total Claimed: {game_session.total_claimed:,}\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

# ==================== MAIN LOOP ====================
async def main():
    global last_update_id
    
    print("\n" + "=" * 60)
    print("🎣 FishMya Coin Miner Bot")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Token: {'✅ Set' if GAME_ACCESS_TOKEN else '❌ Not set'}")
    print(f"📡 WS Server: {WS_URL}")
    print(f"🌐 HTTP Base: {GAME_BASE_URL}")
    print("=" * 60 + "\n")
    
    logger.info("🤖 Bot polling started...")
    logger.info("💡 Send /start to your bot on Telegram!")
    
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
                        logger.info(f"📩 Message from {chat_id}: {text}")
                        await process_command(chat_id, text)
            
            await asyncio.sleep(2)
            
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Bot error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
