"""
Serviço de Análise Técnica 100% REAL
Combina dados OHLCV reais com cálculos técnicos precisos
"""
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

from services.binance_real_data import binance_real_service
from services.pine_data_storage import get_latest_pine_signal
from services.real_technical_calculations import real_calculations
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class RealAnalysisService:
    """
    Serviço de análise técnica com dados 100% REAIS
    - Coleta dados OHLCV históricos reais
    - Calcula indicadores técnicos com fórmulas matemáticas precisas
    - Gera análises IA baseadas em dados reais
    - Fornece recomendações fundamentadas
    """
    
    def __init__(self):
        self.symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'SOL': 'solana',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'AVAX': 'avalanche-2',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'UNI': 'uniswap'
        }
    
    async def analyze_symbol_complete(self, symbol: str, timeframe: str = "1h") -> Dict[str, Any]:
        """
        Análise técnica COMPLETA e 100% REAL de um símbolo
        
        Args:
            symbol: Símbolo da crypto (BTC, ETH, etc.)
            timeframe: Timeframe para análise
        
        Returns:
            Dict com análise técnica completa REAL
        """
        try:
            logger.info(f"🔍 Iniciando análise técnica REAL para {symbol}")
            
            # Validar símbolo
            if symbol.upper() not in self.symbol_to_id:
                raise ValueError(f"Símbolo {symbol} não suportado")
            
            coin_id = self.symbol_to_id[symbol.upper()]
            
            # 1. Tentar obter dados REAIS do Pine Script primeiro
            logger.info(f"📊 Buscando dados REAIS do Pine Script para {symbol}...")
            pine_data = get_latest_pine_signal(symbol)
            
            if pine_data:
                logger.info(f"✅ Dados REAIS do Pine Script encontrados para {symbol}")
                
                # Usar dados diretos do Pine Script (já calculados no TradingView)
                current_price = pine_data.get('price', 0)
                
                technical_indicators = {
                    'rsi': pine_data.get('rsi'),
                    'macd': {
                        'macd': pine_data.get('macd'),
                        'signal': pine_data.get('macd_signal'),
                        'histogram': pine_data.get('macd_histogram')
                    },
                    'bollinger_bands': {
                        'upper': pine_data.get('bb_upper'),
                        'middle': pine_data.get('bb_middle'),
                        'lower': pine_data.get('bb_lower')
                    },
                    'moving_averages': {
                        'ema_12': pine_data.get('ema_12'),
                        'ema_26': pine_data.get('ema_26'),
                        'ema_50': pine_data.get('ema_50'),
                        'sma_20': pine_data.get('sma_20')
                    },
                    'stochastic': {
                        'k': pine_data.get('stoch_k'),
                        'd': pine_data.get('stoch_d')
                    },
                    'williams_r': pine_data.get('williams_r'),
                    'adx': pine_data.get('adx'),
                    'volume_ratio': pine_data.get('volume_ratio')
                }
                
                # Análise baseada nos dados REAIS do Pine Script
                analysis_result = {
                    'score': pine_data.get('score', 50),
                    'recommendation': pine_data.get('recommendation', 'HOLD'),
                    'confidence': pine_data.get('confidence', 70),
                    'bullish_signals': pine_data.get('bullish_signals', 0),
                    'bearish_signals': pine_data.get('bearish_signals', 0),
                    'reasoning': f"Análise baseada em {pine_data.get('bullish_signals', 0)} sinais de alta e {pine_data.get('bearish_signals', 0)} sinais de baixa calculados no TradingView"
                }
                
                # Análise IA com dados REAIS
                ai_analysis = None
                try:
                    if gemini_service.is_configured():
                        ai_prompt = f"""
                        Analise os seguintes dados técnicos REAIS do {symbol} coletados diretamente do TradingView:
                        
                        Preço atual: ${current_price:.2f}
                        RSI: {technical_indicators['rsi']:.2f}
                        MACD: {technical_indicators['macd']['macd']:.2f}
                        MACD Signal: {technical_indicators['macd']['signal']:.2f}
                        Bollinger Superior: ${technical_indicators['bollinger_bands']['upper']:.2f}
                        Bollinger Inferior: ${technical_indicators['bollinger_bands']['lower']:.2f}
                        EMA 12: ${technical_indicators['moving_averages']['ema_12']:.2f}
                        EMA 26: ${technical_indicators['moving_averages']['ema_26']:.2f}
                        Score: {analysis_result['score']}/100
                        Recomendação: {analysis_result['recommendation']}
                        
                        Forneça uma análise profissional em português sobre a situação atual do {symbol}.
                        """
                        
                        ai_analysis = await gemini_service.analyze_market_data(ai_prompt)
                        logger.info(f"✅ Análise IA gerada para {symbol} com dados REAIS")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Falha na análise IA para {symbol}: {e}")
                    ai_analysis = "Análise IA temporariamente indisponível"
                
                return {
                    'success': True,
                    'symbol': symbol,
                    'current_price': current_price,
                    'technical_indicators': technical_indicators,
                    'analysis': analysis_result,
                    'ai_analysis': ai_analysis,
                    'data_source': 'TradingView Pine Script REAL',
                    'calculation_method': 'TradingView Native Calculations',
                    'timestamp': datetime.now().isoformat(),
                    'data_quality': 'REAL',
                    'pine_script_timestamp': pine_data.get('timestamp'),
                    'timeframe': pine_data.get('timeframe', '1h')
                }
            
            # 2. Fallback: Tentar Binance se Pine Script não tiver dados
            logger.info(f"⚠️ Dados do Pine Script não encontrados para {symbol}, tentando Binance...")
            # 1. Coletar dados OHLCV históricos 100% REAIS da Binance
            logger.info(f"📊 Coletando dados OHLCV REAIS da Binance para {symbol}...")
            ohlcv_df = await binance_real_service.get_ohlcv_data(symbol, timeframe, limit=100)
            
            if ohlcv_df is None or len(ohlcv_df) < 26:  # Mínimo para MACD
                logger.error(f"❌ Dados OHLCV insuficientes para {symbol}")
                return self._generate_error_response(symbol, "Dados históricos insuficientes")
            
            # 2. Extrair preços de fechamento
            closes = ohlcv_df['close'].tolist()
            current_price = closes[-1]
            
            logger.info(f"📈 {len(closes)} pontos de preço coletados para {symbol}, preço atual: ${current_price:.2f}")
            
            # 3. Calcular indicadores técnicos REAIS
            logger.info(f"🧮 Calculando indicadores técnicos REAIS...")
            
            # RSI
            rsi = real_calculations.calculate_rsi(closes, period=14)
            
            # MACD
            macd_data = real_calculations.calculate_macd(closes)
            
            # Bollinger Bands
            bollinger = real_calculations.calculate_bollinger_bands(closes, period=20)
            
            # SMAs
            sma_20 = real_calculations.calculate_sma(closes, period=20)
            sma_50 = real_calculations.calculate_sma(closes, period=50)
            
            # EMAs
            ema_12 = real_calculations.calculate_ema(closes, period=12)
            ema_26 = real_calculations.calculate_ema(closes, period=26)
            
            # Volatilidade
            volatility = real_calculations.calculate_volatility(closes)
            
            # Tendência
            trend = real_calculations.analyze_trend(closes)
            
            # 4. Compilar indicadores técnicos
            technical_indicators = {
                'rsi': rsi,
                'macd': macd_data,
                'bollinger_bands': bollinger,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'ema_12': ema_12,
                'ema_26': ema_26,
                'volatility': volatility,
                'trend': trend,
                'data_points': len(closes)
            }
            
            # 5. Gerar análise e recomendação REAL
            analysis_result = self._generate_real_analysis(symbol, current_price, technical_indicators)
            
            # 6. Gerar análise IA baseada em dados REAIS
            ai_analysis = await self._generate_ai_analysis(symbol, current_price, technical_indicators)
            
            # 7. Compilar resultado final
            result = {
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'current_price': current_price,
                'technical_indicators': technical_indicators,
                'analysis': analysis_result,
                'ai_analysis': ai_analysis,
                'data_source': 'Binance Exchange Real',
                'calculation_method': 'Mathematical Formulas',
                'timestamp': datetime.now().isoformat(),
                'data_quality': 'REAL'
            }
            
            logger.info(f"✅ Análise técnica REAL concluída para {symbol}: {analysis_result['recommendation']} ({analysis_result['confidence']}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise técnica REAL de {symbol}: {e}")
            return self._generate_error_response(symbol, str(e))
    
    def _generate_real_analysis(self, symbol: str, price: float, indicators: Dict) -> Dict[str, Any]:
        """
        Gerar análise e recomendação baseada em indicadores REAIS
        """
        try:
            signals = []
            score = 50  # Neutro
            
            # Análise RSI
            if indicators['rsi'] is not None:
                rsi = indicators['rsi']
                if rsi > 70:
                    signals.append("RSI Sobrecomprado")
                    score -= 15
                elif rsi < 30:
                    signals.append("RSI Sobrevendido")
                    score += 15
                elif rsi > 50:
                    score += 5
                else:
                    score -= 5
            
            # Análise MACD
            if indicators['macd'] is not None:
                macd = indicators['macd']
                if macd['histogram'] > 0:
                    signals.append("MACD Positivo")
                    score += 10
                else:
                    signals.append("MACD Negativo")
                    score -= 10
            
            # Análise Bollinger Bands
            if indicators['bollinger_bands'] is not None:
                bb = indicators['bollinger_bands']
                if price > bb['upper']:
                    signals.append("Preço acima Bollinger Superior")
                    score -= 10
                elif price < bb['lower']:
                    signals.append("Preço abaixo Bollinger Inferior")
                    score += 10
            
            # Análise SMAs
            if indicators['sma_20'] is not None and indicators['sma_50'] is not None:
                if indicators['sma_20'] > indicators['sma_50']:
                    signals.append("SMA20 > SMA50 (Bullish)")
                    score += 10
                else:
                    signals.append("SMA20 < SMA50 (Bearish)")
                    score -= 10
            
            # Análise de tendência
            if indicators['trend'] == 'BULLISH':
                signals.append("Tendência de Alta")
                score += 15
            elif indicators['trend'] == 'BEARISH':
                signals.append("Tendência de Baixa")
                score -= 15
            
            # Análise de volatilidade
            if indicators['volatility'] is not None:
                if indicators['volatility'] > 5:
                    signals.append("Alta Volatilidade")
                    score -= 5
            
            # Determinar recomendação
            if score >= 70:
                recommendation = "STRONG_BUY"
            elif score >= 55:
                recommendation = "BUY"
            elif score >= 45:
                recommendation = "HOLD"
            elif score >= 30:
                recommendation = "SELL"
            else:
                recommendation = "STRONG_SELL"
            
            # Calcular confiança baseada na qualidade dos dados
            confidence = min(95, max(60, score + 20))
            
            return {
                'recommendation': recommendation,
                'score': max(0, min(100, score)),
                'confidence': confidence,
                'signals': signals,
                'summary': f"Análise baseada em {indicators['data_points']} pontos de dados REAIS"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na geração de análise: {e}")
            return {
                'recommendation': 'HOLD',
                'score': 50,
                'confidence': 50,
                'signals': ['Erro na análise'],
                'summary': 'Análise incompleta devido a erro'
            }
    
    async def _generate_ai_analysis(self, symbol: str, price: float, indicators: Dict) -> Optional[str]:
        """
        Gerar análise IA baseada em indicadores técnicos REAIS
        """
        try:
            # Preparar prompt com dados REAIS
            prompt = f"""
            Analise tecnicamente {symbol} com os seguintes dados REAIS:
            
            Preço atual: ${price:.2f}
            
            Indicadores Técnicos REAIS:
            - RSI (14): {indicators['rsi']:.2f if indicators['rsi'] else 'N/A'}
            - MACD: {indicators['macd']['macd']:.4f if indicators['macd'] else 'N/A'}
            - MACD Signal: {indicators['macd']['signal']:.4f if indicators['macd'] else 'N/A'}
            - MACD Histogram: {indicators['macd']['histogram']:.4f if indicators['macd'] else 'N/A'}
            - Bollinger Superior: ${indicators['bollinger_bands']['upper']:.2f if indicators['bollinger_bands'] else 'N/A'}
            - Bollinger Inferior: ${indicators['bollinger_bands']['lower']:.2f if indicators['bollinger_bands'] else 'N/A'}
            - SMA 20: ${indicators['sma_20']:.2f if indicators['sma_20'] else 'N/A'}
            - SMA 50: ${indicators['sma_50']:.2f if indicators['sma_50'] else 'N/A'}
            - Volatilidade: {indicators['volatility']:.2f}% if indicators['volatility'] else 'N/A'
            - Tendência: {indicators['trend']}
            
            Baseado nestes dados REAIS calculados matematicamente, forneça uma análise técnica profissional em português com insights específicos sobre a situação atual do ativo.
            """
            
            ai_response = await gemini_service.analyze_market_data(prompt)
            if ai_response and ai_response.get('analysis'):
                return ai_response['analysis']
                
        except Exception as e:
            logger.warning(f"⚠️ Falha na análise IA para {symbol}: {e}")
        
        return None
    
    def _generate_error_response(self, symbol: str, error: str) -> Dict[str, Any]:
        """
        Gerar resposta de erro
        """
        return {
            'symbol': symbol.upper(),
            'error': error,
            'data_quality': 'ERROR',
            'timestamp': datetime.now().isoformat()
        }

# Instância global
real_analysis_service = RealAnalysisService()

