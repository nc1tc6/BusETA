import requests
import json
import os

# 示範：抓取九巴 1 號線往竹園邨方向的數據
# 這是公開的九巴 API 接口
url = "https://data.etabus.gov.hk/v1/transport/kmb/route-eta/1/1"

def fetch_bus_data():
    try:
        # 發送請求
        response = requests.get(url, timeout=10)
        
        # 確認請求成功
        if response.status_code == 200:
            raw_data = response.json()
            
            # 將數據存入 data.json
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(raw_data, f, ensure_ascii=False, indent=4)
            print("數據已成功儲存至 data.json")
        else:
            print(f"API 請求失敗，狀態碼: {response.status_code}")
            
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    fetch_bus_data()
