"""🧠 두근두근 데이터 연구소 - 뇌졸중 예측 실습실: 데이터 소개.

실행: streamlit run main.py
탐색: pages/1_탐색.py · 분류 모델: pages/2_분류_모델.py
"""

import pandas as pd
import streamlit as st


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
COLUMNS = [
    "id", "gender", "age", "hypertension", "heart_disease",
    "ever_married", "work_type", "Residence_type", "avg_glucose_level",
    "bmi", "smoking_status", "stroke",
]

st.set_page_config(
    page_title="뇌졸중 예측 실습실 | 두근두근 데이터 연구소",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🌸 두 페이지가 같은 파스텔 디자인을 사용하도록 CSS를 각각 포함합니다.
st.markdown(
    r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@500;600;700;800;900&display=swap');
:root{--ink:#4b3e68;--muted:#817795;--pink:#ff7bad;--violet:#a68af9;--mint:#75dec5;--line:#f1dded;--paper:#fffafc}
html,body,[data-testid="stApp"]{font-family:'Nunito','Noto Sans KR',sans-serif!important;color:var(--ink)!important}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 12% 3%,#ffe6f0 0,transparent 32%),radial-gradient(circle at 94% 12%,#e5e0ff 0,transparent 36%),radial-gradient(circle at 80% 93%,#e1fff5 0,transparent 29%),#fff9fc!important}
[data-testid="stMain"]{background:transparent!important}
[data-testid="stHeader"]{background:rgba(255,249,252,.76)!important;backdrop-filter:blur(12px)}
[data-testid="stSidebar"]{background:linear-gradient(165deg,#ffecf6 0%,#f4eefe 55%,#edfcf8 100%)!important;border-right:2px solid #fff!important}
[data-testid="stSidebar"] a,[data-testid="stSidebar"] span,[data-testid="stSidebar"] p{color:#64567e!important}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"]{background:rgba(255,255,255,.85)!important;border-radius:14px!important}
.main .block-container,[data-testid="stMainBlockContainer"]{max-width:1240px!important;padding-top:2.2rem!important;padding-bottom:5rem!important}
h1,h2,h3{font-family:'Fredoka','Noto Sans KR',sans-serif!important;color:var(--ink)!important;letter-spacing:-.035em!important}
.stMarkdown p,.stCaption,.stText{color:var(--muted)}
.stButton button,.stDownloadButton button,.stLinkButton a{border:2px solid #f0d8ed!important;border-radius:999px!important;background:#fff!important;color:#755d94!important;font-weight:850!important;box-shadow:0 5px 0 #f5deec!important;transition:transform .15s,box-shadow .15s!important}
.stButton button:hover,.stDownloadButton button:hover,.stLinkButton a:hover{transform:translateY(-2px);box-shadow:0 7px 0 #eacdec!important;border-color:#ff9abc!important}
[data-testid="stSlider"] [role="slider"]{background-color:#ff7bad!important;border-color:#fff!important}
[data-testid="stMetric"]{background:#fff;padding:18px;border-radius:20px}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:2px solid #f1dfed!important;border-radius:18px!important;overflow:hidden!important;background:white!important}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input{border:2px solid #f0d9eb!important;background:#fff!important;color:#5d5277!important;border-radius:17px!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div{border-radius:16px!important;border:2px solid #f0d9eb!important;background:white!important}
hr{border-color:#f1dce9!important;margin-top:2.1rem!important;margin-bottom:2.1rem!important}
.candy-brand{display:flex;align-items:center;gap:11px;font-family:'Fredoka',sans-serif;color:#75548f;margin:5px 0 12px}
.candy-brand .brand-flower{width:42px;height:42px;display:grid;place-items:center;font-size:24px;border-radius:15px;background:#fff;box-shadow:0 5px 0 #e8d9f3}
.candy-brand strong{font-size:17px;letter-spacing:.025em;color:#65517e}
.candy-brand small{display:block;color:#b08eaf;letter-spacing:.1em;font-size:10px}
.side-note{background:#fff9ff;border:1px dashed #e9cce9;border-radius:17px;padding:15px;color:#927b9e;line-height:1.8;font-weight:700;font-size:12px}
.candy-hero{position:relative;overflow:hidden;padding:46px 47px 41px;border-radius:32px;background:linear-gradient(113deg,#ffd6e8 0%,#ffe6f1 42%,#e9e1ff 79%,#dcfbf0 100%);border:3px solid #fff;box-shadow:0 12px 0 #f6e4ed,0 20px 55px rgba(193,126,175,.17);min-height:258px;margin-bottom:35px}
.candy-hero .spark{position:absolute;color:#fff;font-size:26px;text-shadow:0 3px 8px #ed90b7;animation:twinkle 3s ease-in-out infinite}
.candy-hero .spark.a{left:4%;top:9%}.candy-hero .spark.b{right:11%;top:8%;animation-delay:.5s}.candy-hero .spark.c{right:29%;bottom:11%;animation-delay:1s}
.hero-copy{position:relative;z-index:2;max-width:74%}
.hero-eyebrow{display:inline-block;background:#fff9;border:2px solid #fff;border-radius:50px;padding:8px 14px;color:#9a6394;font-weight:900;letter-spacing:.11em;font-size:11px}
.candy-hero h1{font-size:clamp(2.1rem,4.8vw,4.2rem)!important;line-height:1.22!important;margin:16px 0 14px!important;color:#5d4775!important;font-weight:700!important}
.candy-hero .highlight{background:linear-gradient(transparent 60%,#fff49c 61%,#fff49c 89%,transparent 90%);padding:0 4px}
.candy-hero p{color:#755e83!important;font-weight:800;font-size:14px;line-height:1.8;max-width:560px}
.candy-hero .hero-pills{display:flex;gap:7px;flex-wrap:wrap;margin-top:20px}
.candy-hero .hero-pills span{border-radius:30px;background:#fff9;border:1px solid white;color:#8f739d;font-size:11px;font-weight:900;padding:7px 11px}
.hero-buddy{position:absolute;right:6%;top:50%;transform:translateY(-46%);display:flex;align-items:center;flex-direction:column;z-index:1;animation:bounce 4s ease-in-out infinite}
.hero-buddy .buddy-face{display:grid;place-items:center;width:148px;height:148px;font-size:83px;border-radius:47px;background:radial-gradient(circle at 30% 20%,#fff,#fff0fa);border:5px solid white;box-shadow:0 13px 0 #e6d0f4,0 15px 35px #dbaccb99;transform:rotate(-6deg)}
.hero-buddy .buddy-label{margin-top:14px;color:#906d98;background:#fff8;padding:8px 14px;border-radius:999px;font-size:11px;font-weight:900}
.section-title-row{display:flex;align-items:center;gap:12px;margin:13px 0 13px}
.section-emoji{width:46px;height:46px;display:grid;place-items:center;font-size:24px;background:#fff;border:2px solid #fff;border-radius:17px;box-shadow:0 5px 0 #f5ddeb}
.section-title-row h2{font-family:'Fredoka',sans-serif;font-size:25px!important;margin:0!important;font-weight:700!important}
.section-sub{font-size:13px;color:#9785a7;font-weight:800;margin:-4px 0 19px 59px}
.kpi-card{position:relative;min-height:155px;padding:22px 19px 20px;background:white;border:2px solid #fff;border-radius:24px;box-shadow:0 7px 0 var(--base),0 12px 29px rgba(136,98,154,.10);margin-bottom:13px;overflow:hidden}
.kpi-card:after{content:'✦';position:absolute;right:15px;top:8px;color:var(--base);font-size:34px;opacity:.8}
.kpi-card .kpi-label{color:#9685a3;font-weight:900;font-size:12px}
.kpi-card .kpi-number{font-family:'Fredoka',sans-serif;color:#5b4b77;font-size:clamp(1.55rem,2.8vw,2.6rem);margin:8px 0 4px;font-weight:700;letter-spacing:-.02em}
.kpi-card .kpi-foot{color:#a697b4;font-size:11px;font-weight:800}
.candy-panel{background:#fff;border:2px solid #f5e6f0;box-shadow:0 7px 0 #f9eaf2;border-radius:25px;padding:19px 22px;margin:7px 0 20px}
.panel-eyebrow{font-size:11px;font-weight:900;letter-spacing:.16em;color:#df8dab;margin-bottom:9px}
.panel-title{font-family:'Fredoka','Noto Sans KR',sans-serif;color:#5c4b77;font-weight:700;font-size:18px;margin-bottom:5px}
.panel-help{color:#a195ad;font-size:12px;font-weight:750;line-height:1.8}
.rainbow-line{height:7px;background:repeating-linear-gradient(90deg,#ff8eba 0 80px,#ffdb86 80px 150px,#95e5d2 150px 220px,#b6a2ff 220px 300px);border-radius:99px;margin:19px 0}
.sticky-note{background:#fff5cf;border:2px dashed #f9d885;border-radius:18px;padding:16px 20px;color:#a78953;font-weight:800;font-size:12px;line-height:1.9;margin-bottom:16px}
.foot-note{text-align:center;color:#af97b1;font-size:12px;font-weight:800;padding:25px 0 12px}
.chip-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:17px}
.chip{display:inline-block;background:white;border:2px solid #f0ddef;border-radius:999px;padding:8px 12px;color:#9b789d;font-weight:900;font-size:12px}
@keyframes bounce{0%,100%{transform:translateY(-46%)}50%{transform:translateY(-54%)}}
@keyframes twinkle{0%,100%{opacity:.65;transform:scale(.9)}50%{opacity:1;transform:scale(1.25)}}
@media(max-width:800px){.main .block-container,[data-testid="stMainBlockContainer"]{padding-top:1rem!important;padding-left:1rem!important;padding-right:1rem!important}.candy-hero{padding:27px 24px 30px;min-height:240px}.hero-copy{max-width:100%}.hero-buddy{opacity:.19;right:-17px;top:49%}.candy-hero h1{font-size:2.4rem!important}.section-title-row h2{font-size:21px!important}.kpi-card{min-height:130px}}
</style>

""",
    unsafe_allow_html=True,
)



def describe_type(series, name):
    """열의 실제 값 종류(숫자형/범주형)를 설명합니다."""
    if name == "id":
        return "고유번호 · 정수"
    if name in {"stroke", "hypertension", "heart_disease"}:
        return "0 / 1"
    values = series.dropna()
    if pd.api.types.is_numeric_dtype(series):
        if name == "age":
            return "숫자 · 나이"
        return "숫자 · 연속형"
    unique = [str(x) for x in values.unique()]
    return " / ".join(unique) if len(unique) <= 5 else f"범주형 · {len(unique)}종"


def section(icon, title, detail=""):
    st.markdown(
        f'<div class="section-title-row"><div class="section-emoji">{icon}</div>'
        f'<h2>{title}</h2></div><div class="section-sub">{detail}</div>',
        unsafe_allow_html=True,
    )


def kpi(label, value, detail, shade):
    st.markdown(
        f'<div class="kpi-card" style="--base:{shade}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-number">{value}</div>'
        f'<div class="kpi-foot">{detail}</div></div>',
        unsafe_allow_html=True,
    )



# 각 페이지가 동일한 URL 및 업로드 데이터를 공유합니다.
from pathlib import Path
from io import BytesIO

DEFAULT_CSV_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
PROJECT_ROOT = Path(__file__).resolve().parent
PAGE_CODE = "home"


def cute_navigation():
    """기본 Streamlit 페이지 메뉴 사용: 미등록 페이지 링크로 앱이 중단되지 않도록 합니다."""
    st.markdown("### 🧭 연구실 이동하기")
    st.info("🍬 사이드바 맨 위의 기본 페이지 목록에서 **main · 1_탐색 · 2_분류_모델**을 골라 주세요.")
    needed = ["pages/1_탐색.py", "pages/2_분류_모델.py"]
    missing = [path for path in needed if not (PROJECT_ROOT / path).is_file()]
    if missing:
        st.warning("🌷 아직 파일이 없어요: " + ", ".join(missing))
        st.caption("GitHub의 pages 폴더에 정확한 이름으로 올려 주세요.")
    else:
        st.caption("✅ 탐색·분류 모델 파일이 모두 있어요!")

def cute_data_controls():
    st.divider()
    st.markdown("### 📂 데이터 불러오기")
    st.caption("기본 CSV가 자동으로 연결돼요. 주소를 바꾸거나 CSV 파일을 직접 올릴 수도 있어요.")
    current = st.session_state.get("stroke_source_url", DEFAULT_CSV_URL)
    key_number = st.session_state.get("stroke_upload_reset", 0)
    entered = st.text_input(
        "CSV 주소 (직접 입력 가능)", value=current,
        key=f"csv_url_input_{PAGE_CODE}_{key_number}",
        help="CSV 파일의 직접 주소를 붙여 넣으세요. 입력 후 Enter를 누르면 적용돼요.",
    ).strip()
    st.session_state["stroke_source_url"] = entered or DEFAULT_CSV_URL
    uploaded = st.file_uploader(
        "또는 CSV 파일 업로드", type=["csv"],
        key=f"csv_upload_{PAGE_CODE}_{key_number}",
    )
    if uploaded is not None:
        st.session_state["stroke_upload_bytes"] = uploaded.getvalue()
        st.session_state["stroke_upload_name"] = uploaded.name
    if st.session_state.get("stroke_upload_bytes") is not None:
        st.success("🍡 업로드한 파일을 사용하고 있어요.")
        if st.button("업로드 취소 · 주소로 돌아가기", key=f"clear_csv_{PAGE_CODE}", use_container_width=True):
            st.session_state.pop("stroke_upload_bytes", None)
            st.session_state.pop("stroke_upload_name", None)
            st.session_state["stroke_upload_reset"] = key_number + 1
            st.rerun()
    else:
        st.caption("🍓 현재 데이터: 입력한 CSV 주소")
    if st.button("기본 데이터 주소로 복원", key=f"reset_url_{PAGE_CODE}", use_container_width=True):
        st.session_state["stroke_source_url"] = DEFAULT_CSV_URL
        st.session_state.pop("stroke_upload_bytes", None)
        st.session_state.pop("stroke_upload_name", None)
        st.session_state["stroke_upload_reset"] = key_number + 1
        st.rerun()


@st.cache_data(ttl=600, show_spinner=False)
def _read_csv_url(url):
    return pd.read_csv(url, encoding="utf-8")


def load_data():
    """우선 적용된 CSV 업로드, 아니면 지정한 UTF-8 CSV 주소를 불러옵니다."""
    payload = st.session_state.get("stroke_upload_bytes")
    if payload is not None:
        return pd.read_csv(BytesIO(payload), encoding="utf-8")
    url = st.session_state.get("stroke_source_url", DEFAULT_CSV_URL)
    if not url.startswith(("https://", "http://")):
        raise ValueError("CSV 주소는 https:// 또는 http:// 로 시작해야 해요.")
    return _read_csv_url(url)


def explain_load_failure(exc):
    st.error("🍓 데이터를 읽지 못했어요. 왼쪽 '데이터 불러오기'에서 주소를 확인하거나 CSV를 직접 올려 주세요.")
    st.caption(f"상세 원인: {type(exc).__name__} — {exc}")
    st.caption("기본 주소: " + DEFAULT_CSV_URL)
with st.sidebar:
    st.markdown(
        '<div class="candy-brand"><div class="brand-flower">🌷</div>'
        '<div><strong>두근두근 연구소</strong><small>SWEET DATA LAB</small></div></div>',
        unsafe_allow_html=True,
    )
    cute_navigation()
    cute_data_controls()
    st.divider()
    st.markdown(
        '<div class="side-note">🍡 <b>어서 와!</b><br>'
        '사이드바 맨 위의 기본 페이지 메뉴에서 <b>탐색</b> 또는 <b>분류 모델</b>을 누르면 '
        '그래프 놀이터로 이동할 수 있어.<br>'
        '홈에서는 데이터를 먼저 알아보자! ✨</div>',
        unsafe_allow_html=True,
    )
    st.caption("🎀 이 프로젝트는 데이터 학습용이며 의료 진단 도구가 아니에요.")

st.markdown(
    """
    <div class="candy-hero">
      <span class="spark a">✳</span><span class="spark b">✧</span>
      <span class="spark c">✦</span>
      <div class="hero-copy">
        <div class="hero-eyebrow">💌 HELLO, LITTLE RESEARCHER!</div>
        <h1>두근두근<br><span class="highlight">뇌졸중 예측 실습실</span> ♡</h1>
        <p>어려운 숫자도 귀여운 연구실에서는 조금 더 친해질 수 있어요.
        데이터를 살펴보고, 비어 있는 값을 찾고, 직접 설명을 채워 봐요!</p>
        <div class="hero-pills"><span>🍓 데이터 소개</span>
        <span>🧁 12가지 항목</span><span>🫧 탐색 · 분류 모델 페이지</span></div>
      </div>
      <div class="hero-buddy"><div class="buddy-face">🧠</div>
        <div class="buddy-label">오늘도 차근차근! ♡</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    df = load_data()
except Exception as exc:
    explain_load_failure(exc)
    st.stop()

missing_cols = [c for c in COLUMNS if c not in df.columns]
if missing_cols:
    st.error("데이터의 열 구성이 예상과 달라요: " + ", ".join(missing_cols))
    st.stop()

stroke_number = pd.to_numeric(df["stroke"], errors="coerce")
total = len(df)
stroke_cases = int((stroke_number == 1).sum())
rate = (stroke_cases / total * 100) if total else 0.0

section("🧋", "숫자로 만나는 데이터", "4개의 숫자 카드로 전체 데이터의 규모를 확인해요!")
card_cols = st.columns(4, gap="medium")
metrics = [
    ("전체 사람 수", f"{total:,}명", "데이터에 기록된 인원", "#ffd2e6"),
    ("전체 열 개수", f"{df.shape[1]:,}개", "수집된 정보 종류", "#e6d6ff"),
    ("뇌졸중 경험자", f"{stroke_cases:,}명", "stroke가 1인 사람", "#c7f5e8"),
    ("뇌졸중 경험 비율", f"{rate:.2f}%", "전체 사람 중 비율", "#ffe7b2"),
]
for col, metric in zip(card_cols, metrics):
    with col:
        kpi(*metric)

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("📒", "데이터 사전 만들기", "'우리말 뜻' 열에 교재를 보고 직접 설명을 적어 봐요.")
st.markdown(
    '<div class="sticky-note">✏️ 직접 채워 보는 공간! '
    '우리말 뜻 칸만 수정할 수 있어요. 다른 칸은 원본 데이터를 기준으로 자동 작성돼요.</div>',
    unsafe_allow_html=True,
)
if "my_column_meanings" not in st.session_state:
    st.session_state["my_column_meanings"] = {name: "" for name in df.columns}

dictionary = pd.DataFrame(
    {
        "열 이름": df.columns,
        "우리말 뜻": [st.session_state["my_column_meanings"].get(c, "") for c in df.columns],
        "값의 종류": [describe_type(df[c], c) for c in df.columns],
        "빈 값 개수": [int(df[c].isna().sum()) for c in df.columns],
    }
)
modified = st.data_editor(
    dictionary,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    disabled=["열 이름", "값의 종류", "빈 값 개수"],
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름", width="medium"),
        "우리말 뜻": st.column_config.TextColumn("우리말 뜻 ✏️", width="large", help="교재를 참고해 입력하세요"),
        "값의 종류": st.column_config.TextColumn("값의 종류", width="large"),
        "빈 값 개수": st.column_config.NumberColumn("빈 값 개수", format="%d"),
    },
    key="column_dictionary_editor",
)
for _, entry in modified.iterrows():
    value = entry["우리말 뜻"]
    st.session_state["my_column_meanings"][entry["열 이름"]] = "" if pd.isna(value) else str(value)

st.download_button(
    "🎀 내가 채운 데이터 사전 저장하기",
    data=modified.to_csv(index=False).encode("utf-8-sig"),
    file_name="나만의_뇌졸중_데이터사전.csv",
    mime="text/csv",
)

st.write("")
section("🔍", "데이터 살짝 들여다보기", "원본 CSV의 처음 5줄을 그대로 보여 줘요.")
st.dataframe(df.head(5), use_container_width=True, hide_index=True)

st.write("")
section("💌", "데이터 출처 기록하기", "교재에서 출처 정보를 찾아 이곳에 적어 주세요.")
if "my_source_note" not in st.session_state:
    st.session_state["my_source_note"] = ""
source_note = st.text_area(
    "데이터 출처 (직접 입력)",
    value=st.session_state["my_source_note"],
    placeholder="여기에 교재에 있는 데이터 출처를 적어 보세요. ✨",
    height=100,
    key="my_source_input",
)
st.session_state["my_source_note"] = source_note
st.markdown(
    '<div class="candy-panel"><div class="panel-eyebrow">ORIGINAL DATA LINK</div>'
    '<div class="panel-title">🍬 CSV 원본 주소</div>'
    '<div class="panel-help">프로그램이 읽는 데이터 주소예요. 교재의 출처 설명은 위 칸에 직접 적어 주세요.</div></div>',
    unsafe_allow_html=True,
)
st.code(st.session_state.get("stroke_source_url", DEFAULT_CSV_URL), language=None)
st.markdown(
    '<div class="foot-note">♡ made with curiosity & tiny sparkles · SWEET DATA LAB ♡</div>',
    unsafe_allow_html=True,
)
