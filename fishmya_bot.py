#!/usr/bin/env python3
"""
FishMya Game - WebSocket Login + Coin Scanner
Author: GHOST
Version: 9.0 - Working Login Method
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
import threading
from urllib.parse import urlparse, parse_qs
import websocket  # မင်းရဲ့ original library

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
WS_URL = "wss://api-fishmcloud.ugame.vn:2083"
GAME_BASE_URL = "https://fishmya.ugame.vn"
PHONE_NUMBER = "959676109648"

WS_HEADERS = [
    "User-Agent: Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Origin: https://fishmya.ugame.vn",
    "Accept-Language: my-MM,my;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With: com.mytel.myid"
]

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

# ==================== STATE ====================
config_data = {"game_access_token": None}
game_session = {
    'username': '',
    'nickname': '',
    'balance': 0,
    'logged_in': False,
    'headers': {},
    'repeatable_endpoints': [],
    'total_claimed': 0
}

# ==================== TOKEN STORAGE ====================
# မင်းရဲ့ token ကို ဒီမှာ ထည့်ပါ
GAME_ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ"

# ==================== COIN ENDPOINTS ====================
POTENTIAL_ENDPOINTS = [
    "/api/balance",
    "/api/user/balance",
    "/api/user/coins",
    "/api/user/rewards",
    "/api/profile",
    "/api/user",
    "/api/me",
    "/api/user/info",
    "/api/account/balance",
    "/api/account/coins",
    "/api/account/rewards",
    "/api/player/balance",
    "/api/player/coins",
    "/api/player/rewards",
    "/api/coins/claim",
    "/api/coins/collect",
    "/api/coins/reward",
    "/api/claim-coins",
    "/api/collect-coins",
    "/api/coin-reward",
    "/api/daily/claim",
    "/api/daily-reward",
    "/api/daily/checkin",
    "/api/checkin",
    "/api/rewards/daily",
    "/api/rewards/claim",
    "/api/rewards/collect",
    "/api/reward/claim",
    "/api/claim/reward",
    "/api/get-reward",
    "/api/get/balance",
    "/api/get/coins",
    "/api/get/rewards",
    "/api/game/rewards",
    "/api/game/claim",
    "/api/game/coin-reward",
    "/api/login/reward",
    "/api/login-bonus",
    "/api/welcome-reward",
    "/api/missions/complete",
    "/api/tasks/claim",
    "/api/quests/reward",
    "/api/level/reward",
    "/api/levelup/reward",
    "/api/bonus/claim",
    "/api/bonus-rewards",
    "/api/hourly/claim",
    "/api/hourly-reward",
    "/api/spin/reward",
    "/api/lucky-spin",
    "/api/ads/reward",
    "/api/watch-ad",
    "/api/friends/rewards",
    "/api/referral/claim",
    "/api/events/rewards",
    "/api/event/claim",
    "/api/treasure/claim",
    "/api/chest/open",
    "/api/achievements/claim",
    "/api/achievement/reward",
    "/api/fish/catch",
    "/api/fishing/reward",
    "/api/web/claim",
    "/api/web/rewards",
    "/api/client/balance",
    "/api/client/coins",
    "/api/client/rewards",
    "/api/v1/balance",
    "/api/v1/coins",
    "/api/v1/rewards",
    "/api/v1/claim",
    "/api/v2/balance",
    "/api/v2/coins",
    "/api/v2/rewards",
    "/api/v2/claim",
]

# ==================== UTILS ====================
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
        if depth > 10:
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

# ==================== WEBSOCKET LOGIN (မင်းရဲ့နည်း) ====================
def ws_login_sync(access_token: str) -> Dict:
    """Login via WebSocket using your original method"""
    result = {
        'success': False,
        'message': '',
        'username': '',
        'nickname': '',
        'balance': 0
    }
    
    url = f"{WS_URL}?access_token={access_token}"
    
    try:
        ws = websocket.create_connection(
            url,
            header=WS_HEADERS,
            sslopt={"cert_reqs": ssl.CERT_NONE},
            timeout=30
        )
        
        # Send login
        login_payload = {
            "route": "mytelLogin",
            "data": {"accessToken": access_token, "language": "my"},
            "msgId": 1
        }
        ws.send(msgpack.packb(login_payload, use_bin_type=True), opcode=websocket.ABNF.OPCODE_BINARY)
        
        # Wait for response
        ws.settimeout(15)
        try:
            data = ws.recv()
            if data:
                decoded = msgpack.unpackb(data, raw=False)
                inner = decoded.get("data", {})
                msg_id = decoded.get("msgId", -1)
                
                if msg_id == 1 and inner.get("ok"):
                    result['success'] = True
                    result['message'] = 'Login successful'
                    result['username'] = inner.get("username", "")
                    result['nickname'] = inner.get("nickname", "User")
                    result['balance'] = inner.get("cash", 0)
                    
                    logger.info(f"✅ Login OK: {result['nickname']}, Balance: {result['balance']:,}")
                else:
                    result['message'] = f"Login failed: {inner}"
                    logger.error(f"❌ Login failed: {inner}")
        
        except Exception as e:
            result['message'] = f"Response error: {e}"
            logger.error(f"❌ Response error: {e}")
        
        ws.close()
        
    except Exception as e:
        result['message'] = f"Connection error: {e}"
        logger.error(f"❌ Connection error: {e}")
    
    return result

async def websocket_login(chat_id: str = None) -> Dict:
    """Async wrapper for WebSocket login"""
    if chat_id:
        await send_telegram(chat_id, "🔐 *Logging in via WebSocket...*")
    
    # Run sync login in thread
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, ws_login_sync, GAME_ACCESS_TOKEN)
    
    if result['success']:
        game_session['logged_in'] = True
        game_session['username'] = result['username']
        game_session['nickname'] = result['nickname']
        game_session['balance'] = result['balance']
        
        # Build HTTP headers for API calls
        game_session['headers'] = {
            'Authorization': f'Bearer {GAME_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36',
            'Origin': GAME_BASE_URL,
            'Referer': f'{GAME_BASE_URL}/',
            'X-Requested-With': 'com.mytel.myid'
        }
        
        if chat_id:
            await send_telegram(
                chat_id,
                f"✅ *Login Successful!*\n\n"
                f"👤 Nickname: {result['nickname']}\n"
                f"💰 Balance: {result['balance']:,} coins\n\n"
                f"🔍 Now scanning for coin endpoints..."
            )
    
    return result

# ==================== HTTP SCANNER ====================
async def scan_endpoints(chat_id: str = None) -> Dict:
    """Scan HTTP endpoints for coins"""
    
    headers = game_session.get('headers', {
        'Authorization': f'Bearer {GAME_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
        'Origin': GAME_BASE_URL,
        'Referer': f'{GAME_BASE_URL}/',
    })
    
    successful = []
    repeatable = []
    
    if chat_id:
        await send_telegram(chat_id, f"🔍 *Scanning {len(POTENTIAL_ENDPOINTS)} endpoints...*")
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for i, endpoint in enumerate(POTENTIAL_ENDPOINTS, 1):
            url = f"{GAME_BASE_URL}{endpoint}"
            
            result = {
                'endpoint': endpoint,
                'success': False,
                'repeatable': False,
                'coin_amount': 0,
                'status': None
            }
            
            # GET
            try:
                async with session.get(url, timeout=8) as response:
                    result['status'] = response.status
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            coins = extract_coin_amount(data)
                            
                            if coins > 0:
                                result['success'] = True
                                result['coin_amount'] = coins
                                
                                # Test repeatability
                                await asyncio.sleep(0.3)
                                async with session.get(url, timeout=8) as retry:
                                    if retry.status == 200:
                                        retry_data = await retry.json()
                                        if extract_coin_amount(retry_data) > 0:
                                            result['repeatable'] = True
                                
                                successful.append(result)
                                logger.info(f"✅ [{i}] {endpoint} - {coins} coins (Repeat: {result['repeatable']})")
                                
                                if result['repeatable']:
                                    repeatable.append(result)
                                
                                continue
                        except:
                            pass
            except:
                pass
            
            # POST
            try:
                async with session.post(url, json={}, timeout=8) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            coins = extract_coin_amount(data)
                            
                            if coins > 0:
                                result['success'] = True
                                result['coin_amount'] = coins
                                
                                # Test repeatability
                                await asyncio.sleep(0.3)
                                async with session.post(url, json={}, timeout=8) as retry:
                                    if retry.status == 200:
                                        retry_data = await retry.json()
                                        if extract_coin_amount(retry_data) > 0:
                                            result['repeatable'] = True
                                
                                successful.append(result)
                                logger.info(f"✅ [{i}] {endpoint} - {coins} coins (Repeat: {result['repeatable']})")
                                
                                if result['repeatable']:
                                    repeatable.append(result)
                        except:
                            pass
            except:
                pass
            
            await asyncio.sleep(0.2)
    
    game_session['repeatable_endpoints'] = repeatable
    
    return {
        'total_scanned': len(POTENTIAL_ENDPOINTS),
        'successful': successful,
        'repeatable': repeatable,
        'total_coins': sum(r['coin_amount'] for r in successful)
    }

# ==================== AUTO CLAIM ====================
async def auto_claim(chat_id: str, times: int = 100):
    """Auto claim from repeatable endpoints"""
    
    headers = game_session.get('headers', {})
    total_claimed = 0
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for endpoint_info in game_session['repeatable_endpoints']:
            endpoint = endpoint_info['endpoint']
            coins_per_claim = endpoint_info['coin_amount']
            
            logger.info(f"⛏️ Claiming from {endpoint} - {coins_per_claim} coins/claim")
            
            if chat_id:
                await send_telegram(
                    chat_id,
                    f"⛏️ *Claiming:* `{endpoint}`\n"
                    f"💰 {coins_per_claim:,} coins/claim"
                )
            
            for i in range(times):
                url = f"{GAME_BASE_URL}{endpoint}"
                
                # GET
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
                
                # POST
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
                
                break
    
    game_session['total_claimed'] += total_claimed
    return total_claimed

# ==================== MAIN MINING ====================
async def run_miner(chat_id: str):
    """Run complete mining session"""
    
    # Step 1: Login via WebSocket
    login_result = await websocket_login(chat_id)
    
    if not login_result['success']:
        if chat_id:
            await send_telegram(
                chat_id,
                f"❌ *Login Failed!*\n\n"
                f"⚠️ {login_result['message']}\n\n"
                f"🔄 Update GAME_ACCESS_TOKEN in code"
            )
        return
    
    # Step 2: Scan
    scan_result = await scan_endpoints(chat_id)
    
    # Report
    report = (
        f"📊 *Scan Results*\n\n"
        f"📡 Scanned: {scan_result['total_scanned']}\n"
        f"✅ Working: {len(scan_result['successful'])}\n"
        f"🔄 Repeatable: {len(scan_result['repeatable'])}\n"
        f"💰 Available: {scan_result['total_coins']:,} coins\n"
    )
    
    if scan_result['repeatable']:
        report += "\n🎯 *JACKPOT (Can claim multiple times!):*\n"
        for r in scan_result['repeatable'][:10]:
            report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,}/claim\n"
        
        await send_telegram(chat_id, report)
        
        # Step 3: Auto Claim
        await send_telegram(chat_id, "⛏️ *Starting Auto-Claim...*")
        claimed = await auto_claim(chat_id, times=100)
        
        await send_telegram(
            chat_id,
            f"✅ *Claiming Complete!*\n\n"
            f"💰 Claimed: {claimed:,} coins\n"
            f"💎 Total All-Time: {game_session['total_claimed']:,}"
        )
    else:
        await send_telegram(chat_id, report + "\n❌ No repeatable endpoints found")

# ==================== COMMANDS ====================
async def process_command(chat_id: str, command: str):
    """Process commands"""
    command = command.lower().strip()
    
    if command in ['/start', '/help', '1']:
        help_text = (
            "🎣 *FishMya Coin Miner*\n\n"
            "🔐 Login: WebSocket (အလုပ်လုပ်တယ်)\n"
            "🔍 Scan: Auto\n"
            "💰 Claim: Auto\n\n"
            "📋 *Commands:*\n"
            "🔹 `/mine` - Start mining\n"
            "🔹 `/scan` - Scan endpoints\n"
            "🔹 `/claim` - Auto claim\n"
            "🔹 `/balance` - Check balance\n"
            "🔹 `/status` - Bot status\n\n"
            "⚡ *Powered by GHOST AI*"
        )
        await send_telegram(chat_id, help_text)
    
    elif command in ['/mine', '/start', '/play']:
        await run_miner(chat_id)
    
    elif command in ['/scan']:
        login_result = await websocket_login(chat_id)
        if login_result['success']:
            scan_result = await scan_endpoints(chat_id)
            report = f"📊 *Scan Done*\n\n"
            report += f"📡 Scanned: {scan_result['total_scanned']}\n"
            report += f"✅ Working: {len(scan_result['successful'])}\n"
            report += f"🔄 Repeatable: {len(scan_result['repeatable'])}\n"
            report += f"💰 Total: {scan_result['total_coins']:,}\n"
            
            if scan_result['repeatable']:
                report += "\n🎯 *Repeatable:*\n"
                for r in scan_result['repeatable'][:10]:
                    report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,}\n"
            
            await send_telegram(chat_id, report)
    
    elif command in ['/claim']:
        if game_session['repeatable_endpoints']:
            claimed = await auto_claim(chat_id, times=50)
            await send_telegram(chat_id, f"✅ Claimed: {claimed:,} coins")
        else:
            await send_telegram(chat_id, "❌ Run /scan first")
    
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
            f"🔐 Login: {'✅ Yes' if game_session['logged_in'] else '❌ No'}\n"
            f"💰 Total Claimed: {game_session['total_claimed']:,}\n"
            f"🔄 Repeatable: {len(game_session['repeatable_endpoints'])}\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

# ==================== MAIN ====================
async def main():
    global last_update_id
    
    print("\n" + "=" * 60)
    print("🎣 FishMya Coin Miner (WebSocket Login)")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Token: {'✅ Set' if GAME_ACCESS_TOKEN else '❌ Not set'}")
    print(f"📡 WS: {WS_URL}")
    print("=" * 60 + "\n")
    
    logger.info("🤖 Bot polling...")
    logger.info("💡 Send /start to your bot!")
    
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
