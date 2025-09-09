"""
BrislyScore™ Algorithm
Sistema di rating per valutare la qualità delle offerte
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BrislyScore:
    """Calcola il BrislyScore™ per ogni offerta"""
    
    def __init__(self):
        # Pesi per ogni componente (totale = 1.0)
        self.weights = {
            'metacritic': 0.30,    # 30%
            'discount': 0.30,      # 30%
            'price_value': 0.25,   # 25%
            'popularity': 0.15     # 15%
        }
        
        # Tier thresholds
        self.tiers = {
            'SUPER_OFFERTA': (36, '💎'),
            'OTTIMA_OFFERTA': (26, '🔥'),
            'BUONA_OFFERTA': (16, '👍'),
            'OFFERTA_OK': (0, '😐')
        }
    
    def calculate(self, deal: Dict) -> Dict:
        """
        Calcola il BrislyScore per un'offerta
        
        Args:
            deal: Dizionario con i dati dell'offerta
            
        Returns:
            Dict con score, tier e emoji
        """
        score = 0
        components = {}
        
        # 1. METACRITIC SCORE (0-10 punti)
        metacritic = deal.get('metacritic_score', 0)
        if metacritic > 0:
            components['metacritic'] = (metacritic / 100) * 10
        else:
            components['metacritic'] = 5  # Default se non disponibile
            
        # 2. DISCOUNT PERCENTAGE (0-10 punti)
        discount = deal.get('discount_percent', 0)
        components['discount'] = min(discount / 10, 10)  # Max 10 punti
        
        # 3. PRICE VALUE (0-10 punti)
        price = deal.get('discounted_price', 999)
        if price <= 5:
            components['price_value'] = 10
        elif price <= 10:
            components['price_value'] = 9
        elif price <= 15:
            components['price_value'] = 8
        elif price <= 20:
            components['price_value'] = 7
        elif price <= 30:
            components['price_value'] = 6
        elif price <= 40:
            components['price_value'] = 5
        elif price <= 50:
            components['price_value'] = 4
        else:
            components['price_value'] = max(0, 10 - (price / 10))
            
        # 4. POPULARITY BONUS (0-5 punti)
        # TODO: Implementare check popularità basato su wishlist/vendite
        components['popularity'] = 2.5  # Default medio
        
        # 5. BONUS SPECIALI
        bonus = 0
        
        # Historical low bonus
        if deal.get('is_historical_low', False):
            bonus += 5
            
        # AAA game bonus
        if deal.get('is_aaa', False):
            bonus += 2
            
        # New release penalty (giochi troppo nuovi hanno meno sconto)
        release_year = deal.get('release_year', 0)
        if release_year >= 2024:
            bonus -= 1
            
        # Calcolo finale pesato
        for component, value in components.items():
            if component in self.weights:
                score += value * self.weights[component]
                
        # Aggiungi bonus
        final_score = min(45, score * 3 + bonus)  # Scala a 0-45
        
        # Determina tier
        tier_name, emoji = self._get_tier(final_score)
        
        result = {
            'score': round(final_score, 1),
            'tier': tier_name,
            'emoji': emoji,
            'components': components,
            'bonus': bonus,
            'recommendation': self._get_recommendation(tier_name)
        }
        
        logger.info(f"📊 BrislyScore: {result['score']} - {tier_name} {emoji}")
        
        return result
    
    def _get_tier(self, score: float) -> tuple:
        """Determina il tier basato sullo score"""
        for tier_name, (threshold, emoji) in self.tiers.items():
            if score >= threshold:
                return tier_name, emoji
        return 'OFFERTA_OK', '😐'
    
    def _get_recommendation(self, tier: str) -> str:
        """Genera raccomandazione testuale"""
        recommendations = {
            'SUPER_OFFERTA': "💎 IMPERDIBILE! Affare eccezionale da prendere subito!",
            'OTTIMA_OFFERTA': "🔥 Ottimo affare! Altamente consigliato!",
            'BUONA_OFFERTA': "👍 Buon prezzo, vale la pena considerarlo!",
            'OFFERTA_OK': "😐 Offerta discreta, valuta se ti interessa il gioco."
        }
        return recommendations.get(tier, "Offerta da valutare.")
    
    def format_for_post(self, score_data: Dict) -> str:
        """
        Formatta il BrislyScore per il post Telegram
        
        Returns:
            Stringa formattata per il messaggio
        """
        return (
            f"{score_data['emoji']} BrislyScore™: "
            f"{score_data['score']}/45 - {score_data['tier'].replace('_', ' ')}\n"
            f"💬 {score_data['recommendation']}"
        )

# Test del modulo
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test con offerta esempio
    test_deal = {
        'title': 'Cyberpunk 2077',
        'metacritic_score': 86,
        'discount_percent': 67,
        'discounted_price': 19.99,
        'original_price': 59.99,
        'is_historical_low': True,
        'is_aaa': True,
        'release_year': 2020
    }
    
    scorer = BrislyScore()
    result = scorer.calculate(test_deal)
    
    print("\n" + "="*50)
    print("🎮 TEST BRISLYSCORE™")
    print("="*50)
    print(f"Gioco: {test_deal['title']}")
    print(f"Score: {result['score']}/45")
    print(f"Tier: {result['tier']} {result['emoji']}")
    print(f"Raccomandazione: {result['recommendation']}")
    print("="*50)