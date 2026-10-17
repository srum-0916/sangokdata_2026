"""💗 두근두근 뇌졸중 연구소 ♡

실행: streamlit run main.py
- 이 파일 하나에 데이터 소개 / 탐색 / 분류 모델이 모두 들어 있습니다.
- 사이드바 radio로 페이지를 전환하므로 pages 폴더가 필요하지 않습니다.
- 데이터는 아래 고정된 공개 URL에서 UTF-8로 자동 로드합니다.
"""

import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
REQUIRED_COLUMNS = [
    "id", "gender", "age", "hypertension", "heart_disease", "ever_married",
    "work_type", "Residence_type", "avg_glucose_level", "bmi", "smoking_status", "stroke",
]
FEATURE_NAMES = {
    "age": "나이", "avg_glucose_level": "평균 혈당 💜", "bmi": "BMI",
    "hypertension": "고혈압", "heart_disease": "심장병",
}
FEATURES = list(FEATURE_NAMES)
PINK = "#FA7FAA"
MINT = "#6ACFB7"
PURPLE = "#9B83F3"
YELLOW = "#FFC96E"
INK = "#584A70"

st.set_page_config(
    page_title="두근두근 러블리 뇌졸중 연구소 💗",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

home_page = st.Page("main.py", title="홈", icon="🏠", default=True)
dashboard_page = st.Page("pages/1_탐색.py", title="탐색", icon="📊")
settings_page = st.Page("pages/2_분류_모델.py", title="모델", icon="⚙️")

# 한 번만 작성한 CSS가 세 화면에 공통 적용됩니다. 따옴표가 정상적으로 닫혀 있습니다.
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@500;600;700;800;900&display=swap');
:root { --ink:#584a70; --pink:#fa7faa; --purple:#9b83f3; --mint:#6acfb7; }
html,body,[class*="css"],.stApp {font-family:'Nunito','Noto Sans KR',sans-serif;}
[data-testid="stAppViewContainer"] {
  background: radial-gradient(ellipse at 5% 9%,#ffe3ee 0,transparent 34%),
              radial-gradient(ellipse at 92% 8%,#e9e1ff 0,transparent 33%),
              radial-gradient(ellipse at 75% 95%,#e4fff4 0,transparent 38%),#fffbfd;
}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {background:linear-gradient(165deg,#ffeff6,#f3eeff 62%,#edfff9);border-right:2px solid #fff;}
[data-testid="stSidebar"] * {color:#6b597e;}
[data-testid="stSidebarNav"] {display:none;}
[data-testid="stMainBlockContainer"],.main .block-container {max-width:1280px;padding-top:1.7rem;padding-bottom:4rem;}
h1,h2,h3 {color:var(--ink)!important;letter-spacing:-.035em!important;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:2px solid #f4dfed;border-radius:19px;overflow:hidden;}
[data-testid="stPlotlyChart"]{border-radius:22px;overflow:hidden;}
[data-testid="stWidgetLabel"] p {font-weight:800;color:#77638d;font-size:14px;}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div {border-radius:16px;border:2px solid #f1d5e8;background:white;}
[data-testid="stTextArea"] textarea {border:2px solid #eed7ea;border-radius:16px;background:#fff;}
[data-testid="stSlider"] [role="slider"] {background:var(--pink);border-color:white;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {display:flex;padding:13px 12px;margin:5px 0;border:1.5px solid #f2dceb;background:rgba(255,255,255,.8);border-radius:16px;font-weight:900!important;transition:.15s;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:#fff;box-shadow:0 5px 15px #eccbe544;transform:translateY(-1px);}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {border-color:#ed9fca;background:#fff2f8;box-shadow:0 4px 0 #f4d1e4;}
[data-testid="stSidebar"] [data-testid="stRadio"] label p {font-weight:900!important;color:#69547b!important;}
.stButton button,.stDownloadButton button {background:#fff!important;color:#916b98!important;border:2px solid #f1d9e9!important;border-radius:999px!important;font-weight:900!important;box-shadow:0 4px 0 #f4e0ed!important;}
.cute-brand {display:flex;align-items:center;gap:12px;margin:8px 0 26px;}
.cute-logo {display:grid;place-items:center;width:51px;height:51px;border:3px solid white;border-radius:18px;background:white;box-shadow:0 5px 0 #e9d9f5;font-size:28px;}
.cute-brand strong {font-size:19px;color:#725785;}
.cute-brand small {display:block;font-size:10px;font-weight:900;color:#c18ead;letter-spacing:.16em;}
.cute-note {background:#fff;border:2px dashed #efd1e9;border-radius:19px;padding:15px 16px;color:#9578a0;font-size:13px;line-height:1.85;font-weight:800;}
.cute-hero {position:relative;overflow:hidden;background:linear-gradient(112deg,#ffd7e9 0%,#ffe9f2 37%,#ebe1ff 72%,#dffff2 100%);border:3px solid white;border-radius:32px;box-shadow:0 11px 0 #f8e6f0,0 23px 40px #d9b3d022;padding:44px 47px;margin-bottom:39px;min-height:230px;}
.cute-hero .tag {display:inline-block;padding:8px 13px;border:2px solid white;background:#fff9;border-radius:99px;font-size:11px;font-weight:900;color:#a36c9f;letter-spacing:.08em;}
.cute-hero h1 {font-size:clamp(2.0rem,4vw,3.55rem)!important;line-height:1.25;margin:18px 0 13px!important;color:#634878!important;max-width:76%;}
.cute-hero p {font-size:14px;color:#806889!important;line-height:1.95;font-weight:800;max-width:65%;}
.cute-hero .mascot {position:absolute;right:6%;top:19%;height:134px;width:134px;border-radius:39px;display:grid;place-items:center;background:#fff9;border:5px solid white;box-shadow:0 11px 0 #e5d7f4;font-size:74px;transform:rotate(-7deg);animation:floaty 4s ease-in-out infinite;}
.cute-hero .sparkle{position:absolute;right:24%;top:16%;font-size:34px;color:#fff;text-shadow:0 3px 8px #e39cbd;}
@keyframes floaty {0%,100%{transform:translateY(0) rotate(-7deg);}50%{transform:translateY(-10px) rotate(-3deg);}}
.section-name {display:flex;align-items:center;gap:12px;margin:18px 0 10px;}
.section-icon {background:white;width:46px;height:46px;display:grid;place-items:center;border-radius:17px;font-size:22px;border:2px solid #f7e3ef;box-shadow:0 5px 0 #f8e7ef;}
.section-name h2 {font-size:25px!important;margin:0!important;font-weight:900!important;}
.section-desc {color:#9a86a8;font-weight:800;font-size:12px;margin:3px 0 17px 59px;}
.kpi {padding:23px 21px;position:relative;background:#fff;border:2px solid white;border-radius:24px;box-shadow:0 7px 0 var(--tint),0 12px 22px #c6a0be22;min-height:145px;margin-bottom:14px;}
.kpi:after{content:'✦';position:absolute;right:15px;top:10px;color:var(--tint);font-size:30px;}
.kpi .label{color:#9382a3;font-weight:900;font-size:12px;}
.kpi .number{font-size:clamp(1.55rem,2.5vw,2.6rem);font-weight:900;color:#55456f;margin:7px 0 2px;line-height:1.17;}
.kpi .foot{color:#aa95b1;font-weight:800;font-size:11px;}
.cute-card{background:white;border:2px solid #f5e4ef;border-radius:22px;padding:20px 23px;margin:5px 0 15px;box-shadow:0 6px 0 #faeaf2;}
.cute-card h3{font-size:17px!important;font-weight:900;margin:0 0 7px!important;}
.cute-card p{color:#9b89a8;line-height:1.8;font-size:12px;font-weight:750;margin:0;}
.cute-alert{border:2px dashed #efd3aa;border-radius:16px;background:#fff8dd;color:#a3845e;padding:14px 18px;font-size:13px;font-weight:800;line-height:1.8;margin:14px 0;}
.cute-divider {margin:26px 0;height:7px;border-radius:7px;background:repeating-linear-gradient(90deg,#ff92bd 0 78px,#ffdf98 78px 156px,#a7ead4 156px 234px,#c4b3ff 234px 312px);}
.soft-footer{font-size:12px;color:#ad93ac;text-align:center;padding:30px 0 10px;font-weight:800;}
@media(max-width:760px){.cute-hero{padding:26px 24px;min-height:210px}.cute-hero h1,.cute-hero p{max-width:100%}.cute-hero .mascot{right:-25px;opacity:.17}.section-name h2{font-size:20px!important}[data-testid="stMainBlockContainer"]{padding:1.2rem 1rem 3rem;}}
</style>
""",
    unsafe_allow_html=True,
)


def safe(value):
    return html.escape(str(value))


def hero(tag, title, description, mascot):
    st.markdown(
        f'<div class="cute-hero"><span class="tag">{safe(tag)}</span>'
        f'<h1>{safe(title)}</h1><p>{safe(description)}</p>'
        f'<div class="sparkle">✧</div><div class="mascot">{safe(mascot)}</div></div>',
        unsafe_allow_html=True,
    )


def section(icon, title, desc=""):
    st.markdown(
        f'<div class="section-name"><span class="section-icon">{safe(icon)}</span>'
        f'<h2>{safe(title)}</h2></div><div class="section-desc">{safe(desc)}</div>',
        unsafe_allow_html=True,
    )


def card(label, value, note, tint="#FFD9E9"):
    st.markdown(
        f'<div class="kpi" style="--tint:{tint}"><div class="label">{safe(label)}</div>'
        f'<div class="number">{safe(value)}</div><div class="foot">{safe(note)}</div></div>',
        unsafe_allow_html=True,
    )


def panel(title, detail=""):
    st.markdown(
        f'<div class="cute-card"><h3>{safe(title)}</h3><p>{safe(detail)}</p></div>',
        unsafe_allow_html=True,
    )


def cute_plot(fig, height=360):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito, Noto Sans KR, sans-serif", color=INK, size=12),
        margin=dict(l=24, r=18, t=38, b=30),
        hoverlabel=dict(bgcolor="#fff9fd", font_color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0),
    )
    fig.update_xaxes(gridcolor="#f6e9f1", zeroline=False, linecolor="#eddaeb")
    fig.update_yaxes(gridcolor="#f6e9f1", zeroline=False, linecolor="#eddaeb")
    return fig


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    """모든 화면에서 항상 동일한 온라인 CSV를 자동으로 읽습니다."""
    df = pd.read_csv(DATA_URL, encoding="utf-8")
    missing = [name for name in REQUIRED_COLUMNS if name not in df.columns]
    if missing:
        raise ValueError("원본 CSV에서 다음 열을 찾지 못했어요: " + ", ".join(missing))
    return df


def describe_series(series, col):
    if col == "id":
        return "번호를 나타내는 정수 🔢"
    if col in ("hypertension", "heart_disease", "stroke"):
        return "0 / 1"
    if pd.api.types.is_numeric_dtype(series):
        return "연속해서 나타나는 숫자들이에요 💞"
    values = [str(v) for v in series.dropna().unique()]
    if len(values) <= 6:
        return " / ".join(values)
    return f"종류별로 나뉘는 값 · {len(values)}가지 🎀"


def summary_rate(data):
    if len(data) == 0:
        return 0.0
    return float(pd.to_numeric(data["stroke"], errors="coerce").mean()) * 100


def intro_screen(df):
    hero("💌 HELLO, CUTIE RESEARCHER ♡", "💗 두근두근 뇌졸중 연구소 ♡",
         "어서 와아~! 💖 귀여운 데이터들이 벌써 기다리고 있어! 표도 채우고, 그래프랑 AI 모델까지 하트 뿅뿅 탐험해 보자아~! 🥰🌷", "🧠")
    section("🧁", "우리 데이터 친구들 만나볼까~? 💕", "숫자 친구들이 알아서 쏙쏙 계산해 줄 거야~! ✨")
    n_stroke = int(df["stroke"].eq(1).sum())
    cols = st.columns(4)
    items = [
        ("모두 몇 명일까~? 💗", f"{len(df):,}명", "함께 살펴볼 데이터 친구들이야 🧸", "#ffd8e8"),
        ("속성 친구는 몇 개~? 🎀", f"{df.shape[1]}개", "서로 다른 특징들이 쪼르르 💜", "#ddceff"),
        ("뇌졸중 경험한 사람 💗", f"{n_stroke:,}명", "stroke = 1", "#c5f0e2"),
        ("경험 비율은 얼마일까~? 💌", f"{100*n_stroke/len(df):.2f}%", "전체 사람 가운데 차지하는 비율이야 🌸", "#ffe7ba"),
    ]
    for col, values in zip(cols, items):
        with col:
            card(*values)
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("📝", "나만의 데이터 사전 꾸미기~! ✏️💞", "우리말 뜻 칸은 교재를 보고 직접 예쁘게 채워 줘~! 💌 나머지는 준비해 뒀어 🎀")
    if "column_notes" not in st.session_state:
        st.session_state["column_notes"] = {col: "" for col in df.columns}
    initial = pd.DataFrame([
        {"열 이름": col, "우리말 뜻": st.session_state["column_notes"].get(col, ""),
         "값의 종류": describe_series(df[col], col), "빈 값 개수": int(df[col].isna().sum())}
        for col in df.columns
    ])
    edited = st.data_editor(
        initial, hide_index=True, use_container_width=True, num_rows="fixed",
        disabled=["열 이름", "값의 종류", "빈 값 개수"],
        column_config={"우리말 뜻": st.column_config.TextColumn("우리말 뜻 적기 ✏️💗", help="교재를 보면서 사랑스럽게 채워 줘~! 💖")},
        key="column_dictionary",
    )
    st.session_state["column_notes"] = dict(zip(edited["열 이름"], edited["우리말 뜻"].fillna("")))
    st.download_button("💌 내가 꾸민 데이터 사전 간직하기~! ♡", data=edited.to_csv(index=False).encode("utf-8-sig"),
                       file_name="stroke_data_dictionary.csv", mime="text/csv")
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🍰", "데이터 친구들 첫 5줄 엿보기~! 👀💕", "원본 그대로 다섯 줄만 살포시 보여 줄게~! 🌷")
    st.dataframe(df.head(5), hide_index=True, use_container_width=True)
    section("📚", "데이터가 온 곳도 적어 주라~! 📚💌", "교재 속 출처를 이곳에 콕콕 적어 주면 완벽해~! 💗")
    st.text_area("💌 출처 메모 남기기", placeholder="교재 속 출처를 이쪽에 적어 줄래~? 🥰💞", key="source_memo", height=100)
    st.caption("💗 데이터가 살고 있는 주소: " + DATA_URL)


def hist_figure(series, label, color, bins=28):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=series.dropna(), nbinsx=bins, marker_color=color,
                               opacity=.91, hovertemplate="값은 %{x} 💖<br>여기에 %{y:,}명이 모였어~!<extra></extra>"))
    fig.update_layout(bargap=.085, xaxis_title=label, yaxis_title="사람 수 (명) 💗")
    return cute_plot(fig)


def box_figure(data, feature, label):
    fig = go.Figure()
    for state, name, color in [(0, "경험 없음 (0) 💚 💚", MINT), (1, "뇌졸중 경험 (1) 💗", PINK)]:
        values = data.loc[data["stroke"] == state, feature].dropna()
        fig.add_trace(go.Box(y=values, name=name, marker_color=color, line_color=color,
                             boxmean=True, boxpoints=False,
                             hovertemplate=f"{name}<br>{label}: %{{y:.2f}}<extra></extra>"))
    fig.update_layout(yaxis_title=label)
    return cute_plot(fig)


def rate_figure(df, col, title):
    categories = [(0, "없음 (0) 💚"), (1, "있음 (1) 💗")]
    rates, sizes = [], []
    for binary, _ in categories:
        selected = df[df[col] == binary]
        rates.append(summary_rate(selected))
        sizes.append(len(selected))
    fig = go.Figure(go.Bar(
        x=[x[1] for x in categories], y=rates,
        marker_color=[MINT, PINK], text=[f"{v:.2f}%" for v in rates], textposition="outside",
        customdata=sizes, hovertemplate="%{x}<br>뇌졸중 비율은 %{y:.2f}% 💕<br>모두 %{customdata:,}명이야~!<extra></extra>",
    ))
    fig.update_layout(yaxis_title="뇌졸중 경험 비율 (%) 💞", yaxis_range=[0, max(rates)*1.33+1], title=None)
    return cute_plot(fig)


def explore_screen(df):
    hero("🍭 LOVELY DATA PLAYGROUND ♡", "💖 말랑말랑 데이터 탐색 놀이터 ♡",
         "데이터 속에 어떤 비밀이 숨어 있을까~? 💞 나이와 혈당, 뇌졸중 경험과 빈 값까지 같이 찾아보자아~! 🔍🎀", "🔎")
    section("🍓", "나이랑 혈당 친구들이 어디 모였을까~? 🍓", "막대가 클수록 그 구간에 사람이 많이 모인 거야~! 💕")
    bins = st.slider("🍬 막대 구간은 몇 개로 나눠 볼까~?", min_value=10, max_value=60, value=28, step=2, key="bin_slider")
    left, right = st.columns(2)
    with left:
        panel("🍑 나이는 어떻게 퍼져 있을까~? ♡", "가로로 나이를, 세로로 사람 수를 봐 줘~! 💗")
        st.plotly_chart(hist_figure(df["age"], "나이 (세)", PINK, bins), use_container_width=True)
    with right:
        panel("🍋 혈당은 어디에 모여 있을까~? ♡", "가로로 혈당을, 세로로 사람 수를 봐 줘~! 💗")
        st.plotly_chart(hist_figure(df["avg_glucose_level"], "평균 혈당 💜", PURPLE, bins), use_container_width=True)

    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🧸", "뇌졸중 경험에 따라 뭐가 다를까~? 🎀", "상자 속 가운데 선은 중앙값이야~! 평균값도 찾아보자 💌")
    left, right = st.columns(2)
    with left:
        panel("🎀 나이 차이 살펴보기~! ♡")
        st.plotly_chart(box_figure(df, "age", "나이 (세)"), use_container_width=True)
    with right:
        panel("🫧 혈당 차이 살펴보기~! ♡")
        st.plotly_chart(box_figure(df, "avg_glucose_level", "평균 혈당 💜"), use_container_width=True)
    averages = df.groupby("stroke")[["age", "avg_glucose_level"]].mean().reindex([0, 1]).round(2)
    averages.index = ["경험 없음 (0) 💚 💚", "뇌졸중 경험 (1) 💗"]
    averages.columns = ["평균 나이 💗", "평균 혈당 💜"]
    st.markdown("**🌷 두 친구 그룹의 평균을 비교해 볼까~? 💞**")
    st.dataframe(averages, use_container_width=True)

    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("💗", "고혈압·심장병에 따라 비율이 달라질까~? 💖", "각 그룹에서 stroke=1인 사람의 비율을 비교해 보자~! 🌷")
    left, right = st.columns(2)
    with left:
        panel("🌼 고혈압 여부에 따른 비율~! 💕")
        st.plotly_chart(rate_figure(df, "hypertension", "고혈압"), use_container_width=True)
    with right:
        panel("🌻 심장병 여부에 따른 비율~! 💕")
        st.plotly_chart(rate_figure(df, "heart_disease", "심장병"), use_container_width=True)

    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🧩", "BMI가 비어 있는 데이터 친구는 누구~? 🧩💗", "BMI가 비어 있는 그룹과 전체의 뇌졸중 경험 비율을 나란히 볼까~? 💞")
    missing_bmi = df[df["bmi"].isna()]
    table = pd.DataFrame([
        {"비교 집단": "BMI가 비어 있는 사람 🫧", "사람 수": len(missing_bmi),
         "뇌졸중 경험한 사람 💗": int(missing_bmi["stroke"].eq(1).sum()), "뇌졸중 비율 (%)": round(summary_rate(missing_bmi), 2)},
        {"비교 집단": "전체 친구들 💕", "사람 수": len(df),
         "뇌졸중 경험한 사람 💗": int(df["stroke"].eq(1).sum()), "뇌졸중 비율 (%)": round(summary_rate(df), 2)},
    ])
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🚬", "흡연 상태별로 몇 명일까~? 🚬💌", "Unknown은 모름·미기록이라는 표시야~! 진짜 빈 값(NaN)이랑은 달라 💗")
    smoking_counts = df["smoking_status"].fillna("(빈 값)").value_counts(dropna=False)
    smoking_table = pd.DataFrame({"흡연 상태": smoking_counts.index,
                                  "사람 수": smoking_counts.values,
                                  "전체 중 비율 (%) 💞": (smoking_counts.values / len(df) * 100).round(2)})
    c1, c2 = st.columns([1, 1])
    with c1:
        st.dataframe(smoking_table, hide_index=True, use_container_width=True)
    with c2:
        fig = go.Figure(go.Pie(labels=smoking_table["흡연 상태"], values=smoking_table["사람 수"],
                               hole=.66, marker=dict(colors=[PINK,PURPLE,MINT,YELLOW,"#cfc9d8"]),
                               textinfo="percent", hovertemplate="%{label}<br>%{value:,}명<extra></extra>"))
        fig.update_layout(showlegend=True)
        st.plotly_chart(cute_plot(fig, 315), use_container_width=True)


def split_train_test(df, selected):
    """ID 정렬 뒤 열 명마다 앞 세 명은 테스트, 나머지는 훈련으로 고정."""
    d = df.copy()
    for col in ["id", "stroke"] + selected:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d = d.dropna(subset=["id", "stroke"]).sort_values("id", kind="stable").reset_index(drop=True)
    test_flag = (pd.Series(range(len(d)), index=d.index) % 10) < 3
    train, test = d.loc[~test_flag].copy(), d.loc[test_flag].copy()
    if len(train) == 0 or len(test) == 0:
        raise ValueError("훈련 또는 채점 데이터가 텅 비었어~! 다시 확인해 줄래? 🥺")
    if "bmi" in selected:
        # 채점용에는 손대지 않고 훈련 데이터로만 계산한 중앙값을 두 곳에 적용한다.
        mid = train["bmi"].median()
        if pd.isna(mid):
            raise ValueError("훈련용 BMI가 모두 비어 있어서 중앙값을 못 구했어~! 🥺")
        train["bmi"] = train["bmi"].fillna(mid)
        test["bmi"] = test["bmi"].fillna(mid)
    if train[selected].isna().any().any() or test[selected].isna().any().any():
        raise ValueError("선택한 속성에 아직 빈 값이 남아 있어~! 🫧")
    return train, test


def fit_models(train, selected):
    x = train[selected]
    y = train["stroke"].astype(int)
    if y.nunique() < 2:
        raise ValueError("훈련 데이터에 0과 1이 모두 있어야 모델이 공부할 수 있어~! 💌")
    probability = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42))
    question = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=42)
    probability.fit(x, y)
    question.fit(x, y)
    return probability, question


def tree_explanation(model, selected):
    tree = model.tree_
    answers = []
    def visit(node, depth, prefix):
        indent = "   " * depth
        left, right = int(tree.children_left[node]), int(tree.children_right[node])
        if left < 0:
            winner = int(model.classes_[tree.value[node][0].argmax()])
            result = "뇌졸중(1)" if winner == 1 else "뇌졸중 아님(0)"
            answers.append(f"{indent}{prefix}🍡 두근두근 결과는~? {result} (훈련 {tree.n_node_samples[node]}명)")
            return
        name = FEATURE_NAMES[selected[int(tree.feature[node])]]
        threshold = float(tree.threshold[node])
        answers.append(f"{indent}{prefix}💭 하트 질문 {depth+1}: {name} ≤ {threshold:.2f}? ({tree.n_node_samples[node]}명)")
        visit(left, depth+1, "네에~ 💗 → ")
        visit(right, depth+1, "아니야~ 💜 → ")
    visit(0, 0, "")
    return "\n".join(answers)


def axis_bounds(series):
    lo, hi = float(series.min()), float(series.max())
    if lo == hi:
        return lo-1, hi+1
    extra = max((hi-lo)*.06, .08)
    return lo-extra, hi+extra


def boundary_points(model, xmin, xmax, ymin, ymax):
    """표준화한 로지스틱 회귀 계수를 원본 축으로 돌려 사각형 내 교점을 계산."""
    scaler = model.named_steps["standardscaler"]
    reg = model.named_steps["logisticregression"]
    wx = float(reg.coef_[0][0] / scaler.scale_[0])
    wy = float(reg.coef_[0][1] / scaler.scale_[1])
    bias = float(reg.intercept_[0] - wx*scaler.mean_[0] - wy*scaler.mean_[1])
    points = []
    if abs(wy) > 1e-12:
        for x in [xmin, xmax]:
            y = -(wx*x+bias)/wy
            if ymin <= y <= ymax:
                points.append((x, y))
    if abs(wx) > 1e-12:
        for y in [ymin, ymax]:
            x = -(wy*y+bias)/wx
            if xmin <= x <= xmax:
                points.append((x, y))
    unique = []
    for p in points:
        if not any(abs(p[0]-q[0]) < 1e-7 and abs(p[1]-q[1]) < 1e-7 for q in unique):
            unique.append(p)
    if len(unique) < 2:
        return None
    return unique[:2]


def decision_figure(train, test, xkey, ykey):
    selected = [xkey, ykey]
    probability, question = fit_models(train, selected)
    xmin, xmax = axis_bounds(pd.concat([train[xkey], test[xkey]]))
    ymin, ymax = axis_bounds(pd.concat([train[ykey], test[ykey]]))
    nx, ny = 110, 85
    xs = [xmin+(xmax-xmin)*i/(nx-1) for i in range(nx)]
    ys = [ymin+(ymax-ymin)*i/(ny-1) for i in range(ny)]
    grid = pd.DataFrame([(x, y) for y in ys for x in xs], columns=selected)
    prediction = question.predict(grid)
    z = [prediction[i*nx:(i+1)*nx].tolist() for i in range(ny)]
    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        x=xs, y=ys, z=z, zmin=0, zmax=1, showscale=False,
        colorscale=[[0.0,"#b8f3e1"],[0.499,"#b8f3e1"],[0.5,"#ffd0e2"],[1.0,"#ffd0e2"]],
        opacity=.48, hoverinfo="skip", name="질문 모델이 나눈 알록달록 영역 🍡",
    ))
    cut = boundary_points(probability, xmin, xmax, ymin, ymax)
    if cut is not None:
        fig.add_trace(go.Scatter(x=[p[0] for p in cut], y=[p[1] for p in cut], mode="lines",
                                 line=dict(color=PURPLE, width=4, dash="dash"),
                                 name="확률 50% 경계선 💜", hoverinfo="skip"))
    for state, name, color, symbol in [
        (0,"실제: 뇌졸중 아님 (0) 💚",MINT,"circle"),
        (1,"실제: 뇌졸중 (1) 💗",PINK,"diamond"),
    ]:
        selected_test = test[test["stroke"] == state]
        fig.add_trace(go.Scatter(
            x=selected_test[xkey], y=selected_test[ykey], mode="markers", name=name,
            customdata=selected_test["id"],
            marker=dict(color=color, symbol=symbol, size=8 if state==0 else 10,
                        line=dict(color="white",width=1.1), opacity=.83),
            hovertemplate="ID: %{customdata}<br>"+FEATURE_NAMES[xkey]+": %{x:.2f}<br>"+
                          FEATURE_NAMES[ykey]+": %{y:.2f}<extra></extra>",
        ))
    fig.update_layout(xaxis_title=FEATURE_NAMES[xkey], yaxis_title=FEATURE_NAMES[ykey],
                      xaxis_range=[xmin,xmax], yaxis_range=[ymin,ymax])
    return cute_plot(fig, 540), cut, question


def classification_screen(df):
    hero("🧸 LOVELY AI MODEL TIME ♡", "💗 말랑말랑 분류 모델 연구실 ♡",
         "어떤 속성을 골라야 AI 친구들이 잘 맞힐까~? 💖 확률 친구, 질문 친구, 기본 친구까지 함께 비교해 보자아~! 🎀", "🧸")
    section("🎮", "AI 친구에게 알려 줄 힌트를 골라 줘~! 💌", "두 개 이상 골라 줘야 해~! 처음엔 BMI만 빼고 네 개에 하트를 붙여 놨어 💗")
    chosen = st.multiselect(
        "💗 AI 친구가 공부할 속성 고르기", options=FEATURES, default=["age","avg_glucose_level","hypertension","heart_disease"],
        format_func=lambda x: FEATURE_NAMES[x], key="model_features",
    )
    if len(chosen) < 2:
        st.info("🍡 앗! 속성 친구를 최소 두 명 골라 줘야 AI가 공부할 수 있어~! 🥺💗")
        return
    try:
        train, test = split_train_test(df, chosen)
        prob, decision = fit_models(train, chosen)
    except (ValueError, KeyError) as exc:
        st.error(f"앗, AI 친구가 준비하다가 멈췄어~! 🥺 이유: {exc}")
        return
    y_true = test["stroke"].astype(int)
    majority = int(train["stroke"].astype(int).value_counts().idxmax())
    acc1 = accuracy_score(y_true, prob.predict(test[chosen])) * 100
    acc2 = accuracy_score(y_true, decision.predict(test[chosen])) * 100
    acc3 = accuracy_score(y_true, [majority] * len(test)) * 100
    st.caption(f"🎀 전체 {len(train)+len(test):,}명 중 {len(train):,}명으로 공부하고, {len(test):,}명으로 시험 봐~! ID 순서로 열 명 중 앞 세 명이 시험 담당 💌")
    section("🏅", "우리 AI 친구들은 얼마나 잘 맞혔을까~? 💗", "세 친구 모두 똑같은 채점용 데이터로 공평하게 시험 봤어~! 🥰")
    cols = st.columns(3)
    for col, values in zip(cols, [
        ("💗 확률 모델 친구", f"{acc1:.2f}%", "크기 맞추기 + 확률로 대답해~! 💕", "#ffd2e7"),
        ("🍡 질문 모델 친구", f"{acc2:.2f}%", "질문은 한 경로에 최대 세 번이야~! 🌸", "#dfd2ff"),
        ("🧁 기본 모델 친구", f"{acc3:.2f}%", "입력 안 보고 다수 쪽으로만 답해~! 🧁", "#c6f1e5"),
    ]):
        with col:
            card(*values)
    st.markdown('<div class="cute-alert">💌 꼭 알아두기! 뇌졸중 경험자가 적어서 전부 “뇌졸중 아님”이라고 답해도 정확도가 높게 나올 수 있어~! 💗 정확도가 높다고 양성인 사람을 잘 찾아낸다는 뜻은 아니라는 점, 함께 기억해 줘! 🌷</div>', unsafe_allow_html=True)
    if "bmi" in chosen:
        st.caption(f"🎀 BMI의 빈 칸은 훈련용 친구들만으로 계산한 중앙값 {train['bmi'].median():.2f}로 채웠어~! 채점용 답은 몰래 보지 않았지롱 💗")
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🎨", "두 속성으로 알록달록 분류 지도 만들기~! 💞", "가로·세로 속성을 골라 주면 AI 둘이 그 두 속성만 보고 새로 공부해~! 🧸")
    c1, c2 = st.columns(2)
    with c1:
        xkey = st.selectbox("가로축은 뭘로 할까~? 💗", chosen, index=chosen.index("age") if "age" in chosen else 0,
                            format_func=lambda x: FEATURE_NAMES[x], key="x_feature")
    other = [col for col in chosen if col != xkey]
    with c2:
        ykey = st.selectbox("세로축은 뭘로 할까~? 💜", other,
                            index=other.index("avg_glucose_level") if "avg_glucose_level" in other else 0,
                            format_func=lambda x: FEATURE_NAMES[x], key="y_feature")
    try:
        fig, cut, tree2 = decision_figure(train, test, xkey, ykey)
        st.plotly_chart(fig, use_container_width=True)
        if cut is None:
            st.info("🫧 앗! 이 두 속성으로 만든 확률 50% 경계선은 그림 바깥에 있어~! 숨바꼭질 중인가 봐 💗")
        else:
            st.caption("💜 보라 점선은 확률 50% 경계, 🍬 옅은 배경은 질문 모델의 예상, 💗 점 색은 실제 정답이야~!")
    except (ValueError, KeyError) as exc:
        st.warning(f"이 속성 조합으로 그림을 그리기 어려워~! 🥺 이유: {exc}")
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🌳", "질문 모델 친구는 뭐부터 물어볼까~? 💗", "AI 친구가 실제로 선택한 질문과 네/아니요 갈래를 쭈욱 구경해 보자~! 🎀")
    st.code(tree_explanation(decision, chosen), language="text")
    st.caption("💌 질문은 한 길에서 최대 세 번! 마지막 그룹에는 최소 다섯 명이 남게 했어~! 난수는 42로 고정했지롱 💗")


# ── 실제 사이드바: 페이지 파일 링크가 아닌, 언제나 표시되는 버튼 ──
with st.sidebar:
    st.markdown(
        '<div class="cute-brand"><div class="cute-logo">🌷</div>'
        '<div><strong>두근두근 하트 연구소 💗</strong><small>SWEET LOVE DATA LAB ♡</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### 🎀 오늘은 어느 연구실에서 놀까~? 💕")
    page = st.radio(
        "💌 연구실 고르기", ["🏠💗 데이터 소개하트", "🍭💜 데이터 탐색하트", "🧸💞 분류 모델하트"],
        label_visibility="collapsed", key="active_page",
    )
    st.markdown("---")
    st.markdown(
        '<div class="cute-note">💌 <b>어서 와아~ 귀염둥이 연구원! 💗</b><br>위에서 원하는 연구실을 콕~ 골라 줘! 🎀'
        '<br>CSV는 알아서 연결돼 있으니까 마음 편히 놀아 보자아~! 💕✨</div>',
        unsafe_allow_html=True,
    )
    st.caption("🍓 데이터 친구들의 집: greatsong/modudata · stroke.csv")
    st.caption("🩷 이곳은 공부하는 러블리 실습실이야~! 실제 의료 진단에는 사용하지 말아 줘 💌")

try:
    df = load_data()
except Exception as exc:
    st.error("🥺🍓 앗, 데이터 친구들이 아직 도착하지 않았어~! 잠시 뒤 새로고침해 줄래? 💗")
    st.code(f"데이터 주소: {DATA_URL}\n연결 오류: {type(exc).__name__}: {exc}", language="text")
    st.stop()

if page == "🏠💗 데이터 소개하트":
    intro_screen(df)
elif page == "🍭💜 데이터 탐색하트":
    explore_screen(df)
else:
    classification_screen(df)

st.markdown('<div class="soft-footer">🎀💗 두근두근 러블리 연구소 ♡ 오늘도 하트 뿅뿅! 배우는 즐거움이 가득한 실험실이야~ 🧸💕</div>',
            unsafe_allow_html=True)
