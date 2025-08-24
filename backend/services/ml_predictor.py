"""
Machine Learning Predictor para CryptoAnalyzer Pro
Implementa predições reais baseadas em dados históricos e análise técnica
"""

import os
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import asyncio

from .coingecko_service import coingecko_service
from .real_technical_analysis import real_technical_analysis

logger = logging.getLogger(__name__)


class MLPredictor:
    """Sistema de Machine Learning para predições de criptomoedas"""
    
    def __init__(self):
        # Configurações do .env
        self.retrain_interval_hours = int(os.getenv('ML_RETRAIN_INTERVAL_HOURS', 6))
        self.min_confidence_threshold = float(os.getenv('ML_MIN_CONFIDENCE', 70.0))
        self.prediction_horizon_hours = int(os.getenv('ML_PREDICTION_HORIZON_HOURS', 24))
        
        # Modelos
        self.models = {}
        self.scalers = {}
        self.last_training = {}
        self.model_performance = {}
        
        # Símbolos para treinar
        self.supported_symbols = [
            'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'LINK', 'UNI'
        ]
        
        # Features para o modelo
        self.feature_columns = [
            'price', 'volume', 'market_cap', 'price_change_24h',
            'rsi', 'macd', 'bollinger_upper', 'bollinger_lower', 'sma_20', 'ema_12',
            'hour', 'day_of_week', 'volatility_7d'
        ]
    
    def _prepare_features(self, historical_data: List[Dict], technical_data: Dict = None) -> pd.DataFrame:
        """Prepara features para o modelo ML"""
        try:
            if not historical_data:
                return pd.DataFrame()
            
            df = pd.DataFrame(historical_data)
            
            # Converter timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
            else:
                # Usar índice como timestamp aproximado
                df['hour'] = datetime.now().hour
                df['day_of_week'] = datetime.now().weekday()
            
            # Features básicas
            required_cols = ['price', 'volume', 'market_cap']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 0
            
            # Calcular variação de preço
            if 'price_change_24h' not in df.columns:
                df['price_change_24h'] = df['price'].pct_change() * 100
            
            # Adicionar indicadores técnicos se disponíveis
            if technical_data and 'indicators' in technical_data:
                indicators = technical_data['indicators']
                df['rsi'] = indicators.get('rsi', 50)
                df['macd'] = indicators.get('macd', 0)
                df['bollinger_upper'] = indicators.get('bollinger_upper', df['price'].iloc[-1] * 1.02)
                df['bollinger_lower'] = indicators.get('bollinger_lower', df['price'].iloc[-1] * 0.98)
                df['sma_20'] = indicators.get('sma_20', df['price'].mean())
                df['ema_12'] = indicators.get('ema_12', df['price'].mean())
            else:
                # Calcular indicadores básicos
                df['rsi'] = 50  # Neutro
                df['macd'] = 0
                df['bollinger_upper'] = df['price'] * 1.02
                df['bollinger_lower'] = df['price'] * 0.98
                df['sma_20'] = df['price'].rolling(min(20, len(df))).mean()
                df['ema_12'] = df['price'].ewm(span=min(12, len(df))).mean()
            
            # Volatilidade
            df['volatility_7d'] = df['price'].rolling(min(7, len(df))).std()
            
            # Preencher NaN
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            # Selecionar apenas colunas necessárias
            available_features = [col for col in self.feature_columns if col in df.columns]
            df = df[available_features]
            
            return df
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()
    
    def _create_target_variable(self, prices: List[float], horizon_hours: int = 24) -> List[float]:
        """Cria variável target (preço futuro)"""
        try:
            targets = []
            for i in range(len(prices)):
                if i + horizon_hours < len(prices):
                    # Variação percentual futura
                    future_price = prices[i + horizon_hours]
                    current_price = prices[i]
                    change_pct = ((future_price - current_price) / current_price) * 100
                    targets.append(change_pct)
                else:
                    # Para os últimos pontos, usar média das variações
                    if targets:
                        targets.append(np.mean(targets[-min(10, len(targets)):]))
                    else:
                        targets.append(0)
            
            return targets
            
        except Exception as e:
            logger.error(f"Error creating target variable: {e}")
            return [0] * len(prices)
    
    async def _get_training_data(self, symbol: str, days: int = 90) -> Tuple[pd.DataFrame, List[float]]:
        """Obtém dados para treinamento"""
        try:
            # Obter dados históricos
            coin_id = symbol.lower()
            if symbol == 'BTC':
                coin_id = 'bitcoin'
            elif symbol == 'ETH':
                coin_id = 'ethereum'
            elif symbol == 'BNB':
                coin_id = 'binancecoin'
            
            historical_data = await coingecko_service.get_historical_data(coin_id, days, 'hourly')
            
            if not historical_data:
                logger.warning(f"No historical data for {symbol}")
                return pd.DataFrame(), []
            
            # Obter análise técnica atual para features
            technical_data = await real_technical_analysis.analyze_crypto(symbol)
            
            # Preparar features
            df = self._prepare_features(historical_data, technical_data)
            
            if df.empty:
                return df, []
            
            # Criar target variable
            prices = [item.get('price', 0) for item in historical_data]
            targets = self._create_target_variable(prices, self.prediction_horizon_hours)
            
            # Ajustar tamanhos
            min_len = min(len(df), len(targets))
            df = df.iloc[:min_len]
            targets = targets[:min_len]
            
            return df, targets
            
        except Exception as e:
            logger.error(f"Error getting training data for {symbol}: {e}")
            return pd.DataFrame(), []
    
    async def train_model(self, symbol: str) -> Dict[str, Any]:
        """Treina modelo ML para um símbolo específico"""
        try:
            logger.info(f"Training ML model for {symbol}")
            
            # Obter dados de treinamento
            X, y = await self._get_training_data(symbol)
            
            if X.empty or len(y) == 0:
                return {"success": False, "error": "No training data available"}
            
            # Dividir dados
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scaler
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Treinar múltiplos modelos
            models = {
                'random_forest': RandomForestRegressor(
                    n_estimators=100, 
                    max_depth=10, 
                    random_state=42,
                    n_jobs=-1
                ),
                'gradient_boosting': GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
            }
            
            best_model = None
            best_score = float('inf')
            best_model_name = None
            
            for name, model in models.items():
                # Treinar
                model.fit(X_train_scaled, y_train)
                
                # Avaliar
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                
                logger.info(f"{symbol} {name} - MAE: {mae:.2f}, MSE: {mse:.2f}")
                
                if mae < best_score:
                    best_score = mae
                    best_model = model
                    best_model_name = name
            
            # Salvar melhor modelo
            self.models[symbol] = best_model
            self.scalers[symbol] = scaler
            self.last_training[symbol] = datetime.now()
            
            # Calcular confiança baseada na performance
            confidence = max(0, min(100, 100 - (best_score * 2)))  # Ajustar fórmula
            
            self.model_performance[symbol] = {
                'mae': best_score,
                'confidence': confidence,
                'model_type': best_model_name,
                'training_samples': len(X_train),
                'features_used': list(X.columns)
            }
            
            logger.info(f"Model trained for {symbol}: {best_model_name}, Confidence: {confidence:.1f}%")
            
            return {
                "success": True,
                "symbol": symbol,
                "model_type": best_model_name,
                "confidence": confidence,
                "mae": best_score,
                "training_samples": len(X_train),
                "features_count": len(X.columns)
            }
            
        except Exception as e:
            logger.error(f"Error training model for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    async def predict(self, symbol: str) -> Dict[str, Any]:
        """Faz predição para um símbolo"""
        try:
            # Verificar se modelo existe e está atualizado
            if symbol not in self.models or self._needs_retraining(symbol):
                training_result = await self.train_model(symbol)
                if not training_result.get('success'):
                    return {"error": "Failed to train model", "details": training_result}
            
            # Obter dados atuais
            X, _ = await self._get_training_data(symbol, days=30)  # Menos dados para predição
            
            if X.empty:
                return {"error": "No data available for prediction"}
            
            # Usar últimos dados para predição
            X_latest = X.iloc[-1:].values
            X_scaled = self.scalers[symbol].transform(X_latest)
            
            # Fazer predição
            model = self.models[symbol]
            prediction = model.predict(X_scaled)[0]
            
            # Obter performance do modelo
            performance = self.model_performance.get(symbol, {})
            confidence = performance.get('confidence', 50)
            
            # Determinar direção e força
            if prediction > 2:
                direction = "BULLISH"
                strength = "STRONG" if prediction > 5 else "MODERATE"
            elif prediction < -2:
                direction = "BEARISH"
                strength = "STRONG" if prediction < -5 else "MODERATE"
            else:
                direction = "NEUTRAL"
                strength = "WEAK"
            
            # Ajustar confiança baseada na magnitude da predição
            if abs(prediction) > 10:
                confidence = min(confidence * 0.8, 95)  # Reduzir confiança para predições extremas
            
            result = {
                "symbol": symbol,
                "prediction_change_pct": round(prediction, 2),
                "direction": direction,
                "strength": strength,
                "confidence": round(confidence, 1),
                "horizon_hours": self.prediction_horizon_hours,
                "model_type": performance.get('model_type', 'unknown'),
                "last_training": self.last_training.get(symbol, datetime.now()).isoformat(),
                "features_used": performance.get('features_used', []),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Prediction for {symbol}: {prediction:+.2f}% ({direction}, {confidence:.1f}% confidence)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction for {symbol}: {e}")
            return {"error": str(e)}
    
    def _needs_retraining(self, symbol: str) -> bool:
        """Verifica se modelo precisa ser retreinado"""
        if symbol not in self.last_training:
            return True
        
        time_since_training = datetime.now() - self.last_training[symbol]
        return time_since_training.total_seconds() > (self.retrain_interval_hours * 3600)
    
    async def get_predictions_batch(self, symbols: List[str] = None) -> Dict[str, Any]:
        """Obtém predições para múltiplos símbolos"""
        if symbols is None:
            symbols = self.supported_symbols
        
        predictions = {}
        errors = {}
        
        for symbol in symbols:
            try:
                prediction = await self.predict(symbol)
                if "error" in prediction:
                    errors[symbol] = prediction["error"]
                else:
                    predictions[symbol] = prediction
            except Exception as e:
                errors[symbol] = str(e)
        
        return {
            "predictions": predictions,
            "errors": errors,
            "total_symbols": len(symbols),
            "successful_predictions": len(predictions),
            "failed_predictions": len(errors),
            "timestamp": datetime.now().isoformat()
        }
    
    async def retrain_all_models(self) -> Dict[str, Any]:
        """Retreina todos os modelos"""
        results = {}
        
        for symbol in self.supported_symbols:
            try:
                result = await self.train_model(symbol)
                results[symbol] = result
                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(1)
            except Exception as e:
                results[symbol] = {"success": False, "error": str(e)}
        
        return {
            "retrain_results": results,
            "timestamp": datetime.now().isoformat(),
            "total_models": len(self.supported_symbols),
            "successful_retrains": len([r for r in results.values() if r.get('success')])
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Obtém status de todos os modelos"""
        status = {}
        
        for symbol in self.supported_symbols:
            model_exists = symbol in self.models
            needs_retrain = self._needs_retraining(symbol)
            performance = self.model_performance.get(symbol, {})
            
            status[symbol] = {
                "model_exists": model_exists,
                "needs_retraining": needs_retrain,
                "last_training": self.last_training.get(symbol, "Never").isoformat() if isinstance(self.last_training.get(symbol), datetime) else "Never",
                "confidence": performance.get('confidence', 0),
                "model_type": performance.get('model_type', 'None'),
                "mae": performance.get('mae', 0)
            }
        
        return {
            "models_status": status,
            "retrain_interval_hours": self.retrain_interval_hours,
            "min_confidence_threshold": self.min_confidence_threshold,
            "prediction_horizon_hours": self.prediction_horizon_hours,
            "timestamp": datetime.now().isoformat()
        }


# Instância global
ml_predictor = MLPredictor()

