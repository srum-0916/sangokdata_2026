import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# 기본 설정
# ============================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

# 그래프 아래 설명 문구는 여기에서 쉽게 수정할 수 있습니다.
INSIGHT_TEXT_1 = (
    "장르별 영화 편수를 비교해 어떤 장르의 영화가 이 기간 박스오피스 TOP 10에 더 많이 등장했는지 확인할 수 있습니다."
)


# ============================================================
# 데이터 불러오기 / 전처리
# ============================================================
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름에 혹시 들어 있을 수 있는 BOM/공백 제거
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()

    # 개봉일을 실제 날짜(datetime)로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str).str.replace(r"\.0$", "", regex=True),
            format="%Y%m%d",
            errors="coerce",
        )

    # 장르가 "액션|스릴러"처럼 여러 개인 경우 첫 번째 장르만 사용
    def first_genre(value):
        if pd.isna(value):
            return "정보 없음"

        text = str(value).strip()
        if not text:
            return "정보 없음"

        return text.split("|")[0].strip() or "정보 없음"

    df["genre_main"] = df["genre"].apply(first_genre)

    # 수치형 열 정리
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ============================================================
# 그래프 1 : 장르별 영화 편수 도넛 그래프
# ============================================================
def render_graph_1(df):
    st.subheader("1. 장르별 영화 편수")

    genre_counts = (
        df["genre_main"]
        .value_counts()
        .rename_axis("장르")
        .reset_index(name="영화 편수")
    )

    fig = px.pie(
        genre_counts,
        names="장르",
        values="영화 편수",
        hole=0.48,
        title="장르별 영화 편수 분포",
    )

    fig.update_traces(
        textinfo="label+percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value:,}편<br>"
            "비율: %{percent}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        legend_title_text="장르",
        margin=dict(l=20, r=20, t=70, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_1}")


# ============================================================
# 앱 화면
# ============================================================
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 TOP 10에 진입한 영화들의 분포와 변수 사이의 관계를 살펴봅니다.")

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
