import requests
import csv
from datetime import datetime

url = "https://www.binance.com/bapi/futures/v1/public/future/smart-money/signal/overview"

params = {"symbol": "BTCUSDT"}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://www.binance.com/zh-CN/smart-money/signal/BTCUSDT"
}

csv_path = "btc_smart_money_overview.csv"

print("正在获取最新数据...")

try:
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    
    json_data = resp.json()
    if not json_data.get("success"):
        print("接口返回失败:", json_data.get("message"))
        exit()
    
    data = json_data["data"]
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 计算盈利比例（只用普通交易员）
    long_profit_ratio = round(data["longProfitTraders"] / data["longTraders"] * 100, 2) if data["longTraders"] > 0 else "N/A"
    short_profit_ratio = round(data["shortProfitTraders"] / data["shortTraders"] * 100, 2) if data["shortTraders"] > 0 else "N/A"
    
    # 名义多空比率（服务器直接提供）
    long_short_ratio = round(data["longShortRatio"] * 100, 2)
    
    # 输出到控制台（英文 + 中文对照）
    print(f"\n[{now}] 数据获取成功：")
    print(f"Total Traders: {data['totalTraders']}")
    print(f"Long Short Ratio (%): {long_short_ratio}")
    print(f"Long Traders: {data['longTraders']}")
    print(f"Long Profit Traders: {data['longProfitTraders']}")
    print(f"Long Profit Ratio (%): {long_profit_ratio}")
    print(f"Short Traders: {data['shortTraders']}")
    print(f"Short Profit Traders: {data['shortProfitTraders']}")
    print(f"Short Profit Ratio (%): {short_profit_ratio}")
    print(f"Total Positions (USDT): {data['totalPositions']:,.2f}")
    
    # 追加保存到 CSV（用 utf-8-sig 防乱码 + 全英文表头）
    row = [
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
    ]
    
    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:  # utf-8-sig 让 Excel 正确识别
        writer = csv.writer(f)
        if f.tell() == 0:  # 文件为空时写表头
            writer.writerow([
                "Timestamp",
                "Total Traders",
                "Long Short Ratio (%)",
                "Long Traders",
                "Long Profit Traders",
                "Long Profit Ratio (%)",
                "Short Traders",
                "Short Profit Traders",
                "Short Profit Ratio (%)",
                "Total Positions (USDT)"
            ])
        writer.writerow(row)
    
    print(f"\n数据已追加保存到：{csv_path}")
    
except Exception as e:
    print(f"获取失败: {e}")
