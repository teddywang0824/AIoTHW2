import sqlite3
import json
import os

def insert_json_to_db(json_path, db_path):
    if not os.path.exists(json_path):
        print(f"找不到檔案: {json_path}")
        return

    # 連接 SQLite 資料庫 (若不存在會自動建立)
    print(f"正在連線至 SQLite 資料庫: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 建立 Table (若不存在)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate TEXT NOT NULL,
            mint INTEGER NOT NULL,
            maxt INTEGER NOT NULL
        )
    ''')
    
    # 讀取並解析 JSON 資料
    print("正在讀取並解析 JSON...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    try:
        locations = data["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"]
    except KeyError as e:
        print(f"分析失敗，找不到對應的 JSON 節點: {e}")
        conn.close()
        return

    # 準備寫入資料的暫存陣列
    records_to_insert = []
    
    for loc in locations:
        region_name = loc.get("locationName", "未知")
        
        elements = loc.get("weatherElements", {})
        max_t_daily = elements.get("MaxT", {}).get("daily", [])
        min_t_daily = elements.get("MinT", {}).get("daily", [])
        
        # 使用字典把每天的 MaxT 與 MinT 配對起來
        daily_temps = {}
        for temp_data in max_t_daily:
            date = temp_data.get("dataDate")
            if date not in daily_temps:
                daily_temps[date] = {}
            daily_temps[date]['maxt'] = int(temp_data.get("temperature", 0))
            
        for temp_data in min_t_daily:
            date = temp_data.get("dataDate")
            if date not in daily_temps:
                daily_temps[date] = {}
            daily_temps[date]['mint'] = int(temp_data.get("temperature", 0))
            
        # 整理進 records_to_insert，準備執行 executemany
        for date, temps in daily_temps.items():
            mint = temps.get('mint', 0)
            maxt = temps.get('maxt', 0)
            
            records_to_insert.append((region_name, date, mint, maxt))
            
    # 清空原本的資料 (可選，避免重複執行塞入重複資料)
    cursor.execute('DELETE FROM TemperatureForecasts')
    
    # 將解析出的資料一次性寫入資料表
    cursor.executemany('''
        INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
        VALUES (?, ?, ?, ?)
    ''', records_to_insert)
    
    # 儲存 (commit) 與關閉連線
    conn.commit()
    conn.close()
    
    print(f"成功將 {len(records_to_insert)} 筆資料匯入至 TemperatureForecasts 中！")

if __name__ == "__main__":
    # 設定路徑 (絕對路徑以確保讀取正確)
    base_dir = r"d:\SchoolProject\AIoTHW2"
    json_path = os.path.join(base_dir, "HW2-1_2-2", "output.json")
    
    # 寫入 HW2-3 資料夾下的 data.db
    hw2_3_dir = os.path.join(base_dir, "HW2-3")
    if not os.path.exists(hw2_3_dir):
        os.makedirs(hw2_3_dir)
        
    db_path = os.path.join(hw2_3_dir, "data.db")
    
    insert_json_to_db(json_path, db_path)
