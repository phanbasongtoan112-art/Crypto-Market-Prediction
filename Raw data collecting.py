import ccxt
import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse
import time

# --- CẤU HÌNH KẾT NỐI MYSQL ---
START_DATE = pd.Timestamp("2020-01-01")
SYMBOL = "BTC/USDT"
DB_USER = "root"
DB_PASS = "Binh@n32160260"
DB_NAME = "crypto_db"

# Khởi tạo Engine kết nối với MySQL
encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@localhost:3306/{DB_NAME}")

def collect_and_export_to_mysql():
    print("🚀 Đang tải dữ liệu Spot Market (Binance) và xuất về MySQL...")
    exchange = ccxt.binance()
    
    # 1. Truy vấn MySQL xem đã có dữ liệu cũ chưa để chạy nối tiếp
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(timestamp) FROM spot_ohlcv"))
            res = result.fetchone()[0]
            last_ts = pd.to_datetime(res) if res else None
    except Exception:
        last_ts = None

    if last_ts:
        fetch_since = int((last_ts + pd.Timedelta(milliseconds=1)).timestamp() * 1000)
    else:
        fetch_since = int(START_DATE.timestamp() * 1000)

    all_ohlcv = []
    now_ms = int(time.time() * 1000)
    
    # 2. Vòng lặp kéo dữ liệu từ API
    while fetch_since < now_ms:
        try:
            ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe='1d', since=fetch_since, limit=1000)
            if not ohlcv: break
            all_ohlcv.extend(ohlcv)
            fetch_since = ohlcv[-1][0] + 1
            time.sleep(0.1) 
        except Exception as e:
            print(f"⚠️ Lỗi kết nối API: {e}"); time.sleep(2); break

    # 3. Gom dữ liệu và XUẤT VỀ MYSQL
    if all_ohlcv:
        df = pd.DataFrame(all_ohlcv, columns=["timestamp","open","high","low","close","volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.drop_duplicates(subset=['timestamp']).sort_values("timestamp")

        df_final = df.query("timestamp >= @START_DATE")
        
        if not df_final.empty:
            # LỆNH XUẤT DỮ LIỆU VỀ MYSQL:
            # if_exists="append": Sẽ tự động nối thêm dữ liệu mới vào bảng đã có
            df_final.to_sql("spot_ohlcv", con=engine, if_exists="append", index=False)
            
            print(f"✅ THÀNH CÔNG! Đã xuất {len(df_final)} dòng dữ liệu thô về bảng 'spot_ohlcv' trong MySQL.")
        else:
            print("☕ Dữ liệu trong MySQL đã là mới nhất, không cần cập nhật thêm.")

if __name__ == "__main__":
    collect_and_export_to_mysql()