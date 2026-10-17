"""💌 두근두근 데이터 연구소 · 채점표 연구실.

2_분류_모델.py와 같은 데이터 분리 / 중앙값 대체 / 학습 조건을 사용합니다.
채점 집계는 예측용 데이터로만 수행합니다. 실제 의료 진단용 앱이 아닙니다.
"""
import pandas as pd
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
FEATURES = ["age", "avg_glucose_level", "bmi", "hypertension", "heart_disease"]
LABELS = {
    "age": "나이 (age)",
    "avg_glucose_level": "평균 혈당 (avg_glucose_level)",
    "bmi": "체질량지수 (bmi)",
    "hypertension": "고혈압 여부 (hypertension)",
    "heart_disease": "심장병 여부 (heart_disease)",
}

st.set_page_config(
    page_title="채점표 연구실 | 두근두근 데이터 연구소 💗",
    page_icon="💌", layout="wide", initial_sidebar_state="expanded",
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

# ─────────── 혼동행렬 / 평가지표 계산 ───────────
def confusion_counts(actual, predicted):
    """양성=1(뇌졸중), 음성=0 기준. sklearn 의존 없이 네 칸 직접 셉니다."""
    actual = pd.Series(actual).astype(int).reset_index(drop=True)
    predicted = pd.Series(predicted).astype(int).reset_index(drop=True)
    if len(actual) != len(predicted):
        raise ValueError("실제 정답과 예측 결과의 인원 수가 다릅니다.")
    return {
        "TN": int(((actual == 0) & (predicted == 0)).sum()),
        "FP": int(((actual == 0) & (predicted == 1)).sum()),
        "FN": int(((actual == 1) & (predicted == 0)).sum()),
        "TP": int(((actual == 1) & (predicted == 1)).sum()),
    }


def metric_values(c):
    """정밀도 분모가 0이면 None; F1은 별도 원식으로 계산합니다."""
    tn, fp, fn, tp = (c[key] for key in ("TN", "FP", "FN", "TP"))
    n = tn + fp + fn + tp
    precision_den = tp + fp
    recall_den = tp + fn
    f1_den = 2 * tp + fp + fn
    return {
        "정확도": (tp + tn) / n if n else None,
        "정밀도": tp / precision_den if precision_den else None,
        "재현율": tp / recall_den if recall_den else None,
        "F1": 2 * tp / f1_den if f1_den else 0.0,
    }


def score_table(counts):
    tn, fp, fn, tp = (counts[key] for key in ("TN", "FP", "FN", "TP"))
    return pd.DataFrame(
        [
            [f"{tn:,}명 · TN", f"{fp:,}명 · FP", f"{tn + fp:,}명"],
            [f"{fn:,}명 · FN", f"{tp:,}명 · TP", f"{fn + tp:,}명"],
            [f"{tn + fn:,}명", f"{fp + tp:,}명", f"{tn + fp + fn + tp:,}명"],
        ],
        index=["실제 0 · 아님", "실제 1 · 뇌졸중", "열 합계"],
        columns=["예측 0 · 아님", "예측 1 · 뇌졸중", "행 합계"],
    )


def format_metric(value, name):
    if value is None:
        return "계산할 수 없음"
    return f"{value:.3f}"


def show_error_people(test, predicted, missed):
    """FN 또는 FP의 실제 사람들을 나이 내림차순, 상위 20명으로 표시합니다."""
    selected = test.copy()
    selected["예측"] = pd.Series(predicted, index=test.index).astype(int)
    if missed:
        selected = selected[(selected["stroke"].astype(int) == 1) & (selected["예측"] == 0)]
    else:
        selected = selected[(selected["stroke"].astype(int) == 0) & (selected["예측"] == 1)]
    total = len(selected)
    selected = selected.sort_values(["age", "id"], ascending=[False, True]).head(20)
    result = selected[["id", "age", "avg_glucose_level", "hypertension", "heart_disease"]].rename(
        columns={
            "id": "번호 (id)", "age": "나이", "avg_glucose_level": "평균 혈당",
            "hypertension": "고혈압 여부", "heart_disease": "심장병 여부",
        }
    )
    return total, result


with st.sidebar:
    st.markdown("### 🎨 연구실 이동하기 💗")
    st.page_link("main.py", label="🏠 데이터 소개", use_container_width=True)
    st.page_link("pages/1_탐색.py", label="🔎 탐색 놀이터", use_container_width=True)
    st.page_link("pages/2_분류_모델.py", label="🧸 분류 모델 연구실", use_container_width=True)
    st.page_link("pages/3_채점표.py", label="💌 채점표 연구실", use_container_width=True)
    st.divider()
    st.markdown(
        '<div class="candy-brand"><div class="brand-flower">💝</div>'
        '<div><strong>두근두근 연구소</strong><small>SWEET DATA LAB ♡</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="side-note">💌 <b>네 번째 연구 노트!</b><br>'
        '확률 모델과 질문 모델의 예측을 꼼꼼히 채점해 보자아~! 💗<br>'
        '틀린 사람 목록도 아래에서 확인할 수 있어 🎀</div>',
        unsafe_allow_html=True,
    )
    st.caption("🌷 이 화면은 교육용 분석이며 실제 의료 진단이 아니에요.")

st.markdown(
    """
    <div class="candy-hero">
      <span class="spark a">✳</span><span class="spark b">✧</span><span class="spark c">✦</span>
      <div class="hero-copy">
        <div class="hero-eyebrow">💌 SWEET DATA LAB · CHAPTER 04</div>
        <h1>두근두근<br><span class="highlight">채점표 연구실!</span> ♡</h1>
        <p>정답을 몇 명이나 맞혔을까~? 💗<br>
        놓친 사람과 헛짚은 사람까지 차근차근 살펴보자아! 🎀</p>
        <div class="hero-pills"><span>💗 혼동행렬</span><span>🍡 정확도·정밀도</span>
        <span>🧁 재현율·F1</span></div>
      </div>
      <div class="hero-buddy"><div class="buddy-face">💌</div>
      <div class="buddy-label">채점 시작! ♡</div></div>
    </div>
    """, unsafe_allow_html=True,
)

try:
    raw = load_data()
except Exception as exc:
    st.error("🥺 데이터를 불러오지 못했어! 연결을 확인해 줄래~? 💗")
    st.caption(f"오류 종류: {type(exc).__name__}")
    st.stop()

needed = {"id", "stroke", "avg_glucose_level", "hypertension", "heart_disease", *FEATURES}
if not needed.issubset(raw.columns):
    st.error("필수 열이 없어서 채점할 수 없어: " + ", ".join(sorted(needed - set(raw.columns))))
    st.stop()

section("🍓", "모델에 알려 줄 힌트를 골라 볼까~? 💗",
        "분류 모델 페이지와 같은 속성으로 비교할 수 있어~! 두 개 이상 선택해 줘 💌")


def remember_scoring_features():
    st.session_state["stroke_shared_features"] = list(st.session_state["score_features"])


features = st.multiselect(
    "🎀 채점할 모델의 속성 고르기", FEATURES,
    default=st.session_state.get(
        "stroke_shared_features", ["age", "avg_glucose_level", "hypertension", "heart_disease"]
    ),
    format_func=lambda f: LABELS[f],
    key="score_features", on_change=remember_scoring_features,
)
st.session_state["stroke_shared_features"] = list(features)
if len(features) < 2:
    st.info("🍬 힌트가 너무 적어~! 최소 두 개를 골라 주면 채점해 줄게! 💗")
    st.stop()

try:
    train, test, medians = prepare_data(raw, features)
    if train["stroke"].nunique() < 2:
        st.error("훈련 데이터에 뇌졸중(1)과 아님(0)이 모두 있어야 해~! 💗")
        st.stop()
    logistic, tree = train_models(train, features)
    truth = test["stroke"].astype(int)
    predictions = {
        "💗 확률 모델": logistic.predict(test[features]).astype(int),
        "🍡 질문 모델": tree.predict(test[features]).astype(int),
    }
    majority = int(train["stroke"].mode().iloc[0])
    predictions["🧁 다수 모델"] = pd.Series([majority] * len(test), index=test.index, dtype=int)
    scores = {name: confusion_counts(truth, pred) for name, pred in predictions.items()}
except (ValueError, TypeError, KeyError) as exc:
    st.error(f"🥺 채점 준비 중 문제가 생겼어: {exc}")
    st.stop()

st.markdown(
    f'<div class="chip-row"><span class="chip">🫧 채점용 {len(test):,}명</span>'
    f'<span class="chip">💗 그중 뇌졸중 경험 {int(truth.eq(1).sum()):,}명</span>'
    f'<span class="chip">🍰 학습용 {len(train):,}명</span></div>',
    unsafe_allow_html=True,
)
st.caption(f"💌 채점용 사람 {len(test):,}명 중 실제 뇌졸중 경험자는 {int(truth.eq(1).sum()):,}명이야~! 💗")
if medians:
    st.caption(f"🎀 BMI 빈 칸은 훈련용 중앙값 {medians['bmi']:.2f}로 채웠어~! 정답은 훔쳐보지 않았지롱 💞")
else:
    st.caption("🫧 BMI를 선택하지 않았으니 빈 BMI는 그대로 두고 모델 입력에 쓰지 않았어~! 💗")
st.markdown(
    '<div class="sticky-note">📌 데이터는 ID 오름차순으로 정렬하고, '
    '열 명 중 앞의 세 명을 채점용으로 사용해~! 나머지 일곱 명으로만 모델과 표준화를 학습했어 💝</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🧸", "확률 친구랑 질문 친구의 혼동행렬! 💗",
        "행은 실제 정답, 열은 모델의 예측이야~! 네 칸에 TN·FP·FN·TP를 콕콕 적었어 💌")
left, right = st.columns(2, gap="large")
for col, name in zip([left, right], ["💗 확률 모델", "🍡 질문 모델"]):
    with col:
        st.markdown(f"#### {name} ♡")
        st.table(score_table(scores[name]))

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🏅", "AI 친구들의 네 가지 성적표~! 💞",
        "정확도·정밀도·재현율·F1을 0~1 사이 숫자로 표시했어 🎀")
