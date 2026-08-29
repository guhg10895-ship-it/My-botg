#!/usr/bin/env python3
"""
FishMya Game - Auto Coin Miner Bot with Telegram Integration
Author: GHOST
Version: 2.0
Purpose: Auto-mine coins from client-side APIs with repeated claiming
"""

import asyncio
import aiohttp
import json
import re
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
import logging
import signal
import sys

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8801207672:AAEsJfwy12ePwpjvDNalCeIrYQl-91vgMMk"
GAME_URL = "https://fishmya.ugame.vn"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkMDBvMWdJdXhnTHNsY1BoT0tuNkVwNkNLVEw5U21mWEU3ZUVDUUV5OUk4In0.eyJqdGkiOiIxMzFlZWE5OS1mZWNiLTRjNjMtYWZkMy02MDI4MDExYzczYjciLCJleHAiOjE3ODk3NTY5NTAsIm5iZiI6MCwiaWF0IjoxNzg3MDc4NTUwLCJpc3MiOiJodHRwczovL2lkLm15dGVsLmNvbS5tbS9hdXRoL3JlYWxtcy9jaW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiMTgwMjc3MWUtNDI2Mi00MzkwLTkzYTAtNTgxMDA0NTViMDZhIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiY3BtLWNsaWVudCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFjNWViYzI0LTdjMTUtNDYwZC04NDgzLWY0MzI2YzU0NDk2YiIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzYxNDgwMzAtNTMwNS00YWUxLTkwNjYtZDA5MTM0Yzg0MGFlIiwiaWQiOiIxODAyNzcxZS00MjYyLTQzOTAtOTNhMC01ODEwMDQ1NWIwNmEifQ.nG5DWSXOdVkdojz31jD6OonpRbZ_WutgRlzXx93rNBqeX4cTxMpr0B-7z2bDCB5R27EOrbg1DTKPo62eiI8qy94mEeg1wbKFvJOKXxjkugAwq5OZcSUcHeWR9KOS4cZciVAiph4TMNXbwhPWu-mW55zYkRNGXW9NPfd_zJZvnokgGEXFAPUYn0rdGX6vxYIgglbyDPRL1lftxFT0YmfFUruj2_Kva11xh1DN-m5yMlXZA1AtBLAlHDvllEzULXHu6f3ByiuTA_PvdZumJlLVZTBChcIHiDGOniANpK_DKMXoohrOl_DrZD9GcLAGstK6zR98hjmEF0P2OE4BCrkGEQ")
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "959676109648")
CHAT_ID = os.getenv("CHAT_ID", "")  # Your Telegram chat ID for auto-notifications

# ==================== API ENDPOINTS ====================
POTENTIAL_ENDPOINTS = [
    # Daily rewards (can claim multiple times if server bug exists)
    "/api/daily/claim",
    "/api/daily-reward",
    "/api/rewards/daily",
    "/api/daily-bonus",
    
    # Coin collections
    "/api/coins/claim",
    "/api/coins/collect",
    "/api/coins/reward",
    "/api/collect-coins",
    "/api/balance/claim",
    "/api/client/balance",
    
    # Game rewards
    "/api/game/rewards",
    "/api/rewards/claim",
    "/api/rewards/collect",
    "/api/game/claim",
    "/api/game/coin-reward",
    
    # Missions and tasks
    "/api/missions/complete",
    "/api/tasks/claim",
    "/api/quests/reward",
    "/api/mission-rewards",
    
    # Level up rewards
    "/api/level/reward",
    "/api/levelup/reward",
    "/api/level-bonus",
    
    # Login rewards
    "/api/login/reward",
    "/api/login-bonus",
    "/api/welcome-reward",
    
    # Spin/wheel rewards
    "/api/spin/reward",
    "/api/wheel/claim",
    "/api/lucky-spin",
    
    # Watch ads rewards
    "/api/ads/reward",
    "/api/watch-ad",
    "/api/ad-rewards",
    
    # Friend invites
    "/api/friends/rewards",
    "/api/invite/reward",
    "/api/referral/claim",
    
    # Special events
    "/api/events/rewards",
    "/api/event/claim",
    "/api/special-rewards",
    
    # Fish catching rewards
    "/api/fish/catch",
    "/api/fishing/reward",
    "/api/catch-reward",
    
    # Treasure/chest
    "/api/treasure/claim",
    "/api/chest/open",
    "/api/chest-rewards",
    
    # Achievement rewards
    "/api/achievements/claim",
    "/api/achievement/reward",
    
    # Bonus
    "/api/bonus/claim",
    "/api/bonus-rewards",
    "/api/extra-bonus",
    
    # Hourly rewards
    "/api/hourly/claim",
    "/api/hourly-reward",
    "/api/time-rewards",
    
    # Client-side balance endpoints
    "/api/client/balance",
    "/api/client/rewards",
    "/api/client/coins",
    "/api/user/balance",
    "/api/user/rewards",
    "/api/profile/rewards",
    
    # Web client endpoints
    "/api/web/claim",
    "/api/web/rewards",
    "/api/website/claim",
]

