import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

# 그래프 아래 설명 문구는 여기에서 쉽게 수정할 수 있습니다.
INSIGHT_TEXT_1 = (
    "선택한 영화의 날짜별 일관객 변화를 통해 관객이 많이 늘거나 줄어든 시점을 확인할 수 있습니다."
)


# ============================================================
# 데이터 불러오기 / 전처리
# ============================================================
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 혹시 CSV 첫 열에 BOM이 포함되어 있어도 안전하게 처리
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()

    # 20250901 같은 8자리 숫자형 날짜를 실제 날짜(datetime)로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str).str.replace(r"\.0$", "", regex=True),
        format="%Y%m%d",
        errors="coerce",
    )

    # 그래프에 사용할 수치 열을 숫자로 정리
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 영화명 앞뒤 공백 제거
    df["영화명"] = df["영화명"].astype(str).str.strip()

    # 날짜 변환 실패 행 제거 후 날짜순 정렬
    df = df.dropna(subset=["날짜", "영화명", "일관객"]).sort_values("날짜")

    return df


# ============================================================
# 그래프 1 : 영화별 날짜에 따른 일관객 변화
# ============================================================
def render_graph_1(df):
    st.subheader("1. 영화별 날짜에 따른 일관객 변화")

    movie_list = sorted(df["영화명"].dropna().unique())

    selected_movie = st.selectbox(
        "영화를 선택하세요",
        movie_list,
        key="graph1_movie",
    )

    movie_df = (
        df.loc[df["영화명"] == selected_movie, ["날짜", "일관객"]]
        .groupby("날짜", as_index=False)["일관객"]
        .sum()
        .sort_values("날짜")
    )

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{selected_movie} - 날짜별 일관객 변화",
        labels={
            "날짜": "날짜",
            "일관객": "일관객 수",
        },
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "일관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="날짜",
        yaxis_title="일관객 수",
        yaxis_tickformat=",",
        margin=dict(l=20, r=20, t=70, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_1}")


# ============================================================
# 앱 화면
# ============================================================
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("1년치 일별 박스오피스 데이터를 시간의 흐름에 따라 살펴봅니다.")

try:
    data = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결이나 데이터 주소를 확인해 주세요.")
    st.exception(e)
    st.stop()

# ------------------------------------------------------------
# 그래프 구역 1
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_1(data)

st.divider()

# ------------------------------------------------------------
# 그래프 구역 2
# 앞으로 새 그래프를 추가할 때 아래처럼 함수를 만들어 연결하면 됩니다.
#
# with st.container(border=True):
#     render_graph_2(data)
# ------------------------------------------------------------

# ------------------------------------------------------------
# 그래프 구역 3
#
# with st.container(border=True):
#     render_graph_3(data)
# ------------------------------------------------------------
