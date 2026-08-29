#!/usr/bin/env python3
"""
FishMya Game - Auto Coin Miner Bot for GitHub Actions
Author: GHOST
Version: 3.1 - Direct Token (No Secrets Required)
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# ==================== CONFIGURATION (DIRECT) ====================
BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ"
PHONE_NUMBER = "959676109648"
CHAT_ID = "YOUR_CHAT_ID_HERE"  # မင်းရဲ့ Telegram Chat ID ထည့်ပါ

GAME_URL = "https://fishmya.ugame.vn"

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== ENDPOINTS ====================
POTENTIAL_ENDPOINTS = [
    # Balance/Client endpoints
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
    
    # Daily rewards
    "/api/daily/claim",
    "/api/daily-reward",
    "/api/rewards/daily",
    "/api/daily-bonus",
    "/api/daily/checkin",
    "/api/checkin",
    
    # Coin collections
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
    
    # Missions
    "/api/missions/complete",
    "/api/tasks/claim",
    "/api/quests/reward",
    "/api/mission-rewards",
    "/api/task-rewards",
    
    # Level rewards
    "/api/level/reward",
    "/api/levelup/reward",
    "/api/level-bonus",
    
    # Login rewards
    "/api/login/reward",
    "/api/login-bonus",
    "/api/welcome-reward",
    "/api/login/claim",
    
    # Spin rewards
    "/api/spin/reward",
    "/api/wheel/claim",
    "/api/lucky-spin",
    "/api/spin/claim",
    
    # Ads rewards
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
    
    # Web client
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

class FishMyaMiner:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Origin': base_url,
            'Referer': f'{base_url}/',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
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
            
            check_endpoints = ["/api/profile", "/api/user", "/api/balance", "/api/me", "/api/user/info"]
            
            for endpoint in check_endpoints:
                try:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            result['valid'] = True
                            result['message'] = f'Login valid via {endpoint}'
                            data = await response.json()
                            result['balance'] = self.extract_coin_amount(data)
                            logger.info(f"Login OK: {endpoint} - Balance: {result['balance']}")
                            break
                        elif response.status == 401:
                            result['message'] = 'Token expired (401)'
                        elif response.status == 403:
                            result['message'] = 'Access forbidden (403)'
                        else:
                            result['message'] = f'HTTP {response.status}'
                except asyncio.TimeoutError:
                    continue
                except:
                    continue
            
            if not result['valid'] and not result['message']:
                result['message'] = 'All check endpoints failed'
        
        except Exception as e:
            result['message'] = f'Error: {str(e)}'
        
        return result
    
    async def test_endpoint(self, endpoint: str) -> Dict:
        result = {
            'endpoint': endpoint,
            'success': False,
            'repeatable': False,
            'coin_amount': 0,
            'status': None,
            'error': None
        }
        
        session = await self.create_session()
        url = f"{self.base_url}{endpoint}"
        
        # Test GET
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
                            
                            # Test repeatability
                            await asyncio.sleep(0.3)
                            async with session.get(url, timeout=8) as retry:
                                if retry.status == 200:
                                    retry_data = await retry.json()
                                    retry_coins = self.extract_coin_amount(retry_data)
                                    if retry_coins > 0:
                                        result['repeatable'] = True
                            
                            return result
                    except:
                        pass
        except:
            pass
        
        # Test POST
        try:
            payloads = [{}, {"action": "claim"}, {"type": "claim"}]
            for payload in payloads:
                async with session.post(url, json=payload, timeout=8) as response:
                    result['status'] = response.status
                    if response.status == 200:
                        try:
                            data = await response.json()
                            coins = self.extract_coin_amount(data)
                            if coins > 0:
                                result['success'] = True
                                result['coin_amount'] = coins
                                
                                # Test repeatability
                                await asyncio.sleep(0.3)
                                async with session.post(url, json=payload, timeout=8) as retry:
                                    if retry.status == 200:
                                        retry_data = await retry.json()
                                        retry_coins = self.extract_coin_amount(retry_data)
                                        if retry_coins > 0:
                                            result['repeatable'] = True
                                
                                return result
                        except:
                            pass
        except:
            pass
        
        result['error'] = f'HTTP {result["status"]}' if result['status'] else 'Failed'
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
            'diamonds', 'gem', 'gems', 'fish', 'score', 'total'
        ]
        
        def search(obj, depth=0):
            if depth > 8:
                return 0
            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_lower = key.lower()
                    if any(p in key_lower for p in coin_patterns):
                        if isinstance(value, (int, float)):
                            if value > 0:
                                return int(value)
                        elif isinstance(value, str) and value.isdigit():
                            if int(value) > 0:
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
        results = []
        successful = []
        repeatable = []
        
        logger.info(f"Scanning {len(POTENTIAL_ENDPOINTS)} endpoints...")
        
        for i, endpoint in enumerate(POTENTIAL_ENDPOINTS, 1):
            result = await self.test_endpoint(endpoint)
            results.append(result)
            
            if result['success']:
                successful.append(result)
                logger.info(f"[{i}/{len(POTENTIAL_ENDPOINTS)}] ✅ {endpoint} - {result['coin_amount']} coins (Repeatable: {result['repeatable']})")
                
                if result['repeatable']:
                    repeatable.append(result)
            else:
                logger.debug(f"[{i}/{len(POTENTIAL_ENDPOINTS)}] ❌ {endpoint}")
            
            await asyncio.sleep(0.2)
        
        self.found_endpoints = successful
        self.repeatable_endpoints = repeatable
        
        total_available = sum(r['coin_amount'] for r in successful)
        total_repeatable = sum(r['coin_amount'] for r in repeatable)
        
        logger.info(f"Scan complete: {len(successful)} working, {len(repeatable)} repeatable")
        logger.info(f"Total available: {total_available}, Repeatable total: {total_repeatable}")
        
        return {
            'total_scanned': len(results),
            'successful': successful,
            'repeatable': repeatable,
            'total_coins': total_available,
            'repeatable_coins': total_repeatable
        }
    
    async def mine_repeatable(self, times_per_endpoint: int = 50) -> int:
        total_mined = 0
        session = await self.create_session()
        
        for endpoint_info in self.repeatable_endpoints:
            endpoint = endpoint_info['endpoint']
            coins_per_claim = endpoint_info['coin_amount']
            logger.info(f"Mining {endpoint} - {coins_per_claim} coins per claim...")
            
            for i in range(times_per_endpoint):
                try:
                    url = f"{self.base_url}{endpoint}"
                    async with session.get(url, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            coins = self.extract_coin_amount(data)
                            if coins > 0:
                                total_mined += coins
                            await asyncio.sleep(0.15)
                        else:
                            logger.info(f"Stopped at iteration {i+1} (HTTP {response.status})")
                            break
                except asyncio.TimeoutError:
                    logger.info(f"Timeout at iteration {i+1}")
                    break
                except:
                    logger.info(f"Error at iteration {i+1}")
                    break
            
            # Also try POST method
            try:
                for i in range(20):
                    url = f"{self.base_url}{endpoint}"
                    async with session.post(url, json={}, timeout=8) as response:
                        if response.status == 200:
                            data = await response.json()
                            coins = self.extract_coin_amount(data)
                            if coins > 0:
                                total_mined += coins
                            await asyncio.sleep(0.15)
                        else:
                            break
            except:
                pass
        
        self.total_mined += total_mined
        logger.info(f"Total mined: {total_mined}")
        return total_mined
    
    def format_report(self, scan_result: Dict, mined: int = 0, login_balance: int = 0) -> str:
        report = "🎣 **FishMya Mining Report**\n\n"
        report += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"🔐 Login Balance: {login_balance:,} coins\n"
        report += f"📊 Endpoints Scanned: {scan_result['total_scanned']}\n"
        report += f"✅ Working: {len(scan_result['successful'])}\n"
        report += f"🔄 Repeatable: {len(scan_result['repeatable'])}\n"
        report += f"💰 Available: {scan_result['total_coins']:,} coins\n"
        
        if mined > 0:
            report += f"⛏️ Mined This Round: {mined:,} coins\n"
            report += f"🪙 Total Mined All Time: {self.total_mined:,} coins\n"
        
        if scan_result['repeatable']:
            report += "\n🎯 **Repeatable Endpoints (JACKPOT!):**\n"
            for r in scan_result['repeatable'][:10]:
                report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,} coins/claim\n"
        elif scan_result['successful']:
            report += "\n✅ **Working Endpoints:**\n"
            for r in scan_result['successful'][:10]:
                report += f"📍 `{r['endpoint']}` - {r['coin_amount']:,} coins\n"
        else:
            report += "\n❌ No working endpoints found\n"
            report += "🔄 Try updating ACCESS_TOKEN"
        
        return report

async def send_telegram_message(bot_token: str, chat_id: str, message: str):
    """Send message via Telegram API"""
    if not bot_token or not chat_id or chat_id == "YOUR_CHAT_ID_HERE":
        logger.warning("CHAT_ID not set, skipping Telegram notification")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=15) as response:
                if response.status == 200:
                    logger.info("Telegram notification sent ✅")
                else:
                    response_text = await response.text()
                    logger.error(f"Telegram send failed: {response.status} - {response_text}")
    except Exception as e:
        logger.error(f"Telegram error: {e}")

async def main():
    logger.info("=" * 60)
    logger.info("🎣 FishMya Auto Miner Starting...")
    logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    if not ACCESS_TOKEN:
        logger.error("ACCESS_TOKEN not set!")
        return
    
    miner = FishMyaMiner(GAME_URL, ACCESS_TOKEN)
    
    try:
        # Check login
        logger.info("🔐 Checking login status...")
        login_result = await miner.check_login()
        logger.info(f"Login Result: {login_result['message']}")
        
        if not login_result['valid']:
            error_msg = (
                f"❌ **Login Failed!**\n\n"
                f"⚠️ Reason: {login_result['message']}\n\n"
                f"🔄 ACCESS_TOKEN သက်တမ်းကုန်သွားနိုင်တယ်\n"
                f"💡 Game website ကနေ token အသစ်ယူပြီး ထည့်ပါ"
            )
            await send_telegram_message(BOT_TOKEN, CHAT_ID, error_msg)
            logger.error("Login failed, exiting...")
            return
        
        logger.info(f"💰 Current balance: {login_result['balance']:,} coins")
        
        # Scan endpoints
        logger.info("🔍 Scanning for coin endpoints...")
        scan_result = await miner.scan_all()
        
        # Mine repeatable endpoints
        mined = 0
        if scan_result['repeatable']:
            logger.info(f"⛏️ Found {len(scan_result['repeatable'])} repeatable endpoints, mining...")
            mined = await miner.mine_repeatable(times_per_endpoint=100)
            logger.info(f"⛏️ Mined {mined:,} coins this session")
        else:
            logger.info("❌ No repeatable endpoints found")
            if scan_result['successful']:
                logger.info(f"✅ But found {len(scan_result['successful'])} one-time endpoints")
        
        # Generate report
        report = miner.format_report(scan_result, mined, login_result['balance'])
        logger.info("\n" + report)
        
        # Send Telegram notification
        await send_telegram_message(BOT_TOKEN, CHAT_ID, report)
        
        # Final balance check
        await asyncio.sleep(2)
        final_login = await miner.check_login()
        if final_login['valid']:
            final_report = (
                f"📊 **Final Status**\n\n"
                f"💰 Final Balance: {final_login['balance']:,} coins\n"
                f"🪙 Mined This Session: {mined:,} coins\n"
                f"⏰ Completed: {datetime.now().strftime('%H:%M:%S')}"
            )
            await send_telegram_message(BOT_TOKEN, CHAT_ID, final_report)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        error_msg = f"❌ **Error:** {str(e)}"
        await send_telegram_message(BOT_TOKEN, CHAT_ID, error_msg)
    
    finally:
        await miner.close_session()
        logger.info("🏁 Mining session completed")

if __name__ == "__main__":
    asyncio.run(main())
