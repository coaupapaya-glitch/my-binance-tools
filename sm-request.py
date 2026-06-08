import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Smart Money 查询", layout="wide")
st.title("📊 Binance Smart Money 信号查询 (BTCUSDT)")
st.caption("数据来自 Binance 官方接口 • 云端运行 • 不会占用你本地资源")

# ==================== 数据获取函数 ====================
@st.cache_data(ttl=30)  # 每30秒自动刷新一次
def get_smart_money_data():
    url = "https://www.binance.com/bapi/futures/v1/public/future/smart-money/signal/overview"
    params = {"symbol": "BTCUSDT"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.binance.com/zh-CN/smart-money/signal/BTCUSDT"
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        
        if not json_data.get("success"):
            st.error("接口返回失败")
            return None
            
        return json_data["data"]
        
    except Exception as e:
        st.error(f"请求失败: {e}")
        return None

# ==================== 主界面 ====================
data = get_smart_money_data()

if data:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 计算比例
    long_profit_ratio = round(data["longProfitTraders"] / data["longTraders"] * 100, 2) if data["longTraders"] > 0 else 0
    short_profit_ratio = round(data["shortProfitTraders"] / data["shortTraders"] * 100, 2) if data["shortTraders"] > 0 else 0
    long_short_ratio = round(data["longShortRatio"] * 100, 2)

    # 大数字展示
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总交易者", f"{data['totalTraders']:,}")
    with col2:
        st.metric("多空比率", f"{long_short_ratio}%", delta=None)
    with col3:
        st.metric("多头盈利比例", f"{long_profit_ratio}%")
    with col4:
        st.metric("空头盈利比例", f"{short_profit_ratio}%")

    # 详细数据表格
    st.subheader("详细数据")
    detail = {
        "指标": ["总持仓 (USDT)", "多头人数", "多头盈利人数", "空头人数", "空头盈利人数", "更新时间"],
        "数值": [
            f"{data['totalPositions']:,.2f}",
            f"{data['longTraders']:,}",
            f"{data['longProfitTraders']:,}",
            f"{data['shortTraders']:,}",
            f"{data['shortProfitTraders']:,}",
            now
        ]
    }
    st.dataframe(pd.DataFrame(detail), use_container_width=True, hide_index=True)

    # 一键下载 CSV
    csv_data = pd.DataFrame([[
        now,
        data["totalTraders"],
        long_short_ratio,
        data["longTraders"],
        data["longProfitTraders"],
        long_profit_ratio,
        data["shortTraders"],
        data["shortProfitTraders"],
        short_profit_ratio,
        round(data["totalPositions"], 2)
    ]], columns=[
        "Timestamp", "Total Traders", "Long Short Ratio (%)",
        "Long Traders", "Long Profit Traders", "Long Profit Ratio (%)",
        "Short Traders", "Short Profit Traders", "Short Profit Ratio (%)",
        "Total Positions (USDT)"
    ])

    st.download_button(
        label="📥 下载当前数据 (CSV)",
        data=csv_data.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"smart_money_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

else:
    st.warning("正在尝试获取数据...")

# 手动刷新按钮
if st.button("🔄 手动刷新数据"):
    st.cache_data.clear()
    st.rerun()

st.caption("提示：数据每30秒自动更新 • 如需查询其他币种告诉我，我可以帮你扩展")
