"""🍭 두근두근 데이터 연구소 - 뇌졸중 데이터 탐색 페이지.

이 파일을 반드시 `main.py`와 같은 위치의 `pages/1_탐색.py`로 저장하세요.
Streamlit의 기본 멀티페이지 탐색 메뉴가 자동으로 이 페이지를 표시합니다.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"

st.set_page_config(
    page_title="탐색 놀이터 | 두근두근 데이터 연구소",
    page_icon="🍭",
    layout="wide",
    initial_sidebar_state="expanded",
)

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


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")


def section(icon, title, detail=""):
    st.markdown(
        f'<div class="section-title-row"><div class="section-emoji">{icon}</div>'
        f'<h2>{title}</h2></div><div class="section-sub">{detail}</div>',
        unsafe_allow_html=True,
    )


def panel(eyebrow, title, help_text=""):
    st.markdown(
        f'<div class="candy-panel"><div class="panel-eyebrow">{eyebrow}</div>'
        f'<div class="panel-title">{title}</div>'
        f'<div class="panel-help">{help_text}</div></div>',
        unsafe_allow_html=True,
    )


def plot_layout(fig, height=315, horizontal=False):
    """파스텔톤 Plotly 그래프의 공통 스타일."""
    fig.update_layout(
        height=height,
        margin=dict(l=22, r=19, t=18, b=27),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Nunito, Noto Sans KR, sans-serif", color="#6d5b83", size=12),
        hoverlabel=dict(bgcolor="#fff9fd", bordercolor="#f2cce7", font_color="#5a4770"),
        showlegend=False,
    )
    axis = dict(showgrid=True, gridcolor="#f7eaf3", zeroline=False,
                showline=False, ticks="", tickfont=dict(color="#9b89a7"))
    if horizontal:
        fig.update_xaxes(**axis)
        fig.update_yaxes(showgrid=False, zeroline=False, tickfont=dict(color="#6c5a84"))
    else:
        fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color="#9b89a7"))
        fig.update_yaxes(**axis)
    return fig


def histogram(values, color, label, bins):
    data = pd.to_numeric(values, errors="coerce").dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=data, nbinsx=bins, marker=dict(color=color, line=dict(color="white", width=1.2)),
        hovertemplate=f"{label}: %{{x:.1f}}<br>사람 수: %{{y:,}}명<extra></extra>",
    ))
    fig.update_layout(bargap=.075)
    fig.update_xaxes(title_text=label)
    fig.update_yaxes(title_text="사람 수")
    return plot_layout(fig)


def box_plot(df, column, ylabel):
    fig = go.Figure()
    for code, group, color in [(0, "경험 없음", "#9bdecf"), (1, "경험 있음", "#ff91be")]:
        values = df.loc[df["stroke"] == code, column].dropna()
        fig.add_trace(go.Box(
            y=values,
            name=group,
            marker_color=color,
            line=dict(color="#876a9d", width=1.5),
            fillcolor=color,
            boxpoints="outliers",
            jitter=.23,
            pointpos=0,
            marker=dict(color=color, opacity=.62, size=4),
            hovertemplate="값: %{y:.2f}<extra>" + group + "</extra>",
        ))
    fig.update_yaxes(title_text=ylabel)
    return plot_layout(fig)


def outcome_by_flag(df, column):
    """0/1 항목별 뇌졸중 경험자 비율: 각 집단 자체를 분모로 계산."""
    grouped = (
        df[df[column].isin([0, 1]) & df["stroke"].isin([0, 1])]
        .groupby(column)["stroke"]
        .agg(["size", "sum"])
        .reindex([0, 1], fill_value=0)
    )
    grouped.columns = ["사람 수", "경험자 수"]
    grouped["경험 비율(%)"] = (
        grouped["경험자 수"].div(grouped["사람 수"].where(grouped["사람 수"] != 0)) * 100
    ).fillna(0)
    return grouped


def rate_bar(stats, color_pair):
    values = stats["경험 비율(%)"].tolist()
    totals = stats["사람 수"].tolist()
    hits = stats["경험자 수"].tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["없음 (0)", "있음 (1)"],
        y=values,
        marker=dict(color=color_pair, line=dict(color="#fff", width=2)),
        text=[f"{v:.2f}%" for v in values],
        textposition="outside",
        textfont=dict(size=16, color="#6f5b88", family="Nunito"),
        customdata=list(zip(hits, totals)),
        hovertemplate="뇌졸중 경험 비율: %{y:.2f}%<br>경험자: %{customdata[0]}명<br>전체: %{customdata[1]}명<extra></extra>",
    ))
    fig.update_yaxes(title_text="뇌졸중 경험 비율 (%)", range=[0, max(max(values)*1.28, 1)])
    fig.update_layout(bargap=.46)
    return plot_layout(fig)


with st.sidebar:
    st.markdown(
        '<div class="candy-brand"><div class="brand-flower">🍓</div>'
        '<div><strong>두근두근 연구소</strong><small>SWEET DATA LAB</small></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="side-note">🍭 <b>탐색 놀이터에 온 걸 환영해!</b><br>'
        '히스토그램과 상자그림을 살펴보고, 비율도 비교해 봐요.<br>'
        '홈은 왼쪽 기본 페이지 메뉴에서 돌아갈 수 있어요. ♡</div>',
        unsafe_allow_html=True,
    )
    st.caption("📌 이 데이터는 교육용입니다. 그룹 간 차이가 원인이나 개인의 위험도를 뜻하지는 않아요.")

st.markdown(
    """
    <div class="candy-hero">
      <span class="spark a">✳</span><span class="spark b">✧</span>
      <span class="spark c">✦</span>
      <div class="hero-copy">
        <div class="hero-eyebrow">🍬 WELCOME TO THE EXPLORATION ROOM</div>
        <h1>반짝반짝<br><span class="highlight">데이터 탐색 놀이터!</span></h1>
        <p>나이, 혈당, 고혈압, 심장병, BMI와 흡연 상태까지!<br>
        그래프 속에서 숨은 패턴을 찾는 즐거운 시간이에요. ✨</p>
        <div class="hero-pills"><span>🍡 히스토그램</span>
          <span>🧸 그룹별 비교</span><span>🎀 빈 값 살펴보기</span></div>
      </div>
      <div class="hero-buddy"><div class="buddy-face">🐰</div>
        <div class="buddy-label">데이터 탐험 출발! ♡</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    raw = load_data()
