import pandas as pd
import pandas_ta as ta
from sqlalchemy import create_engine
import urllib.parse

# --- CẤU HÌNH KẾT NỐI MYSQL ---
DB_USER = "root"
DB_PASS = "Binh@n32160260"
DB_NAME = "crypto_db"
encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@localhost:3306/{DB_NAME}")

FORECAST_HORIZON = 30 # Tầm nhìn dự báo 30 ngày

def preprocess_and_export_to_mysql():
    print("⏳ Bước 1: Đọc dữ liệu thô (Close, Volume) từ MySQL...")
    # Chỉ query các cột cần thiết để tối ưu bộ nhớ
    df = pd.read_sql("SELECT timestamp, close, volume FROM spot_ohlcv", con=engine)
    
    # Đặt timestamp làm index để xử lý chuỗi thời gian
    df = df.sort_values("timestamp").set_index("timestamp")

    print("⏳ Bước 2: Tính toán chỉ báo kỹ thuật (RSI, MACD)...")
    # Tính RSI chu kỳ 14
    df["RSI_14"] = ta.rsi(df["close"], length=14)
    
    # Tính MACD và lấy cột giá trị đường MACD chính
    macd = ta.macd(df["close"])
    df["MACD"] = macd.iloc[:, 0]

    print("⏳ Bước 3: Thiết lập nhãn dự báo (Target) và làm sạch...")
    # Shift giá lùi 30 ngày để làm target
    df["target_close_30d"] = df["close"].shift(-FORECAST_HORIZON)
    
    # Xóa toàn bộ các dòng chứa giá trị NULL/NaN 
    # (Bao gồm các ngày đầu thiếu đà để tính RSI/MACD và 30 ngày cuối cùng chưa có target)
    df_clean = df.dropna()

    print("🚀 Bước 4: XUẤT DỮ LIỆU ĐÃ TIỀN XỬ LÝ VỀ MYSQL...")
    # Xuất ra một bảng mới tinh tên là 'lstm_ready_data'
    # if_exists="replace": Sẽ ghi đè tạo lại bảng mới mỗi khi chạy để đảm bảo dữ liệu luôn chuẩn xác nhất
    df_clean.to_sql("lstm_ready_data", con=engine, if_exists="replace", index=True, index_label="timestamp")
    
    print(f"✅ THÀNH CÔNG! Đã xuất {len(df_clean)} dòng dữ liệu chuẩn về bảng 'lstm_ready_data'.")
    print("Mô hình LSTM có thể truy vấn bảng này để train ngay lập tức!")

if __name__ == "__main__":
    preprocess_and_export_to_mysql()