"""
Gemini AI Service for CryptoAnalyzer Pro - REAL IMPLEMENTATION
"""

import os
import logging
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GeminiService:
    """Real Gemini AI service for cryptocurrency analysis"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.session = None
        
        if not self.api_key:
            logger.warning("Gemini API key not found - AI features will be disabled")
        else:
            logger.info("🤖 Gemini AI service initialized with API key")
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, prompt: str) -> Optional[str]:
        """Make request to Gemini AI API"""
        if not self.api_key:
            logger.warning("Gemini API key not available")
            return None
        
        try:
            session = await self._get_session()
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            url = f"{self.base_url}?key={self.api_key}"
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "candidates" in data and len(data["candidates"]) > 0:
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        return content.strip()
                    else:
                        logger.error("No candidates in Gemini response")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making Gemini AI request: {e}")
            return None
    
    async def analyze_crypto_signal(self, signal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analisa um sinal de criptomoeda usando Gemini AI
        """
        if not self.api_key:
            return None
        
        try:
            # Extrair dados principais
            symbol = signal_data.get('symbol', 'Unknown')
            price = signal_data.get('price', 0)
            rsi = signal_data.get('rsi', 0)
            macd = signal_data.get('macd', 0)
            recommendation = signal_data.get('signal', 'HOLD')
            confidence = signal_data.get('confidence', 50)
            timeframe = signal_data.get('timeframe', '1h')
            
            # Criar prompt para análise
            prompt = f"""
            Analise este sinal de criptomoeda e forneça insights profissionais:
            
            DADOS DO SINAL:
            - Símbolo: {symbol}
            - Preço: ${price:,.2f}
            - RSI: {rsi:.2f}
            - MACD: {macd:.2f}
            - Recomendação: {recommendation}
            - Confiança: {confidence}%
            - Timeframe: {timeframe}
            
            Por favor, forneça:
            1. Análise técnica detalhada
            2. Contexto de mercado
            3. Níveis de suporte e resistência
            4. Recomendação de ação
            5. Gestão de risco
            
            Responda em formato JSON com as chaves:
            - analysis: análise detalhada
            - market_context: contexto do mercado
            - support_resistance: níveis importantes
            - action_recommendation: recomendação específica
            - risk_management: gestão de risco
            - confidence_score: score de 1-100
            """
            
            response = await self._make_request(prompt)
            
            if response:
                # Tentar extrair JSON da resposta
                try:
                    # Limpar resposta e extrair JSON
                    clean_response = response.strip()
                    if clean_response.startswith('```json'):
                        clean_response = clean_response[7:-3]
                    elif clean_response.startswith('```'):
                        clean_response = clean_response[3:-3]
                    
                    ai_analysis = json.loads(clean_response)
                    
                    # Adicionar metadados
                    ai_analysis['generated_at'] = datetime.now().isoformat()
                    ai_analysis['symbol'] = symbol
                    ai_analysis['model'] = 'gemini-pro'
                    
                    logger.info(f"🤖 Gemini AI analysis successful for {symbol}")
                    return ai_analysis
                    
                except json.JSONDecodeError:
                    # Se não conseguir parsear JSON, retornar resposta simples
                    return {
                        'analysis': response,
                        'generated_at': datetime.now().isoformat(),
                        'symbol': symbol,
                        'model': 'gemini-pro',
                        'confidence_score': 75
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Gemini AI analysis error for {symbol}: {e}")
            return None

    async def get_crypto_recommendation(self, symbol: str, analysis_data: Dict) -> str:
        """Get AI recommendation for a specific cryptocurrency using REAL analysis data"""
        if not self.api_key:
            return self._get_fallback_recommendation(symbol, analysis_data)
        
        try:
            # Extract real analysis data
            rsi = analysis_data.get('indicators', {}).get('rsi')
            macd = analysis_data.get('indicators', {}).get('macd')
            signals = analysis_data.get('signals', [])
            confidence = analysis_data.get('confidence', 50)
            score = analysis_data.get('score', 50)
            recommendation = analysis_data.get('recommendation', 'HOLD')
            
            prompt = f"""
            Analyze this REAL cryptocurrency data for {symbol} and provide a professional trading recommendation:
            
            REAL TECHNICAL ANALYSIS DATA:
            - Current Recommendation: {recommendation}
            - Confidence Score: {confidence}%
            - Technical Score: {score}/100
            - RSI: {rsi if rsi else 'N/A'}
            - MACD: {macd if macd else 'N/A'}
            - Detected Signals: {', '.join(signals) if signals else 'None'}
            - Analysis Source: Real mathematical calculations from CoinGecko data
            
            Please provide:
            1. A concise analysis (2-3 sentences)
            2. Risk assessment (Low/Medium/High)
            3. Time horizon recommendation (Short/Medium/Long term)
            4. Key levels to watch
            
            Keep response under 200 words and focus on actionable insights.
            """
            
            response = await self._make_request(prompt)
            
            if response:
                return f"🤖 **AI Analysis for {symbol}:**\n\n{response}"
            else:
                return self._get_fallback_recommendation(symbol, analysis_data)
                
        except Exception as e:
            logger.error(f"Error getting AI recommendation for {symbol}: {e}")
            return self._get_fallback_recommendation(symbol, analysis_data)
    
    def _get_fallback_recommendation(self, symbol: str, analysis_data: Dict) -> str:
        """Fallback recommendation when AI is not available"""
        recommendation = analysis_data.get('recommendation', 'HOLD')
        confidence = analysis_data.get('confidence', 50)
        score = analysis_data.get('score', 50)
        signals = analysis_data.get('signals', [])
        
        risk_level = "High" if confidence < 60 else "Medium" if confidence < 80 else "Low"
        
        analysis_text = f"""
        📊 **Technical Analysis for {symbol}:**
        
        **Recommendation:** {recommendation}
        **Confidence:** {confidence}%
        **Technical Score:** {score}/100
        **Risk Level:** {risk_level}
        
        **Key Signals:** {', '.join(signals[:3]) if signals else 'No strong signals detected'}
        
        **Analysis:** Based on real mathematical calculations of RSI, MACD, and Bollinger Bands using historical price data from CoinGecko API.
        
        **Note:** This analysis uses real technical indicators but AI recommendations are currently unavailable.
        """
        
        return analysis_text

    async def get_altcoin_recommendation(
        self, 
        altcoin_season_index: float, 
        bitcoin_dominance: float, 
        top_altcoins: List[Dict]
    ) -> str:
        """Get AI-powered altcoin season recommendation"""
        
        altcoins_text = ", ".join([
            f"{coin['symbol']} (+{coin['vs_btc_7d']:.1f}% vs BTC)" 
            for coin in top_altcoins
        ])
        
        prompt = f"""
        As a professional cryptocurrency market analyst, provide a concise investment recommendation based on these REAL market conditions:

        Current Market Data:
        - Altcoin Season Index: {altcoin_season_index}/100
        - Bitcoin Dominance: {bitcoin_dominance}%
        - Top Performing Altcoins vs BTC (7d): {altcoins_text}
        - Analysis Date: {datetime.now().strftime('%Y-%m-%d')}

        Please provide:
        1. A clear, actionable recommendation (2-3 sentences)
        2. Risk assessment
        3. Specific strategy suggestion

        Keep response under 150 words, professional tone, focused on practical advice.
        """
        
        try:
            response = await self._make_request(prompt)
            
            if response:
                return response
            else:
                # Fallback recommendation
                if altcoin_season_index >= 65:
                    return "Strong altcoin momentum detected. Consider diversifying into quality altcoins with solid fundamentals. Risk: Medium. Strategy: Gradual position building in top-tier altcoins."
                elif altcoin_season_index >= 50:
                    return "Mixed market signals. Selective altcoin positions recommended. Risk: Medium-High. Strategy: Focus on established altcoins with strong use cases."
                else:
                    return "Bitcoin dominance remains strong. Conservative approach recommended. Risk: Low-Medium. Strategy: Maintain BTC focus with minimal altcoin exposure."
                    
        except Exception as e:
            logger.error(f"Error getting AI altcoin recommendation: {e}")
            return "Market analysis in progress. Please check back for updated recommendations."
    
    async def get_technical_analysis_insight(
        self, 
        symbol: str, 
        analysis_data: Dict[str, Any]
    ) -> str:
        """Get AI insight for technical analysis"""
        
        indicators_text = ""
        if "indicators" in analysis_data:
            indicators = analysis_data["indicators"]
            indicators_text = f"""
            RSI: {indicators.get('rsi', 'N/A')}
            MACD: {indicators.get('macd', 'N/A')}
            Bollinger Position: {indicators.get('bollinger_position', 'N/A')}
            """
        
        signals_text = ", ".join(analysis_data.get("signals", []))
        
        prompt = f"""
        As a cryptocurrency technical analyst, provide insight on {symbol.upper()} based on this REAL technical analysis:

        Technical Data:
        - Current Recommendation: {analysis_data.get('recommendation', 'N/A')}
        - Technical Score: {analysis_data.get('score', 'N/A')}/100
        - Confidence Level: {analysis_data.get('confidence', 0)*100:.0f}%
        - Key Signals: {signals_text}
        {indicators_text}

        Provide:
        1. Brief market context for {symbol}
        2. Key technical levels to watch
        3. Risk/reward assessment
        
        Keep response under 120 words, actionable and specific.
        """
        
        try:
            response = await self._make_request(prompt)
            
            if response:
                return response
            else:
                # Fallback insight
                recommendation = analysis_data.get('recommendation', 'hold').upper()
                score = analysis_data.get('score', 50)
                
                if score >= 80:
                    return f"{symbol} shows strong technical setup. Multiple bullish signals align. Monitor for continuation patterns. Risk/Reward: Favorable for medium-term positions."
                elif score >= 60:
                    return f"{symbol} presents mixed signals. Selective entry on pullbacks recommended. Watch key support/resistance levels. Risk/Reward: Moderate."
                else:
                    return f"{symbol} lacks clear direction. Wait for better technical setup. Avoid FOMO entries. Risk/Reward: Unfavorable currently."
                    
        except Exception as e:
            logger.error(f"Error getting AI technical insight for {symbol}: {e}")
            return "Technical analysis in progress. AI insights will be available shortly."
    
    async def get_market_sentiment_analysis(self, market_data: Dict[str, Any]) -> str:
        """Get AI-powered market sentiment analysis"""
        
        prompt = f"""
        Analyze the current cryptocurrency market sentiment based on this REAL data:

        Market Metrics:
        - Total Market Cap: ${market_data.get('total_market_cap', 0):,.0f}
        - 24h Volume: ${market_data.get('total_volume_24h', 0):,.0f}
        - Bitcoin Dominance: {market_data.get('bitcoin_dominance', 0):.1f}%
        - Market Cap Change 24h: {market_data.get('market_cap_change_24h', 0):+.1f}%
        - Fear/Greed Index: {market_data.get('fear_greed_index', 50)}/100

        Provide:
        1. Overall market sentiment (1-2 sentences)
        2. Key factors driving current conditions
        3. Short-term outlook

        Keep response under 100 words, professional and insightful.
        """
        
        try:
            response = await self._make_request(prompt)
            
            if response:
                return response
            else:
                # Fallback sentiment
                fear_greed = market_data.get('fear_greed_index', 50)
                dominance = market_data.get('bitcoin_dominance', 60)
                
                if fear_greed >= 70:
                    return "Market sentiment shows strong optimism with elevated greed levels. Caution advised as euphoric conditions often precede corrections."
                elif fear_greed <= 30:
                    return "Market sentiment reflects significant fear. Historically, these conditions present accumulation opportunities for patient investors."
                else:
                    return "Market sentiment remains balanced with neutral fear/greed levels. Selective opportunities emerging across different sectors."
                    
        except Exception as e:
            logger.error(f"Error getting AI market sentiment: {e}")
            return "Market sentiment analysis in progress. Please check back for updated insights."
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None


# Global service instance
gemini_service = GeminiService()

