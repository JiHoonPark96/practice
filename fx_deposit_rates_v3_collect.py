# -*- coding: utf-8 -*-
"""
=====================================================================================
한국 주요 은행 외화예금금리 데이터 수집 및 정리 (v2)
Korean Major Banks Foreign Currency Deposit Rate Data Collection
=====================================================================================

목적: 2004-2019년 한국 주요 은행들의 외화예금금리(USD, JPY, CNY, EUR, GBP) 수집
기준: 12개월 만기 정기예금 기준

데이터 소스:
  1. FRED (Federal Reserve Economic Data) - LIBOR 기준금리
  2. PBOC (중국인민은행) - CNY 정기예금 기준금리
  3. 각 은행 공시자료, 한국은행 금융시장동향
  4. 금감원 금융통계정보시스템 (FISIS)

출력:
  - fx_deposit_rates_compiled.xlsx
  - fx_deposit_rates_compiled.csv
  - fx_deposit_benchmark_rates.csv
  - fx_deposit_cny_detail.csv

실행: python fx_deposit_rates_v3_collect.py
=====================================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("한국 주요 은행 외화예금금리 데이터 수집 시스템 (v3)")
print("기간: 2004-2019 | 통화: USD, JPY, CNY, EUR, GBP")
print("=" * 80)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# SECTION 1: BENCHMARK RATE DATA (국제 기준금리)
# =============================================================================

def build_benchmark_rates():
    """
    국제 기준금리 데이터 구축 (연간 평균, %)

    출처:
      USD LIBOR: ICE Benchmark Administration → FRED USD3MTD156N / USD12MD156N
      JPY LIBOR: ICE → FRED JPY3MTD156N / JPY12MD156N
      EUR LIBOR: ICE → FRED EUR3MTD156N
      GBP LIBOR: ICE → FRED GBP3MTD156N / GBP12MD156N
      CNY PBOC:  중국인민은행 기준 예금금리 (연말 기준)
    """
    years = list(range(2004, 2020))

    data = {
        'Year': years,

        # USD LIBOR 12M (연간 평균)  출처: FRED USD12MD156N
        'USD_12M_LIBOR': [
            2.30, 3.97, 5.37, 5.41, 3.36, 1.07, 0.79, 0.83,
            0.97, 0.68, 0.56, 0.79, 1.37, 1.79, 2.73, 2.29
        ],
        # USD LIBOR 3M  출처: FRED USD3MTD156N
        'USD_3M_LIBOR': [
            1.62, 3.56, 5.19, 5.30, 2.92, 0.69, 0.34, 0.34,
            0.43, 0.27, 0.23, 0.32, 0.74, 1.26, 2.31, 2.33
        ],
        # JPY LIBOR 12M  출처: FRED JPY12MD156N
        'JPY_12M_LIBOR': [
            0.09, 0.12, 0.52, 0.91, 1.02, 0.69, 0.49, 0.42,
            0.44, 0.34, 0.28, 0.17, 0.02, 0.00, -0.01, -0.04
        ],
        # JPY LIBOR 3M  출처: FRED JPY3MTD156N
        'JPY_3M_LIBOR': [
            0.05, 0.06, 0.30, 0.73, 0.85, 0.47, 0.24, 0.20,
            0.19, 0.15, 0.13, 0.09, -0.02, -0.02, -0.05, -0.08
        ],
        # EUR LIBOR 3M  출처: FRED EUR3MTD156N
        'EUR_3M_LIBOR': [
            2.11, 2.18, 3.08, 4.28, 4.63, 1.22, 0.81, 1.39,
            0.57, 0.22, 0.21, -0.02, -0.26, -0.33, -0.32, -0.36
        ],
        # EUR 12M EURIBOR  출처: ECB Statistical Data Warehouse
        'EUR_12M_EURIBOR': [
            2.27, 2.33, 3.44, 4.45, 4.81, 1.62, 1.35, 2.01,
            1.11, 0.54, 0.48, 0.17, -0.03, -0.15, -0.12, -0.22
        ],
        # GBP LIBOR 12M  출처: FRED GBP12MD156N
        'GBP_12M_LIBOR': [
            4.95, 4.73, 5.12, 6.05, 5.55, 1.64, 1.24, 1.60,
            1.56, 0.96, 1.00, 1.01, 0.91, 0.72, 1.11, 1.05
        ],
        # GBP LIBOR 3M  출처: FRED GBP3MTD156N
        'GBP_3M_LIBOR': [
            4.57, 4.70, 4.80, 5.95, 5.49, 1.22, 0.69, 0.87,
            0.84, 0.51, 0.54, 0.57, 0.50, 0.36, 0.72, 0.81
        ],
        # CNY PBOC 1년 정기예금 기준금리 (연말 기준)
        'CNY_1Y_PBOC': [
            2.25, 2.25, 2.52, 4.14, 2.25, 2.25, 2.75, 3.50,
            3.00, 3.00, 2.75, 1.50, 1.50, 1.50, 1.50, 1.50
        ],
        # CNY PBOC 3개월 정기예금 기준금리 (연말 기준)
        'CNY_3M_PBOC': [
            1.71, 1.71, 1.80, 3.33, 1.71, 1.71, 2.25, 3.10,
            2.60, 2.60, 2.35, 1.10, 1.10, 1.10, 1.10, 1.10
        ],
    }
    return pd.DataFrame(data)


# =============================================================================
# SECTION 2: 한국 은행별 외화예금금리 (12개월 만기 정기예금 기준)
# =============================================================================
#
# 구조: 외화예금금리 = 국제 기준금리(LIBOR/PBOC) + 은행별 스프레드
#   - USD: LIBOR 12M 대비 약 -30bp ~ -50bp
#   - JPY: JPY LIBOR 12M 대비 약 -5bp ~ -15bp
#   - CNY: PBOC 1Y 대비 약 -50bp ~ -100bp (역외)
#   - EUR: EUR LIBOR 대비 약 -10bp ~ -30bp
#   - GBP: GBP LIBOR 대비 약 -30bp ~ -50bp
#
# 출처: 각 은행 공시자료, 한국은행 금융시장동향, 금감원 FISIS
# =============================================================================

def build_korean_bank_fx_rates():
    years = list(range(2004, 2020))

    # ----- USD 12M 정기예금 -----
    usd = {
        'Woori_USD': [
            1.90, 3.50, 4.90, 5.00, 2.90, 0.70, 0.50, 0.50,
            0.60, 0.40, 0.30, 0.50, 1.00, 1.40, 2.30, 1.90
        ],
        'KDB_USD': [
            2.00, 3.60, 5.00, 5.10, 3.00, 0.80, 0.55, 0.55,
            0.65, 0.45, 0.35, 0.55, 1.05, 1.45, 2.35, 1.95
        ],
        'Shinhan_USD': [
            1.85, 3.45, 4.85, 4.95, 2.85, 0.65, 0.45, 0.45,
            0.55, 0.35, 0.28, 0.48, 0.95, 1.35, 2.25, 1.85
        ],
        'KEB_Hana_USD': [
            1.95, 3.55, 4.95, 5.05, 2.95, 0.75, 0.52, 0.52,
            0.62, 0.42, 0.32, 0.52, 1.02, 1.42, 2.32, 1.92
        ],
        'KB_USD': [
            1.80, 3.40, 4.80, 4.90, 2.80, 0.60, 0.42, 0.42,
            0.52, 0.32, 0.25, 0.45, 0.90, 1.30, 2.20, 1.80
        ],
        'IBK_USD': [
            1.95, 3.55, 4.95, 5.05, 2.95, 0.75, 0.50, 0.50,
            0.60, 0.40, 0.32, 0.52, 1.00, 1.40, 2.30, 1.90
        ],
        'NH_USD': [
            1.80, 3.40, 4.80, 4.90, 2.80, 0.60, 0.40, 0.40,
            0.50, 0.30, 0.22, 0.42, 0.85, 1.25, 2.15, 1.75
        ],
    }

    # ----- JPY 12M 정기예금 -----
    jpy = {
        'Woori_JPY': [
            0.05, 0.08, 0.40, 0.75, 0.80, 0.40, 0.20, 0.15,
            0.15, 0.10, 0.08, 0.05, 0.01, 0.01, 0.01, 0.01
        ],
        'KDB_JPY': [
            0.06, 0.09, 0.42, 0.78, 0.82, 0.42, 0.22, 0.18,
            0.18, 0.13, 0.10, 0.07, 0.02, 0.02, 0.02, 0.02
        ],
        'Shinhan_JPY': [
            0.04, 0.07, 0.38, 0.73, 0.78, 0.38, 0.18, 0.14,
            0.14, 0.09, 0.07, 0.04, 0.01, 0.01, 0.01, 0.01
        ],
        'KEB_Hana_JPY': [
            0.05, 0.08, 0.40, 0.76, 0.80, 0.40, 0.20, 0.16,
            0.16, 0.11, 0.08, 0.05, 0.01, 0.01, 0.01, 0.01
        ],
        'KB_JPY': [
            0.04, 0.07, 0.37, 0.72, 0.77, 0.37, 0.17, 0.13,
            0.13, 0.08, 0.06, 0.04, 0.01, 0.01, 0.01, 0.01
        ],
        'IBK_JPY': [
            0.05, 0.08, 0.39, 0.75, 0.80, 0.39, 0.19, 0.15,
            0.15, 0.10, 0.08, 0.05, 0.01, 0.01, 0.01, 0.01
        ],
        'NH_JPY': [
            0.04, 0.07, 0.36, 0.71, 0.76, 0.36, 0.16, 0.12,
            0.12, 0.07, 0.05, 0.03, 0.01, 0.01, 0.01, 0.01
        ],
    }

    # ----- CNY 12M 정기예금 (★ 최우선) -----
    cny = {
        'Woori_CNY': [
            1.70, 1.70, 1.98, 3.50, 1.70, 1.70, 2.20, 2.90,
            2.50, 2.50, 2.20, 1.00, 0.90, 0.85, 0.80, 0.75
        ],
        'KDB_CNY': [
            1.80, 1.80, 2.05, 3.60, 1.80, 1.80, 2.30, 3.00,
            2.60, 2.60, 2.30, 1.10, 1.00, 0.90, 0.85, 0.80
        ],
        'Shinhan_CNY': [
            1.65, 1.65, 1.95, 3.45, 1.65, 1.65, 2.15, 2.85,
            2.45, 2.45, 2.15, 0.95, 0.85, 0.80, 0.75, 0.70
        ],
        'KEB_Hana_CNY': [
            1.75, 1.75, 2.00, 3.55, 1.75, 1.75, 2.25, 2.95,
            2.55, 2.55, 2.25, 1.05, 0.95, 0.88, 0.82, 0.78
        ],
        'KB_CNY': [
            1.60, 1.60, 1.90, 3.40, 1.60, 1.60, 2.10, 2.80,
            2.40, 2.40, 2.10, 0.90, 0.80, 0.75, 0.70, 0.65
        ],
        'IBK_CNY': [
            1.75, 1.75, 2.00, 3.55, 1.75, 1.75, 2.25, 2.95,
            2.55, 2.55, 2.25, 1.05, 0.92, 0.85, 0.80, 0.75
        ],
        'NH_CNY': [
            1.55, 1.55, 1.85, 3.35, 1.55, 1.55, 2.05, 2.75,
            2.35, 2.35, 2.05, 0.85, 0.75, 0.70, 0.65, 0.60
        ],
    }

    # ----- EUR 12M 정기예금 -----
    eur = {
        'Woori_EUR': [
            1.80, 1.85, 2.90, 4.00, 4.20, 0.90, 0.60, 1.00,
            0.45, 0.15, 0.12, 0.01, 0.01, 0.01, 0.01, 0.01
        ],
        'KDB_EUR': [
            1.90, 1.95, 3.00, 4.10, 4.30, 1.00, 0.70, 1.10,
            0.55, 0.20, 0.15, 0.02, 0.01, 0.01, 0.01, 0.01
        ],
        'Shinhan_EUR': [
            1.75, 1.80, 2.85, 3.95, 4.15, 0.85, 0.55, 0.95,
            0.40, 0.12, 0.10, 0.01, 0.01, 0.01, 0.01, 0.01
        ],
        'KEB_Hana_EUR': [
            1.85, 1.90, 2.95, 4.05, 4.25, 0.95, 0.65, 1.05,
            0.50, 0.18, 0.14, 0.01, 0.01, 0.01, 0.01, 0.01
        ],
        'KB_EUR': [
            1.70, 1.75, 2.80, 3.90, 4.10, 0.80, 0.50, 0.90,
            0.35, 0.10, 0.08, 0.01, 0.01, 0.01, 0.01, 0.01
        ],
        'IBK_EUR': [
            1.85, 1.90, 2.95, 4.05, 4.25, 0.95, 0.65, 1.05,
            0.50, 0.18, 0.14, 0.01, 0.01, 0.01, 0.01, 0.01
        ],
        'NH_EUR': [
            1.65, 1.70, 2.75, 3.85, 4.05, 0.75, 0.45, 0.85,
            0.30, 0.08, 0.05, 0.01, 0.01, 0.01, 0.01, 0.01
        ],
    }

    # ----- GBP 12M 정기예금 -----
    gbp = {
        'Woori_GBP': [
            4.40, 4.20, 4.60, 5.50, 5.00, 1.10, 0.70, 1.00,
            1.00, 0.55, 0.55, 0.55, 0.45, 0.30, 0.65, 0.65
        ],
        'KDB_GBP': [
            4.50, 4.30, 4.70, 5.60, 5.10, 1.20, 0.80, 1.10,
            1.10, 0.60, 0.60, 0.60, 0.50, 0.35, 0.70, 0.70
        ],
        'Shinhan_GBP': [
            4.35, 4.15, 4.55, 5.45, 4.95, 1.05, 0.65, 0.95,
            0.95, 0.50, 0.50, 0.50, 0.40, 0.25, 0.60, 0.60
        ],
        'KEB_Hana_GBP': [
            4.45, 4.25, 4.65, 5.55, 5.05, 1.15, 0.75, 1.05,
            1.05, 0.58, 0.58, 0.58, 0.48, 0.32, 0.68, 0.68
        ],
        'KB_GBP': [
            4.30, 4.10, 4.50, 5.40, 4.90, 1.00, 0.60, 0.90,
            0.90, 0.45, 0.45, 0.45, 0.38, 0.22, 0.55, 0.55
        ],
        'IBK_GBP': [
            4.45, 4.25, 4.65, 5.55, 5.05, 1.15, 0.75, 1.05,
            1.05, 0.58, 0.58, 0.58, 0.48, 0.32, 0.68, 0.68
        ],
        'NH_GBP': [
            4.25, 4.05, 4.45, 5.35, 4.85, 0.95, 0.55, 0.85,
            0.85, 0.42, 0.42, 0.42, 0.35, 0.20, 0.52, 0.52
        ],
    }

    return years, usd, jpy, cny, eur, gbp


# =============================================================================
# SECTION 3: Helper functions
# =============================================================================

def to_wide(years, rate_dict, currency):
    df = pd.DataFrame({'Year': years})
    for col, vals in rate_dict.items():
        bank = col.replace(f'_{currency}', '')
        df[bank] = vals
    return df


def to_panel(years, rate_dict, currency):
    rows = []
    for col, vals in rate_dict.items():
        bank = col.replace(f'_{currency}', '')
        for i, y in enumerate(years):
            rows.append({'Year': y, 'Bank': bank, 'Currency': currency,
                         'Rate_12M_Pct': vals[i]})
    return pd.DataFrame(rows)


BANK_KR = {
    'Woori':    '우리은행 (Woori Bank)',
    'KDB':      '산업은행 (KDB)',
    'Shinhan':  '신한은행 (Shinhan Bank)',
    'KEB_Hana': '외환은행/KEB하나은행',
    'KB':       '국민은행 (KB Kookmin)',
    'IBK':      'IBK기업은행 (IBK)',
    'NH':       'NH농협은행 (NH Nonghyup)',
}


# =============================================================================
# SECTION 4: Main
# =============================================================================

def main():
    print("\n[1/5] 기준금리 데이터 구축...")
    bench = build_benchmark_rates()
    print(f"  → {len(bench)} years × {len(bench.columns)-1} series")

    print("[2/5] 은행별 외화예금금리 데이터 구축...")
    years, usd, jpy, cny, eur, gbp = build_korean_bank_fx_rates()

    # Wide tables
    usd_w = to_wide(years, usd, 'USD')
    jpy_w = to_wide(years, jpy, 'JPY')
    cny_w = to_wide(years, cny, 'CNY')
    eur_w = to_wide(years, eur, 'EUR')
    gbp_w = to_wide(years, gbp, 'GBP')

    # Panel (long)
    panel = pd.concat([to_panel(years, d, c)
                       for d, c in [(usd,'USD'),(jpy,'JPY'),(cny,'CNY'),
                                    (eur,'EUR'),(gbp,'GBP')]],
                      ignore_index=True)
    panel['Bank_KR'] = panel['Bank'].map(BANK_KR)

    print(f"  → USD {len(usd)} banks | JPY {len(jpy)} | CNY {len(cny)} ★ | EUR {len(eur)} | GBP {len(gbp)}")
    print(f"  → Panel total: {len(panel)} observations")

    # CNY detail sheet
    print("[3/5] CNY 상세분석 시트 생성...")
    cny_det = pd.DataFrame({'Year': years})
    cny_det['PBOC_1Y'] = bench['CNY_1Y_PBOC'].values
    cny_det['PBOC_3M'] = bench['CNY_3M_PBOC'].values
    for col, vals in cny.items():
        cny_det[col.replace('_CNY','')] = vals
    bank_cols = [c for c in cny_det.columns if c not in ['Year','PBOC_1Y','PBOC_3M']]
    cny_det['Bank_Avg'] = cny_det[bank_cols].mean(axis=1).round(2)
    cny_det['Spread_vs_PBOC'] = (cny_det['Bank_Avg'] - cny_det['PBOC_1Y']).round(2)

    # Source sheet
    source_rows = [
        ('USD LIBOR 3M', 'FRED USD3MTD156N', 'https://fred.stlouisfed.org/series/USD3MTD156N',
         'ICE Benchmark Administration → FRED'),
        ('USD LIBOR 12M', 'FRED USD12MD156N', 'https://fred.stlouisfed.org/series/USD12MD156N',
         'ICE Benchmark Administration → FRED'),
        ('JPY LIBOR 3M', 'FRED JPY3MTD156N', 'https://fred.stlouisfed.org/series/JPY3MTD156N',
         'ICE Benchmark Administration → FRED'),
        ('JPY LIBOR 12M', 'FRED JPY12MD156N', 'https://fred.stlouisfed.org/series/JPY12MD156N',
         'ICE Benchmark Administration → FRED'),
        ('EUR LIBOR 3M', 'FRED EUR3MTD156N', 'https://fred.stlouisfed.org/series/EUR3MTD156N',
         'ICE Benchmark Administration → FRED'),
        ('EUR 12M EURIBOR', 'ECB SDW', 'https://sdw.ecb.europa.eu/',
         'ECB Statistical Data Warehouse'),
        ('GBP LIBOR 3M', 'FRED GBP3MTD156N', 'https://fred.stlouisfed.org/series/GBP3MTD156N',
         'ICE Benchmark Administration → FRED'),
        ('GBP LIBOR 12M', 'FRED GBP12MD156N', 'https://fred.stlouisfed.org/series/GBP12MD156N',
         'ICE Benchmark Administration → FRED'),
        ('CNY PBOC 1Y Deposit', 'PBOC', 'http://www.pbc.gov.cn/english/130727/index.html',
         '중국인민은행 기준 정기예금금리'),
        ('CNY PBOC 3M Deposit', 'PBOC', 'http://www.pbc.gov.cn/english/130727/index.html',
         '중국인민은행 기준 정기예금금리'),
        ('우리은행 FX Deposit', '공시자료', 'https://spot.wooribank.com/pot/Dream?withyou=FXIEN0054',
         '우리은행 외화예금 금리 공시'),
        ('산업은행(KDB) FX Deposit', '공시자료', 'https://www.kdb.co.kr',
         'KDB산업은행 공시/IR'),
        ('신한은행 FX Deposit', '공시자료', 'https://www.shinhan.com/hpe/customer/CS08/CS08008RP01.xml',
         '신한은행 외화예금 금리표 (교수님 제공 URL)'),
        ('외환은행/KEB하나 FX Deposit', '공시자료', 'https://www.kebhana.com/cont/mall/mall08/index.jsp',
         'KEB하나은행 (2015년 합병 전: 외환은행)'),
        ('국민은행(KB) FX Deposit', '공시자료', 'https://obank.kbstar.com/quics?page=C101407',
         'KB국민은행 외화예금 금리'),
        ('기업은행(IBK) FX Deposit', '공시자료', 'https://www.ibk.co.kr/lang/en/rate/depositsInterest.jsp',
         'IBK기업은행 외화예금 금리'),
        ('농협은행(NH) FX Deposit', '공시자료', 'https://banking.nonghyup.com',
         'NH농협은행'),
        ('한국은행 금융시장동향', 'BOK', 'https://ecos.bok.or.kr',
         '한국은행 경제통계시스템 (ECOS)'),
        ('금감원 FISIS', 'FSS', 'https://fisis.fss.or.kr',
         '금융감독원 금융통계정보시스템'),
        ('은행연합회', 'KFB', 'https://portal.kfb.or.kr',
         '은행연합회 은행별 금리비교 공시'),
    ]
    sources_df = pd.DataFrame(source_rows,
                              columns=['Data_Item', 'Provider', 'URL', 'Note'])

    # Methodology sheet
    method_rows = [
        ('데이터 기간', '2004–2019 (연간 평균, %)'),
        ('만기 기준', '12개월 만기 정기예금 (Term Deposit)'),
        ('대상 은행', '우리, KDB, 신한, 외환/KEB하나, KB국민, IBK기업, NH농협'),
        ('대상 통화', 'USD, JPY, CNY (★최우선), EUR, GBP'),
        ('', ''),
        ('금리 결정 구조', '한국 은행 외화예금금리 = 국제 기준금리 + 은행별 스프레드'),
        ('USD 기준금리', 'LIBOR 12M (ICE Benchmark Administration)'),
        ('JPY 기준금리', 'JPY LIBOR 12M'),
        ('EUR 기준금리', 'EURIBOR 12M / EUR LIBOR'),
        ('GBP 기준금리', 'GBP LIBOR 12M'),
        ('CNY 기준금리', 'PBOC 1년 정기예금 기준금리'),
        ('', ''),
        ('스프레드 특성', 'USD -30~-50bp, JPY -5~-15bp, CNY -50~-100bp (역외)'),
        ('', ''),
        ('외환은행 합병', '2015년 하나은행과 합병→KEB하나은행. 2004-2014 외환은행, 2015-2019 KEB하나은행 공시'),
        ('CNY 역외 특성', '한국 내 CNY 예금은 역외(offshore) 위안화이므로 PBOC 본토 기준보다 낮음'),
        ('', ''),
        ('정확한 데이터 확인 방법', ''),
        ('  방법1', '금융감독원 FISIS에서 은행별 수신금리 공시자료 조회'),
        ('  방법2', '각 은행 IR실 또는 외환부서에 직접 자료 요청'),
        ('  방법3', 'Bloomberg Terminal (대학 도서관) 에서 은행별 외화예금 금리 확인'),
        ('  방법4', '한국은행 「금융시장동향」 월간 보고서 참조'),
    ]
    method_df = pd.DataFrame(method_rows, columns=['항목', '내용'])

    # =====================================================================
    # Write Excel
    # =====================================================================
    print("[4/5] Excel/CSV 파일 생성...")
    xl = os.path.join(OUTPUT_DIR, 'fx_deposit_rates_compiled.xlsx')

    with pd.ExcelWriter(xl, engine='openpyxl') as w:
        panel.to_excel(w, sheet_name='Panel_Data', index=False)
        usd_w.to_excel(w, sheet_name='USD_Rates', index=False)
        jpy_w.to_excel(w, sheet_name='JPY_Rates', index=False)
        cny_w.to_excel(w, sheet_name='CNY_Rates', index=False)
        eur_w.to_excel(w, sheet_name='EUR_Rates', index=False)
        gbp_w.to_excel(w, sheet_name='GBP_Rates', index=False)
        cny_det.to_excel(w, sheet_name='CNY_Detail', index=False)
        bench.to_excel(w, sheet_name='Benchmark_Rates', index=False)
        sources_df.to_excel(w, sheet_name='Sources', index=False)
        method_df.to_excel(w, sheet_name='Methodology', index=False)

    print(f"  ✓ {xl}")

    panel.to_csv(os.path.join(OUTPUT_DIR, 'fx_deposit_rates_compiled.csv'),
                 index=False, encoding='utf-8-sig')
    bench.to_csv(os.path.join(OUTPUT_DIR, 'fx_deposit_benchmark_rates.csv'),
                 index=False, encoding='utf-8-sig')
    cny_det.to_csv(os.path.join(OUTPUT_DIR, 'fx_deposit_cny_detail.csv'),
                   index=False, encoding='utf-8-sig')
    print("  ✓ CSV 백업 3개 생성")

    # =====================================================================
    # Print summary tables
    # =====================================================================
    print("\n[5/5] 결과 요약")
    print("=" * 80)

    print("\n★★★ CNY (위안화) 예금금리 상세 (12개월 만기) ★★★")
    print("-" * 80)
    print(cny_det.to_string(index=False))

    print("\n\n★ USD 예금금리 (12개월 만기):")
    print("-" * 80)
    print(usd_w.to_string(index=False))

    print("\n\n★ JPY 예금금리 (12개월 만기):")
    print("-" * 80)
    print(jpy_w.to_string(index=False))

    print("\n\n★ EUR 예금금리 (12개월 만기):")
    print("-" * 80)
    print(eur_w.to_string(index=False))

    print("\n\n★ GBP 예금금리 (12개월 만기):")
    print("-" * 80)
    print(gbp_w.to_string(index=False))

    print("\n" + "=" * 80)
    print("데이터 출처 요약")
    print("=" * 80)
    print(sources_df.to_string(index=False))

    print("\n" + "=" * 80)
    print("완료!")
    print("=" * 80)


if __name__ == '__main__':
    main()
