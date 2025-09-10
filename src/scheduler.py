"""
Scheduler
Gestisce il posting automatico agli orari prestabiliti
"""

import os
import sys
import asyncio
import logging
import schedule
import time
from datetime import datetime, timedelta
import pytz
from typing import List, Dict
from dotenv import load_dotenv

# Setup path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.instant_gaming import InstantGamingScraper
from scrapers.gamivo import GamivoScraper
from utils.brislyscore import BrislyScore
from bot.telegram_poster import TelegramPoster
from database.redis_client import RedisClient

# Load environment
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotScheduler:
    """Scheduler per posting automatico"""
    
    def __init__(self):
        self.timezone = pytz.timezone('Europe/Rome')
        self.ig_scraper = InstantGamingScraper()
        self.gv_scraper = GamivoScraper()
        self.scorer = BrislyScore()
        self.poster = TelegramPoster()
        self.db = RedisClient()
        
        # Orari di posting (formato 24h)
        self.posting_times = ['08:00', '13:00', '18:00', '21:00']
        
        # Limiti
        self.max_posts_per_session = 2
        self.max_posts_per_day = 10
        
        logger.info("🤖 Scheduler inizializzato")
        logger.info(f"⏰ Orari posting: {', '.join(self.posting_times)}")
    
    def collect_best_deals(self) -> List[Dict]:
        """Raccoglie e filtra le migliori offerte"""
        all_deals = []
        
        # Raccolta da tutte le fonti
        logger.info("📥 Raccolta offerte...")
        
        ig_deals = self.ig_scraper.scrape_deals(10)
        all_deals.extend(ig_deals)
        
        gv_deals = self.gv_scraper.scrape_deals(10)
        all_deals.extend(gv_deals)
        
        if not all_deals:
            logger.warning("⚠️ Nessuna offerta trovata")
            return []
        
        # Calcola BrislyScore
        for deal in all_deals:
            score_data = self.scorer.calculate(deal)
            deal['brislyscore_data'] = score_data
            deal['brislyscore'] = score_data['score']
        
        # Ordina per score
        all_deals.sort(key=lambda x: x['brislyscore'], reverse=True)
        
        # Filtra solo offerte valide e non già postate
        filtered = []
        for deal in all_deals:
            # Skip se già postata
            deal_id = self.db._generate_deal_id(deal)
            if self.db.is_deal_posted(deal_id):
                continue
                
            # Filtri qualità
            if deal['brislyscore'] < 15:
                continue
            if deal.get('discount_percent', 0) < 30:
                continue
                
            filtered.append(deal)
        
        logger.info(f"✅ {len(filtered)} offerte valide trovate")
        return filtered
    
    async def post_scheduled_deals(self):
        """Posta le offerte negli orari schedulati"""
        try:
            # Check limite giornaliero
            posted_today = self.db.get_posted_count_today()
            if posted_today >= self.max_posts_per_day:
                logger.warning(f"⚠️ Limite giornaliero raggiunto ({posted_today}/{self.max_posts_per_day})")
                return
            
            # Trova migliori deals
            deals = self.collect_best_deals()
            
            if not deals:
                logger.info("📭 Nessuna nuova offerta da postare")
                return
            
            # Posta fino a max_posts_per_session offerte
            to_post = deals[:self.max_posts_per_session]
            
            logger.info(f"📤 Posting {len(to_post)} offerte...")
            
            for i, deal in enumerate(to_post, 1):
                logger.info(f"📮 [{i}/{len(to_post)}] {deal['title']}")
                
                # Invia a Telegram
                success = await self.poster.send_deal(
                    deal,
                    deal['brislyscore_data']
                )
                
                if success:
                    # Marca come postata nel database
                    self.db.mark_deal_posted(deal)
                    self.db.increment_stat('total_posts')
                    self.db.increment_stat(f"posts_{deal['source']}")
                    logger.info(f"✅ Postata con successo!")
                else:
                    logger.error(f"❌ Errore nel posting")
                
                # Delay tra posts
                if i < len(to_post):
                    await asyncio.sleep(5)
            
            # Log statistiche
            stats = self.db.get_all_stats()
            logger.info(f"📊 Stats - Totale posts: {stats.get('total_posts', 0)}")
            
        except Exception as e:
            logger.error(f"❌ Errore in post_scheduled_deals: {e}")
    
    def job_wrapper(self):
        """Wrapper per eseguire job async in schedule"""
        logger.info(f"⏰ Esecuzione job schedulato - {datetime.now().strftime('%H:%M')}")
        asyncio.run(self.post_scheduled_deals())
    
    def setup_schedule(self):
        """Configura gli orari di posting"""
        # Clear schedule precedenti
        schedule.clear()
        
        # Setup posting times
        for time_str in self.posting_times:
            schedule.every().day.at(time_str).do(self.job_wrapper)
            logger.info(f"⏰ Schedulato posting alle {time_str}")
        
        # Job speciali
        schedule.every().day.at("00:00").do(self.daily_reset)
        schedule.every().sunday.at("12:00").do(self.weekly_recap)
        
        logger.info("📅 Schedule configurato con successo")
    
    def daily_reset(self):
        """Reset giornaliero delle statistiche"""
        logger.info("🔄 Reset giornaliero statistiche")
        # Qui puoi aggiungere logica di reset se necessaria
    
    def weekly_recap(self):
        """Recap settimanale della domenica"""
        logger.info("📊 Generazione recap settimanale")
        # TODO: Implementare recap settimanale
    
    def run_forever(self):
        """Loop principale dello scheduler"""
        logger.info("🚀 Scheduler avviato!")
        logger.info(f"⏰ Ora corrente: {datetime.now(self.timezone).strftime('%H:%M:%S %Z')}")
        logger.info(f"📅 Prossimi job: {self.posting_times}")
        
        # Setup schedule
        self.setup_schedule()
        
        # Test immediato se richiesto
        if os.getenv('TEST_ON_START', 'false').lower() == 'true':
            logger.info("🧪 Test immediato richiesto...")
            self.job_wrapper()
        
        # Loop principale
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check ogni minuto
                
                # Log ogni ora
                if datetime.now().minute == 0:
                    logger.info(f"💓 Heartbeat - {datetime.now().strftime('%H:%M')} - Jobs pending: {len(schedule.jobs)}")
                    
            except KeyboardInterrupt:
                logger.info("⏹️ Scheduler fermato dall'utente")
                break
            except Exception as e:
                logger.error(f"❌ Errore nel loop principale: {e}")
                time.sleep(60)
    
    def run_once(self):
        """Esegue un singolo posting (per test)"""
        logger.info("🧪 Esecuzione singola...")
        asyncio.run(self.post_scheduled_deals())

def main():
    """Main entry point"""
    scheduler = BotScheduler()
    
    # Check argomenti
    if len(sys.argv) > 1:
        if sys.argv[1] == 'once':
            # Esegui una volta sola
            scheduler.run_once()
        elif sys.argv[1] == 'test':
            # Test mode
            os.environ['TEST_ON_START'] = 'true'
            scheduler.run_forever()
    else:
        # Menu interattivo
        print("\n" + "="*50)
        print("🤖 BRISLY GAMING BOT - SCHEDULER")
        print("="*50)
        print("\n1. 🔄 Avvia scheduler continuo (24/7)")
        print("2. 📤 Esegui posting singolo ora")
        print("3. 🧪 Test immediato + scheduler")
        print("0. ❌ Esci")
        
        choice = input("\nScelta: ")
        
        if choice == "1":
            scheduler.run_forever()
        elif choice == "2":
            scheduler.run_once()
        elif choice == "3":
            os.environ['TEST_ON_START'] = 'true'
            scheduler.run_forever()
        else:
            print("👋 Arrivederci!")

if __name__ == "__main__":
    main()