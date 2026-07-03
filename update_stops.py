import requests
import json
import csv
import io
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_kmb_stops():
    print("正在抓取九巴...")
    try:
        data = requests.get("https://data.etabus.gov.hk/v1/transport/kmb/stop", headers=HEADERS, timeout=15).json().get('data', [])
        return [{"name": s.get('name_en') or s.get('name_chi'), "id": s.get('stop'), "type": "KMB"} for s in data]
    except Exception as e:
        print(f"KMB Error: {e}")
        return []

def get_ctb_stops():
    print("正在抓取城巴...")
    all_ctb = []
    seen = set()
    try:
        routes = requests.get("https://rt.data.gov.hk/v1/transport/citybus-nwfb/route/CTB", headers=HEADERS, timeout=15).json().get('data', [])
        for r in routes:
            route_id = r.get('route')
            url = f"https://rt.data.gov.hk/v1/transport/citybus-nwfb/route-stop/CTB/{route_id}/outbound"
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                for s in res.json().get('data', []):
                    stop_id = s.get('stop')
                    # 多重備援：嘗試抓取不同名稱欄位
                    name = s.get('name_en') or s.get('name_chi') or s.get('name_tc')
                    if stop_id and stop_id not in seen:
                        all_ctb.append({"name": name, "id": stop_id, "type": "CTB"})
                        seen.add(stop_id)
            time.sleep(0.05)
    except Exception as e:
        print(f"CTB Error: {e}")
    return all_ctb

def get_mtr_stops():
    print("正在抓取港鐵巴士...")
    try:
        res = requests.get("https://opendata.mtr.com.hk/data/mtr_bus_stops.csv", headers=HEADERS, timeout=15)
        f = io.StringIO(res.text.lstrip('\ufeff'))
        reader = csv.DictReader(f)
        stops = []
        for row in reader:
            # 港鐵 CSV 解析
            name = row.get('Stop Name (EN)') or row.get('Stop Name') or next(iter(row.values()))
            stop_id = row.get('Stop ID')
            if stop_id:
                stops.append({"name": name, "id": stop_id, "type": "MTR"})
        return stops
    except Exception as e:
        print(f"MTR Error: {e}")
        return []

def get_gmb_stops():
    print("正在抓取小巴...")
    all_gmb = []
    seen = set()
    try:
        base_url = "https://data.etagmb.gov.hk"
        route_data = requests.get(f"{base_url}/route", headers=HEADERS, timeout=10).json().get('data', {}).get('routes', {})
        for region, route_list in route_data.items():
            for r_code in route_list:
                res = requests.get(f"{base_url}/route/{region}/{r_code}", headers=HEADERS, timeout=5)
                if res.status_code == 200:
                    data = res.json().get('data', [])
                    for item in data:
                        for direction in item.get('directions', []):
                            for s in direction.get('stops', []):
                                stop_id = s.get('stop_id')
                                name = s.get('name_en') or s.get('name_chi')
                                if stop_id and stop_id not in seen:
                                    all_gmb.append({"name": name, "id": stop_id, "type": "GMB"})
                                    seen.add(stop_id)
                time.sleep(0.05)
    except Exception as e:
        print(f"GMB Error: {e}")
    return all_gmb

def update_all():
    print("開始合併所有數據...")
    stops = get_kmb_stops() + get_ctb_stops() + get_mtr_stops() + get_gmb_stops()
    
    # 寫入檔案
    with open('stops.json', 'w', encoding='utf-8') as f:
        json.dump(stops, f, ensure_ascii=False, indent=4)
    print(f"更新完成！總共儲存了 {len(stops)} 個站點資訊。")

if __name__ == "__main__":
    update_all()
