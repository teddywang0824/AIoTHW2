import os
import json
import sqlite3
import requests
import threading
import time
from datetime import datetime, timedelta, timezone

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
        return None

    url = f"https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization={api_key}&downloadType=WEB&format=JSON"
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    try:
        print("[DataUpdater] 正在從氣象署 API 獲取資料...")
        response = requests.get(url, verify=False)
        response.raise_for_status()
        
        # 取得 JSON 資料（不寫入硬碟以避免 Vercel Read-Only 錯誤）
        weather_data = response.json()
        print(f"[DataUpdater] 成功獲取資料，直接進入資料庫寫入階段")
        _insert_json_to_db(weather_data)
        return weather_data
    except Exception as e:
        print(f"[DataUpdater] 抓取 API 發生錯誤: {e}")
        return None

def get_latest_cwa_update_time():
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)
    # CWA API updates at 18:00
    if now.hour >= 18:
        return now.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        return now.replace(hour=18, minute=0, second=0, microsecond=0) - timedelta(days=1)

def get_current_time_str():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).isoformat()

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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Metadata (
                key VARCHAR(255) PRIMARY KEY,
                value VARCHAR(255) NOT NULL
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
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
        
    # 寫入最後更新時間
    cursor.execute("DELETE FROM Metadata WHERE key = 'last_update'")
    current_time_str = get_current_time_str()
    if is_postgres:
        cursor.execute("INSERT INTO Metadata (key, value) VALUES ('last_update', %s)", (current_time_str,))
    else:
        cursor.execute("INSERT INTO Metadata (key, value) VALUES ('last_update', ?)", (current_time_str,))
    
    conn.commit()
    conn.close()
    
    db_type = "Postgres" if is_postgres else "SQLite"
    print(f"[DataUpdater] 成功將 {len(records_to_insert)} 筆資料匯入至 {db_type} 中！")

def init_db_if_needed():
    is_postgres = POSTGRES_URL and psycopg2 is not None
    needs_update = False
    
    if is_postgres:
        try:
            conn = psycopg2.connect(POSTGRES_URL)
            cursor = conn.cursor()
            
            # 檢查 Metadata 是否存在 (小寫或大寫取決於系統，一律用 lower() 比對比較保險，但在 Postgres 建表如果沒加引號預設是小寫)
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'metadata' OR table_name = 'Metadata');")
            has_metadata = cursor.fetchone()[0]
            
            if not has_metadata:
                needs_update = True
            else:
                cursor.execute("SELECT value FROM Metadata WHERE key = 'last_update'")
                row = cursor.fetchone()
                if not row:
                    needs_update = True
                else:
                    last_update_str = row[0]
                    last_update_time = datetime.fromisoformat(last_update_str)
                    if last_update_time < get_latest_cwa_update_time():
                        needs_update = True
            conn.close()
        except Exception as e:
            print(f"[DataUpdater] 初始化 Postgres 檢查時發生錯誤: {e}")
            needs_update = True
    else:
        # SQLite 邏輯
        if not os.path.exists(DB_PATH):
            needs_update = True
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Metadata'")
                has_metadata = cursor.fetchone()[0] > 0
                if not has_metadata:
                    needs_update = True
                else:
                    cursor.execute("SELECT value FROM Metadata WHERE key = 'last_update'")
                    row = cursor.fetchone()
                    if not row:
                        needs_update = True
                    else:
                        last_update_str = row[0]
                        last_update_time = datetime.fromisoformat(last_update_str)
                        if last_update_time < get_latest_cwa_update_time():
                            needs_update = True
                conn.close()
            except Exception as e:
                print(f"[DataUpdater] 初始化 SQLite 檢查時發生錯誤: {e}")
                needs_update = True

    if needs_update:
        print("[DataUpdater] 偵測到無資料或資料已過期，進行即時爬取 (Lazy Update)...")
        fetch_and_save_weather_data()
    else:
        print("[DataUpdater] 檢查完畢：目前資料已是最新，無需爬取。")

def start_scheduler():
    init_db_if_needed()
    # 由於改用 Lazy Update 策略，不需要啟動無窮迴圈的 Background Thread 了
    # 當使用者打 API 進來時，Flask 會自動觸發這段邏輯來檢查是否更新
    print("[DataUpdater] 延遲更新機制 (Lazy Update) 已就緒，不再啟動定時器。")