metrics = []
for name in ["💗 확률 모델", "🍡 질문 모델", "🧁 다수 모델"]:
    values = metric_values(scores[name])
    metrics.append({"모델": name, **{key: format_metric(value, key) for key, value in values.items()}})
st.dataframe(pd.DataFrame(metrics), hide_index=True, use_container_width=True)
st.markdown(
    '<div class="candy-panel"><div class="panel-eyebrow">💘 SCORING NOTES</div>'
    '<div class="panel-title">네 지표가 알려 주는 이야기~! ♡</div>'
    '<div class="panel-help">정확도 = (TP+TN)/전체 · 정밀도 = TP/(TP+FP) · '
    '재현율 = TP/(TP+FN) · F1 = 2TP/(2TP+FP+FN). '
    '뇌졸중(1)이라고 예측한 사람이 0명이면 정밀도만 “계산할 수 없음”으로 나타내고, '
    'F1은 별도 식으로 계산해~! 💌</div></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🔎", "AI 친구가 누구를 놓쳤을까~? 💗",
        "왼쪽은 FN, 오른쪽은 FP! 각 목록은 나이 많은 순서로 최대 스무 명을 보여 줘 🎀")
chosen_model = st.selectbox("💌 어느 모델의 실수 목록을 볼까~?", ["💗 확률 모델", "🍡 질문 모델"],
                            key="score_error_model")
