import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="기온 예측기",
    page_icon="🌡️",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "bb860932644270ad1199f10d3e7670e30231bce4/data/seoul.csv"
)
BASE_YEAR = 1908
LAST_YEAR = 2025
MIN_OBSERVATION_DAYS = 300
RECENT_YEARS = 20


# -----------------------------
# 데이터 불러오기 / 전처리
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    required_columns = ["날짜", "지점", "평균기온", "최저기온", "최고기온"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"필요한 열이 없습니다: {', '.join(missing)}")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 날짜가 없거나 수업 기준 기간(2025년)을 넘는 자료 제외
    df = df.dropna(subset=["날짜"])
    df = df[df["날짜"].dt.year <= LAST_YEAR].copy()
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온과 사용 가능한 평균기온 관측일 수 계산
    annual = (
        df.groupby("연도", as_index=False)
        .agg(
            연평균기온=("평균기온", "mean"),
            관측일수=("평균기온", "count"),
        )
    )

    # 1908년 이후, 관측일 300일 이상인 해만 회귀에 사용
    annual = annual[
        (annual["연도"] >= BASE_YEAR)
        & (annual["연도"] <= LAST_YEAR)
        & (annual["관측일수"] >= MIN_OBSERVATION_DAYS)
        & (annual["연평균기온"].notna())
    ].copy()

    annual = annual.sort_values("연도").reset_index(drop=True)

    if len(annual) < 2:
        raise ValueError("회귀분석에 사용할 수 있는 연도가 2개 미만입니다.")

    # 독립 변수: 1908년부터 지난 연수
    annual["지난연수"] = annual["연도"] - BASE_YEAR

    return annual


try:
    annual = load_data()
except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다.\n\n{e}")
    st.stop()


# -----------------------------
# 전체 기간 선형 회귀 / 상관계수
# -----------------------------
x = annual["지난연수"].to_numpy(dtype=float)
y = annual["연평균기온"].to_numpy(dtype=float)

slope, intercept = np.polyfit(x, y, 1)
correlation = np.corrcoef(x, y)[0, 1]

annual["회귀예측"] = intercept + slope * annual["지난연수"]

start_year = int(annual["연도"].min())
end_year = int(annual["연도"].max())
year_count = len(annual)


# -----------------------------
# 최근 20년 선형 회귀
# 2025년을 포함한 2006~2025년
# -----------------------------
recent_start_year = LAST_YEAR - RECENT_YEARS + 1

recent_20 = annual[
    (annual["연도"] >= recent_start_year)
    & (annual["연도"] <= LAST_YEAR)
].copy()

if len(recent_20) < 2:
    st.error("최근 20년 회귀분석에 사용할 수 있는 연도가 부족합니다.")
    st.stop()

recent_x = recent_20["지난연수"].to_numpy(dtype=float)
recent_y = recent_20["연평균기온"].to_numpy(dtype=float)

recent_slope, recent_intercept = np.polyfit(recent_x, recent_y, 1)

# '1년에 몇 도'가 아니라 '100년에 몇 도'로 환산
century_change_all = slope * 100
century_change_recent = recent_slope * 100


# -----------------------------
# 화면
# -----------------------------
st.title("🌡️ 기온 예측기")
st.caption(
    "서울의 연평균기온 자료로 선형 회귀 직선을 만들고, "
    "선택한 연도의 예상 연평균기온을 계산합니다."
)

st.info(
    f"회귀분석에는 {BASE_YEAR}~{LAST_YEAR}년 자료 중 "
    f"평균기온 관측일이 {MIN_OBSERVATION_DAYS}일 이상인 해만 사용합니다."
)

# 예측 연도 선택
selected_year = st.slider(
    "예상 기온을 확인할 연도",
    min_value=1900,
    max_value=2100,
    value=2025,
    step=1,
)

selected_x = selected_year - BASE_YEAR
predicted_temp = intercept + slope * selected_x

