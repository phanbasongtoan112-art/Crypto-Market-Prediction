import ccxt
import requests
import pandas as pd
from fredapi import Fred
from sqlalchemy import create_engine, text
import urllib.parse
from datetime import date
import time

# --- CẤU HÌNH ---
START_DATE = pd.Timestamp("2020-01-01")
SYMBOL = "BTC/USDT"
FRED_API_KEY = "9413dede70caf9007f0518ba171713e3"
DB_USER = "root"
DB_PASS = "Binh@n32160260"
DB_NAME = "crypto_db"

encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@localhost:3306/{DB_NAME}")

def get_max_timestamp(table_name):
    """Lấy mốc thời gian mới nhất từ database để chỉ cập nhật dữ liệu mới"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT MAX(timestamp) FROM {table_name}"))
            res = result.fetchone()[0]
            return pd.to_datetime(res) if res else None
    except Exception:
        return None

def collect_raw_spot_ohlcv():
    print("🚀 Đang thu thập Spot Market Data (Raw)...")
    exchange = ccxt.binance()
    last_ts = get_max_timestamp("spot_ohlcv")
    
    # Chỉ lấy dữ liệu nối tiếp từ thời điểm cuối cùng trong DB
    if last_ts:
        fetch_since = int((last_ts + pd.Timedelta(milliseconds=1)).timestamp() * 1000)
    else:
        fetch_since = int(START_DATE.timestamp() * 1000)

    all_ohlcv = []
    now_ms = int(time.time() * 1000)
    
    while fetch_since < now_ms:
        try:
            ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe='1d', since=fetch_since, limit=1000)
            if not ohlcv: break
            all_ohlcv.extend(ohlcv)
            fetch_since = ohlcv[-1][0] + 1
            time.sleep(0.1) # Tránh bị rate limit
        except Exception as e:
            print(f"⚠️ Lỗi API Binance: {e}"); time.sleep(2); break

    if all_ohlcv:
        df = pd.DataFrame(all_ohlcv, columns=["timestamp","open","high","low","close","volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.drop_duplicates(subset=['timestamp']).sort_values("timestamp")

        # Lưu trực tiếp dữ liệu thô vào DB
        df_final = df.query("timestamp >= @START_DATE")
        
        if not df_final.empty:
            df_final.to_sql("spot_ohlcv", con=engine, if_exists="append", index=False)
            print(f"✅ Xong Spot Raw: Đã thêm {len(df_final)} dòng mới.")
        else:
            print("☕ Spot Data đã là mới nhất.")

def collect_raw_onchain_macro_sentiment():
    print("🌐 Đang thu thập On-chain, Macro và Sentiment (Raw)...")
    
    try:
        # --- 1. Dữ liệu On-chain Thô ---
        def fetch_blockchain(chart):
            total_days = (pd.Timestamp.now() - START_DATE).days + 10
            url = f"https://api.blockchain.info/charts/{chart}?timespan={total_days}days&sampled=false&format=json"
            r = requests.get(url).json()["values"]
            t = pd.DataFrame(r, columns=["x", "y"]).rename(columns={"y": chart.replace('-', '_')})
            t["timestamp"] = pd.to_datetime(t["x"], unit="s").dt.normalize()
            return t[["timestamp", chart.replace('-', '_')]]

        onchain = fetch_blockchain("hash-rate")
        onchain = pd.merge(onchain, fetch_blockchain("n-unique-addresses"), on="timestamp", how="outer")
        onchain = pd.merge(onchain, fetch_blockchain("n-transactions"), on="timestamp", how="outer")
        
        onchain = onchain.sort_values("timestamp").query("timestamp >= @START_DATE")
        onchain.rename(columns={"n_transactions": "onchain_transactions"}).to_sql("onchain_metrics", con=engine, if_exists="replace", index=False)

        # --- 2. Dữ liệu Vĩ mô (Macro) Thô ---
        fred = Fred(api_key=FRED_API_KEY)
        macro_map = {"DXY":"DTWEXBGS", "SP500":"SP500", "NASDAQ":"NASDAQCOM", "FED_RATE":"FEDFUNDS", "CPI":"CPIAUCSL"}
        macro_list = []
        
        for name, fid in macro_map.items():
            s = fred.get_series(fid, observation_start=START_DATE)
            df_s = pd.DataFrame(s, columns=[name]).reset_index().rename(columns={"index": "timestamp"})
            macro_list.append(df_s)
            
        macro = macro_list[0]
        for df_s in macro_list[1:]:
            macro = pd.merge(macro, df_s, on="timestamp", how="outer")
            
        macro = macro.sort_values("timestamp").query("timestamp >= @START_DATE")
        macro.to_sql("macro_data", con=engine, if_exists="replace", index=False)

        # --- 3. Dữ liệu Tâm lý (Fear & Greed) Thô ---
        fng_res = requests.get("https://api.alternative.me/fng/?limit=0").json()["data"]
        fng_df = pd.DataFrame(fng_res)
        fng_df["timestamp"] = pd.to_datetime(fng_df["timestamp"].astype(int), unit="s").dt.normalize()
        fng_df["fng_val"] = pd.to_numeric(fng_df["value"])
        
        fng_df = fng_df[["timestamp", "fng_val"]].drop_duplicates(subset=['timestamp']).sort_values("timestamp")
        fng_df.query("timestamp >= @START_DATE").to_sql("fear_greed_index", con=engine, if_exists="replace", index=False)
        
        print("✅ Thu thập dữ liệu Raw On-chain, Macro, Sentiment hoàn tất.")
    except Exception as e:
        print(f"❌ Lỗi khi tải dữ liệu: {e}")

if __name__ == "__main__":
    collect_raw_spot_ohlcv()
    collect_raw_onchain_macro_sentiment()