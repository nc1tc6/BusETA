import requests
import json

# 加入 Header 以模擬瀏覽器訪問，防止被 API 伺服器拒絕
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_stops():
    all_stops = []

    # 1. 九巴 (KMB)
    try:
        data = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/stop", headers=HEADERS).json()['data']
        all_stops.extend([{"name": s['name_en'], "id": s['stop'], "type": "KMB"} for s in data])
    except Exception as e: print(f"KMB Error: {e}")

    # 2. 城巴 (CTB) - 注意 URL 結構
    try:
        data = requests.get("https://rt.data.gov.hk/v1/transport/citybus-nwfb/stop", headers=HEADERS).json()['data']
        all_stops.extend([{"name": s['name_en'], "id": s['stop'], "type": "CTB"} for s in data])
    except Exception as e: print(f"CTB Error: {e}")

    # 3. 港鐵巴士 (MTR) - 常需從路線列表反查
    try:
        # 港鐵公開數據通常透過此接口
        data = requests.get("https://rt.data.gov.hk/v1/transport/mtr/bus/getStopList", headers=HEADERS).json()['data']
        all_stops.extend([{"name": s['name_en'], "id": s['stop_id'], "type": "MTR"} for s in data])
    except Exception as e: print(f"MTR Error: {e}")

    # 4. 專線小巴 (GMB) - 此 API 是運輸署核心接口
    try:
        data = requests.get("https://data.etagmb.gov.hk/stop", headers=HEADERS).json()['data']
        all_stops.extend([{"name": s['name_en'], "id": s['stop_id'], "type": "GMB"} for s in data])
    except Exception as e: print(f"GMB Error: {e}")

    with open('stops.json', 'w', encoding='utf-8') as f:
        json.dump(all_stops, f, ensure_ascii=False, indent=4)
    print(f"成功處理，總計 {len(all_stops)} 個站點。")

if __name__ == "__main__":
    fetch_stops()
