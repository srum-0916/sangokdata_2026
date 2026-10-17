"""🎀 두근두근 데이터 연구소 - 분류 모델 페이지.

- 번호 순으로 정렬 후 10명 중 앞 3명을 채점 데이터로 분리
- 결측 BMI는 선택한 경우에만 훈련 데이터 중앙값으로 대체
- 확률 모델: 표준화 + 로지스틱 회귀
- 질문 모델: 최대 3단계, 말단 최소 5명인 결정 트리
- 그림에 표시되는 영역/경계는 사용자가 선택한 두 축으로 다시 학습한 모델
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, _tree


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
FEATURES = ["age", "avg_glucose_level", "bmi", "hypertension", "heart_disease"]
LABELS = {
    "age": "나이 (age)",
    "avg_glucose_level": "평균 혈당 (avg_glucose_level)",
    "bmi": "체질량지수 (bmi)",
    "hypertension": "고혈압 여부 (hypertension)",
    "heart_disease": "심장병 여부 (heart_disease)",
}
COLORS = {0: "#79dcca", 1: "#ff84ae"}

st.set_page_config(
    page_title="분류 모델 | 두근두근 데이터 연구소",
    page_icon="🧸",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(r"""
<style>
[data-testid="stSidebarNav"] {display:none!important;}
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

