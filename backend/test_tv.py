import asyncio
import sys
sys.path.append('/home/ubuntu/CryptoAnalyzer-Pro-Funcional/backend')
from services.tradingview_data_service import tradingview_service

async def test():
    try:
        price = await tradingview_service.get_current_price('BTC')
        print(f'✅ BTC Price: ${price}')
        
        df = await tradingview_service.get_ohlcv_data('BTC', '1h', 50)
        if df is not None:
            print(f'✅ OHLCV Data: {len(df)} rows')
            print(f'Latest close: ${df.iloc[-1]["close"]:.2f}')
        else:
            print('❌ No OHLCV data')
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        await tradingview_service.close()

asyncio.run(test())
