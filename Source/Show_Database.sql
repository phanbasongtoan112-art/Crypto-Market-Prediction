-- Kịch bản SQL dùng để truy vấn và kiểm tra dữ liệu trong SQLite 
-- (Chạy các lệnh này trong DB Browser for SQLite hoặc DBeaver)

-- 1. Xem cấu trúc các bảng đã được Python tự động tạo
SELECT name, sql FROM sqlite_master WHERE type='table';

-- 2. Xem 10 ngày giao dịch gần nhất của dữ liệu gốc (kèm các chỉ báo kỹ thuật)
SELECT timestamp, open, high, low, close, volume, RSI, MACD 
FROM spot_ohlcv 
ORDER BY timestamp DESC 
LIMIT 10;

-- 3. Đánh giá nhanh: Xem những ngày mà AI dự đoán sai lệch nhiều nhất
SELECT Date, Actual_Price, AI_Predicted_Price, Error_USD
FROM ai_6_years_predictions
ORDER BY Error_USD DESC
LIMIT 10;

-- 4. Thống kê nhanh: Giá trung bình, giá cao nhất, thấp nhất của BTC từ trước đến nay
SELECT 
    MIN(low) AS All_Time_Low,
    MAX(high) AS All_Time_High,
    AVG(close) AS Average_Price
FROM spot_ohlcv;