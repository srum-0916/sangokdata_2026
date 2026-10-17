"""🫧 두근두근 데이터 연구소 · 전처리 실험실.

2_분류_모델.py와 같은 데이터 분리 / 중앙값 대체 / 학습 조건을 사용합니다.
채점 집계는 예측용 데이터로만 수행합니다. 실제 의료 진단용 앱이 아닙니다.
"""
import pandas as pd
import plotly.graph_objects as go
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
    page_title="전처리 실험실 | 두근두근 데이터 연구소 💗",
    page_icon="🫧", layout="wide", initial_sidebar_state="expanded",
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

/* Lovelier navigation and content panels */
[data-testid="stPageLink"] a{background:rgba(255,255,255,.85)!important;border:1px solid #eed9ea!important;border-radius:15px!important;padding:8px!important;margin:2px 0!important;}
[data-testid="stPageLink"] a:hover{background:#fff!important;border-color:#e99dc9!important}
[data-testid="stPlotlyChart"]{border:1px solid #f3e3ee!important;border-radius:18px!important;background:rgba(255,255,255,.65)!important}
[data-testid="stMultiSelect"] [data-baseweb="select"]>div{border:2px solid #f0d9ec!important;border-radius:16px!important;background:#fff!important;}
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




# 같은 ID 10명 중 앞 세 명의 채점 번호를 먼저 확정합니다.
# BMI 삭제 때도 분할 번호를 그대로 유지하므로 채점 구성의 기준이 바뀌지 않습니다.
def prepare_data(df, selected, delete_bmi=False):
    data = df.copy()
    for feature in set(["id", "stroke", "bmi"] + selected):
        data[feature] = pd.to_numeric(data[feature], errors="coerce")
    data = data.dropna(subset=["id", "stroke"]).sort_values("id", kind="stable").reset_index(drop=True)
    is_test = (pd.Series(range(len(data)), index=data.index) % 10) < 3
    train, test = data.loc[~is_test].copy(), data.loc[is_test].copy()
    removed = data.loc[data["bmi"].isna()] if delete_bmi else data.iloc[0:0]
    if delete_bmi:
        train = train.dropna(subset=["bmi"]).copy()
        test = test.dropna(subset=["bmi"]).copy()
    elif "bmi" in selected:
        median = train["bmi"].median()
        if pd.isna(median):
            raise ValueError("훈련 집단에서 BMI 중앙값을 계산할 수 없어.")
        train["bmi"] = train["bmi"].fillna(median)
        test["bmi"] = test["bmi"].fillna(median)
    if len(train) == 0 or len(test) == 0:
        raise ValueError("훈련용이나 채점용 집단이 비었어.")
    if train[selected].isna().any().any() or test[selected].isna().any().any():
        raise ValueError("선택한 입력에 처리되지 않은 빈 값이 있어.")
    if train["stroke"].nunique() < 2:
        raise ValueError("학습용 데이터에 뇌졸중 0과 1이 모두 필요해.")
    return train, test, (len(removed), int(removed["stroke"].eq(1).sum()))


def train_models(train, features, balanced=False):
    weight = "balanced" if balanced else None
    prob = make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=2000, random_state=42, class_weight=weight)
    )
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5,
                                  random_state=42, class_weight=weight)
    prob.fit(train[features], train["stroke"].astype(int))
    tree.fit(train[features], train["stroke"].astype(int))
    return {"확률 모델": prob, "질문 모델": tree}


def score_comparison(b, a):
    rows = []
    for name in ("TN", "FP", "FN", "TP"):
        rows.append([name + " · 사람 수", f"{b[name]:,}명", f"{a[name]:,}명"])
    bm, am = metric_values(b), metric_values(a)
    for name in ("정확도", "정밀도", "재현율", "F1"):
        rows.append([name, format_metric(bm[name], name), format_metric(am[name], name)])
    return pd.DataFrame(rows, columns=["항목", "보정 전 💜", "보정 후 💗"]).set_index("항목")


def original_weights(model):
    scaler = model.named_steps["standardscaler"]
    lr = model.named_steps["logisticregression"]
    weights = [float(w/s) for w, s in zip(lr.coef_[0], scaler.scale_)]
    intercept = float(lr.intercept_[0] - sum(w*m for w, m in zip(weights, scaler.mean_)))
    return weights, intercept


def plot_bounds(column):
    lo, hi = float(column.min()), float(column.max())
    pad = max(.2, (hi-lo)*.07)
    return (lo-pad, hi+pad)


def crossing(xb, yb, w, b):
    x0, x1 = xb; y0, y1 = yb
    candidates = []
    if abs(w[1]) > 1e-12:
        for x in (x0, x1):
            y = -(w[0]*x + b)/w[1]
            if y0-1e-8 <= y <= y1+1e-8: candidates.append((x, y))
    if abs(w[0]) > 1e-12:
        for y in (y0, y1):
            x = -(w[1]*y + b)/w[0]
            if x0-1e-8 <= x <= x1+1e-8: candidates.append((x, y))
    unique = []
    for p in candidates:
        if not any(abs(p[0]-q[0]) < 1e-7 and abs(p[1]-q[1]) < 1e-7 for q in unique):
            unique.append(p)
    return unique[:2] if len(unique) >= 2 else []


def add_points(fig, test, axes, three=False):
    for flag, label, color in [(0, "실제 아님 (0) 💚", "#64ceb2"),
                                (1, "실제 뇌졸중 (1) 💗", "#f58ab5")]:
        data = test.loc[test["stroke"].eq(flag)]
        if three:
            fig.add_trace(go.Scatter3d(x=data[axes[0]], y=data[axes[1]], z=data[axes[2]],
                name=label, mode="markers", text=data["id"].astype(str),
                marker=dict(color=color, size=4, opacity=.9),
                hovertemplate="번호 %{text}<br>x %{x:.2f}<br>y %{y:.2f}<br>z %{z:.2f}<extra></extra>"))
        else:
            fig.add_trace(go.Scatter(x=data[axes[0]], y=data[axes[1]],
                name=label, mode="markers", text=data["id"].astype(str),
                marker=dict(color=color, size=8, opacity=.84, line=dict(color="#fff", width=1)),
                hovertemplate="번호 %{text}<br>x %{x:.2f}<br>y %{y:.2f}<extra></extra>"))


def draw_2d(train, test, axes):
    all_data = pd.concat([train, test])
    xb, yb = [plot_bounds(all_data[f]) for f in axes]
    fig = go.Figure()
    outside = []
    for balanced, name, color in [(False,"무게 맞추기 전 💜","#8279db"),
                                  (True,"무게 맞춘 뒤 💗","#f27ea9")]:
        model = train_models(train, axes, balanced)["확률 모델"]
        w,b = original_weights(model)
        line = crossing(xb, yb, w, b)
        if not line:
            outside.append(name)
        else:
            fig.add_trace(go.Scatter(
                x=[p[0] for p in line], y=[p[1] for p in line], mode="lines",
                name=name+" · 0.5", line=dict(color=color,width=4,
                    dash="dash" if balanced else "solid")
            ))
    add_points(fig, test, axes)
    fig.update_layout(height=485, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#5f4c76"),
        margin=dict(l=22, r=18, t=25, b=36), legend=dict(orientation="h", y=1.15, x=0),
        xaxis=dict(title=LABELS[axes[0]], range=list(xb), gridcolor="#f1e4f0"),
        yaxis=dict(title=LABELS[axes[1]], range=list(yb), gridcolor="#f1e4f0"))
    return fig, outside


def make_plane(train, test, axes, model, color, name):
    all_data = pd.concat([train, test])
    bound = [plot_bounds(all_data[f]) for f in axes]
    w, bias = original_weights(model)
    # 수직 평면도 그릴 수 있도록 기여도가 가장 큰 축을 종속 좌표로 설정
    solve = max(range(3), key=lambda k:abs(w[k])*(bound[k][1]-bound[k][0]))
    if abs(w[solve]) < 1e-12:
        return None
    indep = [i for i in range(3) if i != solve]
    v1 = [bound[indep[0]][0] + (bound[indep[0]][1]-bound[indep[0]][0])*k/32 for k in range(33)]
    v2 = [bound[indep[1]][0] + (bound[indep[1]][1]-bound[indep[1]][0])*k/32 for k in range(33)]
    points = [[], [], []]
    visible = 0
    for t in v2:
        rows = [[], [], []]
        for s in v1:
            val = -(bias+w[indep[0]]*s+w[indep[1]]*t)/w[solve]
            vals = {indep[0]:s, indep[1]:t, solve:val}
            if bound[solve][0] <= val <= bound[solve][1]:
                visible += 1
                for j in range(3): rows[j].append(vals[j])
            else:
                for j in range(3): rows[j].append(float("nan"))
        for j in range(3): points[j].append(rows[j])
    if not visible:
        return None
    return go.Surface(x=points[0], y=points[1], z=points[2], name=name,
                      opacity=.33, showscale=False, showlegend=True,
                      colorscale=[[0,color],[1,color]], surfacecolor=[[1]*33 for _ in range(33)],
                      hovertemplate=name+"<extra></extra>")


def draw_3d(train, test, axes):
    fig = go.Figure()
    outside = []
    for balanced, name, color in [(False,"무게 맞추기 전 💜","#8279db"),
                                  (True,"무게 맞춘 뒤 💗","#f27ea9")]:
        model = train_models(train, axes, balanced)["확률 모델"]
        plane = make_plane(train, test, axes, model, color, name)
        if plane is None:
            outside.append(name)
        else:
            fig.add_trace(plane)
    add_points(fig, test, axes, True)
    all_data = pd.concat([train, test])
    b = [plot_bounds(all_data[f]) for f in axes]
    fig.update_layout(height=620, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#5f4c76"),
        margin=dict(l=0,r=0,t=26,b=0), legend=dict(orientation="h", y=1, x=0),
        scene=dict(xaxis=dict(title=LABELS[axes[0]], range=list(b[0])),
                   yaxis=dict(title=LABELS[axes[1]], range=list(b[1])),
                   zaxis=dict(title=LABELS[axes[2]], range=list(b[2])),
                   bgcolor="rgba(0,0,0,0)", aspectmode="cube"))
    return fig, outside


with st.sidebar:
    st.markdown("### 🎨 연구실 이동하기 💗")
    st.page_link("main.py",label="🏠 데이터 소개",use_container_width=True)
    st.page_link("pages/1_탐색.py",label="🔎 탐색 놀이터",use_container_width=True)
    st.page_link("pages/2_분류_모델.py",label="🧸 분류 모델 연구실",use_container_width=True)
    st.page_link("pages/3_채점표.py",label="💌 채점표 연구실",use_container_width=True)
    st.page_link("pages/4_전처리.py",label="🫧 전처리 실험실",use_container_width=True)
    st.page_link("pages/5_내가_만든_모델_소개.py", label="💝 내 모델 소개", use_container_width=True)
    st.divider()
    st.markdown('<div class="candy-brand"><div class="brand-flower">🧁</div>'
                '<div><strong>두근두근 연구소</strong><small>SWEET DATA LAB ♡</small></div></div>',
                unsafe_allow_html=True)
    st.caption("🎀 뇌졸중 데이터는 수업용 예시이며 의료 진단에 쓰면 안 돼요.")

st.markdown("""
<div class="candy-hero">
  <div class="hero-copy">
    <div class="hero-eyebrow">🫧 PREPROCESSING · NOTE 05</div>
    <h1>말랑말랑 <span class="highlight">전처리 연구실 ♡</span></h1>
    <p>BMI를 어떻게 다룰까? 드문 뇌졸중 경험자에게 무게를 맞추면 어떤 변화가 생길까~?
       보정 전과 후를 같은 사람으로 채점하고 그래프로 비교해 보자! 💗</p>
    <div class="hero-pills"><span>💜 보정 전</span><span>💗 보정 후</span><span>🧁 혼동행렬</span></div>
  </div><div class="hero-buddy"><div class="buddy-face">🫧</div><div class="buddy-label">LOVE DATA ♡</div></div>
</div>
""",unsafe_allow_html=True)
section("🎛️","오늘의 실험 조건 먼저 고르기~! 💌",
        "무게를 맞추기 전과 맞춘 뒤 결과는 스위치와 상관없이 항상 나란히 보여 줘!")
a,b=st.columns(2)
with a:
    enabled=st.toggle("💗 아래 놓친 환자 목록에 무게 맞춘 모델 적용",value=False,
                      help="켜도 두 모델 모두 보정 전/후를 항상 계산하고 비교해요.")
with b:
    missing_bmi=st.radio("🧁 BMI 빈 값 다루기",
        ["그대로 두기","빈 값 있는 사람 삭제하기"],horizontal=True)
features=st.multiselect("🎀 모델이 참고할 입력 속성 고르기 (최소 2개)",
    FEATURES,default=["age","avg_glucose_level","hypertension","heart_disease"],
    format_func=lambda f:LABELS[f])
if len(features)<2:
    st.info("🥹 입력 속성을 2개 이상 골라 줄래~? 💞")
    st.stop()

try:
    raw=load_data()
    train,test,removed=prepare_data(raw,features,missing_bmi=="빈 값 있는 사람 삭제하기")
    before=train_models(train,features,False)
    after=train_models(train,features,True)
except Exception as exc:
    st.error(f"🥺 데이터를 준비하거나 학습할 수 없었어: {exc}")
    st.stop()
if missing_bmi=="빈 값 있는 사람 삭제하기":
    st.info(f"🧺 BMI 빈 값이 있는 {removed[0]:,}명을 지웠어. 그중 뇌졸중 경험자는 {removed[1]:,}명이야~! 💕")
else:
    st.caption("💗 BMI를 선택했다면 비어 있는 칸은 훈련용 중앙값으로 채웠어! 선택하지 않았다면 건드리지 않았어.")
st.markdown(f"**🍓 훈련용 {len(train):,}명 · 🧁 채점용 {len(test):,}명 · 💗 채점용 뇌졸중 경험자 {test['stroke'].eq(1).sum():,}명**")
st.caption("🫧 ID순으로 열 명 중 앞 세 명을 채점용으로 고정한 뒤 BMI 삭제를 적용했어. 전후 비교에는 동일한 채점 집단을 사용해!")
section("📋","AI 친구들의 전·후 성적표! 💘",
        "실제=행 / 예측=열 · 뇌졸중을 양성(1)으로 계산했어. TP·FP·FN·TN 인원과 네 지표를 비교해 봐!")
true=test["stroke"].astype(int)
results={}
for name in ("확률 모델","질문 모델"):
    left=confusion_counts(true,before[name].predict(test[features]))
    right=confusion_counts(true,after[name].predict(test[features]))
    results[name]=(left,right)
    st.markdown(f"### {'💗' if name=='확률 모델' else '🍡'} {name} · 전 vs 후")
    col1,col2=st.columns(2)
    with col1:
        st.markdown("**💜 보정 전 혼동행렬**")
        st.dataframe(score_table(left),use_container_width=True)
    with col2:
        st.markdown("**💗 보정 후 혼동행렬**")
        st.dataframe(score_table(right),use_container_width=True)
    st.dataframe(score_comparison(left,right),use_container_width=True)
    st.success(f"💌 찾아낸 환자(TP) {left['TP']}명 → {right['TP']}명 · "
        f"놓친 환자(FN) {left['FN']}명 → {right['FN']}명 · "
        f"헛짚은 사람(FP) {left['FP']}명 → {right['FP']}명")

section("🍬","두 축의 0.5 결정 경계선 비교 💜💗",
        "여기 선은 선택한 두 축만으로 새로 학습했어. 점의 색은 실제 뇌졸중 여부야!")
col1,col2=st.columns(2)
with col1:
    ax=st.selectbox("🍓 가로축",features,format_func=lambda f:LABELS[f])
with col2:
    ay=st.selectbox("🫐 세로축",[f for f in features if f!=ax],format_func=lambda f:LABELS[f])
fig,outside=draw_2d(train,test,[ax,ay])
st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False})
for name in outside:
    st.info(f"🫧 {name}의 0.5 결정 경계는 그래프 표시 범위 밖에 있어.")

