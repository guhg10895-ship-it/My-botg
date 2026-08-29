#!/usr/bin/env python3
"""
FishMya Game - Universal Auto Miner Bot
Author: GHOST
Version: 5.0 - Universal (Everyone can use)
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ"
PHONE_NUMBER = "959676109648"
GAME_URL = "https://fishmya.ugame.vn"

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ==================== TELEGRAM API ====================
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0
processed_users = set()

# ==================== ENDPOINTS ====================
POTENTIAL_ENDPOINTS = [
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
    "/api/daily/claim",
    "/api/daily-reward",
    "/api/rewards/daily",
    "/api/daily-bonus",
    "/api/daily/checkin",
    "/api/checkin",
    "/api/daily/login",
    "/api/coins/claim",
    "/api/coins/collect",
    "/api/coins/reward",
    "/api/collect-coins",
    "/api/claim-coins",
    "/api/coin-reward",
    "/api/game/rewards",
    "/api/rewards/claim",
    "/api/rewards/collect",
    "/api/game/claim",
    "/api/game/coin-reward",
    "/api/game/reward",
    "/api/missions/complete",
    "/api/tasks/claim",
    "/api/quests/reward",
    "/api/mission-rewards",
    "/api/task-rewards",
    "/api/level/reward",
    "/api/levelup/reward",
    "/api/level-bonus",
    "/api/login/reward",
    "/api/login-bonus",
    "/api/welcome-reward",
    "/api/login/claim",
    "/api/spin/reward",
    "/api/wheel/claim",
    "/api/lucky-spin",
    "/api/spin/claim",
    "/api/ads/reward",
    "/api/watch-ad",
    "/api/ad-rewards",
    "/api/ad/claim",
    "/api/friends/rewards",
    "/api/invite/reward",
    "/api/referral/claim",
    "/api/events/rewards",
    "/api/event/claim",
    "/api/special-rewards",
    "/api/fish/catch",
    "/api/fishing/reward",
    "/api/catch-reward",
    "/api/fish/claim",
    "/api/treasure/claim",
    "/api/chest/open",
    "/api/chest-rewards",
    "/api/achievements/claim",
    "/api/achievement/reward",
    "/api/bonus/claim",
    "/api/bonus-rewards",
    "/api/extra-bonus",
    "/api/hourly/claim",
    "/api/hourly-reward",
    "/api/time-rewards",
    "/api/web/claim",
    "/api/web/rewards",
    "/api/website/claim",
    "/api/web/balance",
    "/api/reward/claim",
    "/api/claim/reward",
    "/api/get-reward",
    "/api/get/balance",
    "/api/get/coins",
    "/api/get/rewards",
    "/api/refresh",
    "/api/sync",
    "/api/update/balance",
    "/api/v1/balance",
    "/api/v1/rewards",
    "/api/v1/claim",
    "/api/v2/balance",
    "/api/v2/rewards",
    "/api/v2/claim",
]

class FishMyaMiner:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Origin': base_url,
            'Referer': f'{base_url}/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.found_endpoints = []
        self.total_mined = 0
        self.repeatable_endpoints = []
    
    async def create_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def check_login(self) -> Dict:
        result = {'valid': False, 'message': '', 'balance': 0}
        
        try:
            session = await self.create_session()
            check_endpoints = ["/api/profile", "/api/user", "/api/balance", "/api/me"]
            
            for endpoint in check_endpoints:
                try:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            result['valid'] = True
                            result['message'] = f'Login OK via {endpoint}'
                            data = await response.json()
                            result['balance'] = self.extract_coin_amount(data)
                            logger.info(f"✅ Login OK: {endpoint} - Balance: {result['balance']}")
                            break
                        elif response.status == 401:
                            result['message'] = 'Token expired (401)'
                except:
                    continue
            
            if not result['valid'] and not result['message']:
                result['message'] = 'Cannot connect to game server'
        
        except Exception as e:
            result['message'] = f'Error: {str(e)}'
        
        return result
    
    async def test_endpoint(self, endpoint: str) -> Dict:
        result = {
            'endpoint': endpoint,
            'success': False,
            'repeatable': False,
            'coin_amount': 0,
            'status': None
        }
        
        session = await self.create_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.get(url, timeout=8) as response:
                result['status'] = response.status
                if response.status == 200:
                    try:
                        data = await response.json()
                        coins = self.extract_coin_amount(data)
                        if coins > 0:
                            result['success'] = True
                            result['coin_amount'] = coins
                            
                            await asyncio.sleep(0.3)
                            async with session.get(url, timeout=8) as retry:
                                if retry.status == 200:
                                    retry_data = await retry.json()
                                    if self.extract_coin_amount(retry_data) > 0:
                                        result['repeatable'] = True
                            return result
                    except:
                        pass
        except:
            pass
        
        try:
            async with session.post(url, json={}, timeout=8) as response:
                result['status'] = response.status
                if response.status == 200:
                    try:
                        data = await response.json()
                        coins = self.extract_coin_amount(data)
                        if coins > 0:
                            result['success'] = True
                            result['coin_amount'] = coins
                            
                            await asyncio.sleep(0.3)
                            async with session.post(url, json={}, timeout=8) as retry:
                                if retry.status == 200:
                                    retry_data = await retry.json()
                                    if self.extract_coin_amount(retry_data) > 0:
                                        result['repeatable'] = True
                            return result
                    except:
                        pass
        except:
            pass
        
        return result
    
    def extract_coin_amount(self, data: Any) -> int:
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
    
    async def scan_all(self) -> Dict:
        successful = []
        repeatable = []
        
        logger.info(f"🔍 Scanning {len(POTENTIAL_ENDPOINTS)} endpoints...")
        
        for endpoint in POTENTIAL_ENDPOINTS:
            result = await self.test_endpoint(endpoint)
            
            if result['success']:
                successful.append(result)
                logger.info(f"✅ {endpoint} - {result['coin_amount']} coins (Repeatable: {result['repeatable']})")
                if result['repeatable']:
                    repeatable.append(result)
            
            await asyncio.sleep(0.2)
        
        self.found_endpoints = successful
        self.repeatable_endpoints = repeatable
        
        return {
            'total_scanned': len(POTENTIAL_ENDPOINTS),
            'successful': successful,
            'repeatable': repeatable,
            'total_coins': sum(r['coin_amount'] for r in successful)
        }
    
    async def mine_repeatable(self, times: int = 100) -> int:
        total_mined = 0
        session = await self.create_session()
        
        for endpoint_info in self.repeatable_endpoints:
            endpoint = endpoint_info['endpoint']
            
            for i in range(times):
                try:
                    url = f"{self.base_url}{endpoint}"
                    async with session.get(url, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            coins = self.extract_coin_amount(data)
                            total_mined += coins
                            await asyncio.sleep(0.15)
                        else:
                            break
                except:
                    break
            
            try:
                for i in range(30):
                    url = f"{self.base_url}{endpoint}"
                    async with session.post(url, json={}, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            coins = self.extract_coin_amount(data)
                            total_mined += coins
                            await asyncio.sleep(0.15)
                        else:
                            break
            except:
                pass
        
        self.total_mined += total_mined
        return total_mined
    
    def format_report(self, scan_result: Dict, mined: int, login_balance: int) -> str:
        report = "🎣 *FishMya Mining Report*\n\n"
        report += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"🔐 Balance: {login_balance:,} coins\n"
        report += f"📊 Scanned: {scan_result['total_scanned']}\n"
        report += f"✅ Working: {len(scan_result['successful'])}\n"
        report += f"🔄 Repeatable: {len(scan_result['repeatable'])}\n"
        report += f"💰 Available: {scan_result['total_coins']:,}\n"
        
        if mined > 0:
            report += f"⛏️ Mined: {mined:,} coins\n"
        
        if scan_result['repeatable']:
            report += "\n🎯 *JACKPOT Endpoints:*\n"
            for r in scan_result['repeatable'][:10]:
                report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,}/claim\n"
        elif scan_result['successful']:
            report += "\n✅ *Working:*\n"
            for r in scan_result['successful'][:10]:
                report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,}\n"
        else:
            report += "\n❌ No endpoints found\n"
        
        return report

async def send_message(chat_id: str, text: str):
    """Send message to specific chat"""
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
                    logger.info(f"✅ Message sent to {chat_id}")
                    return True
                else:
                    response_text = await response.text()
                    logger.error(f"Failed to send to {chat_id}: {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False

async def get_updates(offset: int = 0) -> List[Dict]:
    """Get bot updates"""
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

async def process_command(chat_id: str, command: str):
    """Process user commands"""
    command = command.lower().strip()
    
    if command in ['/start', '/help']:
        help_text = (
            "🎣 *FishMya Auto Miner Bot*\n\n"
            "👋 မင်္ဂလာပါ! ဒီ bot က FishMya game ကနေ coins တွေ auto ရှာပေးမယ်။\n\n"
            "📋 *Commands:*\n"
            "🔹 `/mine` - Auto mining စတင်ရန်\n"
            "🔹 `/scan` - Endpoints ရှာဖွေရန်\n"
            "🔹 `/balance` - Balance စစ်ဆေးရန်\n"
            "🔹 `/status` - Bot status ကြည့်ရန်\n\n"
            "⚡ *Powered by GHOST AI*"
        )
        await send_message(chat_id, help_text)
    
    elif command in ['/mine', '/start_mining']:
        await send_message(chat_id, "⛏️ *Mining Started!*\n\nPlease wait...")
        
        miner = FishMyaMiner(GAME_URL, ACCESS_TOKEN)
        
        try:
            # Check login
            login_result = await miner.check_login()
            
            if not login_result['valid']:
                await send_message(chat_id, f"❌ *Login Failed:* {login_result['message']}")
                return
            
            # Scan
            scan_result = await miner.scan_all()
            
            # Mine
            mined = 0
            if scan_result['repeatable']:
                mined = await miner.mine_repeatable(times=100)
            
            # Report
            report = miner.format_report(scan_result, mined, login_result['balance'])
            await send_message(chat_id, report)
            
        except Exception as e:
            await send_message(chat_id, f"❌ Error: {str(e)}")
        finally:
            await miner.close_session()
    
    elif command in ['/scan', '/search']:
        await send_message(chat_id, "🔍 *Scanning endpoints...*\n\nThis may take a minute...")
        
        miner = FishMyaMiner(GAME_URL, ACCESS_TOKEN)
        
        try:
            login_result = await miner.check_login()
            
            if not login_result['valid']:
                await send_message(chat_id, f"❌ *Login Failed:* {login_result['message']}")
                return
            
            scan_result = await miner.scan_all()
            report = miner.format_report(scan_result, 0, login_result['balance'])
            await send_message(chat_id, report)
            
        except Exception as e:
            await send_message(chat_id, f"❌ Error: {str(e)}")
        finally:
            await miner.close_session()
    
    elif command in ['/balance', '/check']:
        await send_message(chat_id, "🔐 *Checking balance...*")
        
        miner = FishMyaMiner(GAME_URL, ACCESS_TOKEN)
        
        try:
            login_result = await miner.check_login()
            
            if login_result['valid']:
                await send_message(
                    chat_id,
                    f"💰 *Balance:* {login_result['balance']:,} coins\n"
                    f"🔑 Token: Active ✅\n"
                    f"📱 Phone: {PHONE_NUMBER}"
                )
            else:
                await send_message(chat_id, f"❌ *Login Failed:* {login_result['message']}")
            
        finally:
            await miner.close_session()
    
    elif command in ['/status', '/info']:
        status_text = (
            "📊 *Bot Status*\n\n"
            f"🎮 Game: FishMya\n"
            f"🔗 URL: {GAME_URL}\n"
            f"📱 Phone: {PHONE_NUMBER}\n"
            f"🔑 Token: Active ✅\n"
            f"⚡ Bot: Running\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await send_message(chat_id, status_text)
    
    else:
        await send_message(
            chat_id,
            "❓ Unknown command\n\n"
            "Use /help to see available commands"
        )

async def main():
    global last_update_id
    global processed_users
    
    print("\n" + "=" * 60)
    print("🎣 FishMya Universal Auto Miner Bot")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Token: {'✅ Set' if ACCESS_TOKEN else '❌ Not set'}")
    print("=" * 60 + "\n")
    
    logger.info("🤖 Bot polling started...")
    logger.info("💡 Send /start to your bot on Telegram!")
    
    miner = FishMyaMiner(GAME_URL, ACCESS_TOKEN)
    
    try:
        while True:
            # Get updates
            updates = await get_updates(last_update_id + 1)
            
            for update in updates:
                update_id = update.get('update_id', 0)
                
                if update_id > last_update_id:
                    last_update_id = update_id
                
                # Process message
                if 'message' in update:
                    message = update['message']
                    chat_id = str(message.get('chat', {}).get('id', ''))
                    text = message.get('text', '')
                    user_id = str(message.get('from', {}).get('id', ''))
                    
                    if chat_id and text:
                        logger.info(f"📩 Message from {chat_id}: {text}")
                        
                        # Process command
                        await process_command(chat_id, text)
                        
                        # Track user
                        processed_users.add(user_id)
            
            # Auto mine every 5 minutes for all users
            if processed_users and datetime.now().minute % 5 == 0:
                logger.info("⛏️ Auto mining for all users...")
                
                login_result = await miner.check_login()
                
                if login_result['valid']:
                    scan_result = await miner.scan_all()
                    
                    if scan_result['repeatable']:
                        mined = await miner.mine_repeatable(times=50)
                        report = miner.format_report(scan_result, mined, login_result['balance'])
                        
                        for chat_id in processed_users:
                            await send_message(chat_id, report)
            
            await asyncio.sleep(2)
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await miner.close_session()

if __name__ == "__main__":
    asyncio.run(main())
