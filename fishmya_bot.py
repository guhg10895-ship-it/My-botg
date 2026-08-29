#!/usr/bin/env python3
"""
FishMya Game - HTTP Login + API Scanner (No WebSocket)
Author: GHOST
Version: 8.0 - Fixed Login
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from urllib.parse import urlparse, parse_qs

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
GAME_URL = "https://fishmya.ugame.vn"
FULL_GAME_URL = "https://fishmya.ugame.vn?accessToken=eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ"
PHONE_NUMBER = "959676109648"

# Extract token from URL
ACCESS_TOKEN = ""
if "accessToken=" in FULL_GAME_URL:
    ACCESS_TOKEN = FULL_GAME_URL.split("accessToken=")[1].split("&")[0]
elif "access_token=" in FULL_GAME_URL:
    ACCESS_TOKEN = FULL_GAME_URL.split("access_token=")[1].split("&")[0]

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

# ==================== COIN ENDPOINTS ====================
POTENTIAL_ENDPOINTS = [
    # Most common coin endpoints
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
    "/api/account/info",
    "/api/player/balance",
    "/api/player/coins",
    "/api/player/rewards",
    "/api/player/info",
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

# ==================== HELPERS ====================
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
        'diamonds', 'gem', 'gems', 'fish', 'score', 'total'
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

# ==================== HTTP LOGIN + SCAN ====================
async def login_and_get_headers() -> Optional[Dict]:
    """Login and get session headers"""
    
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': GAME_URL,
        'Referer': f'{GAME_URL}/',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    # Try to get session via login page
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # Try to access the game page first
            async with session.get(FULL_GAME_URL, timeout=15) as response:
                if response.status == 200:
                    logger.info("✅ Game page accessed")
                    # Get cookies
                    cookies = session.cookie_jar.filter_cookies(GAME_URL)
                    if cookies:
                        cookie_header = "; ".join([f"{k}={v.value}" for k, v in cookies.items()])
                        headers['Cookie'] = cookie_header
                        logger.info(f"✅ Got cookies: {len(cookies)} cookies")
    
    except Exception as e:
        logger.error(f"Login page error: {e}")
    
    return headers

async def scan_endpoints(chat_id: str = None) -> Dict:
    """Scan all endpoints for coins"""
    
    headers = await login_and_get_headers()
    
    successful = []
    repeatable = []
    
    if chat_id:
        await send_telegram(chat_id, f"🔍 *Scanning {len(POTENTIAL_ENDPOINTS)} endpoints...*")
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for i, endpoint in enumerate(POTENTIAL_ENDPOINTS, 1):
            url = f"{GAME_URL}{endpoint}"
            
            result = {
                'endpoint': endpoint,
                'success': False,
                'repeatable': False,
                'coin_amount': 0,
                'status': None
            }
            
            # Test GET
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
                        except json.JSONDecodeError:
                            pass
                    
                    elif response.status in [401, 403]:
                        logger.warning(f"⚠️ [{i}] {endpoint} - Auth failed ({response.status})")
                        # Token might be expired
                        if i > 5 and not successful:
                            break
            
            except asyncio.TimeoutError:
                pass
            except Exception:
                pass
            
            # Test POST
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
                        except json.JSONDecodeError:
                            pass
            except:
                pass
            
            await asyncio.sleep(0.2)
    
    return {
        'total_scanned': len(POTENTIAL_ENDPOINTS),
        'successful': successful,
        'repeatable': repeatable,
        'total_coins': sum(r['coin_amount'] for r in successful)
    }

async def auto_claim(chat_id: str, times: int = 100):
    """Auto claim from repeatable endpoints"""
    
    headers = await login_and_get_headers()
    
    total_claimed = 0
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for endpoint_info in game_state['repeatable_endpoints']:
            endpoint = endpoint_info['endpoint']
            coins_per_claim = endpoint_info['coin_amount']
            
            logger.info(f"⛏️ Claiming from {endpoint} - {coins_per_claim} coins/claim")
            
            if chat_id:
                await send_telegram(
                    chat_id,
                    f"⛏️ *Claiming:* `{endpoint}`\n💰 {coins_per_claim:,} coins/claim"
                )
            
            for i in range(times):
                url = f"{GAME_URL}{endpoint}"
                
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
                
                break  # Stop if both fail
    
    return total_claimed

# ==================== GAME STATE ====================
game_state = {
    'repeatable_endpoints': [],
    'total_claimed': 0,
    'balance': 0,
    'nickname': '',
}

# ==================== COMMANDS ====================
async def process_command(chat_id: str, command: str):
    """Process commands"""
    command = command.lower().strip()
    
    if command in ['/start', '/help', '1']:
        help_text = (
            "🎣 *FishMya Coin Miner*\n\n"
            "🔐 Login: HTTP Method\n"
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
    
    elif command in ['/mine', '/start_mining', '/play']:
        await send_telegram(chat_id, "🎣 *Starting Coin Miner...*\n\nPlease wait...")
        
        # Scan
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
            report += "\n🎯 *JACKPOT Endpoints:*\n"
            for r in scan_result['repeatable'][:10]:
                report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,}/claim\n"
            
            await send_telegram(chat_id, report)
            
            # Auto claim
            claimed = await auto_claim(chat_id, times=100)
            game_state['total_claimed'] += claimed
            
            await send_telegram(
                chat_id,
                f"✅ *Claiming Done!*\n\n💰 Total Claimed: {claimed:,} coins"
            )
        else:
            await send_telegram(chat_id, report + "\n❌ No repeatable endpoints found")
    
    elif command in ['/scan', '/search']:
        await send_telegram(chat_id, "🔍 *Scanning...*")
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
    
    elif command in ['/claim', '/auto_claim']:
        if game_state['repeatable_endpoints']:
            await send_telegram(chat_id, "⛏️ *Auto claiming...*")
            claimed = await auto_claim(chat_id, times=50)
            game_state['total_claimed'] += claimed
            await send_telegram(chat_id, f"✅ Claimed: {claimed:,} coins")
        else:
            await send_telegram(chat_id, "❌ No repeatable endpoints. Run /scan first.")
    
    elif command in ['/balance', '/check']:
        headers = await login_and_get_headers()
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(f"{GAME_URL}/api/balance", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        balance = extract_coin_amount(data)
                        await send_telegram(
                            chat_id,
                            f"💰 *Balance:* {balance:,} coins\n"
                            f"📱 Phone: {PHONE_NUMBER}"
                        )
                    else:
                        await send_telegram(chat_id, f"❌ HTTP {response.status}")
        except Exception as e:
            await send_telegram(chat_id, f"❌ Error: {e}")
    
    elif command in ['/status', '/info']:
        await send_telegram(
            chat_id,
            f"📊 *Bot Status*\n\n"
            f"🎮 Game: FishMya\n"
            f"🔐 Login: HTTP Method\n"
            f"💰 Total Claimed: {game_state['total_claimed']:,}\n"
            f"🔄 Repeatable Endpoints: {len(game_state['repeatable_endpoints'])}\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

# ==================== MAIN ====================
async def main():
    global last_update_id
    
    print("\n" + "=" * 60)
    print("🎣 FishMya Coin Miner (HTTP Login)")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Token: {'✅ Set (' + str(len(ACCESS_TOKEN)) + ' chars)' if ACCESS_TOKEN else '❌ Not set'}")
    print(f"🌐 URL: {GAME_URL}")
    print("=" * 60 + "\n")
    
    if not ACCESS_TOKEN:
        logger.error("❌ ACCESS_TOKEN is empty! Check FULL_GAME_URL")
        return
    
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
            logger.info("Bot stopped")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
