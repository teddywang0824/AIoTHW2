import requests
import json
import os

def main():
    url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/F-A0010-001?Authorization=CWA-F44C59DF-C342-4C2C-8FB4-E236A6383204&downloadType=WEB&format=JSON"
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 抓取資料
    print("正在請求中央氣象署開放資料...")
    response = requests.get(url, verify=False)
    
    # 確認請求是否成功
    if response.status_code == 200:
        print("請求成功！")
        
        # 使用 response.json() 取得 Python dict，相當於 json.loads()
        data = response.json()
        
        # 使用 json.dumps() 解析/格式化資料以便閱讀
        # ensure_ascii=False 確保中文字元正確顯示
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        
        # 將結果存入檔案或印出部分截斷的結果
        output_path = "output.json"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_json)
            
        print(f"資料已解析並儲存至 {os.path.abspath(output_path)}")
        
        # 印出部分資料預覽
        print("資料預覽 (前 500 字元):")
        print("="*40)
        print(formatted_json[:500])
        print("...")
        print("="*40)
    else:
        print(f"請求失敗，狀態碼: {response.status_code}")

if __name__ == "__main__":
    main()
