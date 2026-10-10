"""뇌졸중 예측 실습실 · 데이터 소개.

실행: streamlit run main.py
페이지: pages/1_탐색.py
설치: pip install -r requirements.txt
"""

import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
EXPECTED_COLUMNS = [
    "id", "gender", "age", "hypertension", "heart_disease",
    "ever_married", "work_type", "Residence_type", "avg_glucose_level",
    "bmi", "smoking_status", "stroke",
]

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 각 페이지에서 같은 UI가 보이도록 스타일을 독립적으로 포함한다.
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
    """같은 공개 원본 CSV를 UTF-8로 읽는다."""
    return pd.read_csv(DATA_URL, encoding="utf-8")


def value_kind(series, column):
    if column == "id":
        return "식별번호 (숫자)"
    if column in {"hypertension", "heart_disease", "stroke"}:
        return "0 / 1"
    valid = series.dropna()
    if pd.api.types.is_numeric_dtype(series):
        return f"숫자형 · 고유 값 {valid.nunique():,}개"
    values = [str(v) for v in valid.drop_duplicates().tolist()]
    return " / ".join(values) if len(values) <= 8 else f"범주형 · {len(values)}종"


def section(index, heading, description=""):
    st.markdown(
        f'<div class="section-head"><span class="section-index">{index}</span>'
        f'<span class="section-title">{heading}</span></div>'
        f'<div class="section-help">{description}</div>',
        unsafe_allow_html=True,
    )


