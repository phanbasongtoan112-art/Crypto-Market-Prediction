import ccxt
import pandas as pd
import pandas_ta as ta
from sqlalchemy import create_engine
import time
import os

# 1. TẠO DATABASE SQLITE CỤC BỘ (NGAY TRONG THƯ MỤC CỦA BẠN)
db_name = "crypto_database.db"
engine = create_engine(f"sqlite:///{db_name}")

def get_binance_data():
    print("🚀 Đang kéo dữ liệu từ Binance (từ 2020 đến nay)...")
    exchange = ccxt.binance()
    symbol = 'BTC/USDT'
    timeframe = '1d'
    
    # Bắt đầu từ 01/01/2020
    since = exchange.parse8601('2020-01-01T00:00:00Z')
    all_ohlcv = []
    
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            if len(ohlcv) == 0:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1 
            time.sleep(0.1)
        except Exception as e:
            print(f"Lỗi: {e}")
            break

    # 2. XỬ LÝ DỮ LIỆU
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    df["RSI"] = ta.rsi(df["close"], 14)
    macd = ta.macd(df["close"])
    if macd is not None:
        df["MACD"] = macd.iloc[:, 0]
    
    df = df.dropna().reset_index(drop=True)
    
    # 3. LƯU VÀO SQLITE
    print(f"💾 Đang lưu vào {db_name} (bảng 'spot_ohlcv')...")
    df.to_sql("spot_ohlcv", con=engine, if_exists="replace", index=False)
    print(f"✅ HOÀN TẤT! Đã lưu {len(df)} ngày giao dịch vào '{db_name}'")

if __name__ == "__main__":
    get_binance_data()
