"""
Instant Gaming Scraper
Estrae le migliori offerte da Instant Gaming
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime
from .mock_data import MockDataProvider

logger = logging.getLogger(__name__)

class InstantGamingScraper:
    """Scraper per Instant Gaming deals"""
    
    def __init__(self):
        self.base_url = "https://www.instant-gaming.com/it/"
        self.affiliate_tag = "?igr=giochigameplay"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_deals(self, max_deals: int = 10) -> List[Dict]:
        """
        Scraping delle migliori offerte
        TEMPORANEO: Usa mock data mentre fixiamo lo scraping reale
        """
        logger.info("🎮 Usando MOCK DATA per Instant Gaming (temporaneo)")
        
        # USA MOCK DATA
        provider = MockDataProvider()
        deals = provider.get_instant_gaming_deals(max_deals)
        
        logger.info(f"✅ Trovate {len(deals)} offerte mock da Instant Gaming")
        return deals
    
    def get_deal_details(self, game_url: str) -> Optional[Dict]:
        """
        Ottiene dettagli specifici di un gioco
        
        Args:
            game_url: URL della pagina del gioco
            
        Returns:
            Dizionario con i dettagli o None
        """
        # TODO: Implementare scraping dettagliato quando risolviamo il blocco
        logger.info(f"📝 get_deal_details non ancora implementato per: {game_url}")
        return None
    
    def calculate_savings(self, original: float, discounted: float) -> Dict:
        """
        Calcola risparmio e percentuale
        """
        savings = original - discounted
        percent = int((savings / original) * 100)
        
        return {
            'savings_amount': round(savings, 2),
            'savings_percent': percent
        }

# Test rapido
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = InstantGamingScraper()
    deals = scraper.scrape_deals()
    
    for deal in deals:
        print(f"\n🎮 {deal['title']}")
        print(f"💰 {deal['original_price']}€ → {deal['discounted_price']}€")
        print(f"📊 Sconto: {deal['discount_percent']}%")