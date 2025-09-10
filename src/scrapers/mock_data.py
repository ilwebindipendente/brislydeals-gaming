"""
Mock Data Provider
Fornisce dati di esempio realistici per testing
"""

from datetime import datetime, timedelta
import random
from typing import List, Dict

class MockDataProvider:
    """Provider di dati mock realistici per testing"""
    
    def __init__(self):
        self.mock_deals = [
            # INSTANT GAMING DEALS
            {
                'source': 'instant_gaming',
                'title': 'Black Myth: Wukong',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 47.99,
                'discount_percent': 20,
                'metacritic_score': 82,
                'release_year': 2024,
                'genre': 'Action',
                'is_aaa': True,
                'early_access': False,
            },
            {
                'source': 'instant_gaming',
                'title': 'Baldur\'s Gate 3',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 41.99,
                'discount_percent': 30,
                'metacritic_score': 96,
                'release_year': 2023,
                'genre': 'RPG',
                'is_aaa': True,
                'early_access': False,
            },
            {
                'source': 'instant_gaming',
                'title': 'Red Dead Redemption 2',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 19.99,
                'discount_percent': 67,
                'metacritic_score': 97,
                'release_year': 2019,
                'genre': 'Action',
                'is_aaa': True,
                'is_historical_low': True,
            },
            {
                'source': 'instant_gaming',
                'title': 'EA SPORTS FC 25',
                'platform': 'Steam',
                'original_price': 69.99,
                'discounted_price': 54.99,
                'discount_percent': 21,
                'metacritic_score': 76,
                'release_year': 2024,
                'genre': 'Sports',
                'is_aaa': True,
            },
            {
                'source': 'instant_gaming',
                'title': 'Cyberpunk 2077: Phantom Liberty',
                'platform': 'Steam',
                'original_price': 29.99,
                'discounted_price': 20.99,
                'discount_percent': 30,
                'metacritic_score': 89,
                'release_year': 2023,
                'genre': 'Action',
                'is_dlc': True,
            },
            {
                'source': 'instant_gaming',
                'title': 'Hades II',
                'platform': 'Steam',
                'original_price': 29.99,
                'discounted_price': 25.49,
                'discount_percent': 15,
                'metacritic_score': 0,  # Early access
                'release_year': 2024,
                'genre': 'Indie',
                'early_access': True,
            },
            {
                'source': 'instant_gaming',
                'title': 'The Witcher 3: Wild Hunt GOTY',
                'platform': 'Steam',
                'original_price': 49.99,
                'discounted_price': 9.99,
                'discount_percent': 80,
                'metacritic_score': 92,
                'release_year': 2015,
                'genre': 'RPG',
                'is_aaa': True,
                'is_historical_low': True,
            },
            
            # GAMIVO DEALS
            {
                'source': 'gamivo',
                'title': 'Hogwarts Legacy',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 24.99,
                'discount_percent': 58,
                'metacritic_score': 84,
                'release_year': 2023,
                'genre': 'RPG',
                'is_aaa': True,
                'seller_rating': 99.8,
                'region': 'Global',
            },
            {
                'source': 'gamivo',
                'title': 'Call of Duty: Modern Warfare III',
                'platform': 'Steam',
                'original_price': 69.99,
                'discounted_price': 44.99,
                'discount_percent': 36,
                'metacritic_score': 56,
                'release_year': 2023,
                'genre': 'Action',
                'is_aaa': True,
                'seller_rating': 99.2,
                'region': 'Europe',
            },
            {
                'source': 'gamivo',
                'title': 'Starfield',
                'platform': 'Steam',
                'original_price': 69.99,
                'discounted_price': 39.99,
                'discount_percent': 43,
                'metacritic_score': 83,
                'release_year': 2023,
                'genre': 'RPG',
                'is_aaa': True,
                'seller_rating': 98.9,
                'region': 'Global',
            },
            {
                'source': 'gamivo',
                'title': 'Elden Ring',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 34.99,
                'discount_percent': 42,
                'metacritic_score': 96,
                'release_year': 2022,
                'genre': 'Action',
                'is_aaa': True,
                'seller_rating': 99.5,
                'region': 'Global',
            },
            {
                'source': 'gamivo',
                'title': 'Lies of P',
                'platform': 'Steam',
                'original_price': 59.99,
                'discounted_price': 35.99,
                'discount_percent': 40,
                'metacritic_score': 81,
                'release_year': 2023,
                'genre': 'Action',
                'is_aaa': False,
                'seller_rating': 98.7,
                'region': 'Global',
            },
            {
                'source': 'gamivo',
                'title': 'Palworld',
                'platform': 'Steam',
                'original_price': 29.99,
                'discounted_price': 22.99,
                'discount_percent': 23,
                'metacritic_score': 0,
                'release_year': 2024,
                'genre': 'Indie',
                'early_access': True,
                'seller_rating': 99.1,
                'region': 'Global',
            },
            {
                'source': 'gamivo',
                'title': 'GTA V Premium Edition',
                'platform': 'Epic',
                'original_price': 39.99,
                'discounted_price': 12.99,
                'discount_percent': 68,
                'metacritic_score': 96,
                'release_year': 2013,
                'genre': 'Action',
                'is_aaa': True,
                'seller_rating': 99.9,
                'region': 'Global',
            },
            
            # SUPER OFFERTE
            {
                'source': 'instant_gaming',
                'title': 'Mass Effect Legendary Edition',
                'platform': 'Origin',
                'original_price': 59.99,
                'discounted_price': 9.99,
                'discount_percent': 83,
                'metacritic_score': 86,
                'release_year': 2021,
                'genre': 'RPG',
                'is_aaa': True,
                'is_historical_low': True,
            },
            {
                'source': 'gamivo',
                'title': 'Horizon Zero Dawn Complete',
                'platform': 'Steam',
                'original_price': 49.99,
                'discounted_price': 12.49,
                'discount_percent': 75,
                'metacritic_score': 89,
                'release_year': 2020,
                'genre': 'Action',
                'is_aaa': True,
                'seller_rating': 99.7,
                'region': 'Global',
            },
        ]
    
    def get_instant_gaming_deals(self, max_deals: int = 10) -> List[Dict]:
        """Ritorna mock deals di Instant Gaming"""
        ig_deals = [d for d in self.mock_deals if d['source'] == 'instant_gaming']
        
        # Aggiungi campi mancanti
        for deal in ig_deals:
            deal['url'] = f"https://www.instant-gaming.com/it/game/{deal['title'].lower().replace(' ', '-')}?igr=giochigameplay"
            deal['image_url'] = f"https://placehold.co/600x400?text={deal['title'].replace(' ', '+')}"
            deal['scraped_at'] = datetime.now().isoformat()
            
        # Shuffle e ritorna max_deals
        random.shuffle(ig_deals)
        return ig_deals[:max_deals]
    
    def get_gamivo_deals(self, max_deals: int = 10) -> List[Dict]:
        """Ritorna mock deals di GAMIVO"""
        gv_deals = [d for d in self.mock_deals if d['source'] == 'gamivo']
        
        # Aggiungi campi mancanti
        for deal in gv_deals:
            deal['url'] = f"https://www.gamivo.com/product/{deal['title'].lower().replace(' ', '-')}?glv=indiedealsgaming"
            deal['image_url'] = f"https://placehold.co/600x400?text={deal['title'].replace(' ', '+')}"
            deal['scraped_at'] = datetime.now().isoformat()
            
        # Shuffle e ritorna max_deals
        random.shuffle(gv_deals)
        return gv_deals[:max_deals]
    
    def get_random_deals(self, count: int = 5) -> List[Dict]:
        """Ritorna deals casuali misti"""
        all_deals = self.mock_deals.copy()
        
        for deal in all_deals:
            if 'url' not in deal:
                if deal['source'] == 'instant_gaming':
                    deal['url'] = f"https://www.instant-gaming.com/it/game/{deal['title'].lower().replace(' ', '-')}?igr=giochigameplay"
                else:
                    deal['url'] = f"https://www.gamivo.com/product/{deal['title'].lower().replace(' ', '-')}?glv=indiedealsgaming"
            
            deal['image_url'] = f"https://placehold.co/600x400?text={deal['title'].replace(' ', '+')}"
            deal['scraped_at'] = datetime.now().isoformat()
        
        random.shuffle(all_deals)
        return all_deals[:count]
    
    def get_top_deals_by_score(self, count: int = 3) -> List[Dict]:
        """Ritorna i top deals per testing BrislyScore"""
        # Ritorna quelli con caratteristiche migliori
        top_deals = [
            d for d in self.mock_deals 
            if d.get('discount_percent', 0) > 60 or 
               d.get('metacritic_score', 0) > 90 or
               d.get('is_historical_low', False)
        ]
        
        for deal in top_deals:
            if 'url' not in deal:
                if deal['source'] == 'instant_gaming':
                    deal['url'] = f"https://www.instant-gaming.com/it/game/{deal['title'].lower().replace(' ', '-')}?igr=giochigameplay"
                else:
                    deal['url'] = f"https://www.gamivo.com/product/{deal['title'].lower().replace(' ', '-')}?glv=indiedealsgaming"
            
            deal['image_url'] = f"https://placehold.co/600x400?text={deal['title'].replace(' ', '+')}"
            deal['scraped_at'] = datetime.now().isoformat()
        
        return top_deals[:count]

# Test del modulo
if __name__ == "__main__":
    provider = MockDataProvider()
    
    print("\n🎮 INSTANT GAMING MOCK DEALS:")
    ig_deals = provider.get_instant_gaming_deals(3)
    for deal in ig_deals:
        print(f"  - {deal['title']}: {deal['discounted_price']}€ (-{deal['discount_percent']}%)")
    
    print("\n🎮 GAMIVO MOCK DEALS:")
    gv_deals = provider.get_gamivo_deals(3)
    for deal in gv_deals:
        print(f"  - {deal['title']}: {deal['discounted_price']}€ (-{deal['discount_percent']}%)")
    
    print("\n🏆 TOP DEALS:")
    top_deals = provider.get_top_deals_by_score(3)
    for deal in top_deals:
        print(f"  - {deal['title']}: {deal['discounted_price']}€ (-{deal['discount_percent']}%) [{deal['source'].upper()}]")