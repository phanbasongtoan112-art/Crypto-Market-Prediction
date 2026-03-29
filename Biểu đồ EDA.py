import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import urllib.parse
import os

# --- 1. CẤU HÌNH KẾT NỐI MYSQL ---
DB_USER = "root"
DB_PASS = "Binh@n32160260"
DB_NAME = "crypto_db"
encoded_pass = urllib.parse.quote_plus(DB_PASS)
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@localhost:3306/{DB_NAME}")

# Tạo thư mục lưu ảnh nếu chưa tồn tại
OUTPUT_DIR = "EDA_Charts"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_data_for_eda():
    print("📥 Đang tải dữ liệu từ bảng step3_final_target để phân tích...")
    df = pd.read_sql("SELECT * FROM step3_final_target", con=engine)
    if 'timestamp' in df.columns:
        df = df.set_index("timestamp")
    return df

def plot_price_vs_sentiment(df):
    """Biểu đồ 1: So sánh Giá BTC và Tâm lý thị trường"""
    fig, ax1 = plt.subplots(figsize=(14, 6))

    color = 'tab:blue'
    ax1.set_xlabel('Thời gian')
    ax1.set_ylabel('Giá BTC (USD)', color=color, fontweight='bold')
    ax1.plot(df.index, df['close'], color=color, label='BTC Close Price')
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  
    color = 'tab:orange'
    ax2.set_ylabel('Chỉ số Sợ hãi & Tham lam', color=color, fontweight='bold')
    ax2.plot(df.index, df['fng_val'], color=color, alpha=0.4, label='Fear & Greed Index')
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.title('Biểu đồ 1: Tương quan giữa Giá BTC và Tâm lý đám đông', fontsize=14, fontweight='bold')
    plt.grid(alpha=0.3)
    
    # LƯU ẢNH RA FILE
    filepath = os.path.join(OUTPUT_DIR, "1_Price_vs_Sentiment.png")
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"📸 Đã xuất ảnh: {filepath}")
    plt.close()

def plot_correlation_heatmap(df):
    """Biểu đồ 2: Ma trận tương quan (Heatmap)"""
    plt.figure(figsize=(16, 10))
    
    cols_to_check = ['close', 'volume', 'hash_rate', 'onchain_transactions', 
                     'DXY', 'SP500', 'FED_RATE', 'fng_val', 'RSI_14', 'MACD', 'target_close_30d']
    existing_cols = [col for col in cols_to_check if col in df.columns]
    corr_matrix = df[existing_cols].corr()
    
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, vmin=-1, vmax=1)
    plt.title('Biểu đồ 2: Ma trận tương quan (Correlation Heatmap)', fontsize=14, fontweight='bold')
    
    # LƯU ẢNH RA FILE
    filepath = os.path.join(OUTPUT_DIR, "2_Correlation_Heatmap.png")
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"📸 Đã xuất ảnh: {filepath}")
    plt.close()

def plot_feature_distributions(df):
    """Biểu đồ 3: Phân phối của các chỉ báo kỹ thuật"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    if 'RSI_14' in df.columns:
        sns.histplot(df['RSI_14'], bins=30, kde=True, ax=axes[0], color='purple')
        axes[0].set_title('Phân phối RSI (14 ngày)')
        axes[0].axvline(30, color='r', linestyle='--', label='Oversold (30)') 
        axes[0].axvline(70, color='r', linestyle='--', label='Overbought (70)')
        axes[0].legend()
    
    if 'MACD' in df.columns:
        sns.histplot(df['MACD'], bins=30, kde=True, ax=axes[1], color='green')
        axes[1].set_title('Phân phối MACD')
    
    if 'fng_val' in df.columns:
        sns.histplot(df['fng_val'], bins=30, kde=True, ax=axes[2], color='orange')
        axes[2].set_title('Phân phối Fear & Greed Index')
    
    plt.tight_layout()
    
    # LƯU ẢNH RA FILE
    filepath = os.path.join(OUTPUT_DIR, "3_Feature_Distributions.png")
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"📸 Đã xuất ảnh: {filepath}")
    plt.close()

if __name__ == "__main__":
    df_clean = fetch_data_for_eda()
    
    if not df_clean.empty:
        print("📊 Đang tiến hành vẽ và xuất biểu đồ...")
        plot_price_vs_sentiment(df_clean)
        plot_correlation_heatmap(df_clean)
        plot_feature_distributions(df_clean)
        print(f"✅ HOÀN TẤT! Toàn bộ hình vẽ đã được lưu sắc nét vào thư mục '{OUTPUT_DIR}' tại nơi bạn chạy code.")
    else:
        print("⚠️ Không có dữ liệu. Vui lòng kiểm tra lại bảng step3_final_target.")