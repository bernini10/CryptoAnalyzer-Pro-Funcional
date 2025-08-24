import asyncio
import sys
sys.path.append('/home/ubuntu/CryptoAnalyzer-Pro-Funcional/backend')
from services.real_analysis_service import real_analysis_service

async def test():
    try:
        result = await real_analysis_service.analyze_symbol_complete('BTC', '1h')
        print(f'✅ Analysis result: {result.get("data_source", "Unknown")}')
        print(f'✅ Data quality: {result.get("data_quality", "Unknown")}')
        print(f'✅ Current price: ${result.get("current_price", 0):.2f}')
        if 'technical_indicators' in result:
            rsi = result['technical_indicators'].get('rsi')
            print(f'✅ RSI: {rsi}')
    except Exception as e:
        print(f'❌ Error: {e}')

asyncio.run(test())
