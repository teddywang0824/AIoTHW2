import os
import json
import sqlite3
import requests
import threading
import time

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

# Vercel Deployment handling
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get('VERCEL') == '1' or os.environ.get('AWS_EXECUTION_ENV') or not os.access(_CURRENT_DIR, os.W_OK):
    IS_VERCEL = True
    WORK_DIR = '/tmp'
else:
    IS_VERCEL = False
    WORK_DIR = _CURRENT_DIR

JSON_PATH = os.path.join(WORK_DIR, "output.json")
DB_PATH = os.path.join(WORK_DIR, "data.db")
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

POSTGRES_URL = os.environ.get('POSTGRES_URL')

def fetch_and_save_weather_data():
    api_key = os.environ.get("CWA_API_KEY")
    if not api_key:
        print("[DataUpdater] 錯誤：找不到 CWA_API_KEY 環境變數，請確認 .env 檔案或 Vercel 設定。")
        return

    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={api_key}&downloadType=WEB&format=JSON"
    
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
    is_postgres = POSTGRES_URL and psycopg2 is not None
    
    if is_postgres:
        print("[DataUpdater] 偵測到 POSTGRES_URL，正在連線至 Vercel Postgres...")
        conn = psycopg2.connect(POSTGRES_URL)
    else:
        print(f"[DataUpdater] 正在連線至 SQLite 資料庫: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        
    cursor = conn.cursor()

    if is_postgres:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TemperatureForecasts (
                id SERIAL PRIMARY KEY,
                regionName VARCHAR(255) NOT NULL,
                dataDate VARCHAR(255) NOT NULL,
                mint INTEGER NOT NULL,
                maxt INTEGER NOT NULL
            )
        ''')
    else:
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
    
    if is_postgres:
        cursor.executemany('''
            INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
            VALUES (%s, %s, %s, %s)
        ''', records_to_insert)
    else:
        cursor.executemany('''
            INSERT INTO TemperatureForecasts (regionName, dataDate, mint, maxt)
            VALUES (?, ?, ?, ?)
        ''', records_to_insert)
    
    conn.commit()
    conn.close()
    
    db_type = "Postgres" if is_postgres else "SQLite"
    print(f"[DataUpdater] 成功將 {len(records_to_insert)} 筆資料匯入至 {db_type} 中！")

def init_db_if_needed():
    # 若為 Postgres，連線並檢查 table 是否存在
    is_postgres = POSTGRES_URL and psycopg2 is not None
    if is_postgres:
        try:
            conn = psycopg2.connect(POSTGRES_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'temperatureforecasts');")
            exists = cursor.fetchone()[0]
            conn.close()
            if not exists:
                print("[DataUpdater] 偵測到 Postgres 無資料表，進行初始爬取...")
                fetch_and_save_weather_data()
        except Exception as e:
            print(f"[DataUpdater] 初始化 Postgres 檢查時發生錯誤: {e}")
    else:
        # SQLite 邏輯
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
