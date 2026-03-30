"""
ECOS 전체 통계표 목록에서 외화/금리 관련 찾기
+ 금융감독원 FISIS 데이터 확인
"""
import requests
import re

API_KEY = 'LZ5FB0NNZDPJFXE6ZVTL'

def get_all_stat_tables():
    """모든 통계표 목록 (카테고리별)"""
    # ECOS 통계분류 코드 사용
    categories = [
        ('통화/금융', '01'),
        ('금리', '02'),
        ('환율', '03'),
        ('국제수지/외채', '04'),
    ]
    
    all_tables = []
    
    for cat_name, cat_code in categories:
        # 통계표 목록 API (다른 방식)
        url = f'https://ecos.bok.or.kr/api/StatisticTableList/{API_KEY}/json/kr/1/1000/'
        try:
            resp = requests.get(url, timeout=30)
            data = resp.json()
            if 'StatisticTableList' in data:
                tables = data['StatisticTableList']['row']
                all_tables.extend(tables)
        except Exception as e:
            print(f"Error for {cat_name}: {e}")
    
    return all_tables

def search_keyword_in_tables():
    """금리 관련 통계표 직접 검색"""
    
    # 직접 알려진 통계 코드들 테스트
    possible_codes = [
        '121Y001', '121Y002', '121Y003', '121Y004', '121Y005',
        '121Y010', '121Y011', '121Y012', '121Y013', '121Y014', '121Y015',
        '121Y020', '121Y021', '121Y022', 
        '722Y001', '722Y002', '722Y003',
        '038Y001', '038Y101', '038Y201', '038Y301', '038Y401',
        '036Y001', '036Y002', '036Y003',
        '064Y001', '064Y002',
        '060Y001', '060Y002', '060Y003',
    ]
    
    print("=" * 80)
    print("Checking known ECOS stat codes for foreign currency rates...")
    print("=" * 80)
    
    found_tables = []
    
    for stat_code in possible_codes:
        url = f'https://ecos.bok.or.kr/api/StatisticItemList/{API_KEY}/json/kr/1/10/{stat_code}'
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if 'StatisticItemList' in data:
                items = data['StatisticItemList']['row']
                if items:
                    first_item = items[0].get('ITEM_NAME', '')
                    stat_name = items[0].get('STAT_NAME', stat_code)
                    print(f"[{stat_code}] {stat_name} - {len(items)} items")
                    found_tables.append({
                        'code': stat_code,
                        'name': stat_name,
                        'items': items
                    })
        except:
            pass
    
    return found_tables

def check_fx_related_items(tables):
    """외화 관련 항목 확인"""
    print("\n" + "=" * 80)
    print("Searching for foreign currency items in each table...")
    print("=" * 80)
    
    fx_keywords = ['외화', '달러', 'USD', 'JPY', 'EUR', 'CNY', 'GBP', 
                   '엔화', '위안', '유로', '파운드', '외환']
    
    for table in tables:
        stat_code = table['code']
        
        # 전체 항목 가져오기
        url = f'https://ecos.bok.or.kr/api/StatisticItemList/{API_KEY}/json/kr/1/500/{stat_code}'
        try:
            resp = requests.get(url, timeout=30)
            data = resp.json()
            
            if 'StatisticItemList' in data:
                items = data['StatisticItemList']['row']
                
                fx_items = []
                for item in items:
                    name = item.get('ITEM_NAME', '')
                    code = item.get('ITEM_CODE', '')
                    
                    if any(kw in name for kw in fx_keywords):
                        fx_items.append((code, name))
                
                if fx_items:
                    print(f"\n[{stat_code}] Found {len(fx_items)} foreign currency items:")
                    for code, name in fx_items[:10]:
                        print(f"  {code}: {name}")
        except:
            pass

def get_data_sample(stat_code, item_code):
    """데이터 샘플 조회"""
    for cycle in ['A', 'M', 'Q']:
        if cycle == 'A':
            start, end = '2004', '2019'
        elif cycle == 'M':
            start, end = '200401', '201912'
        else:
            start, end = '2004Q1', '2019Q4'
            
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/1/100/{stat_code}/{cycle}/{start}/{end}/{item_code}'
        try:
            resp = requests.get(url, timeout=30)
            data = resp.json()
            
            if 'StatisticSearch' in data:
                rows = data['StatisticSearch']['row']
                if rows:
                    return rows, cycle
        except:
            pass
    return None, None

# 실행
tables = search_keyword_in_tables()
check_fx_related_items(tables)

# 특별히 038Y, 060Y 시리즈 확인 (국제금융 통계)
print("\n" + "=" * 80)
print("Checking international finance statistics (038Y, 060Y, 064Y series)...")
print("=" * 80)

int_codes = ['038Y001', '038Y002', '038Y101', '038Y201', '038Y202', 
             '060Y001', '060Y002', '060Y003', '060Y004',
             '064Y001', '064Y002', '064Y003']

for stat_code in int_codes:
    url = f'https://ecos.bok.or.kr/api/StatisticItemList/{API_KEY}/json/kr/1/100/{stat_code}'
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if 'StatisticItemList' in data:
            items = data['StatisticItemList']['row']
            if items:
                stat_name = items[0].get('STAT_NAME', '')
                print(f"\n[{stat_code}] {stat_name}")
                print(f"  Items: {len(items)}")
                
                # 처음 5개 항목 출력
                for item in items[:5]:
                    print(f"    {item.get('ITEM_CODE')}: {item.get('ITEM_NAME')}")
    except:
        pass