except Exception as exc:
    st.error("🍓 데이터를 불러오지 못했어요. 인터넷 연결이나 CSV 주소를 확인해 주세요.")
    st.caption(f"오류 종류: {type(exc).__name__}")
    st.stop()

required = {"age", "avg_glucose_level", "hypertension", "heart_disease", "bmi", "smoking_status", "stroke"}
if not required.issubset(raw.columns):
    st.error("데이터 열이 부족해요: " + ", ".join(sorted(required - set(raw.columns))))
    st.stop()

data = raw.copy()
for col in ["age", "avg_glucose_level", "hypertension", "heart_disease", "bmi", "stroke"]:
    data[col] = pd.to_numeric(data[col], errors="coerce")

st.markdown('<div class="chip-row"><span class="chip">🫧 1명 = 1행</span>'
            '<span class="chip">🎈 0 = 경험 없음</span><span class="chip">💗 1 = 경험 있음</span>'
            '<span class="chip">🔎 모든 그래프는 원본 전체 자료 기준</span></div>',
            unsafe_allow_html=True)

section("🍮", "01. 나이와 혈당은 어떻게 퍼져 있을까?", "두 개의 히스토그램을 나란히 비교해요.")
bin_count = st.slider("히스토그램 막대 구간 수", min_value=10, max_value=60, value=25, step=5)
left, right = st.columns(2, gap="large")
with left:
    panel("HISTOGRAM / AGE", "🍑 나이 분포", "막대 높이는 해당 나이 구간의 사람 수예요.")
    st.plotly_chart(histogram(data["age"], "#ff9ac2", "나이 (세)", bin_count), use_container_width=True,
                    config={"displayModeBar": False})
