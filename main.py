import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# ----------------------------------------------------
# 1. 데이터 불러오기 함수 (1시간 동안 결과 기억하기)
# ----------------------------------------------------
# ttl=3600은 3600초(1시간) 동안 데이터를 저장해두고 재사용한다는 뜻이에요.
@st.cache_data(ttl=3600)
def get_boxoffice_data(target_date, api_key):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    try:
        # API 서버에 데이터를 요청해요
        response = requests.get(url, params=params)
        
        # 상태 코드가 200(정상)이 아니면 에러 메시지 반환
        if response.status_code != 200:
            return None, "서버와 연결하는 데 문제가 발생했어요. 잠시 후 다시 시도해 주세요."
            
        data = response.json()
        
        # 1. 인증키 오류 등 KOBIS 자체에서 보내는 에러 상자(faultInfo)가 있는지 확인
        if "faultInfo" in data:
            return None, f"API 요청에 문제가 있어요. 인증키를 확인해 주세요. (사유: {data['faultInfo'].get('message', '알 수 없는 오류')})"
            
        # 2. 결과 데이터가 정상적으로 들어있는지 확인
        if "boxOfficeResult" not in data or "dailyBoxOfficeList" not in data["boxOfficeResult"]:
            return None, "데이터 형식이 예상과 달라요. KOBIS API에 변경이 있는지 확인이 필요해요."
            
        movie_list = data["boxOfficeResult"]["dailyBoxOfficeList"]
        
        # 3. 영화 목록이 비어있는지(아직 집계 전이거나 쉬는 날 등) 확인
        if not movie_list:
            return None, "선택한 날짜의 박스오피스 데이터가 아직 없어요. 나중에 다시 확인해 주세요!"
            
        # 모든 검사를 무사히 통과했다면 데이터를 판다스(Pandas) 표로 만들어서 돌려줍니다
        return pd.DataFrame(movie_list), None
        
    except Exception as e:
        return None, f"데이터를 가져오는 중 알 수 없는 오류가 발생했어요: {str(e)}"

# ----------------------------------------------------
# 2. 화면 구성하기 (Streamlit 앱 메인)
# ----------------------------------------------------
def main():
    # 웹페이지 탭 이름과 아이콘 설정
    st.set_page_config(page_title="어제의 박스오피스", page_icon="🍿")
    
    st.title("🍿 어제의 박스오피스 순위")
    
    # 한국 시간 기준으로 '어제' 날짜 계산하기
    # 배포 서버 시계가 UTC(외국 시간)일 수 있으므로 pytz로 한국 시간을 명시해 줘요.
    kst = pytz.timezone('Asia/Seoul')
    yesterday = datetime.now(kst) - timedelta(days=1)
    target_dt_str = yesterday.strftime("%Y%m%d") # 예: 20231025
    
    st.write(f"📅 **조회 날짜:** {yesterday.strftime('%Y년 %m월 %d일')}")
    
    # 비밀 금고(secrets)에서 API 키 불러오기
    # 코드에 직접 쓰지 않아 안전해요!
    try:
        api_key = st.secrets["KOBIS_KEY"]
    except KeyError:
        st.error("비밀 금고(secrets)에 'KOBIS_KEY'가 설정되지 않았어요. Streamlit Cloud 설정에서 확인해 주세요!")
        return

    # 데이터 가져오기 실행
    with st.spinner('데이터를 불러오는 중입니다...'):
        df, error_msg = get_boxoffice_data(target_dt_str, api_key)
        
    # 만약 에러 메시지가 있다면 화면에 띄우고 멈춤
    if error_msg:
        st.warning(error_msg)
        return
        
    # ----------------------------------------------------
    # 3. 데이터 가공하기 (글자를 숫자로 바꾸기)
    # ----------------------------------------------------
    # API에서 넘어온 숫자들이 사실은 '글자' 형태라서, 그래프나 정렬에 쓰려면 진짜 '숫자'로 바꿔줘야 해요.
    df['rank'] = pd.to_numeric(df['rank'])
    df['audiCnt'] = pd.to_numeric(df['audiCnt'])
    df['audiAcc'] = pd.to_numeric(df['audiAcc'])
    df['scrnCnt'] = pd.to_numeric(df['scrnCnt'])
    
    # 순위대로 예쁘게 정렬 (혹시 모를 뒤섞임 방지)
    df = df.sort_values('rank')
    
    st.divider() # 가로줄 긋기
    
    # ----------------------------------------------------
    # 4. 1위 영화 지표 카드 (크게 보여주기)
    # ----------------------------------------------------
    top1_movie = df.iloc[0] # 순위 1등 영화 뽑기
    
    st.subheader(f"🥇 1위: {top1_movie['movieNm']}")
    
    # 화면을 3칸으로 나누어서 카드 배치
    col1, col2, col3 = st.columns(3)
    
    # 관객수 등에 천 단위 콤마(,)를 넣어서 보기 좋게 만들어요 (예: 1000 -> 1,000)
    with col1:
        st.metric(label="당일 관객수", value=f"{top1_movie['audiCnt']:,}명")
    with col2:
        st.metric(label="누적 관객수", value=f"{top1_movie['audiAcc']:,}명")
    with col3:
        st.metric(label="스크린 수", value=f"{top1_movie['scrnCnt']:,}개")
        
    st.divider()

    # ----------------------------------------------------
    # 5. 관객수 상위 5편 막대그래프
    # ----------------------------------------------------
    st.subheader("📊 상위 5편 일일 관객수 비교")
    # 상위 5개 데이터만 잘라냅니다
    top5_df = df.head(5)
    
    # 그래프를 그리기 위해 영화 제목을 인덱스(기준점)로 설정하고 관객수만 남겨요
    chart_data = top5_df.set_index('movieNm')['audiCnt']
    
    # 스트림릿에 기본 내장된 막대그래프 그리기
    st.bar_chart(chart_data)
    
    st.divider()

    # ----------------------------------------------------
    # 6. 전체 순위표 보여주기
    # ----------------------------------------------------
    st.subheader("📋 전체 박스오피스 순위표")
    
    # 필요한 열(컬럼)만 골라내고, 이름도 한국어로 예쁘게 바꿔줘요
    display_df = df[['rank', 'movieNm', 'openDt', 'audiCnt', 'audiAcc', 'scrnCnt']].copy()
    display_df.columns = ['순위', '영화명', '개봉일', '관객수', '누적관객수', '스크린수']
    
    # 숫자에 콤마 적용 등 표를 더 예쁘게 표시하기 위해 포맷을 지정해요
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True, # 맨 앞의 쓸데없는 번호(인덱스) 숨기기
        column_config={
            "순위": st.column_config.NumberColumn(format="%d위"),
            "관객수": st.column_config.NumberColumn(format="%d 명"),
            "누적관객수": st.column_config.NumberColumn(format="%d 명"),
            "스크린수": st.column_config.NumberColumn(format="%d 개")
        }
    )

if __name__ == "__main__":
    main()
