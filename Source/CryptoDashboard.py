import numpy as np
np.object = object
np.typeDict = dict
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import streamlit as st
import pandas as pd
import sqlite3
import os
from sklearn.metrics import mean_squared_error, r2_score

st.set_page_config(page_title="AI Crypto Dashboard", layout="wide", page_icon="🚀")
st.title("🚀 Hệ thống AI Phân Tích & Dự Đoán Giá Bitcoin")

DB_PATH = "crypto_database.db"

@st.cache_data
def load_data(table_name):
    """Hàm tải dữ liệu có sử dụng cache để web chạy mượt hơn"""
    if os.path.exists(DB_PATH):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                return pd.read_sql(f"SELECT * FROM {table_name}", conn)
        except Exception:
            return None
    return None

# Menu thanh điều hướng
st.sidebar.header("🎯 Menu Quản Lý")
# BỔ SUNG THÊM TAB SỐ 4 CHO FEEDBACK
menu = ["1. 📦 Tiền Xử Lý & Thống Kê (EDA)", "2. 🤖 Đánh Giá Mô Hình AI", "3. 📈 Trực Quan Hóa (Biểu Đồ)", "4. 📝 Feedback (Bước 10)"]
choice = st.sidebar.radio("Chọn bảng điều khiển:", menu)

# ==========================================
# TAB 1: TIỀN XỬ LÝ & THỐNG KÊ
# ==========================================
if choice == "1. 📦 Tiền Xử Lý & Thống Kê (EDA)":
    st.header("📦 Thống Kê Mô Tả Dữ Liệu (Descriptive Statistics)")
    
    # Tải cả 3 bảng từ Database
    df_raw = load_data("raw_ohlcv")
    df_processed = load_data("spot_ohlcv")
    df_stats = load_data("descriptive_statistics") # Tải bảng thống kê từ DB
    
    if df_raw is not None and df_processed is not None and df_stats is not None:
        st.success(f"✅ Đã tải thành công dữ liệu từ Database.")
        
        st.subheader("Bảng Thống Kê Toán Học (Đã lưu trong Database)")
        st.dataframe(df_stats, use_container_width=True)
        
        st.markdown("---")
        st.subheader("1. Dữ liệu thô nguyên bản (Raw Data)")
        st.dataframe(df_raw, use_container_width=True)

        st.subheader("2. Dữ liệu sau Tiền xử lý (Processed Data)")
        st.dataframe(df_processed, use_container_width=True)
        
    else:
        st.warning("⚠️ Chưa có dữ liệu. Hãy chạy lại file 'Collector.py' trước!")

# ==========================================
# TAB 2: ĐÁNH GIÁ MÔ HÌNH AI
# ==========================================
elif choice == "2. 🤖 Đánh Giá Mô Hình AI":
    st.header("🤖 Báo cáo Hiệu suất Mô hình (Model Performance)")
    
    df_pred = load_data("ai_6_years_predictions")
    df_history = load_data("training_history") # Tải lịch sử huấn luyện
    
    if df_pred is not None and df_history is not None:
        # 1. BIỂU ĐỒ LEARNING CURVE
        st.subheader("1. Phân tích Quá trình học (Learning Curve Analysis)")
        st.caption("💡 Biểu đồ kiểm định Overfitting. Nếu khoảng cách giữa 2 đường càng hẹp, mô hình đạt độ cân bằng lý tưởng (Optimal Equilibrium).")
        
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(x=df_history['Epoch'], y=df_history['Training_Error'], mode='lines+markers', name='Training Error', line=dict(color='#1f77b4')))
        fig_curve.add_trace(go.Scatter(x=df_history['Epoch'], y=df_history['Validation_Error'], mode='lines+markers', name='Validation Error', line=dict(color='#ff7f0e')))
        fig_curve.update_layout(xaxis_title="Epochs", yaxis_title="Error (Loss)", hovermode='x unified', height=400)
        st.plotly_chart(fig_curve, use_container_width=True)
        
        st.markdown("---")
        
        # 2. CÁC ĐỘ ĐO ĐÁNH GIÁ 
        st.subheader("2. Diagnostic Evaluation Metrics")
        y_true = df_pred['Actual_Value']
        y_pred = df_pred['Predicted_Value']
        
        mape = (abs(y_true - y_pred) / y_true).mean() * 100
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("RMSE (Root Mean Squared Error)", f"{rmse:.2f}")
        col2.metric("MAPE (Mean Absolute % Error)", f"{mape:.2f}%")
        col3.metric("R-squared (R2 Score)", f"{r2:.4f}")
        
        # 3. BẢNG DỮ LIỆU ĐỐI CHIẾU
        st.subheader("3. Statistical Summaries (Raw Metrics)")
        st.dataframe(df_pred, use_container_width=True)
    else:
        st.warning("⚠️ Chưa có kết quả từ AI. Hãy chạy file 'TrainModel_DB.py' trước!")

