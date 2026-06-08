import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Smart Money 数据监控", layout="wide")
st.title("📊 Binance Smart Money 历史数据监控 (BTCUSDT)")
st.caption("数据来自 Binance 官方公开接口 • 云端稳定运行 • 自动转换为北京时间")

# ==================== 初始化云端会话内存 ====================
# 用 st.session_state 代替本地 CSV 文件，用于在网页运行期间累加历史数据
if "history_df" not in st.session_state:
    st.session_state.history_df = pd.DataFrame(columns=[
        "Timestamp", "Symbol", "Period", "Long Ratio (%)", "Short Ratio (%)", "Long Short Ratio"
    ])

# ==================== 数据获取函数 ====================
@st.cache_data(ttl=30)
def get_smart_money_data():
    # 使用公开的 fapi 接口，避免云端服务器被币安 BAPI 封禁 403
    url = "https://fapi.binance.com/fapi/v1/topLongShortPositionRatio"
    params = {"symbol": "BTCUSDT", "period": "5m", "limit": 1}
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        if json_data and len(json_data) > 0:
            return json_data[0]
        return None
    except Exception as e:
        st.error(f"⚠️ 无法从币安服务器获取数据: {e}")
        return None

# ==================== 业务逻辑处理 ====================
data = get_smart_money_data()

if data:
    # 转换为北京时间
    now_bj = datetime.utcnow() + timedelta(hours=8)
    now_str = now_bj.strftime("%Y-%m-%d %H:%M:%S")
    
    # 解析字段
    long_ratio = round(float(data["longAccount"]) * 100, 2)
    short_ratio = round(float(data["shortAccount"]) * 100, 2)
    ls_ratio = round(float(data["longShortRatio"]), 2)
    
    # 构造当前这一行的新数据
    new_row = {
        "Timestamp": now_str,
        "Symbol": data["symbol"],
        "Period": data["period"],
        "Long Ratio (%)": long_ratio,
        "Short Ratio (%)": short_ratio,
        "Long Short Ratio": ls_ratio
    }
    
    # 💡 模拟本地 CSV 追加：如果当前时间的数据不在历史记录里，就追加进去
    if st.session_state.history_df.empty or st.session_state.history_df.iloc[-1]["Timestamp"] != now_str:
        st.session_state.history_df = pd.concat([st.session_state.history_df, pd.DataFrame([new_row])], ignore_index=True)

    # ---- 界面渲染 ----
    # 1. 仪表盘大数字
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("最新多空比 (Long/Short)", f"{ls_ratio}")
    with col2:
        st.metric("大户多头比例", f"{long_ratio}%")
    with col3:
        st.metric("大户空头比例", f"{short_ratio}%")
        
    st.markdown("---")
    
    # 2. 历史表格展示 (最新获取的数据排在最上面)
    st.subheader("📋 运行期间累计历史数据 (等同于你的本地 CSV 记录)")
    display_df = st.session_state.history_df.iloc[::-1] # 倒序排列方便查看最新行
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # 3. 导出 CSV 按钮
    st.download_button(
        label="📥 导出当前累计的全部数据为 CSV (Excel不乱码)",
        data=st.session_state.history_df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"binance_history_{now_bj.strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

else:
    st.warning("正在等待数据加载...")

# 手动强刷按钮
if st.button("🔄 手动同步并追加最新数据"):
    st.cache_data.clear()
    st.rerun()
