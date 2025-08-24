import asyncio
import sys
sys.path.append('/home/ubuntu/CryptoAnalyzer-Pro-Funcional/backend')
from services.binance_real_data import binance_real_service

async def test():
    try:
        print("🔥 TESTANDO BINANCE API REAL...")
        
        price = await binance_real_service.get_current_price('BTC')
        print(f'✅ BTC Preço REAL: ${price:.2f}')
        
        df = await binance_real_service.get_ohlcv_data('BTC', '1h', 50)
        if df is not None:
            print(f'✅ OHLCV REAL: {len(df)} candles')
            print(f'✅ Último close: ${df.iloc[-1]["close"]:.2f}')
            print(f'✅ Range: ${df["low"].min():.2f} - ${df["high"].max():.2f}')
        else:
            print('❌ Falha nos dados OHLCV')
    except Exception as e:
        print(f'❌ Erro: {e}')
    finally:
        await binance_real_service.close()

asyncio.run(test())