/* 💗 Sweet Data Lab: cards, navigation and inputs */
[data-testid="stPageLink"] a{border:1px solid #f1d8e9!important;border-radius:15px!important;background:rgba(255,255,255,.78)!important;padding:7px 10px!important;margin:2px 0!important;transition:transform .18s ease,background .18s ease,border-color .18s ease!important;}
[data-testid="stPageLink"] a:hover{background:#fff!important;border-color:#f09dc7!important;transform:translateX(3px)!important;}
[data-testid="stPageLink"] a[aria-current="page"]{background:#ffe3ef!important;border-color:#eda5c9!important;font-weight:850!important;}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div{border:2px solid #f1dbed!important;box-shadow:0 3px 0 #f8eaf3!important;}
[data-testid="stPlotlyChart"]{border-radius:20px!important;box-shadow:0 7px 18px rgba(149,109,151,.07)!important;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{box-shadow:0 5px 18px rgba(149,109,151,.08)!important;}

</style>

""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


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


def pastel_chart(fig, height=530):
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=14, t=20, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito, Noto Sans KR, sans-serif", color="#6d5b83", size=12),
        hoverlabel=dict(bgcolor="#fff9fd", font_color="#5d4b75"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )
    fig.update_xaxes(gridcolor="#f2e6f0", zeroline=False, linecolor="#decce3")
    fig.update_yaxes(gridcolor="#f2e6f0", zeroline=False, linecolor="#decce3")
    return fig


def prepare_data(df, selected):
    """훈련/채점 분리부터 시행하고 훈련 데이터만으로 결측값을 채웁니다."""
    data = df.copy()
    data["id"] = pd.to_numeric(data["id"], errors="coerce")
    data["stroke"] = pd.to_numeric(data["stroke"], errors="coerce")
    for feature in selected:
        data[feature] = pd.to_numeric(data[feature], errors="coerce")
    data = data.dropna(subset=["id", "stroke"])
    data = data.sort_values("id", kind="stable").reset_index(drop=True)

    # 정렬 후 매 10명마다 0,1,2번째가 채점용, 나머지가 훈련용입니다.
    is_test = (pd.Series(range(len(data)), index=data.index) % 10) < 3
    train = data.loc[~is_test].copy()
    test = data.loc[is_test].copy()
    if train.empty or test.empty:
        raise ValueError("학습용 또는 채점용 데이터가 비어 있어요.")

    medians = {}
    if "bmi" in selected:
        median = train["bmi"].median()
        if pd.isna(median):
            raise ValueError("훈련 데이터의 BMI 중앙값을 구할 수 없어요.")
        medians["bmi"] = float(median)
        train["bmi"] = train["bmi"].fillna(median)
        test["bmi"] = test["bmi"].fillna(median)

    # 다른 선택 특성은 원본에서 결측이 없어야 합니다.
    if train[selected].isna().any().any() or test[selected].isna().any().any():
        raise ValueError("선택한 특성에 처리되지 않은 빈 값이 있어요.")
    return train, test, medians


def train_models(train, features):
    X = train[features]
    y = train["stroke"].astype(int)
    probability = make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=2000, random_state=42)
    )
    probability.fit(X, y)
    question = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=42)
    question.fit(X, y)
    return probability, question


def tree_questions(model, features):
    """각 경로의 질문은 최대 3번. 질문 순서와 분기 방향을 표시합니다."""
    structure = model.tree_
    lines = []

    def walk(node, level, path):
        left = structure.children_left[node]
        right = structure.children_right[node]
        size = int(structure.n_node_samples[node])
        indent = "    " * level
        branch = "" if not path else f"[{path}] "
        if left == _tree.TREE_LEAF:
            prediction = int(model.classes_[structure.value[node][0].argmax()])
            conclusion = "뇌졸중 경험(1)" if prediction == 1 else "경험 없음(0)"
            lines.append(f"{indent}{branch}🍬 결론: {conclusion} · 훈련 {size:,}명")
            return
        feat = features[int(structure.feature[node])]
        threshold = float(structure.threshold[node])
        lines.append(f"{indent}{branch}❔ 질문 {level + 1}: {LABELS[feat]} ≤ {threshold:.2f} ? · {size:,}명")
        walk(left, level + 1, "예")
        walk(right, level + 1, "아니요")

    walk(0, 0, "")
    return "\n".join(lines)


def axis_span(series):
    lo, hi = float(series.min()), float(series.max())
    if lo == hi:
        return lo - 1, hi + 1
    extra = max((hi - lo) * 0.065, .12 if hi <= 1 and lo >= 0 else .01)
    return lo - extra, hi + extra


def show_decision_plot(train, test, horizontal, vertical):
    """선택한 두 축으로 별도로 학습한 모델의 경계/영역을 표시합니다."""
    subset = [horizontal, vertical]
    probability, question = train_models(train, subset)
    x_min, x_max = axis_span(pd.concat([train[horizontal], test[horizontal]]))
    y_min, y_max = axis_span(pd.concat([train[vertical], test[vertical]]))

    # 균일한 격자와 두 축 모델 예측을 이용해 옅은 영역을 만듭니다.
    width, height = 145, 110
    xs = [x_min + (x_max - x_min) * i / (width - 1) for i in range(width)]
    ys = [y_min + (y_max - y_min) * j / (height - 1) for j in range(height)]
    mesh = pd.DataFrame(
        [(x, y) for y in ys for x in xs], columns=subset
    )
    tree_grid = question.predict(mesh).reshape(height, width)
    # 로지스틱 회귀 식을 원래 축 단위로 변환한 뒤, 사각형 안의 교점을 구합니다.
    # 두 축 데이터만 사용해 훈련한 확률 모델의 0.5 경계입니다.
    scaler = probability.named_steps["standardscaler"]
    logistic = probability.named_steps["logisticregression"]
    wx = float(logistic.coef_[0][0] / scaler.scale_[0])
    wy = float(logistic.coef_[0][1] / scaler.scale_[1])
    bias = float(logistic.intercept_[0] - wx * scaler.mean_[0] - wy * scaler.mean_[1])
    intersections = []
    if abs(wy) > 1e-12:
        for x in (x_min, x_max):
            y = -(wx * x + bias) / wy
            if y_min <= y <= y_max:
                intersections.append((x, y))
    if abs(wx) > 1e-12:
        for y in (y_min, y_max):
            x = -(wy * y + bias) / wx
            if x_min <= x <= x_max:
                intersections.append((x, y))
    distinct = []
    for point in intersections:
        if not any(abs(point[0] - old[0]) < 1e-8 and abs(point[1] - old[1]) < 1e-8
                   for old in distinct):
            distinct.append(point)
    has_boundary = len(distinct) >= 2

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        x=xs, y=ys, z=tree_grid,
        colorscale=[[0, "#b3f5e6"], [0.499, "#b3f5e6"], [0.5, "#ffb5d2"], [1, "#ffb5d2"]],
        showscale=False, opacity=.34, zmin=0, zmax=1,
        hoverinfo="skip", name="질문 모델의 분류 영역",
    ))
    if has_boundary:
        # 사각형에 닿은 경계의 양 끝점을 직접 연결하면 선이 확실하게 보입니다.
        endpoints = sorted(distinct, key=lambda p: (p[0], p[1]))
        fig.add_trace(go.Scatter(
            x=[endpoints[0][0], endpoints[-1][0]],
            y=[endpoints[0][1], endpoints[-1][1]],
            mode="lines", name="확률 모델 0.5 경계",
            line=dict(color="#985fe0", width=4),
            hovertemplate="확률 모델의 50% 결정 경계<extra></extra>",
        ))
    for outcome, name in [(0, "뇌졸중 아님 (0)"), (1, "뇌졸중 (1)")]:
        cases = test.loc[test["stroke"] == outcome]
        fig.add_trace(go.Scatter(
            x=cases[horizontal], y=cases[vertical], mode="markers", name=name,
            marker=dict(size=9 if outcome == 0 else 10, color=COLORS[outcome],
                        line=dict(color="#fff", width=1.2), opacity=.89),
            customdata=cases["id"],
            hovertemplate=("ID: %{customdata}<br>" + LABELS[horizontal] + ": %{x:.2f}<br>"
                           + LABELS[vertical] + ": %{y:.2f}<br>실제: " + name
                           + "<extra></extra>"),
        ))
    fig.update_xaxes(title_text=LABELS[horizontal], range=[x_min, x_max])
    fig.update_yaxes(title_text=LABELS[vertical], range=[y_min, y_max])
    st.plotly_chart(pastel_chart(fig), use_container_width=True)

    if not has_boundary:
        st.info("🫧 두 축으로 학습한 확률 모델의 **0.5 결정 경계가 그림 범위 밖**에 있어 선이 보이지 않아요. 이는 오류가 아니에요.")
    else:
        st.caption("💜 보라색 선: 두 축만 사용한 확률 모델의 50% 경계 · 민트/핑크 배경: 두 축으로 학습한 질문 모델의 예측 영역")
    st.caption("🍓 점은 채점용 사람들의 **실제** 뇌졸중 경험 여부이며, 배경색은 질문 모델의 **예측**이에요. 이 그림의 두 모델은 정확도 카드의 전체 선택 특성 모델과 별도로 학습했어요.")
    return question


