"""
Instant Gaming Scraper
Estrae le migliori offerte da Instant Gaming
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime

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
        
        Returns:
            Lista di dizionari con i dati delle offerte
        """
        deals = []
        
        try:
            # URL delle offerte principali
            url = f"{self.base_url}search/?discount=50"
            
            logger.info(f"🔍 Scraping Instant Gaming: {url}")
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"❌ Errore HTTP: {response.status_code}")
                return deals
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # TODO: Implementare parsing reale della pagina
            # Per ora ritorniamo dati di esempio
            
            example_deal = {
                'source': 'instant_gaming',
                'title': 'Cyberpunk 2077',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 19.99,
                'discount_percent': 67,
                'url': f"{self.base_url}esempio{self.affiliate_tag}",
                'image_url': None,
                'metacritic_score': 86,
                'release_year': 2020,
                'scraped_at': datetime.now().isoformat()
            }
            
            deals.append(example_deal)
            logger.info(f"✅ Trovate {len(deals)} offerte da Instant Gaming")
            
        except Exception as e:
            logger.error(f"❌ Errore scraping: {e}")
            
        return deals
    
    def get_deal_details(self, game_url: str) -> Optional[Dict]:
        """
        Ottiene dettagli specifici di un gioco
        
        Args:
            game_url: URL della pagina del gioco
            
        Returns:
            Dizionario con i dettagli o None
        """
        # TODO: Implementare scraping dettagliato
        pass
    
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