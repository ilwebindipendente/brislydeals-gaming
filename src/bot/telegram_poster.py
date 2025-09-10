"""
Telegram Poster
Gestisce l'invio dei post al canale Telegram
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

class TelegramPoster:
    """Gestisce posting su Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID', '@BrislyDealsGaming')
        
        if not self.bot_token:
            raise ValueError("❌ TELEGRAM_BOT_TOKEN non configurato!")
            
        self.bot = Bot(token=self.bot_token)
        logger.info(f"✅ TelegramPoster inizializzato per {self.channel_id}")
    
    def format_deal_message(self, deal: Dict, score_data: Dict = None) -> str:
        """
        Formatta il messaggio per un'offerta
        
        Args:
            deal: Dati dell'offerta
            score_data: Dati BrislyScore (opzionale)
            
        Returns:
            Messaggio formattato
        """
        # Emoji per fonte
        source_emoji = "🎮" if deal['source'] == 'instant_gaming' else "🌐"
        
        # Titolo e sconto
        message = f"{source_emoji} *{deal['discount_percent']}% DI SCONTO* {source_emoji}\n"
        message += f"*{deal['title']}* - {deal['platform']}\n\n"
        
        # Prezzi
        message += f"💰 Era: ~{deal['original_price']}€~\n"
        message += f"🎯 Ora: *{deal['discounted_price']}€*\n"
        
        # Calcola risparmio
        savings = deal['original_price'] - deal['discounted_price']
        message += f"📈 Risparmi: *{savings:.2f}€*\n\n"
        
        # Metacritic se disponibile
        if deal.get('metacritic_score', 0) > 0:
            message += f"🏆 Metacritic: {deal['metacritic_score']}/100\n"
        
        # Anno e genere
        if deal.get('release_year'):
            message += f"📅 Anno: {deal['release_year']}\n"
        if deal.get('genre'):
            message += f"🎮 Genere: {deal['genre']}\n"
        
        # Early Access o caratteristiche speciali
        if deal.get('early_access'):
            message += f"⚠️ *EARLY ACCESS*\n"
        if deal.get('is_historical_low'):
            message += f"🔥 *MINIMO STORICO!*\n"
        
        message += "\n"
        
        # BrislyScore se disponibile
        if score_data:
            message += f"{score_data['emoji']} *BrislyScore™: {score_data['score']}/45*\n"
            message += f"_{score_data['tier'].replace('_', ' ')}_\n"
            message += f"💬 {score_data['recommendation']}\n\n"
        
        # Tags
        tags = self._generate_tags(deal)
        message += f"#️⃣ {' '.join(tags)}\n\n"
        
        # Footer
        message += "⚡ *OFFERTA LIMITATA* ⚡"
        
        return message
    
    def _generate_tags(self, deal: Dict) -> List[str]:
        """Genera hashtag per il post"""
        tags = []
        
        # Platform tag
        platform = deal.get('platform', 'Steam').replace(' ', '')
        tags.append(f"#{platform}")
        
        # Genre tag
        if deal.get('genre'):
            tags.append(f"#{deal['genre']}")
        
        # Metacritic tier
        score = deal.get('metacritic_score', 0)
        if score >= 90:
            tags.append("#MetaCritic90Plus")
        elif score >= 80:
            tags.append("#MetaCritic80Plus")
        elif score >= 70:
            tags.append("#MetaCritic70Plus")
        elif score >= 60:
            tags.append("#MetaCritic60Plus")
        
        # Source tag
        if deal['source'] == 'instant_gaming':
            tags.append("#InstantGaming")
        else:
            tags.append("#GAMIVO")
        
        # Special tags
        if deal.get('early_access'):
            tags.append("#EarlyAccess")
        if deal.get('is_historical_low'):
            tags.append("#MinimoStorico")
        if deal.get('is_aaa'):
            tags.append("#AAA")
        if deal['discount_percent'] >= 70:
            tags.append("#SuperOfferta")
            
        return tags
    
    def create_keyboard(self, deal: Dict) -> InlineKeyboardMarkup:
        """
        Crea tastiera inline per il post
        
        Args:
            deal: Dati dell'offerta
            
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = []
        
        # Prima riga - Link all'offerta
        source_name = "INSTANT GAMING" if deal['source'] == 'instant_gaming' else "GAMIVO"
        keyboard.append([
            InlineKeyboardButton(
                f"🎮 SCOPRI L'OFFERTA SU {source_name}",
                url=deal['url']
            )
        ])
        
        # Seconda riga - Link BrislyDeals
        keyboard.append([
            InlineKeyboardButton(
                "🌐 VISITA BRISLYDEALS",
                url="https://www.brislydeals.com"
            )
        ])
        
        # Terza riga - Segnalazione
        keyboard.append([
            InlineKeyboardButton(
                "⚠️ SEGNALA ERRORE",
                url="https://t.me/BrislyDealsGaming"  # Per ora link al canale
            )
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def send_deal(self, deal: Dict, score_data: Dict = None, test_mode: bool = False) -> bool:
        """
        Invia un'offerta al canale
        
        Args:
            deal: Dati dell'offerta
            score_data: Dati BrislyScore (opzionale)
            test_mode: Se True, logga solo senza inviare
            
        Returns:
            True se inviato con successo
        """
        try:
            message = self.format_deal_message(deal, score_data)
            keyboard = self.create_keyboard(deal)
            
            if test_mode:
                logger.info("🧪 TEST MODE - Messaggio che verrebbe inviato:")
                logger.info(f"\n{message}")
                return True
            
            # Invia messaggio
            result = await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                disable_web_page_preview=False
            )
            
            logger.info(f"✅ Offerta inviata: {deal['title']} - Message ID: {result.message_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"❌ Errore Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Errore generico: {e}")
            return False
    
    async def send_multiple_deals(self, deals: List[Dict], delay_seconds: int = 5) -> int:
        """
        Invia multiple offerte con delay
        
        Args:
            deals: Lista di offerte
            delay_seconds: Secondi tra un post e l'altro
            
        Returns:
            Numero di offerte inviate con successo
        """
        sent_count = 0
        
        for i, deal in enumerate(deals, 1):
            logger.info(f"📤 Invio offerta {i}/{len(deals)}: {deal['title']}")
            
            success = await self.send_deal(deal)
            if success:
                sent_count += 1
            
            # Delay tra i post (tranne l'ultimo)
            if i < len(deals) and delay_seconds > 0:
                logger.info(f"⏰ Attendo {delay_seconds} secondi...")
                await asyncio.sleep(delay_seconds)
        
        logger.info(f"📊 Inviate {sent_count}/{len(deals)} offerte")
        return sent_count
    
    async def send_test_message(self) -> bool:
        """Invia messaggio di test al canale"""
        try:
            test_message = (
                "🧪 *TEST BOT BRISLY GAMING* 🧪\n\n"
                f"✅ Bot connesso correttamente!\n"
                f"🤖 Bot: @BrislyGamingBot\n"
                f"📢 Canale: {self.channel_id}\n"
                f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                "_Questo è un messaggio di test_"
            )
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("✅ TEST RIUSCITO", callback_data="test_ok")
            ]])
            
            result = await self.bot.send_message(
                chat_id=self.channel_id,
                text=test_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
            logger.info(f"✅ Messaggio di test inviato! ID: {result.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore invio test: {e}")
            return False

# Test del modulo
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from dotenv import load_dotenv
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        poster = TelegramPoster()
        
        # Test message
        print("\n🧪 Invio messaggio di test...")
        success = await poster.send_test_message()
        
        if success:
            print("✅ Test completato con successo!")
        else:
            print("❌ Test fallito!")
    
    # Run test
    asyncio.run(test())