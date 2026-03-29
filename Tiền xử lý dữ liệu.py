import pandas as pd
import pandas_ta as ta
from sqlalchemy import create_engine
import urllib.parse

# --- 1. CẤU HÌNH KẾT NỐI MYSQL ---
DB_USER = "root"
DB_PASS = "Binh@n32160260"
DB_NAME = "crypto_db"
encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@localhost:3306/{DB_NAME}")

FORECAST_HORIZON = 30 # Tầm nhìn dự báo: 30 ngày

def step_1_merge_and_clean():
    print("⏳ Bước 1: Gộp 4 bảng dữ liệu thô và lấp đầy khoảng trống...")
    # Tải dữ liệu từ database
    spot = pd.read_sql("SELECT * FROM spot_ohlcv", con=engine)
    onchain = pd.read_sql("SELECT * FROM onchain_metrics", con=engine)
    macro = pd.read_sql("SELECT * FROM macro_data", con=engine)
    fng = pd.read_sql("SELECT * FROM fear_greed_index", con=engine)

    # Gộp bảng (Left Join) dựa trên trục thời gian
    df = spot.merge(onchain, on="timestamp", how="left")
    df = df.merge(macro, on="timestamp", how="left")
    df = df.merge(fng, on="timestamp", how="left")
    
    # Thiết lập timestamp làm khóa chính và sắp xếp
    df = df.sort_values("timestamp").set_index("timestamp")
    
    # Kỹ thuật Fill Missing Values:
    # ffill() lấy dữ liệu ngày thứ 6 điền cho T7, CN (áp dụng cho chứng khoán/vĩ mô)
    # bfill() dự phòng lấp đầy các ô trống ở những ngày đầu tiên
    df = df.ffill().bfill() 
    
    # Xuất kết quả Bước 1 ra MySQL
    df.to_sql("step1_merged_raw", con=engine, if_exists="replace", index=True, index_label="timestamp")
    print("   -> Đã lưu thành công bảng 'step1_merged_raw'")
    return df

def step_2_feature_engineering(df):
    print("⏳ Bước 2: Tính toán các chỉ báo phân tích kỹ thuật (Feature Engineering)...")
    
    # Tính toán các chỉ báo xu hướng, động lượng và biến động
    df["RSI_14"] = ta.rsi(df["close"], length=14)
    df["SMA_20"] = ta.sma(df["close"], length=20)
    df["EMA_50"] = ta.ema(df["close"], length=50)
    
    macd = ta.macd(df["close"])
    df["MACD"] = macd.iloc[:, 0]
    df["ATR"] = ta.atr(df["high"], df["low"], df["close"])
    
    # Xuất kết quả Bước 2 ra MySQL
    df.to_sql("step2_added_features", con=engine, if_exists="replace", index=True, index_label="timestamp")
    print("   -> Đã lưu thành công bảng 'step2_added_features'")
    return df

def step_3_target_creation(df):
    print("⏳ Bước 3: Tạo nhãn dự báo 30 ngày (Target) và làm sạch cuối cùng...")
    
    # Dịch chuyển cột giá đóng cửa lùi về trước 30 dòng để tạo đáp án (Target)
    df["target_close_30d"] = df["close"].shift(-FORECAST_HORIZON)
    
    # Xóa bỏ các dòng bị rỗng (NaN)
    # Lỗ hổng sinh ra do 50 ngày đầu không đủ dữ liệu tính EMA50 và 30 ngày cuối không có đáp án tương lai
    df = df.dropna()
    
    # Xuất kết quả Bước 3 ra MySQL - Đây là bảng chốt giao cho nhóm làm mô hình
    df.to_sql("step3_final_target", con=engine, if_exists="replace", index=True, index_label="timestamp")
    print("   -> Đã lưu thành công bảng 'step3_final_target'")
    return df

if __name__ == "__main__":
    print("=== BẮT ĐẦU QUY TRÌNH TIỀN XỬ LÝ DỮ LIỆU ===")
    df_step1 = step_1_merge_and_clean()
    df_step2 = step_2_feature_engineering(df_step1)
    df_step3 = step_3_target_creation(df_step2)
    print("=== HOÀN TẤT! Bảng 'step3_final_target' đã sẵn sàng cho mạng LSTM ===")