# ==================== LOGGING ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== FISHMYA SCANNER CLASS ====================
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
        self.mining_active = False
        self.last_scan_time = None
        self.balance_endpoints = []
        
    async def create_session(self):
        """Create aiohttp session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session
    
    async def close_session(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def check_login(self) -> Dict:
        """Check if login is still valid"""
        result = {
            'valid': False,
            'message': '',
            'balance': 0
        }
        
        try:
            session = await self.create_session()
            # Check with a simple endpoint
            async with session.get(f"{self.base_url}/api/profile", timeout=10) as response:
                if response.status == 200:
                    result['valid'] = True
                    result['message'] = 'Login valid ✅'
                    data = await response.json()
                    result['balance'] = self.extract_coin_amount(data)
                elif response.status == 401:
                    result['message'] = 'Token expired ❌'
                else:
                    result['message'] = f'Status: {response.status}'
        except Exception as e:
            result['message'] = f'Error: {str(e)}'
        
        return result
    
    async def test_endpoint(self, endpoint: str) -> Dict:
        """Test a single endpoint for coin rewards"""
        result = {
            'endpoint': endpoint,
            'status': None,
            'coin_amount': 0,
            'success': False,
            'repeatable': False,
            'response_data': None,
            'error': None
        }
        
        try:
            session = await self.create_session()
            url = f"{self.base_url}{endpoint}"
            
            # Test GET request
            async with session.get(url, timeout=10) as response:
                result['status'] = response.status
                if response.status == 200:
                    data = await response.json()
                    coin_amount = self.extract_coin_amount(data)
                    if coin_amount > 0:
                        result['coin_amount'] = coin_amount
                        result['success'] = True
                        result['response_data'] = data
                        
                        # Test if repeatable
                        await asyncio.sleep(0.3)
                        async with session.get(url, timeout=10) as retry_response:
                            if retry_response.status == 200:
                                retry_data = await retry_response.json()
                                retry_coins = self.extract_coin_amount(retry_data)
                                if retry_coins > 0:
                                    result['repeatable'] = True
                        
                        return result
            
            # Test POST request if GET fails
            async with session.post(url, json={}, timeout=10) as post_response:
                result['status'] = post_response.status
                if post_response.status == 200:
                    data = await post_response.json()
                    coin_amount = self.extract_coin_amount(data)
                    if coin_amount > 0:
                        result['coin_amount'] = coin_amount
                        result['success'] = True
                        result['response_data'] = data
                        
                        # Test if repeatable
                        await asyncio.sleep(0.3)
                        async with session.post(url, json={}, timeout=10) as retry_response:
                            if retry_response.status == 200:
                                retry_data = await retry_response.json()
                                retry_coins = self.extract_coin_amount(retry_data)
                                if retry_coins > 0:
                                    result['repeatable'] = True
                        
                        return result
                else:
                    result['error'] = f"HTTP {post_response.status}"
        
        except asyncio.TimeoutError:
            result['error'] = "Timeout"
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def extract_coin_amount(self, data: Any) -> int:
        """Extract coin amount from response data"""
        if not data:
            return 0
        
        coin_patterns = [
            'coin', 'coins', 'coinAmount', 'coin_amount',
            'totalCoins', 'reward', 'rewards', 'amount',
            'gold', 'golds', 'point', 'points', 'balance',
            'currency', 'currencies', 'fishcoin', 'fish_coins',
            'money', 'cash', 'credit', 'credits', 'diamond',
            'diamonds', 'gem', 'gems'
        ]
        
        def search_dict(obj, depth=0):
            if depth > 6:
                return 0
            if isinstance(obj, dict):
                for key, value in obj.items():
                    key_lower = key.lower()
                    if any(pattern in key_lower for pattern in coin_patterns):
                        if isinstance(value, (int, float)):
                            return int(value)
                        elif isinstance(value, str) and value.isdigit():
                            return int(value)
                    result = search_dict(value, depth + 1)
                    if result > 0:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = search_dict(item, depth + 1)
                    if result > 0:
                        return result
            return 0
        
        return search_dict(data)
    
    async def scan_all_endpoints(self) -> List[Dict]:
        """Scan all potential endpoints"""
        results = []
        
        for endpoint in POTENTIAL_ENDPOINTS:
            result = await self.test_endpoint(endpoint)
            results.append(result)
            
            if result['success']:
                logger.info(f"✅ Found: {endpoint} - {result['coin_amount']} coins (Repeatable: {result['repeatable']})")
                if result['repeatable']:
                    self.balance_endpoints.append(endpoint)
            
            await asyncio.sleep(0.2)  # Rate limiting protection
        
        self.found_endpoints = [r for r in results if r['success']]
        self.last_scan_time = datetime.now()
        return results
    
    async def mine_coins(self, endpoint: str, times: int = 10) -> int:
        """Mine coins from a repeatable endpoint multiple times"""
        total_mined = 0
        session = await self.create_session()
        
        for i in range(times):
            try:
                url = f"{self.base_url}{endpoint}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        coins = self.extract_coin_amount(data)
                        total_mined += coins
                        await asyncio.sleep(0.1)  # Small delay
                    else:
                        break
            except:
                break
        
        return total_mined
    
    async def auto_mine_loop(self, chat_id: str, bot: Bot):
        """Continuous mining loop"""
        self.mining_active = True
        
        while self.mining_active:
            try:
                # Check login status
                login_status = await self.check_login()
                
                if not login_status['valid']:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"⚠️ **Login Expired!**\n{login_status['message']}\n\nPlease update access token.",
                        parse_mode='Markdown'
                    )
                    self.mining_active = False
                    break
                
                # Scan for endpoints
                await self.scan_all_endpoints()
                
                # Find repeatable endpoints
                repeatable = [r for r in self.found_endpoints if r['repeatable']]
                
                if repeatable:
                    # Mine from repeatable endpoints
                    for endpoint in repeatable:
                        mined = await self.mine_coins(endpoint['endpoint'], times=20)
                        self.total_mined += mined
                        
                        await bot.send_message(
                            chat_id=chat_id,
                            text=f"💰 **Mined Successfully!**\n\n"
                                 f"📍 Endpoint: `{endpoint['endpoint']}`\n"
                                 f"🪙 Coins Mined: {mined:,}\n"
                                 f"📊 Total Mined: {self.total_mined:,}\n"
                                 f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}",
                            parse_mode='Markdown'
                        )
                        
                        await asyncio.sleep(5)  # Wait before next mining
                else:
                    # No repeatable endpoints, wait
                    await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Mining error: {e}")
                await asyncio.sleep(30)
    
    def format_results(self, results: List[Dict]) -> str:
        """Format scan results for display"""
        successful = [r for r in results if r['success']]
        repeatable = [r for r in successful if r['repeatable']]
        
        total_coins = sum(r['coin_amount'] for r in successful)
        
        message = "🎣 **FishMya Miner Scan Results**\n\n"
        message += f"📊 **Endpoints Scanned:** {len(results)}\n"
        message += f"✅ **Working Endpoints:** {len(successful)}\n"
        message += f"🔄 **Repeatable Endpoints:** {len(repeatable)}\n"
        message += f"💰 **Total Coins Available:** {total_coins:,}\n\n"
        
        if repeatable:
            message += "=" * 40 + "\n"
            message += "🎯 **REPEATABLE ENDPOINTS** (Best for mining)\n"
            message += "=" * 40 + "\n\n"
            
            for r in repeatable:
                message += f"📍 `{r['endpoint']}`\n"
                message += f"💰 Coins per claim: {r['coin_amount']:,}\n"
                message += f"🔄 Can repeat: YES\n\n"
        
        if successful:
            message += "=" * 40 + "\n"
            message += "✅ **OTHER WORKING ENDPOINTS**\n"
            message += "=" * 40 + "\n\n"
            
            for r in successful:
                if not r['repeatable']:
                    message += f"📍 `{r['endpoint']}` - {r['coin_amount']:,} coins\n"
        
        return message

# ==================== TELEGRAM BOT ====================
miner = FishMyaMiner(GAME_URL, ACCESS_TOKEN)
mining_tasks = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome = (
        f"👋 **Welcome {user.first_name}!**\n\n"
        f"🎣 **FishMya Auto Miner Bot**\n"
        f"⚡ Powered by GHOST AI\n\n"
        f"🔐 **Login Status:** Checking...\n"
        f"💰 **Total Mined:** {miner.total_mined:,} coins\n\n"
        f"📋 **Commands:**\n"
        f"`/check` - Check login status\n"
        f"`/scan` - Scan for coin endpoints\n"
        f"`/mine` - Start auto mining\n"
        f"`/stop` - Stop mining\n"
        f"`/balance` - Check mined balance\n"
        f"`/help` - Show help\n\n"
        f"🎯 **Quick Actions:**"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔐 Check Login", callback_data="check_login"),
            InlineKeyboardButton("🔍 Scan Coins", callback_data="scan_coins")
        ],
        [
            InlineKeyboardButton("⛏️ Start Mining", callback_data="start_mining"),
            InlineKeyboardButton("🛑 Stop Mining", callback_data="stop_mining")
        ],
        [
            InlineKeyboardButton("💰 Check Balance", callback_data="check_balance"),
            InlineKeyboardButton("📊 Status", callback_data="status")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode='Markdown')

async def check_login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check login status"""
    message = await update.message.reply_text("🔐 Checking login status...")
    
    result = await miner.check_login()
    
    if result['valid']:
        status_msg = (
            f"✅ **Login Valid**\n"
            f"💰 Current Balance: {result['balance']:,} coins\n"
            f"📱 Phone: {PHONE_NUMBER}\n"
            f"🔑 Token: Active\n"
            f"⏰ Checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        status_msg = (
            f"❌ **Login Invalid**\n"
            f"⚠️ {result['message']}\n"
            f"🔄 Need to update access token"
        )
    
    await message.edit_text(status_msg, parse_mode='Markdown')

