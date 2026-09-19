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
LAST_CLASS_YEAR = 2025
MIN_OBS_DAYS = 300


# -----------------------------
# 데이터 불러오기 및 전처리
# -----------------------------
@st.cache_data
def load_and_prepare_data():
    # 파일 첫 열에 BOM이 있어도 안전하게 읽도록 utf-8-sig 사용
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 날짜/평균기온이 정상인 행만 사용
    df = df.dropna(subset=["날짜", "평균기온"]).copy()
    df["연도"] = df["날짜"].dt.year

    # 수업 기준 기간: 2025년까지
    df = df[df["연도"] <= LAST_CLASS_YEAR]

    # 연도별 평균기온과 실제 사용 가능한 관측일 수 계산
    annual = (
        df.groupby("연도", as_index=False)
        .agg(
            연평균기온=("평균기온", "mean"),
            관측일수=("평균기온", "count"),
        )
    )

    # 관측일이 300일 미만인 해 제외
    annual = annual[annual["관측일수"] >= MIN_OBS_DAYS].copy()
    annual = annual.sort_values("연도").reset_index(drop=True)

    # 회귀분석 독립 변수: 1908년부터 지난 연수
    annual["1908년부터_지난_연수"] = annual["연도"] - BASE_YEAR

    return annual


annual = load_and_prepare_data()

if len(annual) < 2:
    st.error("회귀분석을 수행할 수 있을 만큼 충분한 데이터가 없습니다.")
    st.stop()


# -----------------------------
# 회귀분석 및 상관계수
# -----------------------------
x = annual["1908년부터_지난_연수"].to_numpy()
y = annual["연평균기온"].to_numpy()

slope, intercept = np.polyfit(x, y, 1)
annual["회귀예측기온"] = intercept + slope * x

correlation = annual["1908년부터_지난_연수"].corr(annual["연평균기온"])

start_year = int(annual["연도"].min())
end_year = int(annual["연도"].max())
year_count = len(annual)


# -----------------------------
# 화면
# -----------------------------
st.title("🌡️ 기온 예측기")
st.write(
    "서울의 연도별 평균기온을 이용해 선형 회귀 직선을 만들고, "
    "선택한 연도의 예상 평균기온을 계산합니다."
)

st.caption(
    f"데이터는 {LAST_CLASS_YEAR}년까지 사용하며, "
    f"평균기온 관측일이 {MIN_OBS_DAYS}일 미만인 해는 제외합니다."
)

# 회귀에 사용된 데이터 정보
c1, c2, c3, c4 = st.columns(4)
c1.metric("회귀에 사용한 해", f"{year_count}개")
c2.metric("시작 연도", f"{start_year}년")
c3.metric("끝 연도", f"{end_year}년")
c4.metric("상관계수 r", f"{correlation:.3f}")

st.divider()

# -----------------------------
# 산점도 + 회귀 직선
# -----------------------------
st.subheader("연도별 평균기온과 회귀 직선")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=annual["연도"],
        y=annual["연평균기온"],
        mode="markers",
        name="연평균기온",
        customdata=annual[["관측일수"]],
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "연평균기온: %{y:.2f} ℃<br>"
            "관측일수: %{customdata[0]}일"
            "<extra></extra>"
        ),
    )
)

fig.add_trace(
    go.Scatter(
        x=annual["연도"],
        y=annual["회귀예측기온"],
        mode="lines",
        name="선형 회귀 직선",
        hovertemplate=(
            "<b>%{x}년</b><br>"
            "회귀 예측값: %{y:.2f} ℃"
            "<extra></extra>"
        ),
    )
)

fig.update_layout(
    xaxis_title="연도",
    yaxis_title="연평균기온 (℃)",
    hovermode="x unified",
    height=560,
    legend_title_text="",
)

# 가로축에는 '지난 연수'가 아니라 실제 연도를 표시
fig.update_xaxes(
    tickmode="linear",
    dtick=10,
    tickformat="d",
)

st.plotly_chart(fig, use_container_width=True)

st.info(
    f"피어슨 상관계수는 **r = {correlation:.3f}** 입니다. "
    "회귀식은 1908년부터 지난 연수를 x로 두어 계산했습니다."
)

st.latex(
    rf"\hat{{T}} = {intercept:.4f} "
    rf"{'+' if slope >= 0 else '-'} {abs(slope):.4f}x,"
    rf"\quad x = \mathrm{{연도}} - 1908"
)

st.divider()

# -----------------------------
# 원하는 연도 기온 예측
# -----------------------------
st.subheader("원하는 연도의 예상 기온")

selected_year = st.slider(
    "연도를 선택하세요",
    min_value=1900,
    max_value=2100,
    value=2025,
    step=1,
)

selected_x = selected_year - BASE_YEAR
predicted_temp = intercept + slope * selected_x

st.markdown(
    f"""
    <div style="
        text-align:center;
        padding:28px 20px;
        border:1px solid rgba(128,128,128,0.25);
        border-radius:18px;
        margin-top:12px;
        margin-bottom:12px;
    ">
        <div style="font-size:1.25rem; opacity:0.75;">
            {selected_year}년 예상 연평균기온
        </div>
        <div style="font-size:3.4rem; font-weight:800; line-height:1.2;">
            {predicted_temp:.2f} ℃
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if selected_year < start_year or selected_year > end_year:
    st.warning(
        f"{selected_year}년은 회귀 직선을 만든 실제 데이터 범위 "
        f"({start_year}~{end_year}년) 밖이므로, 이 값은 외삽 예측입니다."
    )

st.caption(
    "이 예측값은 과거 연평균기온의 장기적인 직선 추세만 이용한 단순 선형 회귀 결과입니다. "
    "실제 미래 기온은 여러 요인의 영향을 받을 수 있습니다."
)

# 기울기를 100년 단위로, 그리고 최근 20년과 비교
recent = yearly[yearly["연도"] >= yearly["연도"].max() - 19]
a2, _ = np.polyfit(recent["연도"], recent["연평균기온"], 1)
c1, c2 = st.columns(2)
c1.metric("전체 기간 기울기", f"{a * 100:+.2f}℃ / 100년")
c2.metric("최근 20년 기울기", f"{a2 * 100:+.2f}℃ / 100년")
