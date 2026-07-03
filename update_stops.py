def get_mtr_stops():
    print("正在抓取港鐵巴士站點...")
    try:
        res = requests.get("https://opendata.mtr.com.hk/data/mtr_bus_stops.csv", headers=HEADERS, timeout=15)
        # 顯示原始內容前 100 個字，用來確認是否有抓到東西
        print(f"MTR CSV 前 100 個字: {res.text[:100]}")
        
        reader = csv.DictReader(io.StringIO(res.text))
        stops = []
        for row in reader:
            # 根據實際 CSV 的表頭進行取值 (有些會帶有 BOM 標記，若報錯需處理)
            stops.append({
                "name": row.get('Stop Name (EN)'), 
                "id": row.get('Stop ID'), 
                "type": "MTR"
            })
        print(f"成功抓取 {len(stops)} 個港鐵巴士站點。")
        return stops
    except Exception as e:
        print(f"港鐵巴士錯誤: {e}")
        return []

def get_gmb_stops():
    print("正在抓取專線小巴站點...")
    all_gmb = []
    seen = set()
    try:
        # 先抓取路線列表
        res = requests.get("https://data.etagmb.gov.hk/route", headers=HEADERS, timeout=10)
        data = res.json()
        print(f"小巴路線數據結構: {list(data.keys())}") # 查看頂層結構
        
        routes_data = data.get('data', {}).get('routes', {})
        
        for region, routes in routes_data.items():
            for r_code in routes:
                url = f"https://data.etagmb.gov.hk/route/{region}/{r_code}"
                res = requests.get(url, headers=HEADERS, timeout=5)
                if res.status_code == 200:
                    route_details = res.json().get('data', [])
                    for item in route_details:
                        # 檢查每個路線物件內的結構
                        for direction in item.get('directions', []):
                            for s in direction.get('stops', []):
                                stop_id = s.get('stop_id')
                                if stop_id and stop_id not in seen:
                                    all_gmb.append({"name": s.get('name_en'), "id": stop_id, "type": "GMB"})
                                    seen.add(stop_id)
        print(f"成功抓取 {len(all_gmb)} 個小巴站點。")
    except Exception as e:
        print(f"小巴抓取錯誤: {e}")
    return all_gmb
