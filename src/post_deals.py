"""
Post Deals Script
Unisce scrapers, BrislyScore e posting su Telegram
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Import moduli
from scrapers.instant_gaming import InstantGamingScraper
from scrapers.gamivo import GamivoScraper
from utils.brislyscore import BrislyScore
from bot.telegram_poster import TelegramPoster
from database.redis_client import RedisClient

# Setup
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class DealsPoster:
    """Orchestratore principale per postare deals"""
    
    def __init__(self):
        self.ig_scraper = InstantGamingScraper()
        self.gv_scraper = GamivoScraper()
        self.scorer = BrislyScore()
        self.poster = TelegramPoster()
        self.db = RedisClient()  # AGGIUNGI QUESTA RIGA
        
        logger.info("🎮 DealsPoster inizializzato")
    
    def collect_all_deals(self, max_per_source: int = 5) -> List[Dict]:
        """Raccoglie deals da tutte le fonti"""
        all_deals = []
        
        # Instant Gaming
        logger.info("🔍 Raccolta deals da Instant Gaming...")
        ig_deals = self.ig_scraper.scrape_deals(max_per_source)
        all_deals.extend(ig_deals)
        logger.info(f"  ✅ {len(ig_deals)} deals da IG")
        
        # GAMIVO
        logger.info("🔍 Raccolta deals da GAMIVO...")
        gv_deals = self.gv_scraper.scrape_deals(max_per_source)
        all_deals.extend(gv_deals)
        logger.info(f"  ✅ {len(gv_deals)} deals da GAMIVO")
        
        logger.info(f"📊 Totale deals raccolti: {len(all_deals)}")
        return all_deals
    
    def score_and_rank_deals(self, deals: List[Dict]) -> List[Dict]:
        """Calcola BrislyScore e ordina deals"""
        scored_deals = []
        
        for deal in deals:
            # Calcola score
            score_data = self.scorer.calculate(deal)
            deal['brislyscore_data'] = score_data
            deal['brislyscore'] = score_data['score']
            scored_deals.append(deal)
        
        # Ordina per score (migliori prima)
        scored_deals.sort(key=lambda x: x['brislyscore'], reverse=True)
        
        logger.info("🏆 Top 3 deals per BrislyScore:")
        for i, deal in enumerate(scored_deals[:3], 1):
            logger.info(f"  {i}. {deal['title']}: {deal['brislyscore']}/45 {deal['brislyscore_data']['emoji']}")
        
        return scored_deals
    
    def filter_deals(self, deals: List[Dict], min_score: float = 15, min_discount: int = 30) -> List[Dict]:
        """Filtra deals basandosi su criteri di qualità"""
        filtered = []
        
        for deal in deals:
            # CHECK DATABASE - AGGIUNGI QUESTE RIGHE
            deal_id = self.db._generate_deal_id(deal)
            if self.db.is_deal_posted(deal_id):
                logger.info(f"⏭️ Saltato (già postato): {deal['title']}")
                continue
            # Filtri base
            if deal.get('discount_percent', 0) < min_discount:
                continue
            if deal.get('brislyscore', 0) < min_score:
                continue
            
            # Filtro Metacritic (se disponibile)
            metacritic = deal.get('metacritic_score', 0)
            if metacritic > 0 and metacritic < 50:
                continue
            
            filtered.append(deal)
        
        logger.info(f"🔍 Filtrati: {len(filtered)}/{len(deals)} deals superano i criteri")
        return filtered
    
    async def post_top_deals(self, max_posts: int = 3, test_mode: bool = False):
        """
        Posta i migliori deals su Telegram
        
        Args:
            max_posts: Numero massimo di post
            test_mode: Se True, non invia realmente
        """
        print("\n" + "="*60)
        print("🚀 BRISLY GAMING BOT - POSTING SESSION")
        print("="*60)
        print(f"⏰ Avviato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧪 Test Mode: {'ON' if test_mode else 'OFF'}")
        print("="*60 + "\n")
        
        # 1. Raccolta deals
        print("📥 FASE 1: Raccolta Offerte")
        deals = self.collect_all_deals()
        
        if not deals:
            logger.error("❌ Nessuna offerta trovata!")
            return
        
        # 2. Calcolo score e ranking
        print("\n📊 FASE 2: Calcolo BrislyScore™")
        scored_deals = self.score_and_rank_deals(deals)
        
        # 3. Filtraggio
        print("\n🔍 FASE 3: Filtraggio Qualità")
        filtered_deals = self.filter_deals(scored_deals)
        
        if not filtered_deals:
            logger.warning("⚠️ Nessuna offerta supera i criteri di qualità!")
            return
        
        # 4. Selezione top deals
        top_deals = filtered_deals[:max_posts]
        print(f"\n🏆 FASE 4: Selezione Top {len(top_deals)} Offerte")
        
        for i, deal in enumerate(top_deals, 1):
            score = deal['brislyscore_data']
            print(f"\n{i}. {score['emoji']} {deal['title']}")
            print(f"   Platform: {deal['platform']} | Fonte: {deal['source'].upper()}")
            print(f"   Prezzo: {deal['original_price']}€ → {deal['discounted_price']}€ (-{deal['discount_percent']}%)")
            print(f"   BrislyScore: {score['score']}/45 - {score['tier']}")
        
        # 5. Conferma posting
        print("\n" + "="*60)
        
        if test_mode:
            print("🧪 TEST MODE - Simulo invio senza postare realmente")
            print("="*60)
            
            for deal in top_deals:
                await self.poster.send_deal(
                    deal, 
                    deal['brislyscore_data'],
                    test_mode=True
                )
        else:
            print("📤 INVIO REALE AL CANALE")
            
            # Chiedi conferma
            response = input("\n⚠️ Vuoi procedere con l'invio? (s/n): ")
            
            if response.lower() != 's':
                print("❌ Invio annullato dall'utente")
                return
            
            print("\n📤 Invio in corso...")
            
            sent_count = 0
            for i, deal in enumerate(top_deals, 1):
                print(f"\n📮 Invio {i}/{len(top_deals)}: {deal['title']}...")
                
                success = await self.poster.send_deal(
                    deal,
                    deal['brislyscore_data']
                )
                
                if success:
                    sent_count += 1
                    print(f"   ✅ Inviato con successo!")
                else:
                    print(f"   ❌ Errore nell'invio!")
                
                # Delay tra i post (5 secondi)
                if i < len(top_deals):
                    print(f"   ⏰ Attendo 5 secondi...")
                    await asyncio.sleep(5)
            
            print("\n" + "="*60)
            print(f"✅ COMPLETATO: {sent_count}/{len(top_deals)} offerte inviate")
            print("="*60)
    
    async def post_single_best(self):
        """Posta solo la migliore offerta del momento"""
        deals = self.collect_all_deals()
        
        if not deals:
            logger.error("❌ Nessuna offerta trovata!")
            return
        
        scored_deals = self.score_and_rank_deals(deals)
        filtered_deals = self.filter_deals(scored_deals, min_score=20)
        
        if not filtered_deals:
            logger.warning("⚠️ Nessuna offerta abbastanza buona!")
            return
        
        best_deal = filtered_deals[0]
        score = best_deal['brislyscore_data']
        
        print("\n" + "="*60)
        print("🏆 MIGLIORE OFFERTA DEL MOMENTO")
        print("="*60)
        print(f"{score['emoji']} {best_deal['title']}")
        print(f"Prezzo: {best_deal['original_price']}€ → {best_deal['discounted_price']}€")
        print(f"Sconto: -{best_deal['discount_percent']}%")
        print(f"BrislyScore: {score['score']}/45")
        print(f"Raccomandazione: {score['recommendation']}")
        print("="*60)
        
        response = input("\n📤 Vuoi postare questa offerta? (s/n): ")
        
        if response.lower() == 's':
            success = await self.poster.send_deal(best_deal, score)
            if success:
                print("✅ Offerta postata con successo!")
            else:
                print("❌ Errore nel posting!")

async def main():
    """Main function"""
    poster = DealsPoster()
    
    # Menu
    print("\n" + "🎮"*20)
    print("     BRISLY GAMING BOT - POSTING SYSTEM")
    print("🎮"*20)
    print("\nCosa vuoi fare?")
    print("1. 🧪 Test posting (simula senza inviare)")
    print("2. 📤 Posta TOP 3 offerte")
    print("3. 🏆 Posta SOLO la migliore offerta")
    print("4. 📊 Mostra tutte le offerte senza postare")
    print("0. ❌ Esci")
    
    choice = input("\nScelta (0-4): ")
    
    if choice == "1":
        await poster.post_top_deals(max_posts=3, test_mode=True)
    elif choice == "2":
        await poster.post_top_deals(max_posts=3, test_mode=False)
    elif choice == "3":
        await poster.post_single_best()
    elif choice == "4":
        deals = poster.collect_all_deals()
        scored = poster.score_and_rank_deals(deals)
        for deal in scored[:10]:
            print(f"\n{deal['title']} - {deal['discounted_price']}€ (-{deal['discount_percent']}%)")
            print(f"  BrislyScore: {deal['brislyscore']}/45")
    else:
        print("👋 Arrivederci!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Interrotto dall'utente")