# ==========================================
# TAB 3: TRỰC QUAN HÓA BẰNG BIỂU ĐỒ CHUYÊN NGHIỆP
# ==========================================
elif choice == "3. 📈 Trực Quan Hóa (Biểu Đồ)":
    st.header("📈 Trực Quan Hóa & So Sánh Dữ Liệu (Plotly)")
    
    df_pred = load_data("ai_6_years_predictions")
    df_raw = load_data("spot_ohlcv")
    
    if df_pred is not None and df_raw is not None:
        # 1. ÉP KIỂU NGÀY THÁNG VỀ CHUỖI 'YYYY-MM-DD' ĐỂ ĐẢM BẢO KHỚP NHAU 100%
        df_pred['Date'] = pd.to_datetime(df_pred['Date']).dt.strftime('%Y-%m-%d')
        df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp']).dt.strftime('%Y-%m-%d')
        df_raw = df_raw.rename(columns={'timestamp': 'Date'})
        
        # 2. Gộp 2 bảng lại dựa trên ngày tháng
        df_merged = pd.merge(df_pred, df_raw, on='Date', how='inner')
        
        # 3. Phục hồi lại thành định dạng thời gian chuẩn để vẽ biểu đồ mượt mà
        df_merged['Date'] = pd.to_datetime(df_merged['Date'])
        df_merged['Year'] = df_merged['Date'].dt.year
        
        # BỘ LỌC CHUNG THEO NĂM
        st.markdown("### 🔍 Phân tích chuyên sâu (Giá - Khối lượng - RSI)")
        list_years = ["Toàn thời gian (2020 - nay)"] + sorted(df_merged['Year'].unique().tolist())
        selected_year = st.selectbox("📅 Chọn mốc thời gian:", list_years)
        
        if selected_year != "Toàn thời gian (2020 - nay)":
            df_merged = df_merged[df_merged['Year'] == selected_year]
            
        st.markdown("---")
        
        # TẠO BIỂU ĐỒ BA KHUNG (Giá, Volume, RSI)
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True,           # KHÓA CHẶT TRỤC THỜI GIAN
            vertical_spacing=0.05,       
            row_heights=[0.5, 0.25, 0.25] # Tỷ lệ: Giá 50%, Volume 25%, RSI 25%
        )
        
        # [Khung 1] Đường Giá Thực Tế (Màu xanh)
        fig.add_trace(go.Scatter(x=df_merged['Date'], y=df_merged['Actual_Value'], 
                                 mode='lines', name='Giá Thực Tế', line=dict(color='#1f77b4')), 
                      row=1, col=1)
        
        # [Khung 1] Đường Giá AI Dự Đoán (Màu cam)
        fig.add_trace(go.Scatter(x=df_merged['Date'], y=df_merged['Predicted_Value'], 
                                 mode='lines', name='AI Dự Đoán', line=dict(color='#ff7f0e')), 
                      row=1, col=1)
        
        # [Khung 2] Cột Volume (Màu xanh lá)
        fig.add_trace(go.Bar(x=df_merged['Date'], y=df_merged['volume'], 
                             name='Khối lượng (Volume)', marker_color='#2ca02c'), 
                      row=2, col=1)

        # [Khung 3] Chỉ báo RSI (Màu tím)
        fig.add_trace(go.Scatter(x=df_merged['Date'], y=df_merged['RSI'], 
                                 mode='lines', name='Chỉ số RSI', line=dict(color='#9467bd')), 
                      row=3, col=1)
        
        # Thêm đường ranh giới 70 (Overbought) và 30 (Oversold) cho RSI
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1, annotation_text="Quá mua (70)")
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1, annotation_text="Quá bán (30)")
        
        # Cấu hình tính năng Trỏ chuột (Hover) đồng bộ
        fig.update_layout(
            hovermode='x unified',       
            height=800,
            margin=dict(l=0, r=0, t=20, b=0)
        )
        
        # Đặt tên cho các trục Y
        fig.update_yaxes(title_text="Giá (USDT)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI (0-100)", range=[0, 100], row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("⚠️ Hãy đảm bảo bạn đã chạy cả 2 file Thu thập và Train model!")

# ==========================================
# TAB 4: BƯỚC 10 - FEEDBACK LOOP (BỔ SUNG)
# ==========================================
elif choice == "4. 📝 Feedback (Bước 10)":
    st.header("📝 BƯỚC 10: FEEDBACK LOOP")
    st.write("Thu thập phản hồi từ người dùng/nhà đầu tư để ghi nhận vào hệ thống nhằm cải tiến cấu trúc Dữ liệu và Model AI trong tương lai.")

    # Giao diện nhập Feedback
    st.markdown("### ✍️ Đóng góp ý kiến cho hệ thống AI")
    col1, col2 = st.columns([1, 3])
    with col1:
        user_rating = st.slider("Chấm điểm AI (1-5 ⭐):", 1, 5, 5)
    with col2:
        user_comment = st.text_input("Đề xuất cải tiến (VD: Thêm dữ liệu NLP, chỉnh sửa MACD...):")

    if st.button("💾 Gửi Feedback vào System"):
        # Kết nối DB và lưu dữ liệu bằng DB_PATH
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Tạo bảng tự động nếu chưa có
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_feedback (
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    Rating INTEGER,
                    Comment TEXT
                )
            """)
            # Insert dữ liệu mới
            cursor.execute("INSERT INTO model_feedback (Rating, Comment) VALUES (?, ?)", (user_rating, user_comment))
            conn.commit()
        st.success("✅ Đã ghi nhận Feedback thành công vào cơ sở dữ liệu (bảng 'model_feedback')!")

    st.markdown("---")
    
    # SHOW DATABASE FEEDBACK LÊN WEB
    st.subheader("📊 Lịch sử Feedback hiện tại trong Database")
    with sqlite3.connect(DB_PATH) as conn:
        try:
            # Query để lấy bảng feedback, sắp xếp mới nhất lên đầu
            feedback_df = pd.read_sql("SELECT * FROM model_feedback ORDER BY Timestamp DESC", con=conn)
            st.dataframe(feedback_df, use_container_width=True)
        except Exception:
            st.info("💡 Chưa có feedback nào được ghi nhận trong hệ thống. Hãy là người đầu tiên gửi đánh giá!")