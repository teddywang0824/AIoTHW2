import os
import json
import sqlite3
import requests
import threading
import time

# Vercel Deployment handling
IS_VERCEL = os.environ.get('VERCEL') == '1'

if IS_VERCEL:
    WORK_DIR = '/tmp'
else:
    # Local fallback
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(WORK_DIR, "output.json")
DB_PATH = os.path.join(WORK_DIR, "data.db")

def fetch_and_save_weather_data():
    url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization=CWA-F44C59DF-C342-4C2C-8FB4-E236A6383204&downloadType=WEB&format=JSON"
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("[DataUpdater] 正在請求中央氣象署開放資料...")
    try:
        response = requests.get(url, verify=False, timeout=30)
        if response.status_code == 200:
            data = response.json()
            
            # 儲存 output.json
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[DataUpdater] 資料已解析並儲存至 {JSON_PATH}")
            
            # 解析並存入 SQLite
            _insert_json_to_db(data)
        else:
            print(f"[DataUpdater] 請求失敗，狀態碼: {response.status_code}")
    except Exception as e:
        print(f"[DataUpdater] 爬取資料時發生錯誤: {e}")

def _insert_json_to_db(data):
    print(f"[DataUpdater] 正在連線至 SQLite 資料庫: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TemperatureForecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            regionName TEXT NOT NULL,
            dataDate TEXT NOT NULL,
            mint INTEGER NOT NULL,
            maxt INTEGER NOT NULL
        )
    ''')
    
    try:
        locations = data["cwaopendata"]["resources"]["resource"]["data"]["agrWeatherForecasts"]["weatherForecasts"]["location"]
    except KeyError as e:
        print(f"[DataUpdater] 分析失敗，找不到對應的 JSON 節點: {e}")
        conn.close()
        return

    records_to_insert = []
    for loc in locations:
        region_name = loc.get("locationName", "未知")
        elements = loc.get("weatherElements", {})
        max_t_daily = elements.get("MaxT", {}).get("daily", [])
        min_t_daily = elements.get("MinT", {}).get("daily", [])
        
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
            
        for date, temps in daily_temps.items():
            mint = temps.get('mint', 0)
            maxt = temps.get('maxt', 0)
            records_to_insert.append((region_name, date, mint, maxt))
            
    cursor.execute('DELETE FROM TemperatureForecasts')
    cursor.executemany('''
        INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
        VALUES (?, ?, ?, ?)
    ''', records_to_insert)
    
    conn.commit()
    conn.close()
    print(f"[DataUpdater] 成功將 {len(records_to_insert)} 筆資料匯入至 SQLite 中！")

def init_db_if_needed():
    # 若資料庫不存在，立即進行一次爬取
    if not os.path.exists(DB_PATH):
        print("[DataUpdater] 偵測到本地無資料庫，進行初始爬取...")
        fetch_and_save_weather_data()

def start_scheduler():
    init_db_if_needed()
    
    # 若為 Vercel 佈署，不啟用無窮迴圈的 Background Thread
    if IS_VERCEL:
        print("[DataUpdater] 偵測到 Vercel 環境，跳過 Background Thread 排程，改由 API Router 觸發。")
        return

    print("[DataUpdater] 啟動本地排程器 (每 4 小時執行一次)...")
    def run_update():
        while True:
            time.sleep(4 * 3600)  # 4 hours
            fetch_and_save_weather_data()

    thread = threading.Thread(target=run_update, daemon=True)
    thread.start()
