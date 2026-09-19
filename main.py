import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="기온 예측기",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 기온 예측기")
st.caption("서울의 과거 기온을 바탕으로 연평균기온의 변화 추세를 살펴봅니다.")

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
)

BASE_YEAR = 1908
END_YEAR = 2025
MIN_OBSERVATIONS = 300


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 필요한 값이 없는 행 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 만들기
    df["연도"] = df["날짜"].dt.year

    # 수업 기준인 2025년까지만 사용
    df = df[df["연도"] <= END_YEAR]

    return df


df = load_data()


# --------------------------------------------------
# 연도별 데이터 정리
# --------------------------------------------------
yearly = (
    df.groupby("연도")
    .agg(
        연평균기온=("평균기온", "mean"),
        관측일수=("평균기온", "count")
    )
    .reset_index()
)

# 관측일이 300일 이상인 해만 사용
yearly = yearly[yearly["관측일수"] >= MIN_OBSERVATIONS].copy()

# 연도순 정렬
yearly = yearly.sort_values("연도").reset_index(drop=True)

# 1908년부터 지난 연수
yearly["지난연수"] = yearly["연도"] - BASE_YEAR


# --------------------------------------------------
# 전체 기간 회귀분석
# --------------------------------------------------
x_all = yearly["지난연수"].to_numpy()
y_all = yearly["연평균기온"].to_numpy()

slope_all, intercept_all = np.polyfit(x_all, y_all, 1)

# 상관계수
correlation = np.corrcoef(x_all, y_all)[0, 1]

# 100년당 온도 변화
slope_100_all = slope_all * 100


# --------------------------------------------------
# 최근 20년 회귀분석
# --------------------------------------------------
recent_20 = yearly.tail(20).copy()

x_recent = recent_20["지난연수"].to_numpy()
y_recent = recent_20["연평균기온"].to_numpy()

slope_recent, intercept_recent = np.polyfit(
    x_recent,
    y_recent,
    1
)

slope_100_recent = slope_recent * 100


# --------------------------------------------------
# 데이터 정보
# --------------------------------------------------
year_count = len(yearly)
start_year = int(yearly["연도"].min())
end_year = int(yearly["연도"].max())

recent_start = int(recent_20["연도"].min())
recent_end = int(recent_20["연도"].max())


# --------------------------------------------------
# 핵심 지표
# --------------------------------------------------
st.subheader("📌 기온 변화 핵심 지표")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "전체 기간의 100년당 기온 변화",
        f"{slope_100_all:+.2f} ℃ / 100년"
    )
    st.caption(f"{start_year}년 ~ {end_year}년")

with col2:
    st.metric(
        "최근 20년의 100년당 기온 변화",
        f"{slope_100_recent:+.2f} ℃ / 100년"
    )
    st.caption(f"{recent_start}년 ~ {recent_end}년")


# --------------------------------------------------
# 전체 기간 / 최근 20년 비교
# --------------------------------------------------
st.subheader("🔥 전체 기간과 최근 20년 비교")

compare1, compare2 = st.columns(2)

with compare1:
    st.markdown("#### 전체 기간")
    st.markdown(
        f"""
        <div style="
            padding: 22px;
            border-radius: 15px;
            background-color: rgba(255, 255, 255, 0.05);
            text-align: center;
        ">
            <div style="font-size: 18px;">100년당 변화</div>
            <div style="font-size: 42px; font-weight: bold;">
                {slope_100_all:+.2f} ℃
            </div>
            <div>
                {start_year} ~ {end_year}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with compare2:
    st.markdown("#### 최근 20년")
    st.markdown(
        f"""
        <div style="
            padding: 22px;
            border-radius: 15px;
            background-color: rgba(255, 255, 255, 0.05);
            text-align: center;
        ">
            <div style="font-size: 18px;">100년당 변화</div>
            <div style="font-size: 42px; font-weight: bold;">
                {slope_100_recent:+.2f} ℃
            </div>
            <div>
                {recent_start} ~ {recent_end}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# 산점도 + 회귀 직선
# --------------------------------------------------
st.subheader("📈 서울 연평균기온 변화")

# 전체 기간 회귀선
plot_years = np.arange(start_year, end_year + 1)

plot_elapsed = plot_years - BASE_YEAR

predicted_temp = (
    slope_all * plot_elapsed
    + intercept_all
)

fig = go.Figure()

# 실제 연평균기온
fig.add_trace(
    go.Scatter(
        x=yearly["연도"],
        y=yearly["연평균기온"],
        mode="markers",
        name="실제 연평균기온",
        marker=dict(
            size=7,
            opacity=0.75
        ),
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "평균기온: %{y:.2f} ℃"
            "<extra></extra>"
        )
    )
)