with st.sidebar:
    st.markdown("### 🎨 연구실 이동하기 💗")
    st.page_link("main.py", label="🏠 데이터 소개", use_container_width=True)
    st.page_link("pages/1_탐색.py", label="🔎 탐색 놀이터", use_container_width=True)
    st.page_link("pages/2_분류_모델.py", label="🧸 분류 모델 연구실", use_container_width=True)
    st.page_link("pages/3_채점표.py", label="💌 채점표 연구실", use_container_width=True)
    st.page_link("pages/4_전처리.py", label="🫧 전처리 실험실", use_container_width=True)
    st.divider()
    st.markdown(
        '<div class="candy-brand"><div class="brand-flower">🌷</div>'
        '<div><strong>두근두근 연구소</strong><small>SWEET DATA LAB</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="side-note">🧸 <b>세 번째 연구 노트!</b><br>'
        '데이터 소개 → 탐색 → <b>분류 모델</b>까지 완성! '
        '다섯 속성 중 필요한 것을 골라 모델을 비교해 보자. ✨</div>',
        unsafe_allow_html=True,
    )
    st.caption("🎀 이 페이지는 데이터 분석 실습용이며 실제 의료 진단에 사용할 수 없어요.")

st.markdown(
    """
    <div class="candy-hero">
      <span class="spark a">✳</span><span class="spark b">✧</span><span class="spark c">✦</span>
      <div class="hero-copy">
        <div class="hero-eyebrow">🍓 SWEET DATA LAB · CHAPTER 03</div>
        <h1>말랑말랑<br><span class="highlight">분류 모델 연구실!</span> ♡</h1>
        <p>숫자로 확률을 계산하는 친구와 차근차근 질문하는 친구!<br>
        같은 데이터를 보고 어떤 대답을 하는지 비교해 볼까요?</p>
        <div class="hero-pills"><span>💗 확률 모델</span><span>🍡 질문 모델</span><span>🫧 공정한 채점</span></div>
      </div>
      <div class="hero-buddy"><div class="buddy-face">🧸</div>
      <div class="buddy-label">모델 탐험 시작! ♡</div></div>
    </div>
    """, unsafe_allow_html=True,
)

try:
    raw = load_data()
except Exception as exc:
    st.error("🍓 원본 CSV를 불러오지 못했어요. 주소와 네트워크 상태를 확인해 주세요.")
    st.caption(f"오류 종류: {type(exc).__name__}")
    st.stop()

needed = {"id", "stroke", *FEATURES}
if not needed.issubset(set(raw.columns)):
    st.error("필수 데이터 열이 없어요: " + ", ".join(sorted(needed - set(raw.columns))))
    st.stop()

section("🎀", "모델 재료 고르기", "2~5개 속성을 골라 주세요. 처음에는 BMI를 제외한 4개가 선택되어 있어요.")
def remember_selected_features():
    st.session_state["stroke_shared_features"] = list(st.session_state["classification_features"])


selected = st.multiselect(
    "✨ 모델에 사용할 속성", options=FEATURES,
    default=st.session_state.get(
        "stroke_shared_features", ["age", "avg_glucose_level", "hypertension", "heart_disease"]
    ),
    format_func=lambda feature: LABELS[feature],
    key="classification_features",
    on_change=remember_selected_features,
)
st.session_state["stroke_shared_features"] = list(selected)
if len(selected) < 2:
    st.warning("🧁 속성을 **두 개 이상** 골라야 분류 모델을 학습할 수 있어요!")
    st.stop()

