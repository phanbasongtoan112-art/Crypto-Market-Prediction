# Vá lỗi Numpy cho phiên bản Python mới
import numpy as np
np.object = object
np.typeDict = dict

import streamlit as st
import pandas as pd
import sqlite3
import os

# Cấu hình trang web
st.set_page_config(page_title="AI Crypto Dashboard", layout="wide", page_icon="🚀")
st.title("🚀 Hệ thống AI Phân Tích & Dự Đoán Giá Bitcoin")

# Đường dẫn tới file Database
DB_PATH = "crypto_database.db"

def load_data(table_name):
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            conn.close()
            return df
        except:
            conn.close()
            return None
    return None

# Menu thanh điều hướng
st.sidebar.header("🎯 Menu Quản Lý")
menu = ["1. 📦 Raw Data (Collector)", "2. 🤖 Database AI (Train Model)", "3. 📈 Biểu Đồ Dự Đoán 6 Năm"]
choice = st.sidebar.radio("Chọn bảng điều khiển:", menu)

# ==========================================
# TAB 1: HIỂN THỊ DỮ LIỆU THÔ
# ==========================================
if choice == "1. 📦 Raw Data (Collector)":
    st.header("📦 Dữ liệu Giao dịch Thô (Từ Binance)")
    df_raw = load_data("spot_ohlcv")
    
    if df_raw is not None:
        st.success(f"✅ Đã kết nối Database! Tổng cộng có **{len(df_raw)}** ngày giao dịch.")
        st.dataframe(df_raw, use_container_width=True)
        st.subheader("Biểu đồ Giá đóng cửa (Close Price)")
        chart_data = df_raw.set_index('timestamp')['close']
        st.line_chart(chart_data)
    else:
        st.warning("⚠️ Chưa có dữ liệu. Hãy chạy file 'collector.py' trước!")

# ==========================================
# TAB 2: HIỂN THỊ KẾT QUẢ AI
# ==========================================
elif choice == "2. 🤖 Database AI (Train Model)":
    st.header("🤖 Database Kết Quả AI Dự Đoán")
    df_pred = load_data("ai_6_years_predictions")
    
    if df_pred is not None:
        mape = (df_pred['Error_USD'] / df_pred['Actual_Price']).mean() * 100
        col1, col2 = st.columns(2)
        col1.metric("Tổng số ngày dự đoán", f"{len(df_pred)} ngày")
        col2.metric("Sai số trung bình (MAPE)", f"{mape:.2f}%")
        
        st.success("✅ Database chi tiết từng ngày AI so sánh với thực tế:")
        st.dataframe(df_pred, use_container_width=True)
    else:
        st.warning("⚠️ Chưa có kết quả từ AI. Hãy chạy file 'train_model.py' trước!")

# ==========================================
# TAB 3: HIỂN THỊ BIỂU ĐỒ
# ==========================================
elif choice == "3. 📈 Biểu Đồ Dự Đoán 6 Năm":
    st.header("📈 Biểu đồ AI Dự đoán vs Thực tế (2020 - Nay)")
    df_pred = load_data("ai_6_years_predictions")
    
    if df_pred is not None:
        df_pred['Date'] = pd.to_datetime(df_pred['Date'])
        chart_data = df_pred.set_index('Date')[['Actual_Price', 'AI_Predicted_Price']]
        
        # Biểu đồ mượt mà của Streamlit
        st.line_chart(chart_data, color=["#1f77b4", "#ff7f0e"])
        
        # Ảnh tĩnh
        if os.path.exists('BieuDo_DuDoan_6Nam.png'):
            st.subheader("Ảnh xuất File từ Model")
            st.image('BieuDo_DuDoan_6Nam.png', caption="Biểu đồ xuất ra từ AI")
    else:
        st.warning("⚠️ Chưa có dữ liệu biểu đồ. Hãy chạy file 'train_model.py' trước!")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Quy trình chuẩn:**\n1. Chạy `collector.py`\n2. Chạy `train_model.py`\n3. Mở web Streamlit.")