# 회귀 직선
fig.add_trace(
    go.Scatter(
        x=plot_years,
        y=predicted_temp,
        mode="lines",
        name="전체 기간 회귀 직선",
        line=dict(
            width=4
        ),
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "예상기온: %{y:.2f} ℃"
            "<extra></extra>"
        )
    )
)

fig.update_layout(
    xaxis_title="연도",
    yaxis_title="연평균기온 (℃)",
    hovermode="closest",
    height=600,
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

# 가로축에 실제 연도 표시
fig.update_xaxes(
    tickformat="d"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 통계 정보
# --------------------------------------------------
info1, info2, info3, info4 = st.columns(4)

info1.metric(
    "상관계수",
    f"{correlation:.3f}"
)

info2.metric(
    "사용한 연도 수",
    f"{year_count}개"
)

info3.metric(
    "시작 연도",
    f"{start_year}년"
)

info4.metric(
    "끝 연도",
    f"{end_year}년"
)

st.caption(
    "※ 2025년 이후의 데이터와 연간 관측일이 300일 미만인 해는 "
    "회귀분석에서 제외했습니다."
)


# --------------------------------------------------
# 기온 예측
# --------------------------------------------------
st.divider()

st.subheader("🔮 연도별 예상 기온")

selected_year = st.slider(
    "예상 기온을 확인할 연도를 선택하세요.",
    min_value=1900,
    max_value=2100,
    value=2025,
    step=1
)

# 전체 기간 회귀직선으로 예측
selected_elapsed = selected_year - BASE_YEAR

predicted_selected = (
    slope_all * selected_elapsed
    + intercept_all
)

st.markdown(
    f"""
    <div style="
        padding: 35px;
        margin-top: 15px;
        border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.05);
        text-align: center;
    ">
        <div style="font-size: 24px;">
            {selected_year}년 예상 연평균기온
        </div>

        <div style="
            font-size: 64px;
            font-weight: bold;
            margin-top: 5px;
        ">
            {predicted_selected:.2f} ℃
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 관측 범위를 벗어난 경우 안내
if selected_year < start_year or selected_year > end_year:
    st.warning(
        "선택한 연도는 실제 관측자료 범위를 벗어납니다. "
        "표시된 값은 회귀직선을 연장한 추정값이므로 실제 기온과 "
        "차이가 클 수 있습니다."
    )


# --------------------------------------------------
# 회귀식 설명
# --------------------------------------------------
with st.expander("📐 회귀 직선 정보 자세히 보기"):
    st.write(
        f"""
        회귀분석에서는 **{BASE_YEAR}년부터 지난 연수**를
        독립 변수 x로 사용했습니다.

        **회귀식**

        예상 연평균기온 = {slope_all:.5f} × (연도 - {BASE_YEAR})
        + {intercept_all:.3f}

        - 1년당 기온 변화: **{slope_all:+.4f} ℃**
        - 100년당 기온 변화: **{slope_100_all:+.2f} ℃**
        - 상관계수: **{correlation:.3f}**
        - 사용한 연도 수: **{year_count}개**
        - 사용 기간: **{start_year}년 ~ {end_year}년**
        - 최근 20년 기간: **{recent_start}년 ~ {recent_end}년**
        - 최근 20년 기준 100년당 변화: **{slope_100_recent:+.2f} ℃**
        """
    )
