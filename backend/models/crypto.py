"""
Database models for CryptoAnalyzer Pro
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Cryptocurrency(Base):
    """Cryptocurrency model"""
    __tablename__ = "cryptocurrencies"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    current_price = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)
    volume_24h = Column(Float, default=0.0)
    price_change_24h = Column(Float, default=0.0)
    price_change_percentage_24h = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="cryptocurrency")
    alerts = relationship("Alert", back_populates="cryptocurrency")
    analyses = relationship("TechnicalAnalysis", back_populates="cryptocurrency")


class PriceHistory(Base):
    """Price history model"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    price = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="price_history")


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")


class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    alert_type = Column(String(20), nullable=False)  # price, volume, technical
    condition = Column(String(20), nullable=False)  # above, below, crosses_above, crosses_below
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    message = Column(Text)
    priority = Column(String(10), default="medium")  # low, medium, high, critical
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    cryptocurrency = relationship("Cryptocurrency", back_populates="alerts")


class TechnicalAnalysis(Base):
    """Technical analysis model"""
    __tablename__ = "technical_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 15m, 1h, 4h, 1d, 1w
    rsi = Column(Float)
    macd_value = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    bollinger_upper = Column(Float)
    bollinger_middle = Column(Float)
    bollinger_lower = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    ema_12 = Column(Float)
    ema_26 = Column(Float)
    volume = Column(Float)
    recommendation = Column(String(10))  # buy, sell, hold
    confidence = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="analyses")


class Portfolio(Base):
    """Portfolio model"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    total_value = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    total_pnl_percentage = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio")


class PortfolioHolding(Base):
    """Portfolio holding model"""
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    cryptocurrency_id = Column(Integer, ForeignKey("cryptocurrencies.id"))
    quantity = Column(Float, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)
    pnl = Column(Float, default=0.0)
    pnl_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    cryptocurrency = relationship("Cryptocurrency")


class MarketData(Base):
    """Market data model for caching"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String(50), nullable=False)  # btc_dominance, alt_season_index, etc.
    value = Column(Float, nullable=False)
    metadata = Column(Text)  # JSON string for additional data
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SystemLog(Base):
    """System log model"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(10), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")

