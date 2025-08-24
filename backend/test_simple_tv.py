import asyncio
import sys
sys.path.append('/home/ubuntu/CryptoAnalyzer-Pro-Funcional/backend')
from services.simple_tradingview_service import simple_tradingview_service

async def test():
    try:
        price = await simple_tradingview_service.get_current_price('BTC')
        print(f'✅ BTC Price: ${price:.2f}')
        
        df = await simple_tradingview_service.get_ohlcv_data('BTC', '1h', 50)
        if df is not None:
            print(f'✅ OHLCV Data: {len(df)} rows')
            print(f'Latest close: ${df.iloc[-1]["close"]:.2f}')
            print(f'Price range: ${df["close"].min():.2f} - ${df["close"].max():.2f}')
        else:
            print('❌ No OHLCV data')
    except Exception as e:
        print(f'❌ Error: {e}')
    finally:
        await simple_tradingview_service.close()

asyncio.run(test())
