"""
ECOS API에서 '외화' 관련 통계표 전체 검색
"""
import requests

API_KEY = 'LZ5FB0NNZDPJFXE6ZVTL'

def search_tables(keyword):
    """키워드로 통계표 검색"""
    url = f'https://ecos.bok.or.kr/api/StatisticTableList/{API_KEY}/json/kr/1/500/{keyword}'
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        if 'StatisticTableList' in data:
            return data['StatisticTableList']['row']
    except Exception as e:
        print(f"Error: {e}")
    return []

def get_stat_items(stat_code):
    """통계표의 항목 목록 조회"""
    url = f'https://ecos.bok.or.kr/api/StatisticItemList/{API_KEY}/json/kr/1/500/{stat_code}'
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        if 'StatisticItemList' in data:
            return data['StatisticItemList']['row']
    except:
        pass
    return []

def get_data(stat_code, item_code, start='2004', end='2019', cycle='A'):
    """데이터 조회"""
    url = f'https://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/1/1000/{stat_code}/{cycle}/{start}/{end}/{item_code}'
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        if 'StatisticSearch' in data:
            return data['StatisticSearch']['row']
    except:
        pass
    return []

# 외화 관련 모든 통계표 검색
print("=" * 80)
print("Searching for '외화' related statistics...")
print("=" * 80)

tables = search_tables('외화')
print(f"\nFound {len(tables)} tables:")

for t in tables:
    code = t.get('STAT_CODE', '')
    name = t.get('STAT_NAME', '')
    cycle = t.get('CYCLE', '')
    print(f"  [{code}] {name} ({cycle})")

# 금리 관련도 검색
print("\n" + "=" * 80)
print("Searching for '예금금리' related statistics...")
print("=" * 80)

tables2 = search_tables('예금금리')
print(f"\nFound {len(tables2)} tables:")

for t in tables2:
    code = t.get('STAT_CODE', '')
    name = t.get('STAT_NAME', '')
    print(f"  [{code}] {name}")

# '외화대출' 검색
print("\n" + "=" * 80)
print("Searching for '외화대출' related statistics...")
print("=" * 80)

tables3 = search_tables('외화대출')
print(f"\nFound {len(tables3)} tables:")

for t in tables3:
    code = t.get('STAT_CODE', '')
    name = t.get('STAT_NAME', '')
    print(f"  [{code}] {name}")

# 통화별 검색
print("\n" + "=" * 80)
print("Searching for 'USD' or 'dollar' related...")
print("=" * 80)

for keyword in ['달러', 'USD', '엔화', '위안']:
    tables_cur = search_tables(keyword)
    if tables_cur:
        print(f"\n'{keyword}': {len(tables_cur)} tables")
        for t in tables_cur[:5]:
            print(f"  [{t.get('STAT_CODE')}] {t.get('STAT_NAME')}")

# 유망한 통계표 상세 확인
print("\n" + "=" * 80)
print("Checking promising statistics in detail...")
print("=" * 80)

promising_codes = ['121Y002', '121Y003', '121Y015', '722Y001', '038Y201', '038Y401']

for stat_code in promising_codes:
    items = get_stat_items(stat_code)
    if items:
        print(f"\n[{stat_code}] - {len(items)} items")
        
        # '외화' 또는 'USD', 'JPY' 등이 포함된 항목 찾기
        for item in items:
            name = item.get('ITEM_NAME', '')
            code = item.get('ITEM_CODE', '')
            if any(kw in name for kw in ['외화', 'USD', 'JPY', 'EUR', 'CNY', '달러', '엔', '위안', '유로']):
                print(f"  FOUND: {code} - {name}")
                
                # 데이터 조회 시도
                data = get_data(stat_code, code)
                if data:
                    print(f"    -> DATA EXISTS: {len(data)} records")
                    print(f"       Sample: {data[0]}")
