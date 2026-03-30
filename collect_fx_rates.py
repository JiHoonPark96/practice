# -*- coding: utf-8 -*-
"""
한국 주요 은행 외화예금금리 데이터 수집 스크립트
=================================================
LIBOR 및 PBOC 데이터 기반으로 외화예금금리 추정

출력:
- figure12_fx_deposit_rates.png (Figure 12 스타일)
- figure_6banks_fx_rates.png (6개 은행 전체)
- figure_cny_rates.png (CNY 집중 분석)
- korean_banks_fx_rates_data.xlsx (전체 데이터)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

print("=" * 70)
print("한국 주요 은행 외화예금금리 데이터 수집")
print("=" * 70)

# =============================================================================
# 1. 공식 LIBOR 데이터 (FRED 출처)
# =============================================================================
def create_official_libor_data():
    """
    공식 LIBOR 데이터 (ICE Benchmark Administration 발표 기준)
    출처: FRED - Federal Reserve Economic Data
    """
    official_libor = pd.DataFrame({
        'Year': list(range(2004, 2020)),
        
        # USD 3-Month LIBOR (연간 평균, %)
        # 출처: FRED USD3MTD156N
        'USD_LIBOR_3M': [
            1.62, 3.56, 5.19, 5.30, 2.92, 0.69, 0.34, 0.34,
            0.43, 0.27, 0.23, 0.32, 0.74, 1.26, 2.31, 2.33
        ],
        
        # JPY 3-Month LIBOR (연간 평균, %)
        # 출처: FRED JPY3MTD156N  
        'JPY_LIBOR_3M': [
            0.05, 0.06, 0.30, 0.73, 0.85, 0.47, 0.24, 0.20,
            0.19, 0.15, 0.13, 0.09, 0.02, 0.02, 0.03, 0.01
        ],
        
        # EUR 3-Month LIBOR/EURIBOR (연간 평균, %)
        # 출처: FRED EUR3MTD156N
        'EUR_LIBOR_3M': [
            2.11, 2.18, 3.08, 4.28, 4.63, 1.22, 0.81, 1.39,
            0.57, 0.22, 0.21, 0.02, -0.26, -0.33, -0.32, -0.36
        ],
        
        # GBP 3-Month LIBOR (연간 평균, %)
        # 출처: FRED GBP3MTD156N
        'GBP_LIBOR_3M': [
            4.57, 4.70, 4.80, 5.95, 5.49, 1.22, 0.69, 0.87,
            0.84, 0.51, 0.54, 0.57, 0.50, 0.36, 0.72, 0.81
        ],
    })
    
    return official_libor

# =============================================================================
# 2. 중국 PBOC 기준금리
# =============================================================================
def get_china_deposit_rates():
    """
    중국 예금 기준금리 데이터 (PBOC 공식 데이터)
    출처: 중국인민은행 (People's Bank of China)
    """
    china_rates = pd.DataFrame({
        'Year': [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 
                 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
        'CNY_1Y_DEPOSIT': [
            2.25, 2.25, 2.52, 3.87, 2.25, 2.25, 2.75, 3.50,
            3.00, 3.00, 2.75, 1.50, 1.50, 1.50, 1.50, 1.50
        ],
        'Source': ['PBOC'] * 16
    })
    return china_rates

# =============================================================================
# 3. 한국 은행 외화예금금리 추정
# =============================================================================
def estimate_korean_bank_fx_rates(libor_df, china_df):
    """
    LIBOR 기반 한국 은행 외화예금금리 추정
    추정 방법: 외화예금금리 ≈ LIBOR + 스프레드
    """
    
    banks = {
        '우리은행': {'spread': 0.15, 'term': '3개월 정기예금'},
        '산업은행(IBK)': {'spread': 0.20, 'term': '3개월 정기예금'},
        '신한은행': {'spread': 0.15, 'term': '12개월 정기예금'},
        '외환은행(KEB)': {'spread': 0.20, 'term': '보통예금'},
        '국민은행': {'spread': 0.15, 'term': '3개월 정기예금'},
        '하나은행': {'spread': 0.18, 'term': '3개월 정기예금'},
    }
    
    all_bank_data = []
    
    for bank_name, config in banks.items():
        spread = config['spread']
        term = config['term']
        
        for _, row in libor_df.iterrows():
            year = int(row['Year'])
            
            # USD
            usd = row.get('USD_LIBOR_3M', np.nan)
            if pd.notna(usd):
                usd = max(0.05, usd + spread)
            
            # JPY
            jpy = row.get('JPY_LIBOR_3M', np.nan)
            if pd.notna(jpy):
                jpy = max(0.01, jpy + spread * 0.5)
            
            # EUR
            eur = row.get('EUR_LIBOR_3M', np.nan)
            if pd.notna(eur):
                eur = max(0.01, eur + spread)
            
            # GBP
            gbp = row.get('GBP_LIBOR_3M', np.nan)
            if pd.notna(gbp):
                gbp = max(0.05, gbp + spread)
            
            # CNY
            cny_row = china_df[china_df['Year'] == year]
            if len(cny_row) > 0:
                cny = max(0.5, cny_row['CNY_1Y_DEPOSIT'].values[0] - 0.4 + (spread * 0.5))
            else:
                cny = np.nan
            
            all_bank_data.append({
                'Year': year,
                'Bank': bank_name,
                'Term': term,
                'USD': round(usd, 2) if pd.notna(usd) else np.nan,
                'JPY': round(jpy, 2) if pd.notna(jpy) else np.nan,
                'EUR': round(eur, 2) if pd.notna(eur) else np.nan,
                'GBP': round(gbp, 2) if pd.notna(gbp) else np.nan,
                'CNY': round(cny, 2) if pd.notna(cny) else np.nan,
            })
    
    return pd.DataFrame(all_bank_data)

# =============================================================================
# 4. Long Format 변환
# =============================================================================
def to_long_format(df):
    """Wide -> Long format 변환"""
    currencies = ['USD', 'JPY', 'EUR', 'GBP', 'CNY']
    long_list = []
    
    for _, row in df.iterrows():
        for curr in currencies:
            if curr in df.columns and pd.notna(row[curr]):
                long_list.append({
                    'Year': row['Year'],
                    'Bank': row['Bank'],
                    'Term': row['Term'],
                    'Currency': curr,
                    'Rate': row[curr]
                })
    return pd.DataFrame(long_list)

# =============================================================================
# 5. Figure 12 스타일 그래프
# =============================================================================
def create_figure12(data_long, output_file='figure12_fx_deposit_rates.png'):
    """Figure 12: Korean Banks' Deposit Rates on Foreign Currencies"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    colors = {
        'USD': '#1f77b4', 'JPY': '#ff7f0e', 'EUR': '#2ca02c',
        'GBP': '#d62728', 'CNY': '#9467bd'
    }
    
    panels = [
        ('우리은행', '(a) Woori Bank 3-month Term Deposit Rate', axes[0,0]),
        ('산업은행(IBK)', '(b) Industrial Bank of Korea (IBK) 3-month\n     Term Deposit Rate', axes[0,1]),
        ('신한은행', '(c) Shinhan Bank 12-month Term Deposit Rate', axes[1,0]),
        ('외환은행(KEB)', '(d) Korean Exchange Bank (KEB) Ordinary\n     Deposit Rate', axes[1,1])
    ]
    
    for bank_name, title, ax in panels:
        bank_data = data_long[data_long['Bank'] == bank_name]
        
        if len(bank_data) == 0:
            ax.text(0.5, 0.5, f'{bank_name}\nNo Data', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12)
            ax.set_title(title, fontsize=10, fontweight='bold')
            continue
        
        pivot = bank_data.pivot(index='Year', columns='Currency', values='Rate')
        
        for curr in ['USD', 'JPY', 'EUR', 'GBP', 'CNY']:
            if curr in pivot.columns:
                valid = pivot[curr].dropna()
                if len(valid) > 0:
                    ax.plot(valid.index, valid.values,
                           marker='o', markersize=4, linewidth=1.8,
                           label=curr, color=colors[curr])
        
        ax.set_xlabel('Year', fontsize=9)
        ax.set_ylabel('Deposit Rate (%)', fontsize=9)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.legend(loc='upper right', ncol=2, fontsize=8, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(bottom=0)
        ax.tick_params(axis='both', labelsize=8)
    
    fig.suptitle("Figure 12: Korean Banks' Deposit Rates on Foreign Currencies",
                fontsize=14, fontweight='bold', y=1.02)
    
    fig.text(0.5, -0.02,
            "Notes: Estimated based on LIBOR + spread. Source: FRED (LIBOR), PBOC (CNY).",
            ha='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  ✅ 저장: {output_file}")
    return fig

# =============================================================================
# 6. 6개 은행 전체 그래프
# =============================================================================
def create_6bank_figure(data_long, output_file='figure_6banks_fx_rates.png'):
    """6개 은행 전체 그래프"""
    
    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    
    colors = {
        'USD': '#1f77b4', 'JPY': '#ff7f0e', 'EUR': '#2ca02c',
        'GBP': '#d62728', 'CNY': '#9467bd'
    }
    
    banks = data_long['Bank'].unique()
    
    for idx, (bank, ax) in enumerate(zip(banks, axes.flatten())):
        bank_data = data_long[data_long['Bank'] == bank]
        if len(bank_data) == 0:
            continue
            
        pivot = bank_data.pivot(index='Year', columns='Currency', values='Rate')
        term = bank_data['Term'].iloc[0]
        
        for curr in ['USD', 'JPY', 'EUR', 'GBP', 'CNY']:
            if curr in pivot.columns:
                valid = pivot[curr].dropna()
                if len(valid) > 0:
                    ax.plot(valid.index, valid.values,
                           marker='o', markersize=4, linewidth=1.8,
                           label=curr, color=colors[curr])
        
        ax.set_xlabel('Year', fontsize=9)
        ax.set_ylabel('Rate (%)', fontsize=9)
        ax.set_title(f'{bank}\n({term})', fontsize=10, fontweight='bold')
        ax.legend(loc='upper right', ncol=2, fontsize=7)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)
    
    fig.suptitle("Korean Banks' Foreign Currency Deposit Rates (2004-2019)",
                fontsize=14, fontweight='bold', y=1.01)
    
    plt.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 저장: {output_file}")
    return fig

# =============================================================================
# 7. CNY 집중 분석 그래프
# =============================================================================
def create_cny_chart(data_long, china_df, output_file='figure_cny_rates.png'):
    """CNY 예금금리 은행별 비교"""
    
    cny = data_long[data_long['Currency'] == 'CNY'].dropna(subset=['Rate'])
    
    if len(cny) == 0:
        print("  ❌ CNY 데이터 없음")
        return None
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    bank_colors = plt.cm.Set1(np.linspace(0, 1, len(cny['Bank'].unique())))
    
    for idx, bank in enumerate(cny['Bank'].unique()):
        bank_cny = cny[cny['Bank'] == bank].sort_values('Year')
        term = bank_cny['Term'].iloc[0]
        
        ax.plot(bank_cny['Year'], bank_cny['Rate'],
               marker='o', markersize=8, linewidth=2.5,
               label=f'{bank} ({term})', color=bank_colors[idx])
    
    # PBOC 기준금리
    ax.plot(china_df['Year'], china_df['CNY_1Y_DEPOSIT'],
           marker='s', markersize=6, linewidth=2, linestyle='--',
           label='PBOC 1Y Deposit Rate (Reference)', color='black', alpha=0.7)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('CNY Deposit Rate (%)', fontsize=12)
    ax.set_title('CNY (Chinese Yuan) Deposit Rates by Korean Banks\nvs PBOC Benchmark Rate',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.4, linestyle='--')
    ax.set_ylim(bottom=0)
    
    plt.tight_layout()
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✅ 저장: {output_file}")
    return fig

# =============================================================================
# 8. 엑셀 저장
# =============================================================================
def save_to_excel(wide_df, long_df, libor_df, china_df, filename='korean_banks_fx_rates_data.xlsx'):
    """모든 데이터를 엑셀로 저장"""
    
    # 요약 통계
    summary = long_df.groupby(['Bank', 'Currency'])['Rate'].agg(
        ['mean', 'std', 'min', 'max', 'count']
    ).round(3)
    summary.columns = ['평균(%)', '표준편차', '최소', '최대', '관측치수']
    
    # 연도별 평균
    yearly = long_df.groupby(['Year', 'Currency'])['Rate'].mean().unstack().round(3)
    
    # CNY 테이블
    cny = long_df[long_df['Currency']=='CNY'].pivot_table(
        index='Year', columns='Bank', values='Rate'
    ).round(3)
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        wide_df.to_excel(writer, sheet_name='Bank_FX_Rates', index=False)
        summary.to_excel(writer, sheet_name='Summary_Stats')
        yearly.to_excel(writer, sheet_name='Yearly_Average')
        cny.to_excel(writer, sheet_name='CNY_by_Bank')
        libor_df.to_excel(writer, sheet_name='LIBOR_Source', index=False)
        china_df.to_excel(writer, sheet_name='China_PBOC_Rate', index=False)
        
        # 출처 정보
        sources = pd.DataFrame({
            '항목': ['데이터 기간', 'LIBOR 출처', 'CNY 출처', '추정 방법', '대상 은행', '통화'],
            '내용': [
                '2004-2019년',
                'FRED (Federal Reserve Economic Data) - ICE LIBOR',
                'PBOC (People\'s Bank of China) 1년 정기예금 기준금리',
                '한국 은행 외화예금금리 ≈ LIBOR + 스프레드 (0.15~0.20%p)',
                '우리은행, 산업은행(IBK), 신한은행, 외환은행(KEB), 국민은행, 하나은행',
                'USD, JPY, EUR, GBP, CNY'
            ]
        })
        sources.to_excel(writer, sheet_name='Sources', index=False)
    
    print(f"  ✅ 저장: {filename}")

# =============================================================================
# 9. 메인 실행
# =============================================================================
if __name__ == "__main__":
    print("\n[1/5] LIBOR 데이터 로드 중...")
    libor_df = create_official_libor_data()
    print(f"     LIBOR 데이터: {len(libor_df)}년 (2004-2019)")
    
    print("\n[2/5] 중국 PBOC 금리 로드 중...")
    china_df = get_china_deposit_rates()
    print(f"     PBOC 데이터: {len(china_df)}년")
    
    print("\n[3/5] 한국 은행 외화예금금리 추정 중...")
    estimated_rates = estimate_korean_bank_fx_rates(libor_df, china_df)
    rates_long = to_long_format(estimated_rates)
    banks = estimated_rates['Bank'].unique().tolist()
    print(f"     은행: {len(banks)}개")
    print(f"     - {', '.join(banks)}")
    print(f"     데이터: {len(estimated_rates)}행 (Wide), {len(rates_long)}행 (Long)")
    
    print("\n[4/5] 그래프 생성 중...")
    create_figure12(rates_long)
    create_6bank_figure(rates_long)
    create_cny_chart(rates_long, china_df)
    
    print("\n[5/5] 엑셀 저장 중...")
    save_to_excel(estimated_rates, rates_long, libor_df, china_df)
    
    # 결과 요약
    print("\n" + "=" * 70)
    print("✅ 완료!")
    print("=" * 70)
    
    output_files = [
        ('figure12_fx_deposit_rates.png', 'Figure 12 스타일 (4패널)'),
        ('figure_6banks_fx_rates.png', '6개 은행 전체'),
        ('figure_cny_rates.png', 'CNY 집중 분석'),
        ('korean_banks_fx_rates_data.xlsx', '전체 데이터 엑셀')
    ]
    
    print("\n📁 생성된 파일:")
    for fname, desc in output_files:
        if os.path.exists(fname):
            size = os.path.getsize(fname) / 1024
            print(f"   ✅ {fname} ({size:.1f} KB) - {desc}")
        else:
            print(f"   ❌ {fname} - 생성 실패")
    
    # 데이터 미리보기
    print("\n📊 데이터 미리보기 (우리은행):")
    print("-" * 60)
    woori = estimated_rates[estimated_rates['Bank'] == '우리은행']
    print(woori.to_string(index=False))
    
    print("\n📊 CNY 금리 은행별 비교:")
    print("-" * 60)
    cny_pivot = rates_long[rates_long['Currency']=='CNY'].pivot_table(
        index='Year', columns='Bank', values='Rate'
    ).round(2)
    print(cny_pivot.to_string())
    
    print("\n" + "=" * 70)
    print("데이터 출처:")
    print("  - LIBOR: FRED (Federal Reserve Economic Data)")
    print("  - CNY: PBOC (People's Bank of China)")
    print("  - 추정 방법: 외화예금금리 ≈ LIBOR + 스프레드")
    print("=" * 70)
