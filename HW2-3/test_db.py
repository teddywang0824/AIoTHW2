import sqlite3
import os

def test_database(db_path):
    if not os.path.exists(db_path):
        print(f"錯誤：找不到資料庫檔案 {db_path}")
        return
        
    print(f"成功連接至資料庫: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "="*40)
    print("1. 所有地區名稱")
    print("="*40)
    
    # 查詢所有不重複的地區名稱
    cursor.execute("SELECT DISTINCT regionName FROM TemperatureForecasts")
    regions = cursor.fetchall()
    
    if regions:
        for idx, row in enumerate(regions, 1):
            print(f"{idx}. {row[0]}")
    else:
        print("目前沒有任何地區資料。")

    print("\n" + "="*40)
    print("2. 中部地區的氣溫資料")
    print("="*40)
    
    # 查詢中部地區的所有日期與氣溫
    cursor.execute("""
        SELECT dataDate, mint, maxt 
        FROM TemperatureForecasts 
        WHERE regionName = '中部地區'
        ORDER BY dataDate ASC
    """)
    central_data = cursor.fetchall()
    
    if central_data:
        print(f"{'日期':<15} | {'最低溫(˚C)':<10} | {'最高溫(˚C)':<10}")
        print("-" * 40)
        for row in central_data:
            date, mint, maxt = row
            print(f"{date:<15} | {mint:<12} | {maxt:<10}")
    else:
        print("找不到中部地區的氣溫資料。")

    print("\n" + "="*40)

    # 關閉連線
    conn.close()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "data.db")
    
    test_database(db_path)
