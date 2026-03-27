import numpy as np
# Fix lỗi tương thích giữa pandas_ta và numpy phiên bản mới
np.object = object
np.typeDict = dict

import ccxt
import pandas as pd
import pandas_ta as ta
import time
import sqlite3

DB_PATH = "crypto_database.db"

def fetch_binance_ohlcv(symbol='BTC/USDT', timeframe='1d', start_date='2020-01-01T00:00:00Z'):
    """Kéo dữ liệu OHLCV từ Binance"""
    print(f"🚀 Đang kéo dữ liệu {symbol} từ Binance (từ {start_date[:4]} đến nay)...")
    exchange = ccxt.binance()
    since = exchange.parse8601(start_date)
    all_ohlcv = []

    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit=1000)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1 
            time.sleep(0.1) # Tránh bị rate limit
        except Exception as e:
            print(f"❌ Lỗi khi lấy dữ liệu: {e}")
            break

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def apply_technical_indicators(df):
    """Tính toán các chỉ báo kỹ thuật RSI, MACD"""
    df["RSI"] = ta.rsi(df["close"], 14)
    macd = ta.macd(df["close"])
    if macd is not None:
        df["MACD"] = macd.iloc[:, 0]
    return df.dropna().reset_index(drop=True)

def save_to_database(raw_df, processed_df):
    """Lưu toàn bộ các bảng vào SQLite"""
    print(f"💾 Đang lưu dữ liệu vào {DB_PATH}...")
    with sqlite3.connect(DB_PATH) as conn:
        # 1. Lưu bảng nguyên thủy
        raw_df.to_sql("raw_ohlcv", con=conn, if_exists="replace", index=False)
        
        # 2. Lưu bảng đã xử lý
        processed_df.to_sql("spot_ohlcv", con=conn, if_exists="replace", index=False)
        
        # 3. TÍNH TOÁN VÀ LƯU LUÔN BẢNG THỐNG KÊ (STATISTICS) VÀO DATABASE
        cols_to_stat = ['open', 'high', 'low', 'close', 'volume']
        stats_df = processed_df[cols_to_stat].describe().T
        stats_df['variance'] = processed_df[cols_to_stat].var()
        
        display_stats = stats_df[['min', 'max', 'mean', 'std', 'variance']].copy()
        display_stats.columns = ['Min', 'Max', 'Mean', 'Std', 'Variance']
        display_stats.insert(0, 'Thuoc_Tinh', display_stats.index) # Thêm cột tên
        
        display_stats.to_sql("descriptive_statistics", con=conn, if_exists="replace", index=False)
        
    print(f"✅ HOÀN TẤT! Đã lưu bản thô, bản xử lý và bảng thống kê vào Database.")

# Đảm bảo phần dưới cùng chạy đúng như này:
if __name__ == "__main__":
    raw_df = fetch_binance_ohlcv()
    processed_df = apply_technical_indicators(raw_df.copy())
    save_to_database(raw_df, processed_df)
    