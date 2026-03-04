# 🚀 AI Crypto Price Predictor & Dashboard

Hệ thống thu thập dữ liệu tự động, huấn luyện mô hình Deep Learning (LSTM) để dự đoán giá Bitcoin (BTC/USDT) và trực quan hóa kết quả thông qua Web Dashboard tương tác.

## 📌 Tổng quan dự án (Overview)
Dự án này là một quy trình (pipeline) khép kín bao gồm 3 giai đoạn chính:
1. **Data Collection:** Tự động kéo dữ liệu lịch sử giá từ Binance (từ 2020 đến nay), tính toán các chỉ báo kỹ thuật (RSI, MACD) và lưu trữ cục bộ.
2. **AI Training:** Sử dụng mạng nơ-ron hồi quy LSTM (Long Short-Term Memory) để học chuỗi thời gian (look-back 60 ngày) và dự đoán giá đóng cửa.
3. **Visualization:** Xây dựng trang Web Dashboard bằng Streamlit để hiển thị dữ liệu thô, đánh giá sai số (MAPE) và vẽ biểu đồ so sánh giữa giá thực tế và giá AI dự đoán.

## 🛠️ Công nghệ sử dụng (Tech Stack)
* **Ngôn ngữ:** Python 3.13+
* **Machine Learning / AI:** TensorFlow (Keras), Scikit-learn
* **Xử lý dữ liệu:** Pandas, Numpy, Pandas-TA
* **Giao tiếp API:** CCXT (Binance API)
* **Cơ sở dữ liệu:** SQLite3
* **Giao diện Web:** Streamlit, Matplotlib

## 📂 Cấu trúc thư mục (File Structure)
```text
📦 project-folder
 ┣ 📜 collector.py            # Script kéo dữ liệu từ Binance và lưu vào SQLite
 ┣ 📜 train_model.py          # Script huấn luyện AI (LSTM) và lưu kết quả dự đoán
 ┣ 📜 CryptoDashboard.py      # Giao diện Web Streamlit
 ┣ 📜 requirements.txt        # Danh sách thư viện cần cài đặt
 ┣ 📜 crypto_database.db      # (Tự động tạo) Database lưu trữ toàn bộ dữ liệu
 ┗ 📜 BieuDo_DuDoan_6Nam.png  # (Tự động tạo) Ảnh biểu đồ dự đoán tĩnh
