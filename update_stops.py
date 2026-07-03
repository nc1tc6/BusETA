import requests
import json
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}
# 九巴基礎 API
URL_KMB = "https://data.etabus.gov.hk/v1/transport/kmb/stop"
# 城巴基礎 API (確保路徑精確)
BASE_URL_CTB = "https://rt.data.gov.hk/v1/transport/citybus-nwfb"

def get_kmb_stops():
    print("正在抓取九巴...")
    try:
        data = requests.get(URL_KMB, headers=HEADERS, timeout=15).json().get('data', [])
        return [{"name": s.get('name_en'), "id": s.get('stop'), "type": "KMB"} for s in data]
    except: return []

def get_ctb_stops():
    print("正在抓取城巴...")
    all_ctb = []
    seen_ids = set()
    
    try:
        # 1. 取得所有路線
        routes_url = f"{BASE_URL_CTB}/route/CTB"
        routes = requests.get(routes_url, headers=HEADERS, timeout=15).json().get('data', [])
        
        # 2. 遍歷每條路線
        for r in routes:
            route_id = r.get('route')
            # 嘗試抓取去程
            url = f"{BASE_URL_CTB}/route-stop/CTB/{route_id}/outbound"
            res = requests.get(url, headers=HEADERS, timeout=10)
            
            if res.status_code == 200:
                stops = res.json().get('data', [])
                for s in stops:
                    stop_id = s.get('stop')
                    if stop_id and stop_id not in seen_ids:
                        all_ctb.append({"name": s.get('name_en'), "id": stop_id, "type": "CTB"})
                        seen_ids.add(stop_id)
            time.sleep(0.05) # 降低請求頻率，避免觸發防護機制
    except Exception as e:
        print(f"城巴抓取錯誤: {e}")
    return all_ctb

def update_all():
    stops = get_kmb_stops() + get_ctb_stops()
    with open('stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)
    print(f"完成！總計 {len(stops)} 個站點已儲存。")

if __name__ == "__main__":
    update_all()
