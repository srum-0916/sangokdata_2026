import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# ----------------------------------------------------
# 1. 앱 페이지 설정 및 테마 (디자인 예쁘게!)
# ----------------------------------------------------
st.set_page_config(page_title="BoxOffice Pro", page_icon="🎬", layout="wide")

# 전문가 느낌의 CSS 주입
st.markdown("""
    <style>
    /* 메인 배경 및 폰트 */
    .stApp { background-color: #0F172A; }
    h1, h2, h3 { color: #F8FAF7 !important; font-family: 'Pretendard', sans-serif; }
    p, span, label { color: #CBD5E1 !important; }
    
    /* 지표 카드 스타일 */
    div[data-testid="stMetricValue"] { color: #10B981 !important; font-weight: 700 !important; }
    
    /* 버튼 및 입력창 스타일 */
    .stButton>button { 
        background-color: #10B981; color: white; border-radius: 10px; border: none;
        padding: 0.5rem 2rem; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #059669; transform: translateY(-2px); }
    
    /* 테이블 스타일 커스텀 */
    .stDataFrame { border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 데이터 처리 및 API 연동
# ----------------------------------------------------
@st.cache_data(ttl=3600)
def get_boxoffice_data(target_date, api_key):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    try:
        response = requests.get(url, params={"key": api_key, "targetDt": target_date})
        if response.status_code != 200:
            return None, "서버 연결에 실패했습니다. 네트워크를 확인해주세요."
        
        data = response.json()
        if "faultInfo" in data:
            return None, f"API 키 오류: {data['faultInfo'].get('message')}"
            
        movie_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        if not movie_list:
            return None, "empty" # 목록이 비어있을 때
            
        return pd.DataFrame(movie_list), None
    except Exception as e:
        return None, f"오류 발생: {str(e)}"

def format_trend(val):
    """순위 증감 화살표 포맷팅"""
    try:
        n = int(val)
        if n > 0: return f"<span style='color:#EF4444'>▲ {n}</span>"
        if n < 0: return f"<span style='color:#3B82F6'>▼ {abs(n)}</span>"
        return "<span style='color:#94A3B8'>-</span>"
    except: return val

# ----------------------------------------------------
# 3. 메인 앱 레이아웃
# ----------------------------------------------------
def main():
    # 헤더 섹션
    st.title("🎬 BoxOffice Pro")
    st.write("실시간 영화 데이터를 분석하는 가장 아름다운 방법")
    st.divider()

    # 사이드바: 날짜 선택 (한국 시간 기준)
    kst = pytz.timezone('Asia/Seoul')
    now_kst = datetime.now(kst)
    yesterday_kst = now_kst - timedelta(days=1)
    
    with st.sidebar:
        st.header("🗓️ 데이터 탐색")
        # 고를 수 있는 가장 늦은 날짜는 어제까지
        selected_date = st.date_input(
            "조회 날짜를 선택하세요",
            value=yesterday_kst,
            max_value=yesterday_kst,
            help="오늘 데이터는 다음 날 오전부터 집계됩니다."
        )
        target_dt_str = selected_date.strftime("%Y%m%d")
        
        st.info(f"선택일: {selected_date.strftime('%Y-%m-%d')}")

    # API 키 확인
    if "KOBIS_KEY" not in st.secrets:
        st.error("Secrets에 'KOBIS_KEY'를 설정해주세요!")
        return
    
    api_key = st.secrets["KOBIS_KEY"]

    # 데이터 호출
    df, error = get_boxoffice_data(target_dt_str, api_key)

    if error == "empty":
        st.warning(f"⚠️ {selected_date.strftime('%Y년 %m월 %d일')}은 아직 집계 전입니다.")
        return
    elif error:
        st.error(f"❌ {error}")
        return

    # ----------------------------------------------------
    # 4. 데이터 가공 (숫자 변환 및 로직 적용)
    # ----------------------------------------------------
    df['rank'] = pd.to_numeric(df['rank'])
    df['audiCnt'] = pd.to_numeric(df['audiCnt'])
    df['audiAcc'] = pd.to_numeric(df['audiAcc'])
    df['scrnCnt'] = pd.to_numeric(df['scrnCnt'])
    
    # 🏆 100만 돌파 영화에 트로피 붙이기
    df['movieNm'] = df.apply(
        lambda x: f"🏆 {x['movieNm']}" if x['audiAcc'] >= 1000000 else x['movieNm'], 
        axis=1
    )
    
    # 🔺🔻 순위 변동 화살표 생성
    df['rankTrend'] = df['rankInten'].apply(format_trend)

    # ----------------------------------------------------
    # 5. 시각화 (하이라이트 카드)
    # ----------------------------------------------------
    top1 = df.iloc[0]
    st.subheader(f"🥇 오늘의 1위: {top1['movieNm']}")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("일일 관객수", f"{top1['audiCnt']:,} 명")
    with m2: st.metric("누적 관객수", f"{top1['audiAcc']:,} 명")
    with m3: st.metric("전일대비 순위", top1['rankInten'], delta_color="normal")
    with m4: st.metric("스크린 수", f"{top1['scrnCnt']:,} 개")

    # ----------------------------------------------------
    # 6. 관객수 상위 5편 막대그래프
    # ----------------------------------------------------
    st.subheader("📊 관객수 상위 5편")
    top5 = df.head(5)
    st.bar_chart(top5.set_index('movieNm')['audiCnt'], color="#10B981")

    # ----------------------------------------------------
    # 7. 전체 순위표 (HTML 랜더링 포함)
    # ----------------------------------------------------
    st.subheader("📋 전체 박스오피스 순위")
    
    # 표시용 데이터프레임 정리
    display_df = df[['rank', 'rankTrend', 'movieNm', 'openDt', 'audiCnt', 'audiAcc', 'scrnCnt']].copy()
    display_df.columns = ['순위', '변동', '영화명', '개봉일', '일일관객', '누적관객', '스크린수']
    
    # Streamlit에서 HTML 랜더링을 위해 변동 열 스타일 적용
    st.write(
        display_df.to_html(escape=False, index=False), 
        unsafe_allow_html=True
    )
    
    st.caption("🏆 이모지는 누적 관객 100만 명을 돌파한 흥행작을 의미합니다.")

if __name__ == "__main__":
    main()
