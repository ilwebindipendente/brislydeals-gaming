"""
Test Script per tutti gli scrapers
Testa Instant Gaming e GAMIVO insieme
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime
from scrapers.instant_gaming import InstantGamingScraper
from scrapers.gamivo import GamivoScraper
from utils.brislyscore import BrislyScore

# Setup logging con colori
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_instant_gaming():
    """Test scraper Instant Gaming"""
    print("\n" + "="*60)
    print("🎮 TESTING INSTANT GAMING SCRAPER")
    print("="*60)
    
    scraper = InstantGamingScraper()
    deals = scraper.scrape_deals(max_deals=5)
    
    if not deals:
        print("❌ Nessuna offerta trovata!")
        return []
        
    print(f"✅ Trovate {len(deals)} offerte\n")
    
    for i, deal in enumerate(deals, 1):
        print(f"📦 Deal #{i}: {deal.get('title', 'N/A')}")
        print(f"   💰 Prezzo: {deal.get('original_price', 0)}€ → {deal.get('discounted_price', 0)}€")
        print(f"   📊 Sconto: -{deal.get('discount_percent', 0)}%")
        print(f"   🎮 Platform: {deal.get('platform', 'N/A')}")
        print(f"   🔗 URL: {deal.get('url', 'N/A')[:60]}...")
        print()
        
    return deals

def test_gamivo():
    """Test scraper GAMIVO"""
    print("\n" + "="*60)
    print("🎮 TESTING GAMIVO SCRAPER")
    print("="*60)
    
    scraper = GamivoScraper()
    deals = scraper.scrape_deals(max_deals=5)
    
    if not deals:
        print("❌ Nessuna offerta trovata!")
        return []
        
    print(f"✅ Trovate {len(deals)} offerte\n")
    
    for i, deal in enumerate(deals, 1):
        print(f"📦 Deal #{i}: {deal.get('title', 'N/A')}")
        print(f"   💰 Prezzo: {deal.get('original_price', 0)}€ → {deal.get('discounted_price', 0)}€")
        print(f"   📊 Sconto: -{deal.get('discount_percent', 0)}%")
        print(f"   🎮 Platform: {deal.get('platform', 'N/A')}")
        print(f"   🔗 URL: {deal.get('url', 'N/A')[:60]}...")
        print()
        
    return deals

def test_brislyscore(deals):
    """Test BrislyScore su tutte le offerte"""
    print("\n" + "="*60)
    print("🏆 TESTING BRISLYSCORE™ ALGORITHM")
    print("="*60)
    
    if not deals:
        print("❌ Nessuna offerta da valutare!")
        return
        
    scorer = BrislyScore()
    scored_deals = []
    
    for deal in deals:
        score_data = scorer.calculate(deal)
        deal['brislyscore'] = score_data
        scored_deals.append(deal)
        
    # Ordina per score
    scored_deals.sort(key=lambda x: x['brislyscore']['score'], reverse=True)
    
    print("\n🏆 TOP DEALS PER BRISLYSCORE™:\n")
    
    for i, deal in enumerate(scored_deals[:10], 1):
        score = deal['brislyscore']
        print(f"{i}. {score['emoji']} {deal.get('title', 'N/A')}")
        print(f"   Score: {score['score']}/45 - {score['tier']}")
        print(f"   Fonte: {deal.get('source', 'N/A').upper()}")
        print(f"   Prezzo: {deal.get('discounted_price', 0)}€ (-{deal.get('discount_percent', 0)}%)")
        print(f"   {score['recommendation']}")
        print()
        
    return scored_deals

def compare_sources(ig_deals, gv_deals):
    """Confronta le offerte tra le due fonti"""
    print("\n" + "="*60)
    print("📊 CONFRONTO FONTI")
    print("="*60)
    
    print(f"\n📈 Instant Gaming: {len(ig_deals)} offerte")
    print(f"📈 GAMIVO: {len(gv_deals)} offerte")
    
    # Trova il miglior prezzo per fonte
    if ig_deals:
        best_ig = min(ig_deals, key=lambda x: x.get('discounted_price', 999))
        print(f"\n💰 Miglior prezzo IG: {best_ig.get('title', 'N/A')} a {best_ig.get('discounted_price', 0)}€")
        
    if gv_deals:
        best_gv = min(gv_deals, key=lambda x: x.get('discounted_price', 999))
        print(f"💰 Miglior prezzo GAMIVO: {best_gv.get('title', 'N/A')} a {best_gv.get('discounted_price', 0)}€")
    
    # Trova il miglior sconto
    all_deals = ig_deals + gv_deals
    if all_deals:
        best_discount = max(all_deals, key=lambda x: x.get('discount_percent', 0))
        print(f"\n🔥 Miglior sconto: {best_discount.get('title', 'N/A')} -{best_discount.get('discount_percent', 0)}% ({best_discount.get('source', 'N/A').upper()})")

def main():
    """Main test function"""
    print("\n" + "🎮"*30)
    print("     BRISLY GAMING BOT - SCRAPER TEST SUITE")
    print("🎮"*30)
    print(f"\n⏰ Test avviato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Instant Gaming
    ig_deals = test_instant_gaming()
    
    # Test GAMIVO
    gv_deals = test_gamivo()
    
    # Combina tutte le offerte
    all_deals = ig_deals + gv_deals
    
    # Test BrislyScore
    if all_deals:
        scored_deals = test_brislyscore(all_deals)
        
        # Confronta fonti
        compare_sources(ig_deals, gv_deals)
        
        print("\n" + "="*60)
        print("✅ TEST COMPLETATO!")
        print(f"📊 Totale offerte analizzate: {len(all_deals)}")
        print("="*60)
    else:
        print("\n❌ Nessuna offerta trovata da nessuna fonte!")
        print("Possibili problemi:")
        print("- Connessione internet")
        print("- Struttura HTML dei siti cambiata")
        print("- Rate limiting / blocking")
    
    return all_deals

if __name__ == "__main__":
    try:
        deals = main()
        print(f"\n💾 Pronto per salvare {len(deals)} offerte nel database!")
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrotto dall'utente")
    except Exception as e:
        print(f"\n\n❌ Errore critico: {e}")
        import traceback
        traceback.print_exc()