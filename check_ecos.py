"""
ECOS API에서 실제 사용 가능한 외화예금금리 데이터 찾기
"""
import requests
import json
import pandas as pd

API_KEY = 'LZ5FB0NNZDPJFXE6ZVTL'

def get_stat_items(stat_code):
    """통계표의 항목 목록 조회"""
    url = f'https://ecos.bok.or.kr/api/StatisticItemList/{API_KEY}/json/kr/1/500/{stat_code}'
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        if 'StatisticItemList' in data:
            return data['StatisticItemList']['row']
    except Exception as e:
        print(f"Error: {e}")
    return []

def get_data(stat_code, item_code, start='200401', end='201912', cycle='M'):
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

# 외화 관련 통계표 확인
stat_codes = [
    ('722Y001', 'Foreign Currency Deposit/Loan Rate'),
    ('121Y002', 'Deposit Bank Foreign Loan Rate'),
    ('121Y015', 'Deposit Bank Deposit Rate'),
]

print("=" * 80)
print("ECOS API - Available Item Codes")
print("=" * 80)

for stat_code, desc in stat_codes:
    print(f"\n[{stat_code}] {desc}")
    print("-" * 60)
    
    items = get_stat_items(stat_code)
    if items:
        print(f"Found {len(items)} items:")
        for item in items[:15]:
            code = item.get('ITEM_CODE', '')
            name = item.get('ITEM_NAME', '')
            cycle = item.get('CYCLE', '')
            start = item.get('START_TIME', '')
            end = item.get('END_TIME', '')
            print(f"  {code:20} | {name[:40]:40} | {cycle} | {start}-{end}")
    else:
        print("  No items found")

# 실제 데이터 조회 테스트
print("\n" + "=" * 80)
print("Testing Data Retrieval")
print("=" * 80)

# 722Y001에서 첫 번째 항목으로 테스트
items_722 = get_stat_items('722Y001')
if items_722:
    test_codes = [items_722[i]['ITEM_CODE'] for i in range(min(5, len(items_722)))]
    
    for item_code in test_codes:
        print(f"\nTrying: 722Y001 / {item_code}")
        
        # 연간 데이터로 시도
        data = get_data('722Y001', item_code, '2004', '2019', 'A')
        if data:
            print(f"  SUCCESS (Annual): {len(data)} records")
            for d in data[:3]:
                print(f"    {d.get('TIME', '')} : {d.get('DATA_VALUE', '')} ({d.get('ITEM_NAME1', '')})")
            break
        
        # 월간 데이터로 시도
        data = get_data('722Y001', item_code, '200401', '201912', 'M')
        if data:
            print(f"  SUCCESS (Monthly): {len(data)} records")
            break
        
        print(f"  No data")

# 121Y002도 테스트
print("\n" + "-" * 60)
items_121 = get_stat_items('121Y002')
if items_121:
    test_codes = [items_121[i]['ITEM_CODE'] for i in range(min(5, len(items_121)))]
    
    for item_code in test_codes:
        print(f"\nTrying: 121Y002 / {item_code}")
        
        data = get_data('121Y002', item_code, '2004', '2019', 'A')
        if data:
            print(f"  SUCCESS (Annual): {len(data)} records")
            for d in data[:3]:
                print(f"    {d.get('TIME', '')} : {d.get('DATA_VALUE', '')} ({d.get('ITEM_NAME1', '')})")
            break
        
        data = get_data('121Y002', item_code, '200401', '201912', 'M')
        if data:
            print(f"  SUCCESS (Monthly): {len(data)} records")
            break
        
        print(f"  No data")
