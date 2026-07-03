import requests
import json
import csv
import io
import time

# 設定請求標頭，模擬瀏覽器請求
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

def get_kmb_stops():
    print("正在抓取九巴站點...")
    try:
        data = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/stop", headers=HEADERS, timeout=15).json().get('data', [])
        return [{"name": s.get('name_en'), "id": s.get('stop'), "type": "KMB"} for s in data]
    except Exception as e:
        print(f"九巴錯誤: {e}")
        return []

def get_ctb_stops():
    print("正在抓取城巴站點...")
    all_ctb = []
    seen = set()
    try:
        routes = requests.get("https://rt.data.gov.hk/v1/transport/citybus-nwfb/route/CTB", headers=HEADERS, timeout=15).json().get('data', [])
        for r in routes:
            route_id = r.get('route')
            res = requests.get(f"https://rt.data.gov.hk/v1/transport/citybus-nwfb/route-stop/CTB/{route_id}/outbound", headers=HEADERS, timeout=10)
            if res.status_code == 200:
                for s in res.json().get('data', []):
                    stop_id = s.get('stop')
                    if stop_id and stop_id not in seen:
                        all_ctb.append({"name": s.get('name_en'), "id": stop_id, "type": "CTB"})
                        seen.add(stop_id)
            time.sleep(0.05)
    except Exception as e:
        print(f"城巴錯誤: {e}")
    return all_ctb

def get_mtr_stops():
    print("正在抓取港鐵巴士站點...")
    try:
        res = requests.get("https://opendata.mtr.com.hk/data/mtr_bus_stops.csv", headers=HEADERS, timeout=15)
        reader = csv.DictReader(io.StringIO(res.text))
        return [{"name": row['Stop Name (EN)'], "id": row['Stop ID'], "type": "MTR"} for row in reader]
    except Exception as e:
        print(f"港鐵巴士錯誤: {e}")
        return []

def get_gmb_stops():
    print("正在抓取專線小巴站點...")
    all_gmb = []
    seen = set()
    try:
        route_list = requests.get("https://data.etagmb.gov.hk/route", headers=HEADERS, timeout=10).json().get('data', {}).get('routes', {})
        for region, routes in route_list.items():
            for r_code in routes:
                res = requests.get(f"https://data.etagmb.gov.hk/route/{region}/{r_code}", headers=HEADERS, timeout=5)
                if res.status_code == 200:
                    for route_info in res.json().get('data', []):
                        for direction in route_info.get('directions', []):
                            for s in direction.get('stops', []):
                                stop_id = s.get('stop_id')
                                if stop_id and stop_id not in seen:
                                    all_gmb.append({"name": s.get('name_en'), "id": stop_id, "type": "GMB"})
                                    seen.add(stop_id)
                time.sleep(0.05)
    except Exception as e:
        print(f"小巴錯誤: {e}")
    return all_gmb

def update_all():
    print("開始合併所有數據...")
    stops = get_kmb_stops() + get_ctb_stops() + get_mtr_stops() + get_gmb_stops()
    
    with open('stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)
    print(f"更新完成！總共儲存了 {len(stops)} 個站點資訊。")

if __name__ == "__main__":
    update_all()
