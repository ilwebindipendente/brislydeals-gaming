"""
GAMIVO Scraper
Estrae le migliori offerte da GAMIVO.com
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from .mock_data import MockDataProvider

logger = logging.getLogger(__name__)

class GamivoScraper:
    """Scraper per GAMIVO deals"""
    
    def __init__(self):
        self.base_url = "https://www.gamivo.com"
        self.affiliate_tag = "?glv=indiedealsgaming"
        self.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
}
        
    def scrape_deals(self, max_deals: int = 10) -> List[Dict]:
        """
        Scraping delle migliori offerte GAMIVO
        TEMPORANEO: Usa mock data mentre fixiamo lo scraping reale
        """
        logger.info("🎮 Usando MOCK DATA per GAMIVO (temporaneo)")
        
        # USA MOCK DATA
        provider = MockDataProvider()
        deals = provider.get_gamivo_deals(max_deals)
        
        logger.info(f"✅ Trovate {len(deals)} offerte mock da GAMIVO")
        return deals
        
        try:
            # GAMIVO usa /it per italiano e ha una sezione deals
            urls_to_try = [
                f"{self.base_url}/it/top-deals",
                f"{self.base_url}/it/games/bestsellers",
                f"{self.base_url}/it/pc-games"
            ]
            
            for url in urls_to_try:
                logger.info(f"🔍 Tentativo scraping GAMIVO: {url}")
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # GAMIVO structure (potrebbero cambiare)
                        # Cerca diversi possibili selettori
                        game_selectors = [
                            'div.product-tile',
                            'div.game-card',
                            'article.product',
                            'div[data-product]',
                            'a.product-link'
                        ]
                        
                        games_found = False
                        for selector in game_selectors:
                            game_cards = soup.select(selector)
                            if game_cards:
                                logger.info(f"✅ Trovati {len(game_cards)} giochi con selector: {selector}")
                                games_found = True
                                
                                for card in game_cards[:max_deals]:
                                    deal = self._parse_game_card(card)
                                    if deal and deal['discount_percent'] >= 30:  # Min 30% sconto
                                        deals.append(deal)
                                break
                        
                        if not games_found:
                            logger.warning(f"⚠️ Nessun gioco trovato su {url}")
                            # Proviamo a loggare parte dell'HTML per debug
                            logger.debug(f"HTML sample: {str(soup)[:500]}")
                    else:
                        logger.error(f"❌ HTTP {response.status_code} per {url}")
                        
                except Exception as e:
                    logger.error(f"❌ Errore su {url}: {e}")
                    continue
                    
                if deals:
                    break  # Se abbiamo trovato deals, fermiamoci
            
            # Se non troviamo nulla, mettiamo un esempio
            if not deals:
                logger.info("📦 Usando dati esempio per GAMIVO")
                example_deal = {
                    'source': 'gamivo',
                    'title': 'Hogwarts Legacy',
                    'platform': 'Steam',
                    'original_price': 69.99,
                    'discounted_price': 29.99,
                    'discount_percent': 57,
                    'url': f"{self.base_url}/product/hogwarts-legacy{self.affiliate_tag}",
                    'image_url': None,
                    'metacritic_score': 83,
                    'release_year': 2023,
                    'seller_rating': 99.8,
                    'region': 'Global',
                    'scraped_at': datetime.now().isoformat()
                }
                deals.append(example_deal)
            
            logger.info(f"✅ Totale offerte GAMIVO trovate: {len(deals)}")
            
        except Exception as e:
            logger.error(f"❌ Errore generale scraping GAMIVO: {e}")
            
        return deals
    
    def _parse_game_card(self, card) -> Optional[Dict]:
        """
        Parse di una card gioco da GAMIVO
        
        Args:
            card: BeautifulSoup element della card
            
        Returns:
            Dict con i dati o None
        """
        try:
            deal = {'source': 'gamivo'}
            
            # Titolo - prova diversi selettori
            title_selectors = [
                'h3', 'h4', 'h2',
                '.product-name', '.game-title',
                'a[title]', '[data-name]'
            ]
            
            for selector in title_selectors:
                title_elem = card.select_one(selector)
                if title_elem:
                    deal['title'] = title_elem.get_text(strip=True) or title_elem.get('title', '')
                    if deal['title']:
                        break
            
            if not deal.get('title'):
                return None
                
            # Prezzi - cerca in diversi formati
            price_selectors = [
                '.price-current', '.price-new', '.final-price',
                '[data-price]', '.product-price'
            ]
            
            original_selectors = [
                '.price-old', '.price-was', '.original-price',
                'del', 's'
            ]
            
            # Prezzo scontato
            for selector in price_selectors:
                price_elem = card.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = self._extract_price(price_text)
                    if price:
                        deal['discounted_price'] = price
                        break
            
            # Prezzo originale
            for selector in original_selectors:
                orig_elem = card.select_one(selector)
                if orig_elem:
                    orig_text = orig_elem.get_text(strip=True)
                    orig_price = self._extract_price(orig_text)
                    if orig_price:
                        deal['original_price'] = orig_price
                        break
            
            # Se non troviamo prezzi, skip
            if 'discounted_price' not in deal:
                return None
                
            # Se manca il prezzo originale, stimalo
            if 'original_price' not in deal:
                # Cerca percentuale sconto
                discount_elem = card.select_one('.discount, .badge-discount, [class*="discount"]')
                if discount_elem:
                    discount_text = discount_elem.get_text(strip=True)
                    discount = self._extract_discount(discount_text)
                    if discount:
                        deal['discount_percent'] = discount
                        # Calcola prezzo originale dalla percentuale
                        deal['original_price'] = round(deal['discounted_price'] / (1 - discount/100), 2)
                else:
                    # Assume 30% di default
                    deal['discount_percent'] = 30
                    deal['original_price'] = round(deal['discounted_price'] * 1.43, 2)
            else:
                # Calcola percentuale
                savings = deal['original_price'] - deal['discounted_price']
                deal['discount_percent'] = int((savings / deal['original_price']) * 100)
            
            # URL del prodotto
            link = card.select_one('a[href*="/product/"], a[href*="/it/"]')
            if link:
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = self.base_url + href
                deal['url'] = href + self.affiliate_tag
            else:
                deal['url'] = self.base_url + self.affiliate_tag
                
            # Piattaforma (default Steam se non trovata)
            deal['platform'] = 'Steam'
            platform_elem = card.select_one('[class*="platform"], [data-platform]')
            if platform_elem:
                platform_text = platform_elem.get_text(strip=True).lower()
                if 'epic' in platform_text:
                    deal['platform'] = 'Epic'
                elif 'uplay' in platform_text or 'ubisoft' in platform_text:
                    deal['platform'] = 'Uplay'
                elif 'origin' in platform_text or 'ea' in platform_text:
                    deal['platform'] = 'Origin'
                elif 'gog' in platform_text:
                    deal['platform'] = 'GOG'
                    
            # Altri dati
            deal['metacritic_score'] = 0  # TODO: implementare
            deal['release_year'] = 2023  # TODO: implementare
            deal['scraped_at'] = datetime.now().isoformat()
            
            return deal
            
        except Exception as e:
            logger.debug(f"Errore parsing card: {e}")
            return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Estrae il prezzo da una stringa"""
        import re
        # Rimuovi tutto tranne numeri, virgole e punti
        price_text = re.sub(r'[^\d,.]', '', text)
        # Sostituisci virgola con punto
        price_text = price_text.replace(',', '.')
        try:
            return float(price_text)
        except:
            return None
            
    def _extract_discount(self, text: str) -> Optional[int]:
        """Estrae la percentuale di sconto"""
        import re
        match = re.search(r'(\d+)\s*%', text)
        if match:
            return int(match.group(1))
        return None

# Test del modulo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*50)
    print("🎮 TEST SCRAPER GAMIVO")
    print("="*50)
    
    scraper = GamivoScraper()
    deals = scraper.scrape_deals(max_deals=5)
    
    for i, deal in enumerate(deals, 1):
        print(f"\n📦 Deal #{i}:")
        print(f"  Titolo: {deal.get('title', 'N/A')}")
        print(f"  Prezzo: {deal.get('original_price', 0)}€ → {deal.get('discounted_price', 0)}€")
        print(f"  Sconto: -{deal.get('discount_percent', 0)}%")
        print(f"  Platform: {deal.get('platform', 'N/A')}")
        print(f"  URL: {deal.get('url', 'N/A')[:50]}...")
    
    print("\n" + "="*50)