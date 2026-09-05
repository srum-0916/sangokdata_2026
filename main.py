import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# ----------------------------------------------------
# 1. 앱 페이지 설정 및 테마 (화사하고 예쁜 화이트 톤!)
# ----------------------------------------------------
st.set_page_config(page_title="BoxOffice Pro", page_icon="🎬", layout="wide")

# 세련된 라이트 모드 CSS 주입
st.markdown("""
    <style>
    /* 전체 배경 하얀색/아주 연한 회색으로 깔끔하게 */
    .stApp { background-color: #F8F9FA; }
    
    /* 폰트 스타일 (기본 텍스트 색상을 진한 회색으로) */
    h1, h2, h3 { color: #111827 !important; font-family: 'Pretendard', sans-serif; font-weight: 800; }
    p, span, label { color: #374151 !important; }
    
    /* 1위 영화 지표 카드 스타일 (토스 느낌의 파란색 포인트) */
    div[data-testid="stMetricValue"] { color: #3182F6 !important; font-weight: 800 !important; }
    
    /* 깔끔한 커스텀 테이블 디자인 */
    .custom-table { 
        width: 100%; border-collapse: collapse; background-color: #FFFFFF; 
        border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-top: 1rem; margin-bottom: 2rem; font-size: 0.95rem;
    }
    .custom-table th { background-color: #F1F5F9; color: #475569; padding: 14px; text-align: center; font-weight: 700; border-bottom: 2px solid #E2E8F0; }
    .custom-table td { padding: 14px; text-align: center; border-bottom: 1px solid #F1F5F9; color: #1E293B; }
    .custom-table tr:hover td { background-color: #F8FAFC; }
    .movie-title { text-align: left !important; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 데이터 처리 및 API 연동 (1시간 기억하기)
# ----------------------------------------------------
@st.cache_data(ttl=3600)
def get_boxoffice_data(target_date, api_key):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    try:
        response = requests.get(url, params={"key": api_key, "targetDt": target_date})
        if response.status_code != 200:
            return None, "서버 연결에 실패했습니다. 잠시 후 다시 시도해 주세요."
        
        data = response.json()
        if "faultInfo" in data:
            return None, f"API 요청 오류가 발생했어요. 인증키를 확인해 주세요. ({data['faultInfo'].get('message')})"
            
        movie_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        if not movie_list:
            return None, "empty" # 목록이 비어있을 때
            
        return pd.DataFrame(movie_list), None
    except Exception as e:
        return None, f"오류가 발생했어요: {str(e)}"

def format_trend(val):
    """순위 증감 화살표 예쁘게 포맷팅"""
    try:
        n = int(val)
        if n > 0: return f"<span style='color:#EF4444; font-weight:600;'>▲ {n}</span>"
        if n < 0: return f"<span style='color:#3B82F6; font-weight:600;'>▼ {abs(n)}</span>"
        return "<span style='color:#94A3B8;'>-</span>"
    except: return val

# ----------------------------------------------------
# 3. 메인 앱 레이아웃
# ----------------------------------------------------
def main():
    st.title("🎬 오늘의 박스오피스")
    st.write("달력에서 날짜를 골라 한국 영화관의 생생한 트렌드를 확인해 보세요.")
    st.divider()

    # 한국 시간 기준 어제 날짜 계산
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    yesterday_kst = now_kst - timedelta(days=1)
    
    # 사이드바: 달력에서 날짜 선택
    with st.sidebar:
        st.header("🗓️ 날짜 선택")
        selected_date = st.date_input(
            "조회할 날짜를 골라주세요",
            value=yesterday_kst,
            max_value=yesterday_kst, # 오늘 날짜는 선택 못 하게 막음
            help="오늘 데이터는 아직 집계 중이라 어제까지만 볼 수 있어요!"
        )
        target_dt_str = selected_date.strftime("%Y%m%d")
        st.info(f"선택한 날짜:\n**{selected_date.strftime('%Y년 %m월 %d일')}**")

    # API 키 확인
    if "KOBIS_KEY" not in st.secrets:
        st.error("비밀 금고(secrets)에 'KOBIS_KEY'가 없어요. 설정을 확인해 주세요!")
        return
    
    api_key = st.secrets["KOBIS_KEY"]

    # 데이터 호출
    with st.spinner('데이터를 예쁘게 정리하는 중입니다...'):
        df, error = get_boxoffice_data(target_dt_str, api_key)

    # 에러 및 빈 데이터 처리
    if error == "empty":
        st.warning(f"💡 {selected_date.strftime('%Y년 %m월 %d일')}은 아직 집계 전입니다. 다른 날짜를 선택해 주세요!")
        return
    elif error:
        st.error(f"❌ {error}")
        return

    # ----------------------------------------------------
    # 4. 데이터 가공 (숫자 변환, 화살표, 트로피)
    # ----------------------------------------------------
    df['rank'] = pd.to_numeric(df['rank'])
    df['audiCnt'] = pd.to_numeric(df['audiCnt'])
    df['audiAcc'] = pd.to_numeric(df['audiAcc'])
    df['scrnCnt'] = pd.to_numeric(df['scrnCnt'])
    
    # 🏆 100만 돌파 영화에 트로피 이모지 붙이기
    df['movieNm'] = df.apply(
        lambda x: f"🏆 {x['movieNm']}" if x['audiAcc'] >= 1000000 else x['movieNm'], 
        axis=1
    )
    
    # 🔺🔻 순위 변동 화살표 생성 (빨간색 위, 파란색 아래)
    df['rankTrend'] = df['rankInten'].apply(format_trend)

    # ----------------------------------------------------
    # 5. 시각화 1: 1위 영화 하이라이트
    # ----------------------------------------------------
    top1 = df.iloc[0]
    st.subheader(f"🥇 영광의 1위: {top1['movieNm']}")
    
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("일일 관객수", f"{top1['audiCnt']:,} 명")
    with m2: st.metric("누적 관객수", f"{top1['audiAcc']:,} 명")
    with m3: st.metric("스크린 수", f"{top1['scrnCnt']:,} 개")
    
    st.divider()

    # ----------------------------------------------------
    # 6. 시각화 2: 관객수 상위 5편 막대그래프 (파란색)
    # ----------------------------------------------------
    st.subheader("📊 상위 5편 관객수 비교")
    top5 = df.head(5)
    # 촌스러운 초록색 대신 세련된 파란색(#3182F6) 적용
    st.bar_chart(top5.set_index('movieNm')['audiCnt'], color="#3182F6")
    
    st.divider()

    # ----------------------------------------------------
    # 7. 전체 순위표 (커스텀 HTML로 예쁘게 랜더링)
    # ----------------------------------------------------
    st.subheader("📋 전체 박스오피스 순위표")
    
    # 표에 보여줄 데이터만 깔끔하게 정리
    display_df = df[['rank', 'rankTrend', 'movieNm', 'openDt', 'audiCnt', 'audiAcc', 'scrnCnt']].copy()
    
    # 숫자에 천 단위 콤마 찍기
    display_df['audiCnt'] = display_df['audiCnt'].apply(lambda x: f"{x:,.0f}")
    display_df['audiAcc'] = display_df['audiAcc'].apply(lambda x: f"{x:,.0f}")
    display_df['scrnCnt'] = display_df['scrnCnt'].apply(lambda x: f"{x:,.0f}")
    
    display_df.columns = ['순위', '변동', '영화명', '개봉일', '일일관객(명)', '누적관객(명)', '스크린수(개)']
    
    # 영화명 컬럼만 왼쪽 정렬을 위해 클래스 추가
    display_df['영화명'] = display_df['영화명'].apply(lambda x: f"<div class='movie-title'>{x}</div>")
    
    # 스트림릿 기본 표 대신, 직접 만든 예쁜 CSS가 적용된 HTML 표 출력
    html_table = display_df.to_html(escape=False, index=False, classes='custom-table')
    st.write(html_table, unsafe_allow_html=True)
    
    st.caption("✨ 팁: 영화 이름 앞의 🏆 이모지는 누적 관객 100만 명을 돌파한 흥행작을 의미해요!")

if __name__ == "__main__":
    main()
