"""두근두근 뇌졸중 데이터 연구소 ♡

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
    "age": "나이", "avg_glucose_level": "평균 혈당", "bmi": "BMI",
    "hypertension": "고혈압", "heart_disease": "심장병",
}
FEATURES = list(FEATURE_NAMES)
PINK = "#FA7FAA"
MINT = "#6ACFB7"
PURPLE = "#9B83F3"
YELLOW = "#FFC96E"
INK = "#584A70"

st.set_page_config(
    page_title="두근두근 뇌졸중 연구소 ♡",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
        return "정수 · 식별 번호"
    if col in ("hypertension", "heart_disease", "stroke"):
        return "0 / 1"
    if pd.api.types.is_numeric_dtype(series):
        return "숫자 · 연속형"
    values = [str(v) for v in series.dropna().unique()]
    if len(values) <= 6:
        return " / ".join(values)
    return f"범주형 · {len(values)}종류"


def summary_rate(data):
    if len(data) == 0:
        return 0.0
    return float(pd.to_numeric(data["stroke"], errors="coerce").mean()) * 100


def intro_screen(df):
    hero("🌸 HELLO, LITTLE RESEARCHER!", "두근두근 뇌졸중 데이터 연구소 ♡",
         "입력 없이 자동 연결된 데이터를 먼저 알아봐요! 표를 채우고, 탐색과 AI 모델까지 재미있게 공부해요.", "🧠")
    section("🧁", "우리 데이터 한눈에 보기", "원본 CSV의 숫자로 자동 계산해요")
    n_stroke = int(df["stroke"].eq(1).sum())
    cols = st.columns(4)
    items = [
        ("전체 사람 수", f"{len(df):,}명", "분석에 포함된 기록", "#ffd8e8"),
        ("열 개수", f"{df.shape[1]}개", "데이터의 속성", "#ddceff"),
        ("뇌졸중 경험자", f"{n_stroke:,}명", "stroke = 1", "#c5f0e2"),
        ("경험자 비율", f"{100*n_stroke/len(df):.2f}%", "전체 사람 중 비율", "#ffe7ba"),
    ]
    for col, values in zip(cols, items):
        with col:
            card(*values)
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("📝", "데이터 사전 만들기", "우리말 뜻은 직접 입력하는 공부 노트야. 다른 열은 자동으로 채워져 있어!")
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
        column_config={"우리말 뜻": st.column_config.TextColumn("우리말 뜻 ✏️", help="교재를 보고 직접 입력해요")},
        key="column_dictionary",
    )
    st.session_state["column_notes"] = dict(zip(edited["열 이름"], edited["우리말 뜻"].fillna("")))
    st.download_button("💌 작성한 데이터 사전 저장", data=edited.to_csv(index=False).encode("utf-8-sig"),
                       file_name="stroke_data_dictionary.csv", mime="text/csv")
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🍰", "원본 데이터 살짝 보기", "처음 다섯 줄을 내용 변경 없이 보여 줘요")
    st.dataframe(df.head(5), hide_index=True, use_container_width=True)
    section("📚", "데이터 출처 적기", "교재에 나온 출처 설명을 여기에 적어 봐요")
    st.text_area("출처 메모", placeholder="교재의 데이터 출처 내용을 여기에 입력해 줘!", key="source_memo", height=100)
    st.caption("원본 CSV: " + DATA_URL)


def hist_figure(series, label, color, bins=28):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=series.dropna(), nbinsx=bins, marker_color=color,
                               opacity=.91, hovertemplate="값: %{x}<br>사람 수: %{y:,}명<extra></extra>"))
    fig.update_layout(bargap=.085, xaxis_title=label, yaxis_title="사람 수 (명)")
    return cute_plot(fig)


def box_figure(data, feature, label):
    fig = go.Figure()
    for state, name, color in [(0, "경험 없음 (0)", MINT), (1, "뇌졸중 경험 (1)", PINK)]:
        values = data.loc[data["stroke"] == state, feature].dropna()
        fig.add_trace(go.Box(y=values, name=name, marker_color=color, line_color=color,
                             boxmean=True, boxpoints=False,
                             hovertemplate=f"{name}<br>{label}: %{{y:.2f}}<extra></extra>"))
    fig.update_layout(yaxis_title=label)
    return cute_plot(fig)


def rate_figure(df, col, title):
    categories = [(0, "없음 (0)"), (1, "있음 (1)")]
    rates, sizes = [], []
    for binary, _ in categories:
        selected = df[df[col] == binary]
        rates.append(summary_rate(selected))
        sizes.append(len(selected))
    fig = go.Figure(go.Bar(
        x=[x[1] for x in categories], y=rates,
        marker_color=[MINT, PINK], text=[f"{v:.2f}%" for v in rates], textposition="outside",
        customdata=sizes, hovertemplate="%{x}<br>뇌졸중 비율: %{y:.2f}%<br>사람: %{customdata:,}명<extra></extra>",
    ))
    fig.update_layout(yaxis_title="뇌졸중 경험 비율 (%)", yaxis_range=[0, max(rates)*1.33+1], title=None)
    return cute_plot(fig)


def explore_screen(df):
    hero("🍭 EXPLORE / OUR DATA", "말랑말랑 데이터 탐색 놀이터",
         "나이와 혈당의 모양, 뇌졸중 경험 여부의 차이, 결측값까지 그래프로 찾아봐요.", "🔎")
    section("🍓", "나이와 혈당의 분포", "각 막대는 해당 값 구간에 속한 사람 수를 뜻해요")
    bins = st.slider("히스토그램 구간 수", min_value=10, max_value=60, value=28, step=2, key="bin_slider")
    left, right = st.columns(2)
    with left:
        panel("🍑 나이 분포", "가로축은 나이, 세로축은 사람 수")
        st.plotly_chart(hist_figure(df["age"], "나이 (세)", PINK, bins), use_container_width=True)
    with right:
        panel("🍋 평균 혈당 분포", "가로축은 평균 혈당, 세로축은 사람 수")
        st.plotly_chart(hist_figure(df["avg_glucose_level"], "평균 혈당", PURPLE, bins), use_container_width=True)

    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🧸", "뇌졸중 경험별 상자그림", "가운데 선은 중앙값, 작은 평균 표시도 함께 볼 수 있어요")
    left, right = st.columns(2)
    with left:
        panel("🎀 나이 비교")
        st.plotly_chart(box_figure(df, "age", "나이 (세)"), use_container_width=True)
    with right:
        panel("🫧 평균 혈당 비교")
        st.plotly_chart(box_figure(df, "avg_glucose_level", "평균 혈당"), use_container_width=True)
    averages = df.groupby("stroke")[["age", "avg_glucose_level"]].mean().reindex([0, 1]).round(2)
    averages.index = ["경험 없음 (0)", "뇌졸중 경험 (1)"]
    averages.columns = ["평균 나이", "평균 혈당"]
    st.markdown("**🌷 두 무리의 평균값 비교**")
    st.dataframe(averages, use_container_width=True)

    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("💗", "질환 유무에 따른 뇌졸중 비율", "각 무리에서 stroke = 1인 사람이 차지하는 비율이에요")
    left, right = st.columns(2)
    with left:
        panel("🌼 고혈압 유무 비교")
        st.plotly_chart(rate_figure(df, "hypertension", "고혈압"), use_container_width=True)
    with right:
        panel("🌻 심장병 유무 비교")
        st.plotly_chart(rate_figure(df, "heart_disease", "심장병"), use_container_width=True)

    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🧩", "BMI가 비어 있는 사람 살펴보기", "빈 값이 있는 집단의 뇌졸중 비율과 전체 비율을 같은 표로 비교해요")
    missing_bmi = df[df["bmi"].isna()]
    table = pd.DataFrame([
        {"비교 집단": "BMI가 빈 사람", "사람 수": len(missing_bmi),
         "뇌졸중 경험자": int(missing_bmi["stroke"].eq(1).sum()), "뇌졸중 비율 (%)": round(summary_rate(missing_bmi), 2)},
        {"비교 집단": "전체", "사람 수": len(df),
         "뇌졸중 경험자": int(df["stroke"].eq(1).sum()), "뇌졸중 비율 (%)": round(summary_rate(df), 2)},
    ])
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🚬", "흡연 상태별 사람 수", "Unknown은 모름/미기록으로 표시된 값이며 빈 값(NaN)과는 달라요")
    smoking_counts = df["smoking_status"].fillna("(빈 값)").value_counts(dropna=False)
    smoking_table = pd.DataFrame({"흡연 상태": smoking_counts.index,
                                  "사람 수": smoking_counts.values,
                                  "전체 비율 (%)": (smoking_counts.values / len(df) * 100).round(2)})
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
        raise ValueError("훈련용 또는 채점용 데이터가 비어 있어요.")
    if "bmi" in selected:
        # 채점용에는 손대지 않고 훈련 데이터로만 계산한 중앙값을 두 곳에 적용한다.
        mid = train["bmi"].median()
        if pd.isna(mid):
            raise ValueError("훈련 데이터에 BMI 값이 없어서 중앙값을 구할 수 없어요.")
        train["bmi"] = train["bmi"].fillna(mid)
        test["bmi"] = test["bmi"].fillna(mid)
    if train[selected].isna().any().any() or test[selected].isna().any().any():
        raise ValueError("선택한 속성에 처리되지 않은 빈 값이 있어요.")
    return train, test


def fit_models(train, selected):
    x = train[selected]
    y = train["stroke"].astype(int)
    if y.nunique() < 2:
        raise ValueError("훈련 데이터에 0과 1 두 종류가 모두 있어야 해요.")
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
            answers.append(f"{indent}{prefix}🍡 결과: {result} (훈련 {tree.n_node_samples[node]}명)")
            return
        name = FEATURE_NAMES[selected[int(tree.feature[node])]]
        threshold = float(tree.threshold[node])
        answers.append(f"{indent}{prefix}❔ 질문 {depth+1}: {name} ≤ {threshold:.2f}? ({tree.n_node_samples[node]}명)")
        visit(left, depth+1, "예 → ")
        visit(right, depth+1, "아니요 → ")
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
        opacity=.48, hoverinfo="skip", name="질문 모델의 영역",
    ))
    cut = boundary_points(probability, xmin, xmax, ymin, ymax)
    if cut is not None:
        fig.add_trace(go.Scatter(x=[p[0] for p in cut], y=[p[1] for p in cut], mode="lines",
                                 line=dict(color=PURPLE, width=4, dash="dash"),
                                 name="확률 0.5 경계", hoverinfo="skip"))
    for state, name, color, symbol in [
        (0,"실제: 뇌졸중 아님 (0)",MINT,"circle"),
        (1,"실제: 뇌졸중 (1)",PINK,"diamond"),
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
    hero("🧠 MODEL / LET'S PLAY!", "말랑말랑 분류 모델 연구실 ♡",
         "입력 속성을 골라 두 가지 AI 모델을 만들고, 문제 푸는 방식과 정확도를 비교해 봐요!", "🧸")
    section("🎮", "AI에게 알려 줄 속성 고르기", "속성을 두 개 이상 골라 주세요. 처음에는 BMI만 빼고 선택되어 있어요.")
    chosen = st.multiselect(
        "학습에 사용할 속성", options=FEATURES, default=["age","avg_glucose_level","hypertension","heart_disease"],
        format_func=lambda x: FEATURE_NAMES[x], key="model_features",
    )
    if len(chosen) < 2:
        st.info("🍡 최소 2개의 속성을 골라야 모델을 학습할 수 있어요!")
        return
    try:
        train, test = split_train_test(df, chosen)
        prob, decision = fit_models(train, chosen)
    except (ValueError, KeyError) as exc:
        st.error(f"모델을 준비할 수 없어요: {exc}")
        return
    y_true = test["stroke"].astype(int)
    majority = int(train["stroke"].astype(int).value_counts().idxmax())
    acc1 = accuracy_score(y_true, prob.predict(test[chosen])) * 100
    acc2 = accuracy_score(y_true, decision.predict(test[chosen])) * 100
    acc3 = accuracy_score(y_true, [majority] * len(test)) * 100
    st.caption(f"📋 전체 {len(train)+len(test):,}명 · 훈련 {len(train):,}명 · 채점 {len(test):,}명 · ID 순서로 10명마다 앞 3명을 채점")
    section("🏅", "모델 정확도 비교", "세 모델 모두 동일한 채점용 사람들로 평가해요")
    cols = st.columns(3)
    for col, values in zip(cols, [
        ("💗 확률 모델", f"{acc1:.2f}%", "표준화 + 로지스틱 회귀", "#ffd2e7"),
        ("🍡 질문 모델", f"{acc2:.2f}%", "결정 트리 · 질문 최대 3번", "#dfd2ff"),
        ("🧁 기준 모델", f"{acc3:.2f}%", "입력을 무시하고 훈련용의 다수로만 답함", "#c6f1e5"),
    ]):
        with col:
            card(*values)
    st.markdown('<div class="cute-alert">💡 뇌졸중 경험자가 적기 때문에 모두 “뇌졸중 아님”으로 답해도 정확도가 높을 수 있어요. 높은 정확도가 곧 뇌졸중 환자를 잘 찾는다는 뜻은 아니랍니다!</div>', unsafe_allow_html=True)
    if "bmi" in chosen:
        st.caption(f"🎀 BMI의 결측값은 훈련용 BMI 중앙값 {train['bmi'].median():.2f}로만 계산해 두 데이터에 적용했어요.")
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🎨", "두 속성으로 분류 지도 그리기", "선택한 두 축으로 확률·질문 모델을 다시 학습해서 그림을 만들어요")
    c1, c2 = st.columns(2)
    with c1:
        xkey = st.selectbox("가로축", chosen, index=chosen.index("age") if "age" in chosen else 0,
                            format_func=lambda x: FEATURE_NAMES[x], key="x_feature")
    other = [col for col in chosen if col != xkey]
    with c2:
        ykey = st.selectbox("세로축", other,
                            index=other.index("avg_glucose_level") if "avg_glucose_level" in other else 0,
                            format_func=lambda x: FEATURE_NAMES[x], key="y_feature")
    try:
        fig, cut, tree2 = decision_figure(train, test, xkey, ykey)
        st.plotly_chart(fig, use_container_width=True)
        if cut is None:
            st.info("🫧 이 두 축으로 학습한 확률 모델의 0.5 결정 경계가 현재 그림 범위 밖에 있어요.")
        else:
            st.caption("보라색 점선 = 확률 모델의 0.5 경계 / 배경색 = 두 축 질문 모델의 예측 / 점 색 = 채점용 사람의 실제 결과")
    except (ValueError, KeyError) as exc:
        st.warning(f"이 조합으로 그림을 그릴 수 없어요: {exc}")
    st.markdown('<div class="cute-divider"></div>', unsafe_allow_html=True)
    section("🌳", "질문 모델의 질문 순서", "전체 선택 속성으로 학습한 모델의 실제 질문과 예/아니요 갈래")
    st.code(tree_explanation(decision, chosen), language="text")
    st.caption("질문은 한 경로에서 최대 세 번, 마지막 마디에는 최소 다섯 명이 남도록 설정했어요. 난수 고정: 42")


# ── 실제 사이드바: 페이지 파일 링크가 아닌, 언제나 표시되는 버튼 ──
with st.sidebar:
    st.markdown(
        '<div class="cute-brand"><div class="cute-logo">🌷</div>'
        '<div><strong>두근두근 연구소</strong><small>SWEET DATA LAB</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### 🧭 연구실 선택하기")
    page = st.radio(
        "연구실 이동 메뉴", ["🏠 데이터 소개", "🍭 데이터 탐색", "🧸 분류 모델"],
        label_visibility="collapsed", key="active_page",
    )
    st.markdown("---")
    st.markdown(
        '<div class="cute-note">💌 <b>어서 와!</b><br>위 버튼을 누르면 페이지가 바로 바뀌어!'
        '<br>CSV 파일을 올릴 필요 없이 자동 연결돼 있어. ✨</div>',
        unsafe_allow_html=True,
    )
    st.caption("📊 원본: greatsong/modudata · stroke.csv")
    st.caption("🩷 학습용 데이터 분석 앱 · 의료 진단에 사용하지 않아요")

try:
    df = load_data()
except Exception as exc:
    st.error("🍓 공개 CSV를 자동으로 읽지 못했어요. 잠시 후 새로고침해 주세요.")
    st.code(f"주소: {DATA_URL}\n오류: {type(exc).__name__}: {exc}", language="text")
    st.stop()

if page == "🏠 데이터 소개":
    intro_screen(df)
elif page == "🍭 데이터 탐색":
    explore_screen(df)
else:
    classification_screen(df)

st.markdown('<div class="soft-footer">🌷 두근두근 데이터 연구소 ♡ · 공부하는 마음으로 만들어진 작은 실험실</div>',
            unsafe_allow_html=True)
