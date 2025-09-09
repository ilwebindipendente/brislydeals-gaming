"""
Configurazioni principali del bot
"""

import os
from datetime import time
from typing import List, Dict

# ==========================================
# TELEGRAM SETTINGS
# ==========================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '@BrislyDealsGaming')
TELEGRAM_CHANNEL_LINK = 'https://t.me/BrislyDealsGaming'

# ==========================================
# POSTING SCHEDULE
# ==========================================
# Orari di posting (formato 24h)
POSTING_TIMES = [
    time(8, 0),   # 08:00
    time(13, 0),  # 13:00
    time(18, 0),  # 18:00
    time(21, 0),  # 21:00
]

# Limiti posting
MAX_POSTS_PER_DAY = 10
MIN_HOURS_BETWEEN_SIMILAR = 2
SATURDAY_PAUSE = True  # Pausa il sabato
SUNDAY_RECAP = True    # Recap domenicale

# ==========================================
# SCRAPING SETTINGS
# ==========================================
SCRAPING_INTERVAL_MINUTES = 30
SOURCES = {
    'instant_gaming': {
        'enabled': True,
        'base_url': 'https://www.instant-gaming.com/it/',
        'affiliate': '?igr=giochigameplay',
        'min_discount': 30,
    },
    'gamivo': {
        'enabled': True,
        'base_url': 'https://www.gamivo.com/',
        'affiliate': '?glv=indiedealsgaming',
        'min_discount': 30,
    }
}

# ==========================================
# BRISLYSCORE™ SETTINGS
# ==========================================
BRISLYSCORE_WEIGHTS = {
    'metacritic': 0.3,      # 30% peso
    'discount': 0.3,        # 30% peso
    'price_value': 0.25,    # 25% peso
    'popularity': 0.15,     # 15% peso
}

BRISLYSCORE_TIERS = {
    'SUPER_DEAL': 36,     # 💎 SUPER OFFERTA!
    'GREAT_DEAL': 26,     # 🔥 Ottima OFFERTA!
    'GOOD_DEAL': 16,      # 👍 L'Offerta è buona!
    'OK_DEAL': 0,         # 😐 Offerta non male
}

# ==========================================
# QUALITY FILTERS
# ==========================================
FILTERS = {
    'min_metacritic': 50,
    'exclude_dlc_standalone': True,
    'allow_early_access': True,
    'max_price': 100,
    'min_discount_percent': 30,
}

# ==========================================
# POST PRIORITIES
# ==========================================
PRIORITY_RULES = {
    'HIGH': {
        'discount_min': 70,
        'metacritic_min': 85,
        'price_max': 10,
        'post_delay_minutes': 0,
    },
    'MEDIUM': {
        'discount_min': 50,
        'metacritic_min': 70,
        'price_max': 30,
        'post_delay_minutes': 120,
    },
    'LOW': {
        'discount_min': 30,
        'metacritic_min': 50,
        'price_max': 100,
        'post_delay_minutes': 240,
    }
}

# ==========================================
# MESSAGE TEMPLATES
# ==========================================
POST_TEMPLATE = """
🔥 {discount_percent}% DI SCONTO 🔥
{game_title} - {platform}

💰 Era: ~~{original_price}€~~
🎯 Ora: {discounted_price}€
📈 Risparmi: {savings}€

🏆 Metacritic: {metacritic}/100
📅 Anno: {year}

#️⃣ Tags:
{tags}

⚡ OFFERTA LIMITATA ⚡
"""

# ==========================================
# DATABASE SETTINGS
# ==========================================
REDIS_URL = os.getenv('UPSTASH_REDIS_URL')
REDIS_TOKEN = os.getenv('UPSTASH_REDIS_TOKEN')
CACHE_EXPIRY_HOURS = 24

# ==========================================
# DEVELOPMENT
# ==========================================
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
TIMEZONE = 'Europe/Rome'