"""뇌졸중 예측 실습실 · 탐색 페이지.

실행: Streamlit이 pages/1_탐색.py 를 자동 인식합니다.
원본 CSV와 4개 허용 라이브러리만 사용합니다(표준 라이브러리 제외).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
REQUIRED = ["age", "avg_glucose_level", "hypertension", "heart_disease", "bmi", "smoking_status", "stroke"]
COLORS = {
    "mint": "#29E8CF",
    "lilac": "#AD9BFF",
    "pink": "#FF7899",
    "gold": "#F8CD82",
    "ink": "#EAF5FF",
    "muted": "#93AFC2",
    "grid": "rgba(146,187,218,.115)",
    "chart": "#0D1D2F",
}

st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    r"""<style>
:root {
  --ink: #eaf5ff;
  --muted: #8fa6bc;
  --mint: #29e8cf;
  --lilac: #ad9bff;
  --pink: #ff7899;
  --line: rgba(168, 201, 232, .13);
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: "Pretendard", "Inter", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}
.stApp {
  background:
    radial-gradient(ellipse 70% 42% at 85% -7%, rgba(39, 228, 206, .11) 0%, transparent 75%),
    radial-gradient(ellipse 55% 36% at -14% 48%, rgba(136, 117, 252, .08) 0%, transparent 80%),
    #07111f;
  color: #eaf5ff;
}
[data-testid="stHeader"] {background: rgba(7,17,31,.75) !important; backdrop-filter: blur(10px)}
.main .block-container, [data-testid="stMainBlockContainer"] {
  max-width: 1320px;
  padding-top: 2.0rem;
  padding-bottom: 5rem;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0c1a2a 0%, #091321 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {border-radius: 11px;}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {background: rgba(41,232,207,.08);}
#MainMenu, footer {visibility:hidden;}
/* Navigation / brand */
.brand {display:flex; align-items:center; gap:11px; margin:0 0 24px;}
.brand-mark {height:39px; width:39px; display:grid; place-items:center; border:1px solid rgba(41,232,207,.47); border-radius:13px; color:var(--mint); background:rgba(41,232,207,.08); font-size:21px;}
.brand-name {font-weight:900; font-size:15px; letter-spacing:.13em; color:white;}
.brand-small {font-size:10px; letter-spacing:.22em; color:#83a3b4; margin-top:2px;}
.side-kicker {font-size:10px; font-weight:800; letter-spacing:.17em; color:var(--mint); margin:10px 0 8px;}
.side-line {font-size:12px; color:#8ca5ba; line-height:1.9;}
/* Rich hero */
.lab-hero {
  position:relative; overflow:hidden;
  padding:40px 46px 38px;
  border:1px solid rgba(71,234,215,.21);
  border-radius:27px;
  background:
    radial-gradient(circle at 90% 50%, rgba(64,248,223,.17), transparent 32%),
    radial-gradient(circle at 44% -100%, rgba(158,132,255,.14), transparent 70%),
    linear-gradient(118deg, #101f33, #0a2032 58%, #092a34);
  box-shadow: 0 18px 70px rgba(0,0,0,.24), inset 0 1px rgba(255,255,255,.045);
  margin-bottom:32px;
}
.lab-hero:before {
  content:""; pointer-events:none; position:absolute; inset:0;
  opacity:.14;
  background-image: linear-gradient(rgba(142,223,230,.25) 1px, transparent 1px), linear-gradient(90deg, rgba(142,223,230,.25) 1px, transparent 1px);
  background-size:32px 32px;
  mask-image:linear-gradient(to left,#000,transparent 70%);
}
.lab-hero:after {
  content:""; position:absolute; pointer-events:none;
  width:225px; height:225px; border-radius:50%; right:7%; top:50%; transform:translateY(-50%);
  border:1px solid rgba(69,243,221,.23);
  box-shadow:0 0 0 27px rgba(41,232,207,.04),0 0 0 55px rgba(41,232,207,.025),0 0 80px rgba(41,232,207,.11);
}
.lab-hero > * {position:relative; z-index:1;}
.hero-eyebrow {display:flex;align-items:center;gap:10px;color:#8aefdf;font-weight:800;letter-spacing:.18em;font-size:11px;margin-bottom:16px;}
.live-dot {width:7px;height:7px;display:inline-block;border-radius:50%;background:var(--mint);box-shadow:0 0 10px var(--mint);animation:livepulse 2.5s ease-in-out infinite;}
@keyframes livepulse {0%,100%{opacity:1}50%{opacity:.35}}
.lab-hero h1 {font-size:clamp(2rem,4.4vw,3.55rem);letter-spacing:-.07em;font-weight:900;margin:0 0 14px;line-height:1.24;color:#fff;}
.hero-highlight {color:var(--mint);}
.lab-hero p {font-size:14px;color:#abc2d2;max-width:680px;line-height:1.9;margin:0;}
.hero-status {display:flex; flex-wrap:wrap; gap:10px;margin-top:21px;}
.hero-chip {font-size:11px;letter-spacing:.04em;color:#b5d5df;border:1px solid rgba(172,214,227,.2);background:rgba(12,30,48,.65);padding:7px 12px;border-radius:100px;}
/* Labels and headings */
.section-head {display:flex;align-items:center;gap:13px;margin:12px 0 5px;}
.section-index {font-weight:900;color:var(--mint);font-size:12px;letter-spacing:.13em;background:rgba(41,232,207,.085);border:1px solid rgba(41,232,207,.14);border-radius:9px;padding:8px 10px;}
.section-title {font-weight:850;color:#f3f9ff;letter-spacing:-.045em;font-size:clamp(1.2rem,2.2vw,1.68rem);line-height:1.35;}
.section-help {color:#8fa6bb;font-size:13px;line-height:1.85;margin-bottom:17px;}
/* KPI cards */
.lab-kpi {position:relative;overflow:hidden;border:1px solid var(--line);border-radius:18px;background:linear-gradient(150deg,rgba(22,40,60,.9),rgba(13,28,46,.95));min-height:153px;padding:20px 20px 18px;margin-bottom:8px;box-shadow:inset 0 1px rgba(255,255,255,.025);}
.lab-kpi:after{position:absolute;content:"";height:75px;width:75px;border-radius:50%;right:-25px;top:-27px;background:var(--tint,#29e8cf);opacity:.10;filter:blur(7px)}
.lab-kpi .kpi-id{font-family:monospace;font-size:10px;color:var(--tint,#29e8cf);letter-spacing:.18em;margin-bottom:8px;font-weight:800}
.lab-kpi .kpi-label{color:#9fb5c7;font-size:13px;font-weight:600;margin-bottom:9px}
.lab-kpi .kpi-value{font-size:clamp(1.6rem,2.7vw,2.45rem);font-weight:850;letter-spacing:-.06em;color:#fff;line-height:1.1}
.lab-kpi .kpi-footer{font-size:11px;color:#7390a6;margin-top:11px}
/* Charts and tables */
[data-testid="stVerticalBlockBorderWrapper"] > div {border-color:var(--line) !important;border-radius:21px !important;background:linear-gradient(145deg,#0d1d2f,#0a1929) !important;}
[data-testid="stPlotlyChart"] {border-radius:14px;overflow:hidden;}
.chart-eyebrow {color:var(--mint);letter-spacing:.14em;font-size:10px;font-weight:800;margin-bottom:5px;}
.chart-title {color:#f4f8fd;font-size:17px;font-weight:800;letter-spacing:-.04em;line-height:1.4}
.chart-subtitle{color:#7d97ad;font-size:12px;margin-top:6px;line-height:1.7}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {border:1px solid rgba(169,198,221,.19);border-radius:14px;overflow:hidden;}
[data-testid="stDataFrame"] div[role="grid"], [data-testid="stDataEditor"] div[role="grid"] {background:#0d1b2b;}
[data-testid="stTextArea"] textarea {background:#101f30;border-color:rgba(125,173,210,.22);color:#ecf7ff;border-radius:12px;}
[data-testid="stSlider"] {padding-top:4px}
div.stButton > button, div[data-testid="stDownloadButton"] > button, div[data-testid="stPageLink"] a {
  border-radius:11px;transition:all .18s ease;
}
div.stButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {box-shadow:0 0 22px rgba(41,232,207,.15);}
.note-box {border:1px solid rgba(167,157,250,.18);background:rgba(132,112,220,.065);padding:15px 18px;border-radius:14px;margin:8px 0 18px;color:#aabbd0;font-size:12px;line-height:1.9;}
.note-box b{color:#d8ddff}
.tiny-label{font-family:monospace;color:#7894ab;font-size:11px;letter-spacing:.13em;margin:12px 0}
hr {border-color:rgba(140,181,210,.14) !important;margin:23px 0 !important;}
/* smaller mobile */
@media(max-width:740px) {
 .main .block-container,[data-testid="stMainBlockContainer"] {padding-top:1rem;padding-left:1rem;padding-right:1rem}
 .lab-hero{padding:28px 24px;border-radius:20px}
 .lab-hero:after {right:-80px;opacity:.4}
 .lab-hero p{font-size:13px}
 .lab-kpi{min-height:130px}
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    """원본 파일을 다른 페이지와 동일한 주소에서 UTF-8로 읽는다."""
    return pd.read_csv(DATA_URL, encoding="utf-8")


def section(index, heading, description=""):
    st.markdown(
        f'<div class="section-head"><span class="section-index">{index}</span>'
        f'<span class="section-title">{heading}</span></div>'
        f'<div class="section-help">{description}</div>',
        unsafe_allow_html=True,
    )


def chart_header(kicker, title, desc):
    st.markdown(
        f'<div class="chart-eyebrow">{kicker}</div>'
        f'<div class="chart-title">{title}</div>'
        f'<div class="chart-subtitle">{desc}</div>',
        unsafe_allow_html=True,
    )


def chart_layout(fig, ymax=None):
    """모든 Plotly 차트의 디자인을 통일한다."""
    fig.update_layout(
        height=335,
        paper_bgcolor=COLORS["chart"],
        plot_bgcolor=COLORS["chart"],
        font=dict(family="Arial, Noto Sans KR, sans-serif", color=COLORS["ink"], size=12),
        margin=dict(l=12, r=16, t=18, b=24),
        showlegend=False,
        bargap=0.055,
        hoverlabel=dict(bgcolor="#182F43", bordercolor="#42647A", font=dict(color="#FFFFFF", size=13)),
    )
    fig.update_xaxes(showline=False, zeroline=False, gridcolor=COLORS["grid"], tickfont_color=COLORS["muted"], title_font_color=COLORS["muted"])
    fig.update_yaxes(showline=False, zeroline=False, gridcolor=COLORS["grid"], tickfont_color=COLORS["muted"], title_font_color=COLORS["muted"])
    if ymax is not None:
        fig.update_yaxes(range=[0, ymax])
    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        theme=None,
        config={"displaylogo": False, "responsive": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
    )


def hist_figure(data, label, color, bins):
    clean = pd.to_numeric(data, errors="coerce").dropna()
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=clean, nbinsx=bins, name=label,
            marker=dict(color=color, line=dict(color="#132638", width=1)),
            opacity=.90,
            hovertemplate="값: %{x}<br>해당 구간 인원: %{y:,}명<extra></extra>",
        )
    )
    if not clean.empty:
        fig.add_vline(x=float(clean.median()), line_width=2, line_dash="dot", line_color="#E7F4FD", opacity=.8)
    fig.update_xaxes(title_text=label)
    fig.update_yaxes(title_text="사람 수 (명)", rangemode="tozero")
    return chart_layout(fig)


def box_figure(df, column, label):
    fig = go.Figure()
    for stroke, color, name in [(0, COLORS["mint"], "미경험 (0)"), (1, COLORS["pink"], "경험 (1)")]:
        items = df.loc[df["stroke"].eq(stroke), column].dropna()
        fig.add_trace(
            go.Box(
                y=items,
                name=name,
                marker=dict(color=color, size=4, opacity=.62),
                line=dict(color=color, width=2),
                fillcolor="rgba(255,120,153,.18)" if stroke else "rgba(41,232,207,.16)",
                boxpoints="outliers",
                boxmean=True,
                whiskerwidth=.8,
                hovertemplate=f"{name}<br>{label}: %{{y:.1f}}<extra></extra>",
            )
        )
    fig.update_yaxes(title_text=label)
    fig.update_xaxes(title_text="뇌졸중 경험 여부")
    return chart_layout(fig)


def risk_rows(df, column):
    rows = []
    for num, label in [(0, "없음 (0)"), (1, "있음 (1)")]:
        subset = df.loc[df[column].eq(num)]
        people = len(subset)
        stroke_count = int(subset["stroke"].eq(1).sum())
        rate = stroke_count * 100 / people if people else 0.0
        rows.append({"그룹": label, "사람 수": people, "뇌졸중 경험자 수": stroke_count, "비율 (%)": rate})
    return pd.DataFrame(rows)


def ratio_figure(rate_df, column_title):
    fig = go.Figure(
        go.Bar(
            x=rate_df["그룹"],
            y=rate_df["비율 (%)"],
            marker=dict(color=[COLORS["lilac"], COLORS["pink"]], line=dict(color="rgba(255,255,255,.13)", width=1)),
            text=[f"{r:.2f}%" for r in rate_df["비율 (%)"]],
            textposition="outside",
            textfont=dict(size=15, color=COLORS["ink"]),
            customdata=rate_df[["사람 수", "뇌졸중 경험자 수"]].to_numpy(),
            hovertemplate="%{x}<br>뇌졸중 비율: %{y:.2f}%<br>전체: %{customdata[0]:,}명<br>뇌졸중: %{customdata[1]:,}명<extra></extra>",
            width=.5,
        )
    )
    ceiling = float(rate_df["비율 (%)"].max()) if len(rate_df) else 0
    chart_layout(fig, ymax=max(10, ceiling * 1.38))
    fig.update_xaxes(title_text=column_title)
    fig.update_yaxes(title_text="뇌졸중 경험 비율 (%)", ticksuffix="%")
    return fig


with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">✳</span>'
        '<div><div class="brand-name">NEURO / LAB</div>'
        '<div class="brand-small">STROKE DATA STUDIO</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-kicker">WORKSPACE / 02</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-line">한 사람을 한 행으로 보고, 집단별 분포와 비율을 비교합니다.</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="side-kicker">VISUAL CONTROLS</div>', unsafe_allow_html=True)
    bins = st.slider("히스토그램 구간 수", min_value=10, max_value=60, value=30, step=5, help="막대의 개수만 조절합니다. 사람 수나 비율 계산에는 영향을 주지 않습니다.")
    st.caption("흰 점선은 각 분포의 중앙값입니다.")
    st.markdown('<div class="side-kicker">LEGEND</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-line">🟢 뇌졸중 미경험 (0)<br>🔴 뇌졸중 경험 (1)</div>', unsafe_allow_html=True)


st.markdown(
    """
    <div class="lab-hero">
        <div class="hero-eyebrow"><span class="live-dot"></span> NEURO / LAB — EXPLORATION SUITE 002</div>
        <h1>숫자 속의 패턴을<br><span class="hero-highlight">발견하다.</span></h1>
        <p>분포는 어디에 몰려 있을까요? 두 집단은 얼마나 다를까요?
        뇌졸중 경험 여부와 건강 정보의 관계를 그래프로 살피고,
        결측값과 범주형 데이터를 꼼꼼히 점검하는 탐색 공간입니다.</p>
        <div class="hero-status">
          <span class="hero-chip">● 02 / EXPLORE THE DATA</span>
          <span class="hero-chip">6 INTERACTIVE CHARTS</span>
          <span class="hero-chip">PLOTLY POWERED</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    with st.spinner("탐색용 데이터를 읽는 중입니다…"):
        raw = load_data()
except Exception as err:
    st.error("데이터를 불러올 수 없습니다. CSV 주소나 인터넷 연결을 확인하세요.")
    with st.expander("자세한 오류"):
        st.code(str(err))
    st.stop()

missing_columns = [name for name in REQUIRED if name not in raw.columns]
if missing_columns:
    st.error("탐색에 필요한 열이 없습니다: " + ", ".join(missing_columns))
    st.stop()

# 원본 CSV는 캐시에 보관하고, 수치 계산에 필요한 복사본만 사용합니다.
df = raw.copy()
for name in ["age", "avg_glucose_level", "hypertension", "heart_disease", "bmi", "stroke"]:
    df[name] = pd.to_numeric(df[name], errors="coerce")

n = len(df)
n_stroke = int(df["stroke"].eq(1).sum())
n_missing = int(df["bmi"].isna().sum())

c1, c2, c3, c4 = st.columns(4, gap="medium")
for col, index, title, value, foot, tint in [
    (c1, "01", "분석 대상", f"{n:,}", "원본 데이터 행 수", COLORS["mint"]),
    (c2, "02", "뇌졸중 경험", f"{n_stroke:,}", "stroke = 1", COLORS["pink"]),
    (c3, "03", "BMI 결측", f"{n_missing:,}", "BMI 값이 비어 있는 사람", COLORS["lilac"]),
    (c4, "04", "탐색 변수", "6", "나이 · 혈당 · 고혈압 등", COLORS["gold"]),
]:
    with col:
        st.markdown(
            f'<div class="lab-kpi" style="--tint:{tint}"><div class="kpi-id">LIVE / {index}</div>'
            f'<div class="kpi-label">{title}</div><div class="kpi-value">{value}</div>'
            f'<div class="kpi-footer">{foot}</div></div>', unsafe_allow_html=True,
        )

st.divider()
section("01", "분포 · 전체 데이터", "나이와 평균 혈당을 각각 히스토그램으로 살펴보세요. 사이드바에서 구간 수를 바꿀 수 있습니다.")
col_a, col_b = st.columns(2, gap="large")
with col_a:
    with st.container(border=True):
        chart_header("DISTRIBUTION / A", "나이 분포", "전체 사람 · 흰 점선은 중앙값")
        show_chart(hist_figure(df["age"], "나이 (세)", COLORS["mint"], bins))
with col_b:
    with st.container(border=True):
        chart_header("DISTRIBUTION / B", "평균 혈당 분포", "전체 사람 · 흰 점선은 중앙값")
        show_chart(hist_figure(df["avg_glucose_level"], "평균 혈당", COLORS["lilac"], bins))

st.divider()
section("02", "상자그림 · 두 집단 비교", "뇌졸중 미경험(0)과 경험(1)을 비교합니다. 상자는 사분위 범위, 상자 안의 점선은 평균을 나타냅니다.")
col_c, col_d = st.columns(2, gap="large")
with col_c:
    with st.container(border=True):
        chart_header("COMPARISON / A", "뇌졸중 여부에 따른 나이", "중앙값 · 사분위 · 이상치 비교")
        show_chart(box_figure(df, "age", "나이 (세)"))
with col_d:
    with st.container(border=True):
        chart_header("COMPARISON / B", "뇌졸중 여부에 따른 평균 혈당", "중앙값 · 사분위 · 이상치 비교")
        show_chart(box_figure(df, "avg_glucose_level", "평균 혈당"))

st.markdown('<div class="tiny-label">GROUP SUMMARY / 두 집단 평균 비교</div>', unsafe_allow_html=True)
mean_rows = []
for flag, label in [(0, "미경험 (0)"), (1, "경험 (1)")]:
    subset = df.loc[df["stroke"].eq(flag)]
    mean_rows.append({
        "뇌졸중 경험 여부": label,
        "사람 수": len(subset),
        "평균 나이 (세)": round(subset["age"].mean(), 2),
        "평균 혈당": round(subset["avg_glucose_level"].mean(), 2),
    })
st.dataframe(pd.DataFrame(mean_rows), hide_index=True, use_container_width=True)

st.divider()
section("03", "조건별 뇌졸중 비율", "각 막대는 해당 그룹 안에서 stroke = 1인 사람의 비율입니다. 고혈압과 심장병을 각각 독립적으로 비교합니다.")
col_e, col_f = st.columns(2, gap="large")
with col_e:
    with st.container(border=True):
        chart_header("RISK FACTOR / A", "고혈압 유무에 따른 비율", "0 = 고혈압 없음 · 1 = 고혈압 있음")
        show_chart(ratio_figure(risk_rows(df, "hypertension"), "고혈압"))
with col_f:
    with st.container(border=True):
        chart_header("RISK FACTOR / B", "심장병 유무에 따른 비율", "0 = 심장병 없음 · 1 = 심장병 있음")
        show_chart(ratio_figure(risk_rows(df, "heart_disease"), "심장병"))
st.markdown('<div class="note-box"><b>그래프 읽는 법</b>　예를 들어 고혈압이 있는 그룹의 비율은 '
            '“고혈압이 있는 사람 중 뇌졸중 경험자의 비율”입니다. 관찰된 연관성은 인과관계나 개인의 예측 결과를 뜻하지 않습니다.</div>', unsafe_allow_html=True)

st.divider()
section("04", "BMI 결측값 집중 점검", "BMI가 비어 있는 사람만 따로 계산하여, 전체 데이터에서의 뇌졸중 비율과 비교합니다.")
missing_bmi = df.loc[df["bmi"].isna()]

def percent_text(subset):
    return f"{subset['stroke'].eq(1).sum() / len(subset) * 100:.2f}%" if len(subset) else "—"

bmi_summary = pd.DataFrame([
    {"비교 대상": "BMI가 비어 있는 사람", "사람 수": len(missing_bmi), "뇌졸중 경험자 수": int(missing_bmi["stroke"].eq(1).sum()), "뇌졸중 비율": percent_text(missing_bmi)},
    {"비교 대상": "전체 사람", "사람 수": n, "뇌졸중 경험자 수": n_stroke, "뇌졸중 비율": percent_text(df)},
])
st.dataframe(bmi_summary, hide_index=True, use_container_width=True)
st.markdown('<div class="note-box"><b>MISSING DATA NOTE</b>　BMI가 비어 있어도 해당 행을 버리지 않습니다. '
            '위 표는 결측값이 있는 집단을 그대로 사용하여 계산합니다.</div>', unsafe_allow_html=True)

st.divider()
section("05", "흡연 상태별 사람 수", "smoking_status 열에 실제로 기록된 값을 그대로 묶어 셉니다. 'Unknown'도 데이터에 있는 하나의 값입니다.")
smoking_counts = (
    df["smoking_status"]
    .astype("string")
    .fillna("(빈 값)")
    .value_counts(dropna=False)
    .rename_axis("흡연 상태 값")
    .reset_index(name="사람 수")
)
smoking_counts["전체 중 비율"] = smoking_counts["사람 수"].apply(lambda count: f"{100 * count / n:.2f}%" if n else "—")
st.dataframe(smoking_counts, hide_index=True, use_container_width=True)
st.caption(f"합계: {int(smoking_counts['사람 수'].sum()):,}명 / 전체 {n:,}명")

st.divider()
st.markdown('<div class="tiny-label">END OF EXPLORATION / KEEP EXPLORING</div>', unsafe_allow_html=True)
st.page_link("main.py", label="01 · 데이터 소개로 돌아가기", icon="🏠")
st.caption("이 앱은 데이터 분석 교육용입니다. 특정 건강 상태의 원인이나 개인별 의학적 위험을 판단하는 도구가 아닙니다.")