# 핵심 지표
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label=f"{selected_year}년 예상 연평균기온",
        value=f"{predicted_temp:.2f} °C",
    )

with col2:
    st.metric(
        label="상관계수 r",
        value=f"{correlation:.3f}",
    )


# -----------------------------
# 100년당 기온 변화량 비교
# -----------------------------
st.subheader("🌡️ 100년에 몇 도 오르는가?")

slope_col1, slope_col2 = st.columns(2)

with slope_col1:
    st.metric(
        label=f"전체 기간 ({start_year}~{end_year})",
        value=f"{century_change_all:+.2f} °C / 100년",
        help="전체 기간 회귀 직선의 기울기를 100년 단위로 환산한 값입니다.",
    )

with slope_col2:
    st.metric(
        label=f"최근 20년 ({recent_start_year}~{LAST_YEAR})",
        value=f"{century_change_recent:+.2f} °C / 100년",
        delta=f"{century_change_recent - century_change_all:+.2f} °C vs 전체",
        help="2006~2025년 자료만으로 회귀 직선을 만든 뒤 기울기를 100년 단위로 환산한 값입니다.",
    )

st.caption(
    "양수이면 기온 상승, 음수이면 기온 하락을 뜻합니다. "
    "최근 20년 기울기도 비교를 쉽게 하기 위해 100년 기준으로 환산했습니다."
)


# -----------------------------
# 그래프
# -----------------------------
st.subheader("연평균기온과 전체 기간 회귀 직선")

fig = go.Figure()

# 실제 연평균기온 산점도
fig.add_trace(
    go.Scatter(
        x=annual["연도"],
        y=annual["연평균기온"],
        mode="markers",
        name="연평균기온",
        marker=dict(size=8),
        hovertemplate=(
            "연도: %{x}년<br>"
            "연평균기온: %{y:.2f} °C"
            "<extra></extra>"
        ),
    )
)

# 전체 기간 회귀 직선
fig.add_trace(
    go.Scatter(
        x=annual["연도"],
        y=annual["회귀예측"],
        mode="lines",
        name="전체 기간 회귀 직선",
        line=dict(width=3),
        hovertemplate=(
            "연도: %{x}년<br>"
            "회귀 예측: %{y:.2f} °C"
            "<extra></extra>"
        ),
    )
)

fig.update_layout(
    xaxis_title="연도",
    yaxis_title="연평균기온 (°C)",
    hovermode="x unified",
    legend_title_text="",
    margin=dict(l=20, r=20, t=20, b=20),
)

# 가로축에는 실제 연도를 그대로 표시
fig.update_xaxes(
    tickformat="d",
    range=[start_year - 2, end_year + 2],
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# 회귀 정보
# -----------------------------
st.subheader("회귀 정보")

info1, info2, info3 = st.columns(3)
info1.metric("직선을 만든 해의 개수", f"{year_count}개")
info2.metric("시작 연도", f"{start_year}년")
info3.metric("끝 연도", f"{end_year}년")

st.write(
    f"전체 기간 회귀식은 **예상 기온 = {intercept:.4f} "
    f"{slope:+.4f} × (연도 - {BASE_YEAR})** 입니다."
)

st.write(
    f"최근 20년 회귀식은 **예상 기온 = {recent_intercept:.4f} "
    f"{recent_slope:+.4f} × (연도 - {BASE_YEAR})** 입니다."
)

st.caption(
    "※ 1900~2100년 예측값은 전체 기간의 과거 자료에 맞춘 단순 선형 회귀를 "
    "연장한 값입니다. 특히 관측 기간 밖의 연도에서는 실제 기후와 차이가 커질 수 있습니다."
)

with st.expander("회귀에 사용된 연도별 데이터 보기"):
    display_df = annual[["연도", "관측일수", "연평균기온"]].copy()
    display_df["연평균기온"] = display_df["연평균기온"].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
