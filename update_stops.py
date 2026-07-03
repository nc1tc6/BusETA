import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_stops():
    all_stops = []

    # 數據源列表
    sources = [
        {"name": "KMB", "url": "https://data.etabus.gov.hk/v1/transport/kmb/stop"},
        {"name": "CTB", "url": "https://rt.data.gov.hk/v1/transport/citybus-nwfb/stop"},
        {"name": "MTR", "url": "https://rt.data.gov.hk/v1/transport/mtr/bus/getStopList"},
        {"name": "GMB", "url": "https://data.etagmb.gov.hk/stop"}
    ]

    for source in sources:
        try:
            print(f"正在抓取 {source['name']}...")
            response = requests.get(source['url'], headers=HEADERS, timeout=15)
            
            # 檢查是否連線成功
            if response.status_code != 200:
                print(f"!!! {source['name']} 請求失敗，狀態碼: {response.status_code}")
                continue
                
            data = response.json()
            
            # 解析數據 (不同 API 的結構可能不同，這裡檢查 'data' 層)
            records = data.get('data', [])
            
            for s in records:
                # 統一格式化：有些 ID 鍵值是 'stop', 有些是 'stop_id'
                stop_id = s.get('stop') or s.get('stop_id')
                if stop_id:
                    all_stops.append({
                        "name": s.get('name_en', 'Unknown'), 
                        "id": stop_id, 
                        "type": source['name']
                    })
            print(f"--- {source['name']} 成功，目前總數: {len(all_stops)}")
            
        except Exception as e:
            print(f"!!! {source['name']} 發生未知錯誤: {str(e)}")

    with open('stops.json', 'w', encoding='utf-8') as f:
        json.dump(all_stops, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_stops()