try:
    train, test, medians = prepare_data(raw, selected)
    if train["stroke"].nunique() < 2:
        st.warning("훈련 데이터에 뇌졸중(1)과 아님(0)이 모두 있어야 모델을 만들 수 있어요.")
        st.stop()
    probability, question = train_models(train, selected)
    X_test = test[selected]
    truth = test["stroke"].astype(int)
    acc_prob = float(accuracy_score(truth, probability.predict(X_test)))
    acc_tree = float(accuracy_score(truth, question.predict(X_test)))
    majority_label = int(train["stroke"].mode().iloc[0])
    acc_base = float((truth == majority_label).mean())
except (ValueError, TypeError) as exc:
    st.error(f"데이터 또는 학습 과정에 문제가 있어요: {exc}")
    st.stop()

st.markdown(
    '<div class="chip-row">'
    f'<span class="chip">🍬 학습용 {len(train):,}명</span>'
    f'<span class="chip">🫧 채점용 {len(test):,}명</span>'
    f'<span class="chip">🎀 선택 속성 {len(selected)}개</span>'
    '</div>', unsafe_allow_html=True,
)
if medians:
    st.info(f"🌷 BMI 빈 값은 **훈련용에서 계산한 중앙값 {medians['bmi']:.2f}**로 학습용과 채점용 모두 채웠어요.")
else:
    st.caption("🍡 BMI를 선택하지 않았으므로 BMI 결측값은 채우지도, 학습에 사용하지도 않았어요.")
st.markdown('<div class="sticky-note">📌 번호(id) 오름차순 정렬 → **매 10명 중 앞 3명은 채점**, 나머지 7명은 학습에 사용해요. 표준화도 오직 학습용 데이터로만 배운 뒤 채점용에 적용해요.</div>', unsafe_allow_html=True)

section("🏆", "세 모델의 성적표", "세 모델 모두 같은 채점용 사람들로 정확도를 계산했어요.")
columns = st.columns(3, gap="medium")
cards = [
    ("💗 확률 모델 · 로지스틱 회귀", f"{acc_prob*100:.2f}%", "표준화 + 로지스틱 회귀 / 기준 0.5", "#ffd2e6"),
    ("🍡 질문 모델 · 결정 트리", f"{acc_tree*100:.2f}%", "질문 최대 3번 / 말단 최소 5명", "#e6d6ff"),
    ("🧁 눈 감고 찍기 · 다수 클래스", f"{acc_base*100:.2f}%", "입력 무시 · 훈련용 최빈 범주만 답", "#c7f5e8"),
]
for col, card in zip(columns, cards):
    with col:
        kpi(*card)
st.caption("💡 뇌졸중 경험자(1)가 적은 불균형 데이터에서는 정확도만 높아도 양성을 잘 찾아낸다고 볼 수 없어요. 기준 모델과 나란히 비교해 보세요.")

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🍭", "분류 그림 놀이터", "가로축·세로축을 고르면 **그 두 축만으로 모델을 새로 학습해** 그림을 그려요.")
axis_cols = st.columns(2, gap="medium")
with axis_cols[0]:
    x_axis = st.selectbox("🩷 가로축", selected, index=0,
                          format_func=lambda f: LABELS[f], key="classification_x")
with axis_cols[1]:
    y_options = [f for f in selected if f != x_axis]
    y_axis = st.selectbox("🩵 세로축", y_options, index=0,
                          format_func=lambda f: LABELS[f], key="classification_y")

try:
    axis_question = show_decision_plot(train, test, x_axis, y_axis)
except (ValueError, TypeError) as exc:
    st.error(f"그림 생성 중 데이터 문제가 생겼어요: {exc}")
    st.stop()

section("📖", "질문 모델의 질문 순서", "왼쪽 가지는 '예', 오른쪽 가지는 '아니요'예요. 각 경로에서 질문은 최대 세 번만 해요.")
full_tree = tree_questions(question, selected)
axis_tree = tree_questions(axis_question, [x_axis, y_axis])
with st.expander("🍓 전체 선택 속성으로 만든 질문 모델", expanded=True):
    st.code(full_tree, language=None)
with st.expander("🍬 위 그림의 두 축만으로 만든 질문 모델", expanded=False):
    st.code(axis_tree, language=None)
st.markdown(
    '<div class="candy-panel"><div class="panel-eyebrow">HOW TO READ · 모델 해석</div>'
    '<div class="panel-title">💌 선은 확률, 색칠은 질문!</div>'
    '<div class="panel-help">보라색 선은 두 축만 사용한 확률 모델의 0.5 기준, 옅은 배경은 두 축 질문 모델의 예측이에요. '
    '데이터에서 찾은 통계적 패턴은 개인의 진단이나 인과관계를 증명하지 않아요.</div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="foot-note">♡ tiny questions, lovely discoveries · SWEET DATA LAB ♡</div>', unsafe_allow_html=True)
