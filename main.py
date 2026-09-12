import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
INSIGHT_TEXT_1 = "선택한 영화의 날짜별 일관객 변화를 통해 관객이 많이 늘거나 줄어든 시점을 확인할 수 있습니다."
INSIGHT_TEXT_2 = "기간 전체에서 관객이 가장 많았던 영화 5편의 흥행 흐름과 서로 다른 관객 추이를 비교할 수 있습니다."
INSIGHT_TEXT_3 = "날짜별 박스오피스 TOP 10 전체 관객 규모의 변화를 보고 특히 관객이 몰린 날을 확인할 수 있습니다."
INSIGHT_TEXT_4 = "기간 전체에서 가장 많은 관객을 모은 영화와 각 영화가 TOP 10에 오래 머문 정도를 함께 비교할 수 있습니다."
INSIGHT_TEXT_5 = "월과 요일에 따라 박스오피스 TOP 10 관객 규모가 어떻게 달라지는지 한눈에 비교할 수 있습니다."

WEEKDAY_ORDER = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
WEEKDAY_MAP = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일",
}


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
# 공통 레이아웃
# ============================================================
def apply_common_layout(fig, yaxis_title="일관객 수"):
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title=yaxis_title,
        yaxis_tickformat=",",
        margin=dict(l=20, r=20, t=70, b=20),
        legend_title_text="영화명",
    )
    return fig


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
        labels={"날짜": "날짜", "일관객": "일관객 수"},
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "일관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig.update_layout(hovermode="x unified")
    apply_common_layout(fig)

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_1}")


# ============================================================
# 그래프 2 : 기간 일관객 합계 TOP 5 영화의 날짜별 변화
# ============================================================
def render_graph_2(df):
    st.subheader("2. 관객 합계 TOP 5 영화의 날짜별 변화")

    top5_movies = (
        df.groupby("영화명", as_index=False)["일관객"]
        .sum()
        .nlargest(5, "일관객")["영화명"]
        .tolist()
    )

    top5_daily = (
        df[df["영화명"].isin(top5_movies)]
        .groupby(["날짜", "영화명"], as_index=False)["일관객"]
        .sum()
        .sort_values("날짜")
    )

    fig = px.line(
        top5_daily,
        x="날짜",
        y="일관객",
        color="영화명",
        title="기간 일관객 합계 TOP 5 영화 비교",
        labels={"날짜": "날짜", "일관객": "일관객 수", "영화명": "영화명"},
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "%{x|%Y-%m-%d}<br>"
            "일관객: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        hovermode="x unified",
        legend=dict(itemclick="toggle", itemdoubleclick="toggleothers"),
    )
    apply_common_layout(fig)

    st.plotly_chart(fig, use_container_width=True)
    st.caption("범례의 영화명을 클릭하면 해당 영화의 선을 켜거나 끌 수 있습니다.")
    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_2}")


# ============================================================
# 그래프 3 : 날짜별 TOP 10 일관객 합계 영역 그래프
# ============================================================
def render_graph_3(df):
    st.subheader("3. 날짜별 박스오피스 TOP 10 전체 관객 변화")

    daily_total = (
        df.groupby("날짜", as_index=False)["일관객"]
        .sum()
        .sort_values("날짜")
    )

    top3_days = daily_total.nlargest(3, "일관객").sort_values("날짜")

    fig = px.area(
        daily_total,
        x="날짜",
        y="일관객",
        title="날짜별 TOP 10 일관객 합계",
        labels={"날짜": "날짜", "일관객": "TOP 10 일관객 합계"},
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>"
            "TOP 10 합계: %{y:,.0f}명"
            "<extra></extra>"
        )
    )

    # 가장 관객이 많았던 3일을 점과 날짜 라벨로 표시
    fig.add_trace(
        go.Scatter(
            x=top3_days["날짜"],
            y=top3_days["일관객"],
            mode="markers+text",
            text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
            textposition="top center",
            marker=dict(size=10),
            name="관객 최다 3일",
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "TOP 10 합계: %{y:,.0f}명"
                "<extra></extra>"
            ),
        )
    )

    apply_common_layout(fig, "TOP 10 일관객 합계")
    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_3}")


# ============================================================
# 그래프 4 : 기간 일관객 합계 TOP 10 가로 막대그래프
# ============================================================
def render_graph_4(df):
    st.subheader("4. 기간 전체 일관객 합계 TOP 10")

    movie_summary = (
        df.groupby("영화명")
        .agg(
            일관객_합계=("일관객", "sum"),
            TOP10_진입일수=("날짜", "nunique"),
        )
        .reset_index()
        .nlargest(10, "일관객_합계")
        .sort_values("일관객_합계", ascending=True)
    )

    fig = px.bar(
        movie_summary,
        x="일관객_합계",
        y="영화명",
        orientation="h",
        title="기간 전체 일관객 합계 TOP 10",
        labels={"일관객_합계": "일관객 합계", "영화명": "영화명"},
        custom_data=["TOP10_진입일수"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "일관객 합계: %{x:,.0f}명<br>"
            "10위권 진입 일수: %{customdata[0]}일"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="일관객 합계",
        yaxis_title="영화명",
        xaxis_tickformat=",",
        margin=dict(l=20, r=20, t=70, b=20),
        height=560,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_4}")


# ============================================================
# 그래프 5 : 월 × 요일 일관객 합계 히트맵
# ============================================================
def render_graph_5(df):
    st.subheader("5. 월 × 요일별 일관객 합계 히트맵")

    heat_df = df.copy()
    heat_df["월"] = heat_df["날짜"].dt.month
    heat_df["요일"] = heat_df["날짜"].dt.dayofweek.map(WEEKDAY_MAP)

    heat_summary = (
        heat_df.groupby(["월", "요일"], as_index=False)["일관객"]
        .sum()
    )

    pivot = (
        heat_summary.pivot(index="월", columns="요일", values="일관객")
        .reindex(index=range(1, 13), columns=WEEKDAY_ORDER)
        .fillna(0)
    )

    # y축에 1월~12월로 표시
    pivot.index = [f"{month}월" for month in pivot.index]

    fig = px.imshow(
        pivot,
        labels=dict(x="요일", y="월", color="일관객 합계"),
        x=WEEKDAY_ORDER,
        y=pivot.index,
        aspect="auto",
        title="월 × 요일별 일관객 합계",
        color_continuous_scale="Blues",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y} · %{x}</b><br>"
            "일관객 합계: %{z:,.0f}명"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        xaxis_title="요일",
        yaxis_title="월",
        margin=dict(l=20, r=20, t=70, b=20),
        height=600,
        coloraxis_colorbar=dict(title="일관객 합계"),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info(f"💡 이 그래프로 알 수 있는 것: {INSIGHT_TEXT_5}")


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

# 각 그래프를 독립된 구역으로 분리
with st.container(border=True):
    render_graph_1(data)

st.divider()

with st.container(border=True):
    render_graph_2(data)

st.divider()

with st.container(border=True):
    render_graph_3(data)

st.divider()

with st.container(border=True):
    render_graph_4(data)

st.divider()

with st.container(border=True):
    render_graph_5(data)
