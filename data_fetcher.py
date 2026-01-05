"""
Data Fetcher Module
Fetches historical and live data from Zerodha Kite Connect API for Indian stocks
"""

from kiteconnect import KiteConnect
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict
import os
import json

logger = logging.getLogger(__name__)


class KiteDataFetcher:
    """Fetches market data from Zerodha Kite Connect API"""
    
    def __init__(self, api_key: str, api_secret: str = None, access_token: str = None):
        """
        Initialize the Kite Connect data fetcher
        
        Args:
            api_key: Kite Connect API key
            api_secret: Kite Connect API secret (needed for first-time authentication)
            access_token: Pre-generated access token (if available)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.kite = KiteConnect(api_key=api_key)
        
        # Load or set access token
        if access_token:
            self.kite.set_access_token(access_token)
            logger.info("Access token loaded successfully")
        else:
            logger.warning("No access token provided. You need to authenticate first.")
    
    def get_login_url(self) -> str:
        """
        Get the login URL for authentication
        
        Returns:
            Login URL string
        """
        login_url = self.kite.login_url()
        logger.info(f"Login URL: {login_url}")
        return login_url
    
    def generate_session(self, request_token: str) -> Dict:
        """
        Generate session and get access token
        
        Args:
            request_token: Request token from login callback
            
        Returns:
            Dictionary with access token and user data
        """
        if not self.api_secret:
            raise ValueError("API secret is required for session generation")
        
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.kite.set_access_token(data["access_token"])
            
            # Save access token for future use
            self._save_access_token(data["access_token"])
            
            logger.info("Session generated successfully")
            logger.info(f"User: {data.get('user_name', 'Unknown')}")
            
            return data
        except Exception as e:
            logger.error(f"Failed to generate session: {e}")
            raise
    
    def _save_access_token(self, access_token: str, filename: str = "kite_access_token.json"):
        """
        Save access token to file
        
        Args:
            access_token: Access token to save
            filename: Filename to save to
        """
        try:
            data = {
                "access_token": access_token,
                "timestamp": datetime.now().isoformat()
            }
            with open(filename, 'w') as f:
                json.dump(data, f)
            logger.info(f"Access token saved to {filename}")
        except Exception as e:
            logger.warning(f"Failed to save access token: {e}")
    
    def _load_access_token(self, filename: str = "kite_access_token.json") -> Optional[str]:
        """
        Load access token from file
        
        Args:
            filename: Filename to load from
            
        Returns:
            Access token or None
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    # Check if token is from today (tokens expire daily)
                    token_date = datetime.fromisoformat(data["timestamp"]).date()
                    if token_date == datetime.now().date():
                        logger.info("Loaded valid access token from file")
                        return data["access_token"]
                    else:
                        logger.warning("Access token expired (from previous day)")
            return None
        except Exception as e:
            logger.warning(f"Failed to load access token: {e}")
            return None
    
    def fetch_ohlcv(
        self,
        instrument_token: int,
        from_date: datetime,
        to_date: datetime,
        interval: str = "15minute"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV historical data
        
        Args:
            instrument_token: Instrument token for the stock/index
            from_date: Start date
            to_date: End date
            interval: Candle interval ('minute', '3minute', '5minute', '15minute', 
                                      '30minute', '60minute', 'day')
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching historical data for instrument {instrument_token}")
            
            # Fetch historical data
            records = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(records)
            
            if df.empty:
                logger.warning("No data received")
                return df
            
            # Rename columns to match our standard format
            df.rename(columns={'date': 'timestamp'}, inplace=True)
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Fetched {len(df)} candles")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            raise
    
    def fetch_ohlcv_by_symbol(
        self,
        symbol: str,
        exchange: str = "NSE",
        days: int = 7,
        interval: str = "15minute"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data by symbol name
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS', 'INFY')
            exchange: Exchange name ('NSE', 'BSE', 'NFO', 'MCX')
            days: Number of days of historical data
            interval: Candle interval
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Get instrument token for the symbol
            instruments = self.kite.instruments(exchange)
            instrument_df = pd.DataFrame(instruments)
            
            # Find the instrument
            instrument = instrument_df[
                (instrument_df['tradingsymbol'] == symbol) & 
                (instrument_df['exchange'] == exchange)
            ]
            
            if instrument.empty:
                raise ValueError(f"Symbol {symbol} not found on {exchange}")
            
            instrument_token = instrument.iloc[0]['instrument_token']
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Fetch data
            return self.fetch_ohlcv(instrument_token, from_date, to_date, interval)
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            raise
    
    def fetch_multiple_symbols(
        self,
        symbols: list,
        exchange: str = "NSE",
        days: int = 7,
        interval: str = "15minute"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLCV data for multiple symbols
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange name
            days: Number of days of historical data
            interval: Candle interval
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data = {}
        
        for symbol in symbols:
            try:
                df = self.fetch_ohlcv_by_symbol(symbol, exchange, days, interval)
                data[symbol] = df
                logger.info(f"Successfully fetched data for {symbol}")
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                continue
        
        return data
    
    def get_quote(self, symbols: list, exchange: str = "NSE") -> Dict:
        """
        Get current market quote for symbols
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange name
            
        Returns:
            Dictionary with quote data
        """
        try:
            # Format symbols with exchange prefix
            formatted_symbols = [f"{exchange}:{symbol}" for symbol in symbols]
            quotes = self.kite.quote(formatted_symbols)
            return quotes
        except Exception as e:
            logger.error(f"Failed to fetch quotes: {e}")
            raise
    
    def get_ltp(self, symbols: list, exchange: str = "NSE") -> Dict:
        """
        Get last traded price for symbols
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange name
            
        Returns:
            Dictionary with LTP data
        """
        try:
            formatted_symbols = [f"{exchange}:{symbol}" for symbol in symbols]
            ltp = self.kite.ltp(formatted_symbols)
            return ltp
        except Exception as e:
            logger.error(f"Failed to fetch LTP: {e}")
            raise
    
    def search_instruments(self, query: str, exchange: str = "NSE") -> pd.DataFrame:
        """
        Search for instruments by name or symbol
        
        Args:
            query: Search query
            exchange: Exchange to search in
            
        Returns:
            DataFrame with matching instruments
        """
        try:
            instruments = self.kite.instruments(exchange)
            df = pd.DataFrame(instruments)
            
            # Search in tradingsymbol and name
            mask = (
                df['tradingsymbol'].str.contains(query, case=False, na=False) |
                df['name'].str.contains(query, case=False, na=False)
            )
            
            return df[mask]
        except Exception as e:
            logger.error(f"Failed to search instruments: {e}")
            raise


def authenticate_kite(api_key: str, api_secret: str) -> KiteDataFetcher:
    """
    Helper function to authenticate with Kite Connect
    
    Args:
        api_key: Kite Connect API key
        api_secret: Kite Connect API secret
        
    Returns:
        Authenticated KiteDataFetcher instance
    """
    fetcher = KiteDataFetcher(api_key, api_secret)
    
    # Try to load existing access token
    access_token = fetcher._load_access_token()
    
    if access_token:
        fetcher.kite.set_access_token(access_token)
        logger.info("Using existing access token")
        return fetcher
    
    # Need to authenticate
    print("\n" + "="*60)
    print("KITE CONNECT AUTHENTICATION")
    print("="*60)
    print("\nPlease follow these steps to authenticate:")
    print(f"\n1. Open this URL in your browser:")
    print(f"   {fetcher.get_login_url()}")
    print("\n2. Log in with your Zerodha credentials")
    print("\n3. After login, you'll be redirected to a URL like:")
    print("   http://127.0.0.1/?request_token=XXXXXX&action=login&status=success")
    print("\n4. Copy the 'request_token' value from the URL")
    
    request_token = input("\nEnter the request_token: ").strip()
    
    # Generate session
    data = fetcher.generate_session(request_token)
    
    print(f"\n✓ Authentication successful!")
    print(f"  User: {data.get('user_name', 'Unknown')}")
    print(f"  Access token saved for today's session")
    print("="*60 + "\n")
    
    return fetcher


if __name__ == "__main__":
    # Test the Kite data fetcher
    logging.basicConfig(level=logging.INFO)
    
    # You need to provide your API credentials
    API_KEY = "your_api_key_here"
    API_SECRET = "your_api_secret_here"
    
    if API_KEY == "your_api_key_here":
        print("Please update API_KEY and API_SECRET in the code")
    else:
        # Authenticate
        fetcher = authenticate_kite(API_KEY, API_SECRET)
        
        # Fetch data for a stock
        df = fetcher.fetch_ohlcv_by_symbol('RELIANCE', exchange='NSE', days=7, interval='15minute')
        
        print(f"\nFetched {len(df)} candles for RELIANCE")
        print(f"\nFirst 5 rows:")
        print(df.head())
        print(f"\nLast 5 rows:")
        print(df.tail())