if len(features)>=3:
    section("🌈","빙글빙글 3차원 결정 평면 ♡",
            "선택한 세 축만으로 각각 모델을 다시 학습했어. 그래프를 드래그해서 회전해 봐~! 💕")
    a,b,c=st.columns(3)
    with a:
        x=st.selectbox("🍓 X축",features,key="axis_3d_x",format_func=lambda f:LABELS[f])
    with b:
        y=st.selectbox("🪻 Y축",[f for f in features if f!=x],key="axis_3d_y",format_func=lambda f:LABELS[f])
    with c:
        z=st.selectbox("🫧 Z축",[f for f in features if f not in (x,y)],key="axis_3d_z",format_func=lambda f:LABELS[f])
    chart,outside3=draw_3d(train,test,[x,y,z])
    st.plotly_chart(chart,use_container_width=True,config={"displaylogo":False})
    for name in outside3:
        st.info(f"🫧 {name}의 0.5 결정 평면은 현재 3D 표시 범위 밖에 있어.")

section("💌","확률 모델이 놓친 환자 목록 ♡",
        "스위치 ON은 보정 후, OFF는 보정 전 · 나이가 어린 순으로 정렬해!")
active=after["확률 모델"] if enabled else before["확률 모델"]
pred=active.predict(test[features])
miss=test.loc[(test["stroke"].eq(1))&(pred==0)].copy()
miss=miss.sort_values(["age","id"],ascending=[True,True])
st.markdown(f"**{'💗 보정 후' if enabled else '💜 보정 전'}: 놓친 환자 {len(miss):,}명**")
st.dataframe(miss[["id","age","hypertension","heart_disease"]].rename(
    columns={"id":"번호","age":"나이","hypertension":"고혈압 여부",
             "heart_disease":"심장병 여부"}),hide_index=True,use_container_width=True)
st.caption(f"🍓 목록의 {len(miss)}명 = 혼동행렬 FN {results['확률 모델'][1 if enabled else 0]['FN']}명 · 딱 맞아~! 💕")
st.caption("🩷 이 프로젝트는 학습용 통계 예시이며 의료 진단이나 인과관계 증명에 사용하지 않아요.")