async def scan_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Scan for coin endpoints"""
    message = await update.message.reply_text("🔍 Scanning for coin endpoints...\n\n⏳ This may take a minute...")
    
    results = await miner.scan_all_endpoints()
    formatted = miner.format_results(results)
    
    await message.edit_text(formatted, parse_mode='Markdown')
    
    repeatable = [r for r in results if r['success'] and r['repeatable']]
    
    if repeatable:
        keyboard = [
            [InlineKeyboardButton("⛏️ Start Mining Now", callback_data="start_mining")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎯 **Found {len(repeatable)} repeatable endpoints!**\n"
            f"💰 Total potential: {sum(r['coin_amount'] for r in repeatable):,} coins per claim\n\n"
            f"Click below to start auto-mining!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def mine_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start auto mining"""
    chat_id = update.effective_chat.id
    
    if miner.mining_active:
        await update.message.reply_text("⛏️ Mining is already running!")
        return
    
    message = await update.message.reply_text("⛏️ Starting auto-miner...\n\n🔄 This will run continuously!")
    
    # Check if we have endpoints first
    if not miner.found_endpoints:
        await message.edit_text("🔍 No endpoints found. Scanning first...")
        await miner.scan_all_endpoints()
    
    repeatable = [r for r in miner.found_endpoints if r['repeatable']]
    
    if not repeatable:
        await message.edit_text("❌ No repeatable endpoints found. Try scanning again.")
        return
    
    # Start mining in background
    task = asyncio.create_task(miner.auto_mine_loop(chat_id, context.bot))
    mining_tasks[chat_id] = task
    
    await message.edit_text(
        f"✅ **Auto-Miner Started!**\n\n"
        f"🔄 Mining from {len(repeatable)} endpoints\n"
        f"💰 Total mined so far: {miner.total_mined:,} coins\n\n"
        f"Use /stop to stop mining"
    )

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop auto mining"""
    chat_id = update.effective_chat.id
    
    miner.mining_active = False
    
    if chat_id in mining_tasks:
        mining_tasks[chat_id].cancel()
        del mining_tasks[chat_id]
    
    await update.message.reply_text(
        f"🛑 **Mining Stopped!**\n\n"
        f"💰 Total Mined: {miner.total_mined:,} coins"
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check mined balance"""
    await update.message.reply_text(
        f"💰 **Mining Statistics**\n\n"
        f"🪙 Total Coins Mined: {miner.total_mined:,}\n"
        f"📊 Endpoints Found: {len(miner.found_endpoints)}\n"
        f"🔄 Mining Status: {'Active' if miner.mining_active else 'Inactive'}\n"
        f"⏰ Last Scan: {miner.last_scan_time.strftime('%Y-%m-%d %H:%M:%S') if miner.last_scan_time else 'Never'}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = (
        "📚 **FishMya Auto Miner Help**\n\n"
        "🔹 **Commands:**\n"
        "`/start` - Start bot\n"
        "`/check` - Check login status\n"
        "`/scan` - Scan for coin endpoints\n"
        "`/mine` - Start auto mining\n"
        "`/stop` - Stop mining\n"
        "`/balance` - Check mined balance\n"
        "`/help` - Show this help\n\n"
        "🔹 **Features:**\n"
        "✅ Auto-login validation\n"
        "✅ Multi-endpoint scanning\n"
        "✅ Repeatable endpoint detection\n"
        "✅ Continuous auto-mining\n"
        "✅ Real-time balance tracking\n\n"
        "⚡ **Powered by GHOST AI**"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_login":
        await query.edit_message_text("🔐 Checking login...")
        result = await miner.check_login()
        
        if result['valid']:
            await query.edit_message_text(
                f"✅ **Login Valid**\n"
                f"💰 Balance: {result['balance']:,} coins\n"
                f"📱 Phone: {PHONE_NUMBER}"
            )
        else:
            await query.edit_message_text(
                f"❌ **Login Invalid**\n"
                f"⚠️ {result['message']}"
            )
    
    elif query.data == "scan_coins":
        await query.edit_message_text("🔍 Scanning for coins...")
        results = await miner.scan_all_endpoints()
        formatted = miner.format_results(results)
        await query.edit_message_text(formatted, parse_mode='Markdown')
    
    elif query.data == "start_mining":
        chat_id = query.message.chat_id
        
        if miner.mining_active:
            await query.edit_message_text("⛏️ Mining already running!")
            return
        
        if not miner.found_endpoints:
            await query.edit_message_text("🔍 Scanning first...")
            await miner.scan_all_endpoints()
        
        repeatable = [r for r in miner.found_endpoints if r['repeatable']]
        
        if repeatable:
            task = asyncio.create_task(miner.auto_mine_loop(chat_id, context.bot))
            mining_tasks[chat_id] = task
            
            await query.edit_message_text(
                f"✅ **Mining Started!**\n"
                f"🔄 {len(repeatable)} endpoints\n"
                f"💰 Total mined: {miner.total_mined:,}"
            )
        else:
            await query.edit_message_text("❌ No repeatable endpoints found")
    
    elif query.data == "stop_mining":
        miner.mining_active = False
        
        chat_id = query.message.chat_id
        if chat_id in mining_tasks:
            mining_tasks[chat_id].cancel()
            del mining_tasks[chat_id]
        
        await query.edit_message_text(
            f"🛑 **Mining Stopped**\n"
            f"💰 Total: {miner.total_mined:,} coins"
        )
    
    elif query.data == "check_balance":
        await query.edit_message_text(
            f"💰 **Balance**\n\n"
            f"🪙 Total Mined: {miner.total_mined:,}\n"
            f"📊 Endpoints: {len(miner.found_endpoints)}\n"
            f"🔄 Status: {'Active' if miner.mining_active else 'Inactive'}"
        )
    
    elif query.data == "status":
        login_result = await miner.check_login()
        await query.edit_message_text(
            f"📊 **System Status**\n\n"
            f"🔐 Login: {'✅ Valid' if login_result['valid'] else '❌ Invalid'}\n"
            f"💰 Balance: {login_result['balance']:,} coins\n"
            f"⛏️ Mining: {'Active' if miner.mining_active else 'Inactive'}\n"
            f"🪙 Total Mined: {miner.total_mined:,}\n"
            f"📱 Phone: {PHONE_NUMBER}"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Main function"""
    print("""
    ╔══════════════════════════════════════════╗
    ║   🎣 FishMya Auto Miner Bot v2.0        ║
    ║   Created by GHOST AI                   ║
    ║   GitHub Actions Ready                  ║
    ╚══════════════════════════════════════════╝
    """)
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("check", check_login_command))
    application.add_handler(CommandHandler("scan", scan_command))
    application.add_handler(CommandHandler("mine", mine_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    print("🚀 Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