def kpi(index, title, value, caption, tint):
    st.markdown(
        f'<div class="lab-kpi" style="--tint:{tint}">'
        f'<div class="kpi-id">METRIC / {index}</div>'
        f'<div class="kpi-label">{title}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-footer">{caption}</div></div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">✳</span>'
        '<div><div class="brand-name">NEURO / LAB</div>'
        '<div class="brand-small">STROKE DATA STUDIO</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-kicker">WORKSPACE / 01</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-line">데이터 소개 → 탐색 → 이후 예측 모델까지 확장할 수 있는 실습 공간입니다.</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("왼쪽의 페이지 목록에서 **탐색**으로 이동하세요.")
    st.markdown('<div class="side-kicker">DATASET</div>', unsafe_allow_html=True)
    st.markdown('<div class="side-line">Stroke Prediction Dataset<br>CSV · UTF-8 · 공개 학습용</div>', unsafe_allow_html=True)


st.markdown(
    """
    <div class="lab-hero">
        <div class="hero-eyebrow"><span class="live-dot"></span> NEURO / LAB — RESEARCH WORKSPACE 001</div>
        <h1>뇌졸중 예측<br><span class="hero-highlight">실습실.</span></h1>
        <p>데이터를 보는 눈에서 예측의 출발점이 만들어집니다.
        나이, 혈당, 생활 습관과 뇌졸중 경험 여부를 담은 자료를 먼저 이해해 보세요.
        열의 뜻을 직접 기록하고 결측값을 확인한 다음, 탐색 페이지에서 패턴을 찾아봅니다.</p>
        <div class="hero-status">
          <span class="hero-chip">● 01 / DATA OVERVIEW</span>
          <span class="hero-chip">02 / EXPLORATION READY ↗</span>
          <span class="hero-chip">CSV · UTF-8</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    with st.spinner("뇌졸중 데이터를 불러오는 중입니다…"):
        df = load_data()
except Exception as err:
    st.error("데이터를 불러오지 못했습니다. 네트워크 연결이나 CSV 주소를 확인해 주세요.")
    with st.expander("오류 내용 확인"):
        st.code(str(err))
    st.stop()

missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
if missing:
    st.error("다음 필수 열이 없습니다: " + ", ".join(missing))
    st.stop()

n = len(df)
strokes = int(pd.to_numeric(df["stroke"], errors="coerce").eq(1).sum())
ratio = 100 * strokes / n if n else 0.0

section("01", "데이터 한눈에 보기", "전체 파일을 기준으로 계산했습니다. 필터를 적용하지 않은 원본 데이터의 수치입니다.")
c1, c2, c3, c4 = st.columns(4, gap="medium")
with c1:
    kpi("01", "전체 사람 수", f"{n:,}<small style='font-size:.39em;color:#9eb5c5'> 명</small>", "데이터 행 수", "#29e8cf")
with c2:
    kpi("02", "열 개수", f"{len(df.columns)}<small style='font-size:.39em;color:#9eb5c5'> 개</small>", "기록된 변수 수", "#ad9bff")
with c3:
    kpi("03", "뇌졸중 경험자", f"{strokes:,}<small style='font-size:.39em;color:#9eb5c5'> 명</small>", "stroke = 1", "#ff7899")
with c4:
    kpi("04", "뇌졸중 비율", f"{ratio:.2f}<small style='font-size:.39em;color:#9eb5c5'> %</small>", "경험자 / 전체 × 100", "#f8cd82")

st.divider()
section("02", "데이터 사전 완성하기", "<b>우리말 뜻</b> 열만 직접 수정할 수 있어요. 교재를 보고 작성하세요. 입력한 내용은 현재 접속 중인 세션에 유지됩니다.")
if "stroke_column_meanings" not in st.session_state:
    st.session_state.stroke_column_meanings = {col: "" for col in df.columns}

schema = pd.DataFrame(
    {
        "열 이름": df.columns,
        "우리말 뜻": [st.session_state.stroke_column_meanings.get(c, "") for c in df.columns],
        "값의 종류": [value_kind(df[c], c) for c in df.columns],
        "빈 값 개수": [int(df[c].isna().sum()) for c in df.columns],
    }
)
edited = st.data_editor(
    schema,
    key="stroke_dictionary_editor_2026",
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    disabled=["열 이름", "값의 종류", "빈 값 개수"],
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름", width="medium"),
        "우리말 뜻": st.column_config.TextColumn("우리말 뜻 ✏️", width="medium", help="교재를 보고 직접 입력하세요."),
        "값의 종류": st.column_config.TextColumn("값의 종류", width="large"),
        "빈 값 개수": st.column_config.NumberColumn("빈 값 개수", format="%d", width="small"),
    },
)
st.session_state.stroke_column_meanings = {
    str(c): "" if pd.isna(m) else str(m)
    for c, m in zip(edited["열 이름"], edited["우리말 뜻"])
}
left, right = st.columns([1, 2], gap="large")
with left:
    st.download_button(
        "↓ 작성한 데이터 사전 저장",
        data=edited.to_csv(index=False).encode("utf-8-sig"),
        file_name="stroke_data_dictionary.csv",
        mime="text/csv",
        use_container_width=True,
    )
with right:
    st.caption(f"누락된 셀 전체 {df.isna().sum().sum():,}개 · 빈 값은 임의로 채우지 않았습니다.")

st.divider()
section("03", "실제 데이터 미리 보기", "CSV의 처음 다섯 행을 가공하지 않고 그대로 표시합니다.")
st.dataframe(df.head(5), hide_index=True, use_container_width=True)

st.divider()
section("04", "출처와 참고 기록", "교재에 적힌 출처를 직접 입력하세요. 데이터 출처를 임의로 만들어 넣지 않았습니다.")
st.text_area(
    "데이터 출처 기록",
    key="stroke_source_note",
    placeholder="교재에 나온 데이터 출처를 여기에 기록하세요…",
    height=115,
    label_visibility="collapsed",
)

st.markdown(
    '<div class="note-box"><b>NEXT STEP / 02</b>　📊 탐색 페이지에서 분포, 상자그림, '
    '고혈압·심장병 비율, BMI 결측값, 흡연 상태를 분석할 수 있어요.</div>',
    unsafe_allow_html=True,
)
st.page_link("pages/1_탐색.py", label="02 · 탐색 대시보드로 이동 ↗", icon="🔬")
st.caption("이 자료는 데이터 분석 교육용이며, 개인의 건강을 진단하거나 실제 위험도를 판단하는 데 사용할 수 없습니다.")
