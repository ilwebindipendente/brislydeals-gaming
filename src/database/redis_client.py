"""
Redis Database Client
Gestisce la connessione e le operazioni con Upstash Redis
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class RedisClient:
    """Client per gestire il database Redis"""
    
    def __init__(self):
        self.url = os.getenv('UPSTASH_REDIS_URL')
        self.token = os.getenv('UPSTASH_REDIS_TOKEN')
        
        if not self.url or not self.token:
            raise ValueError("❌ Redis credentials non configurate!")
        
        # Prefisso per questo bot (per non mischiare con altri canali)
        self.prefix = "brisly:gaming:"
        
        # Connessione
        try:
            # Upstash usa REST API, convertiamo in formato Redis
            if 'upstash.io' in self.url:
                # Estrai l'ID del database dall'URL
                match = re.search(r'https://([^.]+)', self.url)
                if match:
                    db_id = match.group(1)
                    # Crea URL Redis compatibile
                    redis_url = f"rediss://default:{self.token}@{db_id}.upstash.io:6379"
                else:
                    raise ValueError("URL Upstash non valido")
            else:
                redis_url = self.url
                
            self.client = redis.from_url(
                url=redis_url,
                decode_responses=True,
                ssl_cert_reqs=None
            )
            # Test connessione
            self.client.ping()
            logger.info("✅ Redis connesso con successo")
        except Exception as e:
            logger.error(f"❌ Errore connessione Redis: {e}")
            raise
    
    # ==========================================
    # GESTIONE OFFERTE POSTATE
    # ==========================================
    
    def is_deal_posted(self, deal_id: str) -> bool:
        """
        Verifica se un'offerta è già stata postata
        
        Args:
            deal_id: ID univoco dell'offerta (es: "cyberpunk-2077-steam")
            
        Returns:
            True se già postata
        """
        key = f"{self.prefix}posted:{deal_id}"
        return self.client.exists(key) > 0
    
    def mark_deal_posted(self, deal: Dict, message_id: int = None) -> bool:
        """
        Marca un'offerta come postata
        
        Args:
            deal: Dizionario con i dati dell'offerta
            message_id: ID del messaggio Telegram (opzionale)
            
        Returns:
            True se salvata con successo
        """
        try:
            # Crea ID univoco
            deal_id = self._generate_deal_id(deal)
            key = f"{self.prefix}posted:{deal_id}"
            
            # Dati da salvare
            data = {
                'title': deal.get('title'),
                'platform': deal.get('platform'),
                'source': deal.get('source'),
                'price': deal.get('discounted_price'),
                'discount': deal.get('discount_percent'),
                'posted_at': datetime.now().isoformat(),
                'message_id': message_id,
                'brislyscore': deal.get('brislyscore', 0)
            }
            
            # Salva con TTL di 30 giorni (per non tenere troppo storico)
            self.client.setex(
                key,
                timedelta(days=30),
                json.dumps(data)
            )
            
            # Aggiungi a set giornaliero
            today_key = f"{self.prefix}posted:daily:{datetime.now().strftime('%Y-%m-%d')}"
            self.client.sadd(today_key, deal_id)
            self.client.expire(today_key, timedelta(days=7))
            
            logger.info(f"✅ Offerta salvata: {deal_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore salvataggio offerta: {e}")
            return False
    
    def get_posted_count_today(self) -> int:
        """
        Conta quante offerte sono state postate oggi
        
        Returns:
            Numero di offerte postate oggi
        """
        today_key = f"{self.prefix}posted:daily:{datetime.now().strftime('%Y-%m-%d')}"
        return self.client.scard(today_key)
    
    # ==========================================
    # GESTIONE STATISTICHE
    # ==========================================
    
    def increment_stat(self, stat_name: str, value: int = 1) -> int:
        """
        Incrementa una statistica
        
        Args:
            stat_name: Nome della statistica
            value: Valore da aggiungere (default 1)
            
        Returns:
            Nuovo valore
        """
        key = f"{self.prefix}stats:{stat_name}"
        return self.client.incrby(key, value)
    
    def get_stat(self, stat_name: str) -> int:
        """
        Ottiene una statistica
        
        Args:
            stat_name: Nome della statistica
            
        Returns:
            Valore della statistica (0 se non esiste)
        """
        key = f"{self.prefix}stats:{stat_name}"
        value = self.client.get(key)
        return int(value) if value else 0
    
    def get_all_stats(self) -> Dict[str, int]:
        """
        Ottiene tutte le statistiche
        
        Returns:
            Dizionario con tutte le stats
        """
        stats = {}
        pattern = f"{self.prefix}stats:*"
        
        for key in self.client.scan_iter(match=pattern):
            stat_name = key.replace(f"{self.prefix}stats:", "")
            stats[stat_name] = self.get_stat(stat_name)
        
        return stats
    
    # ==========================================
    # GESTIONE WISHLIST UTENTI
    # ==========================================
    
    def add_to_wishlist(self, user_id: int, game_title: str) -> bool:
        """
        Aggiunge un gioco alla wishlist di un utente
        
        Args:
            user_id: ID utente Telegram
            game_title: Titolo del gioco
            
        Returns:
            True se aggiunto con successo
        """
        key = f"{self.prefix}wishlist:{user_id}"
        return self.client.sadd(key, game_title.lower()) > 0
    
    def get_wishlist(self, user_id: int) -> List[str]:
        """
        Ottiene la wishlist di un utente
        
        Args:
            user_id: ID utente Telegram
            
        Returns:
            Lista di giochi nella wishlist
        """
        key = f"{self.prefix}wishlist:{user_id}"
        return list(self.client.smembers(key))
    
    def check_wishlist_match(self, user_id: int, game_title: str) -> bool:
        """
        Verifica se un gioco è nella wishlist dell'utente
        
        Args:
            user_id: ID utente Telegram
            game_title: Titolo del gioco
            
        Returns:
            True se il gioco è nella wishlist
        """
        key = f"{self.prefix}wishlist:{user_id}"
        return self.client.sismember(key, game_title.lower())
    
    # ==========================================
    # CACHE PREZZI
    # ==========================================
    
    def cache_price(self, deal_id: str, price_data: Dict) -> bool:
        """
        Salva prezzo in cache per confronti futuri
        
        Args:
            deal_id: ID univoco dell'offerta
            price_data: Dati prezzo
            
        Returns:
            True se salvato
        """
        key = f"{self.prefix}price:{deal_id}"
        
        # Aggiungi timestamp
        price_data['cached_at'] = datetime.now().isoformat()
        
        # Salva con TTL di 24 ore
        return self.client.setex(
            key,
            timedelta(hours=24),
            json.dumps(price_data)
        )
    
    def get_cached_price(self, deal_id: str) -> Optional[Dict]:
        """
        Ottiene prezzo dalla cache
        
        Args:
            deal_id: ID univoco dell'offerta
            
        Returns:
            Dati prezzo o None
        """
        key = f"{self.prefix}price:{deal_id}"
        data = self.client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    # ==========================================
    # UTILITY
    # ==========================================
    
    def _generate_deal_id(self, deal: Dict) -> str:
        """
        Genera ID univoco per un'offerta
        
        Args:
            deal: Dizionario offerta
            
        Returns:
            ID univoco (es: "cyberpunk-2077-steam-instant-gaming")
        """
        title = deal.get('title', '').lower().replace(' ', '-').replace(':', '')
        platform = deal.get('platform', '').lower()
        source = deal.get('source', '').lower()
        
        return f"{title}-{platform}-{source}"
    
    def health_check(self) -> bool:
        """
        Verifica se il database è raggiungibile
        
        Returns:
            True se connesso
        """
        try:
            self.client.ping()
            return True
        except:
            return False
    
    def get_info(self) -> Dict:
        """
        Ottiene informazioni sul database
        
        Returns:
            Info database
        """
        try:
            info = {
                'connected': self.health_check(),
                'posted_today': self.get_posted_count_today(),
                'total_posts': self.get_stat('total_posts'),
                'prefix': self.prefix
            }
            return info
        except Exception as e:
            logger.error(f"Errore get_info: {e}")
            return {'connected': False, 'error': str(e)}

# Test del modulo
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    logging.basicConfig(level=logging.INFO)
    
    print("\n🔧 TEST REDIS CLIENT")
    print("="*50)
    
    try:
        # Connessione
        db = RedisClient()
        
        # Test health
        if db.health_check():
            print("✅ Connessione OK!")
        
        # Info
        info = db.get_info()
        print(f"\n📊 Info Database:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        # Test offerta
        test_deal = {
            'title': 'Test Game',
            'platform': 'Steam',
            'source': 'instant_gaming',
            'discounted_price': 9.99,
            'discount_percent': 75
        }
        
        deal_id = db._generate_deal_id(test_deal)
        print(f"\n🎮 Test Deal ID: {deal_id}")
        
        # Check se già postata
        if not db.is_deal_posted(deal_id):
            print("  ➡️ Offerta non ancora postata")
            
        print("\n✅ Redis client funzionante!")
        
    except Exception as e:
        print(f"\n❌ Errore: {e}")