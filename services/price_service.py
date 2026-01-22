"""
Stock Price Service - VNStock Implementation
Fetches real-time stock prices using vnstock library with caching
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from vnstock import stock_historical_data
from utils.logger import get_logger

logger = get_logger(__name__)


class StockAPIError(Exception):
    """Custom exception for stock API errors"""
    pass


@dataclass
class PriceData:
    """Price data with metadata"""
    symbol: str
    price: float
    timestamp: datetime
    source: str


class PriceCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, ttl_seconds: int = 7):
        self._cache: dict[str, PriceData] = {}
        self._ttl = timedelta(seconds=ttl_seconds)
    
    def get(self, symbol: str) -> Optional[PriceData]:
        """Get cached price if not expired"""
        if symbol not in self._cache:
            return None
        
        cached_data = self._cache[symbol]
        age = datetime.now() - cached_data.timestamp
        
        if age > self._ttl:
            logger.debug(f"Cache expired for {symbol} (age: {age.total_seconds():.1f}s)")
            del self._cache[symbol]
            return None
        
        logger.debug(f"Cache hit for {symbol} (age: {age.total_seconds():.1f}s)")
        return cached_data
    
    def set(self, data: PriceData):
        """Store price data in cache"""
        self._cache[data.symbol] = data
        logger.debug(f"Cached {data.symbol} at {data.price:,.0f}")
    
    def clear(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.debug("Cache cleared")


class VNStockProvider:
    """VNStock provider for fetching stock prices"""
    
    def __init__(self):
        logger.info("VNStockProvider initialized")
    
    def fetch_price(self, symbol: str) -> PriceData:
        """
        Fetch current stock price using vnstock
        
        Args:
            symbol: Stock symbol (e.g., 'SHB', 'VNM')
            
        Returns:
            PriceData object with current price
            
        Raises:
            StockAPIError: If unable to fetch price
        """
        try:
            logger.debug(f"Fetching price for {symbol} using VNStock")
            
            # Get recent historical data
            # vnstock 0.2.x: stock_historical_data(symbol, start_date, end_date, resolution, type)
            df = stock_historical_data(
                symbol=symbol.upper(),
                start_date='2026-01-20',
                end_date='2026-01-22',
                resolution='1D',
                type='stock'
            )
            
            if df is None or df.empty:
                raise StockAPIError(f"No data returned for {symbol}")
            
            # Get the most recent close price
            latest_price = float(df['close'].iloc[-1])
            
            logger.info(f"✅ {symbol}: {latest_price:,.0f} VND (vnstock)")
            
            return PriceData(
                symbol=symbol.upper(),
                price=latest_price,
                timestamp=datetime.now(),
                source="vnstock"
            )
            
        except Exception as e:
            error_msg = f"VNStock error for {symbol}: {str(e)}"
            logger.error(error_msg)
            raise StockAPIError(error_msg) from e
    
    @property
    def name(self) -> str:
        return "vnstock"


class PriceService:
    """Main service for stock price operations with caching"""
    
    def __init__(self, cache_ttl: int = 7):
        """
        Initialize price service
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 7)
        """
        self.provider = VNStockProvider()
        self.cache = PriceCache(ttl_seconds=cache_ttl)
        logger.info(f"PriceService initialized with {self.provider.name} (cache TTL: {cache_ttl}s)")
    
    def get_price(self, symbol: str) -> PriceData:
        """
        Get stock price with caching
        
        Args:
            symbol: Stock symbol
            
        Returns:
            PriceData object
            
        Raises:
            StockAPIError: If unable to fetch price
        """
        # Check cache first
        cached = self.cache.get(symbol)
        if cached:
            logger.debug(f"Returning cached price for {symbol}")
            return cached
        
        # Fetch fresh data
        logger.debug(f"Cache miss - fetching fresh price for {symbol}")
        price_data = self.provider.fetch_price(symbol)
        
        # Cache the result
        self.cache.set(price_data)
        
        return price_data
    
    def is_healthy(self) -> bool:
        """Check if service is operational (no actual API call)"""
        return True


# Global service instance
_service_instance: Optional[PriceService] = None


def get_service() -> PriceService:
    """Get or create the global PriceService instance (singleton)"""
    global _service_instance
    if _service_instance is None:
        _service_instance = PriceService()
    return _service_instance


def fetch_price(symbol: str) -> float:
    """
    Legacy compatibility function - fetch stock price
    
    Args:
        symbol: Stock symbol
        
    Returns:
        Current stock price
        
    Raises:
        StockAPIError: If unable to fetch price
    """
    service = get_service()
    price_data = service.get_price(symbol)
    return price_data.price


def is_healthy() -> bool:
    """Legacy compatibility function - check service health"""
    service = get_service()
    return service.is_healthy()
