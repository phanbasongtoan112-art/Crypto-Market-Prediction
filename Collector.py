import ccxt
import pandas as pd
import pandas_ta as ta
from sqlalchemy import create_engine
import time

# Tạo database SQLite cục bộ (KHÔNG CẦN PASSWORD, KHÔNG BAO GIỜ LỖI 10061)
engine = create_engine("sqlite:///crypto_database.db")

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
            since = ohlcv[-1][0] + 1 # Chạy tiếp từ cây nến cuối cùng
            time.sleep(0.1)
        except Exception as e:
            print(f"Lỗi: {e}")
            break

    # Xử lý dữ liệu
    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Tính các chỉ báo kỹ thuật cơ bản
    df["RSI"] = ta.rsi(df["close"], 14)
    macd = ta.macd(df["close"])
    if macd is not None:
        df["MACD"] = macd.iloc[:, 0]
    
    df = df.dropna().reset_index(drop=True)
    
    # Lưu vào SQL
    print("💾 Đang lưu vào SQL Database (bảng 'spot_ohlcv')...")
    df.to_sql("spot_ohlcv", con=engine, if_exists="replace", index=False)
    print(f"✅ HOÀN TẤT! Đã lưu {len(df)} ngày giao dịch vào 'crypto_database.db'")

if __name__ == "__main__":
    get_binance_data()