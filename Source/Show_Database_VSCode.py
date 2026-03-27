import sqlite3
import pandas as pd

DB_PATH = "crypto_database.db"

def show_database_in_terminal():
    print("🚀 ĐANG TRUY XUẤT CƠ SỞ DỮ LIỆU SQLITE (crypto_database.db)...\n")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            
            print("=========================================================")
            print("1. BẢNG DỮ LIỆU THÔ (RAW DATA) - 5 dòng đầu tiên")
            print("=========================================================")
            df_raw = pd.read_sql("SELECT * FROM raw_ohlcv LIMIT 5", conn)
            print(df_raw.to_string(index=False), "\n")

            print("=========================================================")
            print("2. BẢNG DỮ LIỆU ĐÃ TIỀN XỬ LÝ (PROCESSED) - 5 dòng đầu tiên")
            print("=========================================================")
            df_processed = pd.read_sql("SELECT timestamp, close, volume, RSI, MACD FROM spot_ohlcv LIMIT 5", conn)
            print(df_processed.to_string(index=False), "\n")

            print("=========================================================")
            print("3. BẢNG THỐNG KÊ MÔ TẢ (STATISTICS) - Toàn bộ")
            print("=========================================================")
            df_stats = pd.read_sql("SELECT * FROM descriptive_statistics", conn)
            print(df_stats.to_string(index=False), "\n")

            print("=========================================================")
            print("4. BẢNG KẾT QUẢ AI DỰ ĐOÁN (PREDICTIONS) - 5 dòng gần nhất")
            print("=========================================================")
            df_pred = pd.read_sql("SELECT Date, Actual_Value, Predicted_Value, Difference FROM ai_6_years_predictions ORDER BY Date DESC LIMIT 5", conn)
            print(df_pred.to_string(index=False), "\n")
            
            print("✅ HOÀN TẤT TRUY VẤN DATABASE!")
            
    except Exception as e:
        print(f"❌ Lỗi: Không thể đọc Database. Chi tiết: {e}")

if __name__ == "__main__":
    show_database_in_terminal()