with right:
    panel("HISTOGRAM / GLUCOSE", "🫐 평균 혈당 분포", "사람들이 어떤 혈당 범위에 많이 모였을까요?")
    st.plotly_chart(histogram(data["avg_glucose_level"], "#a995f6", "평균 혈당", bin_count),
                    use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🧸", "02. 뇌졸중 경험에 따라 다를까?", "나이와 혈당의 상자그림을 비교하고 평균값을 확인해요.")
left, right = st.columns(2, gap="large")
with left:
    panel("BOX PLOT / AGE", "🌷 나이 상자그림", "상자와 중앙선을 보면 데이터의 분포를 비교할 수 있어요.")
    st.plotly_chart(box_plot(data, "age", "나이 (세)"), use_container_width=True,
                    config={"displayModeBar": False})
with right:
    panel("BOX PLOT / GLUCOSE", "🍇 평균 혈당 상자그림", "점은 상자그림에서 벗어난 값(이상치)을 나타내요.")
    st.plotly_chart(box_plot(data, "avg_glucose_level", "평균 혈당"), use_container_width=True,
                    config={"displayModeBar": False})

means = (
    data[data["stroke"].isin([0, 1])]
    .groupby("stroke")[["age", "avg_glucose_level"]]
    .mean().reindex([0, 1])
)
mean_table = pd.DataFrame({
    "그룹": ["뇌졸중 경험 없음 (0)", "뇌졸중 경험 있음 (1)"],
    "평균 나이": means["age"].round(2).to_numpy(),
    "평균 혈당": means["avg_glucose_level"].round(2).to_numpy(),
})
panel("GROUP MEANS", "📋 두 그룹의 평균값", "각 그룹별 결측값은 해당 열의 평균 계산에서 제외했어요.")
st.dataframe(mean_table, hide_index=True, use_container_width=True,
             column_config={"평균 나이": st.column_config.NumberColumn(format="%.2f"),
                            "평균 혈당": st.column_config.NumberColumn(format="%.2f")})

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("💝", "03. 질환 여부에 따른 비율 비교", "각 집단의 전체 사람 수를 기준으로 뇌졸중 경험 비율을 계산했어요.")
left, right = st.columns(2, gap="large")
with left:
    panel("CONDITION / HYPERTENSION", "🍓 고혈압 여부", "없음(0)과 있음(1)의 비율을 비교해요.")
    hypertension = outcome_by_flag(data, "hypertension")
    st.plotly_chart(rate_bar(hypertension, ["#a9e3d6", "#ff8bb9"]), use_container_width=True,
                    config={"displayModeBar": False})
with right:
    panel("CONDITION / HEART DISEASE", "💜 심장병 여부", "없음(0)과 있음(1)의 비율을 비교해요.")
    heart = outcome_by_flag(data, "heart_disease")
    st.plotly_chart(rate_bar(heart, ["#bcaaf8", "#ffc777"]), use_container_width=True,
                    config={"displayModeBar": False})
st.markdown(
    '<div class="sticky-note">🍰 이 그래프의 비율은 “각 그룹의 뇌졸중 경험자 수 ÷ 해당 그룹의 전체 사람 수”예요. '
    '관찰된 차이는 인과관계를 증명하지 않아요.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🫧", "04. BMI가 비어 있는 사람은?", "BMI 결측 집단과 전체 집단의 뇌졸중 경험 비율을 나란히 비교해요.")
missing_bmi = data[data["bmi"].isna()]
valid_all = data["stroke"].isin([0, 1])
valid_missing = missing_bmi["stroke"].isin([0, 1])
whole_count = int(valid_all.sum())
whole_hits = int((data.loc[valid_all, "stroke"] == 1).sum())
missing_count = int(valid_missing.sum())
missing_hits = int((missing_bmi.loc[valid_missing, "stroke"] == 1).sum())
missing_rate = missing_hits / missing_count * 100 if missing_count else None
whole_rate = whole_hits / whole_count * 100 if whole_count else None
bmi_table = pd.DataFrame({
    "비교 집단": ["BMI가 비어 있는 사람", "전체 사람"],
    "사람 수": [missing_count, whole_count],
    "뇌졸중 경험자 수": [missing_hits, whole_hits],
    "뇌졸중 경험 비율 (%)": [missing_rate, whole_rate],
})
panel("MISSING VALUES / BMI", "📋 BMI 결측과 뇌졸중 비율", "BMI 결측은 숫자를 채우지 않고 실제 비어 있는 행만 골랐어요.")
st.dataframe(bmi_table, hide_index=True, use_container_width=True,
             column_config={"뇌졸중 경험 비율 (%)": st.column_config.NumberColumn(format="%.2f%%")})
st.caption(f"🧁 BMI가 비어 있는 사람: {len(missing_bmi):,}명 / 전체: {len(data):,}명 · BMI가 전부 채워져 있다면 결측 그룹 비율은 표시되지 않아요.")

st.markdown('<div class="rainbow-line"></div>', unsafe_allow_html=True)
section("🚬", "05. 흡연 상태별로 몇 명일까?", "CSV의 흡연 상태 값을 있는 그대로 구분하여 인원을 세었어요.")
smoking = raw["smoking_status"].fillna("(빈 값)").astype(str).value_counts(dropna=False)
smoking_table = pd.DataFrame({
    "흡연 상태": smoking.index,
    "사람 수": smoking.values,
    "전체 비율 (%)": (smoking.values / len(raw) * 100).round(2) if len(raw) else 0,
})
left, right = st.columns([1.1, .9], gap="large")
with left:
    panel("SMOKING STATUS / TABLE", "📒 흡연 상태 인원표", "Unknown은 원본의 '알 수 없음' 범주로 유지했어요.")
    st.dataframe(smoking_table, hide_index=True, use_container_width=True,
                 column_config={"전체 비율 (%)": st.column_config.NumberColumn(format="%.2f%%")})
with right:
    fig = go.Figure(go.Pie(
        labels=smoking.index.tolist(), values=smoking.values.tolist(),
        hole=.62, sort=False,
        marker=dict(colors=["#ff8eb8", "#bca7ff", "#91dfce", "#ffd27f", "#92c9f5"],
                    line=dict(color="white", width=3)),
        textinfo="percent", textposition="inside",
        hovertemplate="%{label}<br>%{value:,}명 · %{percent}<extra></extra>",
    ))
    fig = plot_layout(fig, height=290)
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-.20, x=.5, xanchor="center",
                                                  font=dict(size=10)))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown(
    '<div class="foot-note">✧ 그래프를 누르고 마우스를 올려 자세한 값을 확인해 봐요! · SWEET DATA LAB ♡</div>',
    unsafe_allow_html=True,
)
