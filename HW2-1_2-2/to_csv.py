import json
import csv
import os

def json_to_csv(json_file_path, csv_file_path):
    # 確保 JSON 檔案存在
    if not os.path.exists(json_file_path):
        print(f"找不到檔案: {json_file_path}")
        return

    print("開始解析 JSON 資料...")
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 取得 各地區氣象預測陣列
    try:
        locations = data["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"]
    except KeyError as e:
        print(f"分析失敗，找不到對應的 JSON 節點: {e}")
        return

    # 建立要寫入 CSV 的資料陣列
    csv_data = []
    
    # 寫入標題列 (Header)
    headers = ["地區", "日期", "天氣狀況", "最高溫(˚C)", "最低溫(˚C)"]
    csv_data.append(headers)

    # 遍歷每一個地區
    for loc in locations:
        region_name = loc.get("locationName", "未知地區")
        
        # 取得 Wx(天氣狀況), MaxT(最高溫), MinT(最低溫) 的陣列資料
        elements = loc.get("weatherElements", {})
        wx_daily = elements.get("Wx", {}).get("daily", [])
        max_t_daily = elements.get("MaxT", {}).get("daily", [])
        min_t_daily = elements.get("MinT", {}).get("daily", [])

        # 假設該地每天的資料對齊，以最大天數為基準打包
        # 將資料利用日期作為 Key 正規化，避免資料順序出錯
        daily_dict = {}
        
        for w in wx_daily:
            date = w.get("dataDate")
            if date not in daily_dict:
                daily_dict[date] = {}
            daily_dict[date]["wx"] = w.get("weather", "")
            
        for m in max_t_daily:
            date = m.get("dataDate")
            if date not in daily_dict:
                daily_dict[date] = {}
            daily_dict[date]["max_t"] = m.get("temperature", "")
            
        for m in min_t_daily:
            date = m.get("dataDate")
            if date not in daily_dict:
                daily_dict[date] = {}
            daily_dict[date]["min_t"] = m.get("temperature", "")

        # 將該地區的每日資料依日期排序並存入清單
        for date in sorted(daily_dict.keys()):
            info = daily_dict[date]
            csv_data.append([
                region_name,
                date,
                info.get("wx", ""),
                info.get("max_t", ""),
                info.get("min_t", "")
            ])

    # 寫入 CSV 檔案
    print(f"正在輸出 CSV 到: {csv_file_path}")
    with open(csv_file_path, "w", encoding="utf-8-sig", newline="") as f:
        # 使用 utf-8-sig 可以讓 Excel 直接開啟不會有中文亂碼
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    print("CSV 輸出完成！可使用 Excel 或是資料視覺化套件開啟。")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "output.json")
    csv_path = os.path.join(current_dir, "weather_data.csv")
    
    json_to_csv(json_path, csv_path)
