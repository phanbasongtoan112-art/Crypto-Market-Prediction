import numpy as np
np.object = object
np.typeDict = dict

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import sqlite3

DB_PATH = "crypto_database.db"

def load_data():
    """Tải dữ liệu từ database"""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql("SELECT * FROM spot_ohlcv", con=conn)

def build_lstm_model(input_shape):
    """Khởi tạo kiến trúc mạng LSTM"""
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(64, return_sequences=False),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def train_and_predict():
    print("🚀 Bắt đầu đọc dữ liệu từ SQL Database...")
    try:
        df = load_data()
    except Exception as e:
        print("❌ Chưa có Database. Hãy chạy file Collector.py trước!")
        return

    # 1. Chuẩn bị dữ liệu
    features = ['close', 'volume', 'RSI', 'MACD']
    data = df[features].values
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    close_scaler = MinMaxScaler(feature_range=(0, 1))
    close_scaler.fit(df[['close']])

    LOOK_BACK = 60
    X, y = [], []
    for i in range(LOOK_BACK, len(scaled_data)):
        X.append(scaled_data[i-LOOK_BACK:i])
        y.append(scaled_data[i, 0])
        
    X, y = np.array(X), np.array(y)
    
# 2. Huấn luyện Model (Có chia tập Validation theo yêu cầu Slide 7)
    print("🧠 Đang huấn luyện AI LSTM (Xin chờ một lát)...")
    model = build_lstm_model((X.shape[1], X.shape[2]))

    model.summary()
    
    # BỔ SUNG: validation_split=0.2 để chia 20% dữ liệu làm tập kiểm định
    # BỔ SUNG: Gán vào biến 'history' để lưu lại quá trình học
    history = model.fit(X, y, batch_size=32, epochs=10, validation_split=0.2, verbose=1)

    # LƯU LỊCH SỬ HỌC (LEARNING CURVE) VÀO DATABASE
    hist_df = pd.DataFrame({
        'Epoch': range(1, len(history.history['loss']) + 1),
        'Training_Error': history.history['loss'],
        'Validation_Error': history.history['val_loss']
    })
    with sqlite3.connect(DB_PATH) as conn:
        hist_df.to_sql("training_history", con=conn, if_exists="replace", index=False)

    # 3. Dự đoán
    print("\n🔮 Đang tính toán dự đoán...")
    all_predictions_scaled = model.predict(X)
    predicted_prices = close_scaler.inverse_transform(all_predictions_scaled).flatten()
    actual_prices = close_scaler.inverse_transform(y.reshape(-1, 1)).flatten()
    dates = df['timestamp'].iloc[LOOK_BACK:].values

    # 4. Lưu kết quả
    results_df = pd.DataFrame({
        'Date': pd.to_datetime(dates),
        'Actual_Value': actual_prices,
        'Predicted_Value': predicted_prices
    })
    # BỔ SUNG: Sửa lại cách tính Difference (Có âm/dương) cho khớp Slide 13
    results_df['Difference'] = results_df['Actual_Value'] - results_df['Predicted_Value']
    
    with sqlite3.connect(DB_PATH) as conn:
        results_df.to_sql("ai_6_years_predictions", con=conn, if_exists="replace", index=False)
    print("💾 Đã lưu kết quả vào bảng 'ai_6_years_predictions'")
    
    # 5. Xuất biểu đồ
    plt.figure(figsize=(16, 8))
    # Đã sửa Actual_Price thành Actual_Value, và AI_Predicted_Price thành Predicted_Value
    plt.plot(results_df['Date'], results_df['Actual_Value'], color='blue', label='Giá Thực Tế', alpha=0.6)
    plt.plot(results_df['Date'], results_df['Predicted_Value'], color='red', label='AI Dự Đoán', alpha=0.8)
    
    plt.title('AI DỰ ĐOÁN GIÁ BITCOIN TRONG 6 NĂM (2020 - 2026)')
    plt.xlabel('Thời Gian')
    plt.ylabel('Giá (USDT)')
    plt.legend()
    plt.grid(True)
    
    plt.savefig('BieuDo_DuDoan_6Nam.png', dpi=300)
    print("✅ HOÀN TẤT! Hãy kiểm tra file 'BieuDo_DuDoan_6Nam.png'")

if __name__ == "__main__":
    train_and_predict()