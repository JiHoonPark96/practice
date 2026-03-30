"""
실제 데이터 수집 가능한 소스들:
1. FRED API - LIBOR 금리 (국제 기준금리)
2. 은행연합회 - 은행 공시 금리
3. 각 은행 공시/IR 자료

이 스크립트는 FRED에서 2004-2019 LIBOR 금리를 수집합니다.
"""
import requests
import pandas as pd
from datetime import datetime

# FRED API (무료, API 키 필요)
# API 키 발급: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = "YOUR_FRED_API_KEY"  # 무료로 발급 가능

def get_fred_series(series_id, start='2004-01-01', end='2019-12-31'):
    """
    FRED API에서 시계열 데이터 조회
    """
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'observation_start': start,
        'observation_end': end
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        if 'observations' in data:
            df = pd.DataFrame(data['observations'])
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            return df[['date', 'value']]
    except Exception as e:
        print(f"Error: {e}")
    return None

# FRED에서 제공하는 주요 금리 시리즈 ID
# (실제 데이터를 위해 API 키 필요)
FRED_SERIES = {
    # USD LIBOR
    'USD_3M': 'USD3MTD156N',  # 3-Month London Interbank Offered Rate (LIBOR)
    'USD_6M': 'USD6MTD156N',  # 6-Month LIBOR
    'USD_12M': 'USD12MD156N', # 12-Month LIBOR
    
    # JPY LIBOR
    'JPY_3M': 'JPY3MTD156N',
    'JPY_6M': 'JPY6MTD156N',
    
    # EUR LIBOR
    'EUR_3M': 'EUR3MTD156N',
    'EUR_6M': 'EUR6MTD156N',
    
    # GBP LIBOR
    'GBP_3M': 'GBP3MTD156N',
    'GBP_6M': 'GBP6MTD156N',
    
    # 중앙은행 기준금리
    'FED_RATE': 'FEDFUNDS',    # US Federal Funds Rate
    'ECB_RATE': 'ECBDFR',      # ECB Deposit Facility Rate
    'BOJ_RATE': 'IRSTCB01JPM156N',  # Bank of Japan Rate
    'BOE_RATE': 'BOERUKM',     # Bank of England Rate
    'PBOC_RATE': 'INTDSRCNM193N',  # China 1-Year Lending Rate
}

print("=" * 80)
print("FRED 금리 데이터 시리즈 정보")
print("=" * 80)
print("""
FRED API를 사용하면 다음 금리 데이터를 무료로 받을 수 있습니다:

1. LIBOR 금리 (London Interbank Offered Rate)
   - USD 3M/6M/12M LIBOR
   - JPY 3M/6M LIBOR
   - EUR 3M/6M LIBOR
   - GBP 3M/6M LIBOR
   
2. 중앙은행 기준금리
   - US Federal Funds Rate
   - ECB Deposit Rate
   - BOJ Policy Rate
   - PBOC Lending Rate (China)

⚠️ 중요: 
- LIBOR는 은행간 거래 금리이므로, 실제 예금금리와는 다릅니다.
- 한국 은행들의 외화예금금리는 LIBOR + 스프레드로 결정됩니다.
- FRED API 키가 필요합니다: https://fred.stlouisfed.org/docs/api/api_key.html
""")

# 중국 위안화 관련 데이터는 FRED에 제한적
print("\n" + "=" * 80)
print("CNY (위안화) 금리 데이터 소스")
print("=" * 80)
print("""
중국 위안화(CNY/RMB) 예금금리는 다음에서 찾을 수 있습니다:

1. 중국인민은행 (PBOC)
   - 공식 웹사이트: http://www.pbc.gov.cn/
   - PBOC 기준금리 (1년 예금금리 등)

2. CEIC Data (유료)
   - 중국 금융 데이터 전문

3. Wind Information (유료)
   - 중국 금융 데이터 전문

4. 한국 은행 공시
   - 각 은행 IR 페이지에서 위안화 예금 상품 금리 확인
""")

print("\n" + "=" * 80)
print("한국 은행 외화예금금리 실제 데이터 소스")
print("=" * 80)
print("""
⭐ 가장 확실한 방법 ⭐

1. 금융감독원 FISIS (금융통계정보시스템)
   URL: https://fisis.fss.or.kr/
   경로: 업무보고서 > 금리현황 > 은행별 예금금리
   
2. 은행연합회 소비자포털
   URL: https://portal.kfb.or.kr/
   경로: 금리비교 > 예금금리
   
3. 각 은행 공시실/IR
   - 우리은행: https://www.wooribank.com > 은행소개 > 경영공시
   - 신한은행: https://www.shinhan.com > 고객센터 > 금리/수수료 안내
   - 국민은행: https://www.kbstar.com > 고객센터 > 금리안내
   - 하나은행: https://www.kebhana.com > 고객센터 > 금리안내
   - 산업은행: https://www.kdb.co.kr > 금융상품 > 상품공시

4. 신한은행 과거 금리 (참고)
   https://www.shinhan.com/hpe/index.jsp#w2xPath=/hpe/customer/CS08/CS08008RP01.xml
   (페이지가 변경되었을 수 있음)

⚠️ 참고사항:
- 2004-2019년 기간의 과거 데이터는 대부분 은행 웹사이트에서 직접 제공하지 않습니다.
- 과거 데이터는 은행에 직접 문의하거나, 학술 DB를 통해 접근해야 합니다.
- 첨부된 Figure 12 그래프의 원본 논문을 찾으면 데이터 출처를 확인할 수 있습니다.
""")

print("\n" + "=" * 80)
print("대안: 학술 데이터베이스")
print("=" * 80)
print("""
대학 도서관을 통해 접근 가능한 데이터베이스:

1. Bloomberg Terminal
   - 가장 포괄적인 금융 데이터
   - 대학 도서관 또는 금융기관에서 접근 가능

2. Refinitiv Eikon (구 Thomson Reuters)
   - 글로벌 금융 데이터

3. CEIC Asia Database
   - 아시아 경제/금융 데이터 전문

4. Datastream
   - 역사적 금융 데이터

5. 한국학술정보 (KISS)
   - 한국 논문에서 사용된 데이터 확인
""")

# 실제로 FRED API 테스트 (API 키 필요)
if FRED_API_KEY != "YOUR_FRED_API_KEY":
    print("\n" + "=" * 80)
    print("FRED API 테스트")
    print("=" * 80)
    
    for name, series_id in list(FRED_SERIES.items())[:3]:
        print(f"\n{name} ({series_id}):")
        df = get_fred_series(series_id)
        if df is not None and len(df) > 0:
            print(f"  Data points: {len(df)}")
            print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"  Sample: {df.head(3).to_string()}")
        else:
            print("  No data or API error")
else:
    print("\n⚠️ FRED API 키를 설정하면 실제 데이터를 받을 수 있습니다.")
    print("   무료 발급: https://fred.stlouisfed.org/docs/api/api_key.html")
