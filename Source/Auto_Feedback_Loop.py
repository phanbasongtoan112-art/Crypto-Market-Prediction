import schedule
import time
from datetime import datetime
import subprocess

def daily_feedback_job():
    print(f"\n[{datetime.now()}] 🔄 KÍCH HOẠT FEEDBACK LOOP...")
    
    print("1. Đang kéo dữ liệu mới nhất từ Binance (Step 4)...")
    subprocess.run(["python", "Collector.py"]) # Chạy lại file cào data
    
    print("2. Đang Train lại mô hình với dữ liệu mới (Step 7)...")
    subprocess.run(["python", "TrainModel_DB.py"]) # Chạy lại file Train AI
    
    print(f"[{datetime.now()}] ✅ Hoàn tất cập nhật AI!")

# Đặt lịch định kỳ tự động chạy vào lúc 00:00 (Nửa đêm) mỗi ngày
schedule.every().day.at("00:00").do(daily_feedback_job)

print("⏳ Hệ thống Feedback Tự động đang chạy ngầm. Bấm Ctrl+C để thoát.")
while True:
    schedule.run_pending()
    time.sleep(60) # Cứ 60 giây check lịch 1 lần