fn_count, fn_people = show_error_people(test, predictions[chosen_model], missed=True)
fp_count, fp_people = show_error_people(test, predictions[chosen_model], missed=False)
left, right = st.columns(2, gap="large")
with left:
    st.markdown(f"#### 🧸 놓친 사람 (FN) · 전체 {fn_count:,}명 💗")
    st.caption("실제로 뇌졸중을 겪었지만, 모델이 '아님(0)'이라고 예측한 사람이야.")
    st.dataframe(fn_people, hide_index=True, use_container_width=True)
    if fn_count > 20:
        st.caption("🍬 앞의 20명만 보여 줄게~! 전체 인원은 제목에 적혀 있어 💌")
with right:
    st.markdown(f"#### 🫧 헛짚은 사람 (FP) · 전체 {fp_count:,}명 💜")
    st.caption("실제로 뇌졸중이 아니지만, 모델이 '뇌졸중(1)'이라고 예측한 사람이야.")
    st.dataframe(fp_people, hide_index=True, use_container_width=True)
    if fp_count > 20:
        st.caption("🍬 앞의 20명만 보여 줄게~! 전체 인원은 제목에 적혀 있어 💌")

c = scores[chosen_model]
st.success(
    f"💌 {chosen_model}: 놓친 사람 {fn_count:,}명 = 혼동행렬 FN {c['FN']:,}명 · "
    f"헛짚은 사람 {fp_count:,}명 = 혼동행렬 FP {c['FP']:,}명! 딱 맞아~! 💗"
)
st.markdown(
    '<div class="foot-note">🎀 두근두근 채점표 연구실 · 데이터는 교육용, 예측은 진단이 아니야 ♡</div>',
    unsafe_allow_html=True,
)
