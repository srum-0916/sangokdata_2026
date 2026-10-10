"""급식 규칙 찾기: 학교 중식 장바구니 연관 규칙 대시보드."""

from __future__ import annotations

import re
from collections import Counter
from itertools import combinations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


DATA_URL = (
    "https://raw.githubusercontent.com/teacher188-netizen/2026-datascience/"
    "refs/heads/main/dorim_meals.csv"
)
COLUMNS = ["조건", "결과", "동시", "지지도", "신뢰도", "향상도"]
SORT_OPTIONS = {
    "향상도 높은 순": ["향상도", "신뢰도", "동시"],
    "신뢰도 높은 순": ["신뢰도", "동시", "향상도"],
    "동시 등장 많은 순": ["동시", "신뢰도", "향상도"],
}

st.set_page_config(
    page_title="급식 규칙 찾기 | MEAL LAB",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"], [data-testid="stApp"] {
        font-family: 'DM Sans', 'Noto Sans KR', sans-serif;
    }
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 92% 2%, #e9eefe 0, transparent 28%),
                    linear-gradient(180deg, #f7f9fd 0%, #f1f5fb 100%);
    }
    [data-testid="stHeader"] {background: transparent;}
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7ecf6;
    }
    [data-testid="stSidebar"] .block-container {padding-top: 2rem;}
    .block-container {padding-top: 2.0rem; padding-bottom: 3rem; max-width: 1400px;}
    h1, h2, h3 {letter-spacing: -.045em;}
    div[data-testid="stVerticalBlock"] {gap: .75rem;}
    .hero {
        background: linear-gradient(112deg, #151f46 0%, #293a89 55%, #6654d5 100%);
        color: white;
        padding: 35px 40px 38px;
        border-radius: 25px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 16px 35px rgba(43, 64, 145, .15);
        margin-bottom: 16px;
    }
    .hero:after {
        content: ''; position: absolute; width: 290px; height: 290px;
        right: -90px; top: -160px; border: 57px solid rgba(255,255,255,.09);
        border-radius: 50%; pointer-events: none;
    }
    .eyebrow {font-size: 12px; font-weight: 800; letter-spacing: .2em;
              color: #c3d2ff; margin-bottom: 13px;}
    .hero-title {font-size: clamp(30px, 3.3vw, 48px); font-weight: 900;
                 letter-spacing: -.055em; line-height: 1.25; margin-bottom: 10px;}
    .hero-sub {color: #e4e9ff; font-size: 15px; line-height: 1.85; max-width: 790px;}
    .stat-card {
        padding: 19px 22px 18px;
        background: white; border: 1px solid #e6ebf6;
        border-radius: 18px;
        box-shadow: 0 7px 25px rgba(33, 53, 105, .045);
        min-height: 117px;
    }
    .stat-label {font-size: 13px; font-weight: 700; color: #75829c;}
    .stat-value {font-size: clamp(27px, 2.7vw, 38px); font-weight: 900;
                 color: #1d2855; letter-spacing: -.04em; margin-top: 5px;}
    .stat-unit {font-size: 14px; font-weight: 700; color: #8b97ae; margin-left: 5px;}
    .section-title {font-weight: 900; font-size: 22px; color: #1b2852;
                    letter-spacing: -.045em; margin: 26px 0 4px;}
    .section-desc {font-size: 13px; color: #71809d; margin-bottom: 8px;}
    .side-brand {font-weight: 900; font-size: 19px; color: #253575;
                 letter-spacing: -.04em; margin: 0 0 7px;}
    .side-caption {font-size: 12px; color: #8190ab; margin: 0 0 17px; line-height: 1.75;}
    div[data-testid="stDataFrame"] {
        border: 1px solid #e7ebf5; border-radius: 14px; overflow: hidden;
        box-shadow: 0 7px 24px rgba(33, 53, 105, .04);
    }
    div.stButton > button, div.stDownloadButton > button {
        border-radius: 11px; font-weight: 750; border: 1px solid #d6dff2;
    }
    div.stDownloadButton > button {
        background: #253a82; color: white; border-color: #253a82;
    }
    div.stDownloadButton > button:hover {
        background: #3b50a8; color: white; border-color: #3b50a8;
    }
    div[data-testid="stPlotlyChart"] {
        border: 1px solid #e7ebf5; border-radius: 17px;
        background: #fff; overflow: hidden;
        box-shadow: 0 7px 24px rgba(33, 53, 105, .04);
    }
    .help-note {background: #edf2fe; border: 1px solid #dfe8ff;
                border-radius: 13px; color: #45608e; padding: 13px 17px;
                font-size: 13px; line-height: 1.8; margin-top: 13px;}
    @media(max-width: 720px) {
        .hero {padding: 26px 22px; border-radius: 18px;}
        .hero-sub {font-size: 13px;}
        .stat-card {padding: 15px 12px; min-height: 98px;}
        .stat-label {font-size: 11px;}
        .stat-value {font-size: 25px;}
        .stat-unit {font-size: 11px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_meals() -> pd.DataFrame:
    """원본 CSV를 가져와 중식만 골라 날짜당 1개의 장바구니로 정리한다."""
    raw = pd.read_csv(DATA_URL, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    raw.columns = raw.columns.str.strip().str.replace("\ufeff", "", regex=False)
    missing = set(("날짜", "식사", "메뉴")) - set(raw.columns)
    if missing:
        raise ValueError(f"CSV에 필요한 열이 없습니다: {', '.join(sorted(missing))}")

    raw = raw.loc[raw["식사"].str.strip().eq("중식")].copy()
    date_text = raw["날짜"].str.strip().str.replace(r"\.0$", "", regex=True)
    raw["날짜"] = pd.to_datetime(date_text, format="%Y%m%d", errors="coerce")
    raw = raw.dropna(subset=["날짜"])

    # 같은 날짜의 행이 두 개 이상 있어도 장바구니는 하루에 정확히 하나.
    meals = (
        raw.groupby("날짜", as_index=False)["메뉴"]
        .agg(lambda values: " | ".join(values))
        .sort_values("날짜")
        .reset_index(drop=True)
    )
    meals["메뉴목록"] = meals["메뉴"].map(parse_menu_items)
    meals = meals.loc[meals["메뉴목록"].map(bool)].reset_index(drop=True)
    return meals


def clean_name(name: str) -> str:
    """괄호(중첩 괄호 포함) 및 그 내부 설명을 완전히 제거한다."""
    name = str(name)
    # 일반 소괄호, 전각 소괄호, 대괄호, 전각 대괄호도 제거.
    pattern = r"\([^()]*\)|（[^（）]*）|\[[^\[\]]*\]|【[^【】]*】"
    previous = None
    while name != previous:
        previous = name
        name = re.sub(pattern, "", name)
    return re.sub(r"\s+", " ", name).strip()


def parse_menu_items(text: str) -> list[str]:
    # 하루에 동일한 이름의 음식이 중복되어도 한 번만 센다.
    return sorted({item for chunk in str(text).split("|") if (item := clean_name(chunk))})


def find_rules(baskets: list[list[str]]) -> tuple[pd.DataFrame, Counter, Counter]:
    """두 방향 A→B, B→A의 지지도/신뢰도/향상도를 계산한다.

    지지도(%) = P(A ∩ B) × 100
    신뢰도(%) = P(B | A) × 100
    향상도     = P(B | A) / P(B)
    """
    n_days = len(baskets)
    singles: Counter = Counter()
    pairs: Counter = Counter()

    for basket in baskets:
        unique = sorted(set(basket))
        singles.update(unique)
        pairs.update(combinations(unique, 2))

    rows = []
    for (a, b), both in pairs.items():
        for condition, result in ((a, b), (b, a)):
            rows.append(
                {
                    "조건": condition,
                    "결과": result,
                    "동시": both,
                    "지지도": both / n_days * 100,
                    "신뢰도": both / singles[condition] * 100,
                    "향상도": (both * n_days) / (singles[condition] * singles[result]),
                }
            )

    return pd.DataFrame(rows, columns=COLUMNS), singles, pairs


def section(title: str, description: str) -> None:
    st.markdown(
        f'<div class="section-title">{title}</div>'
        f'<div class="section-desc">{description}</div>',
        unsafe_allow_html=True,
    )


def draw_lift_chart(rules: pd.DataFrame) -> None:
    top = rules.sort_values(
        by=["향상도", "신뢰도", "동시", "조건", "결과"],
        ascending=[False, False, False, True, True],
        kind="stable",
    ).head(10).iloc[::-1].copy()
    top["이름"] = top["조건"] + " → " + top["결과"]
    hover_data = top[["동시", "지지도", "신뢰도"]].to_numpy()

    fig = go.Figure(
        go.Bar(
            x=top["향상도"],
            y=top["이름"],
            orientation="h",
            customdata=hover_data,
            text=top["향상도"].map(lambda v: f"{v:.2f}배"),
            textposition="outside",
            cliponaxis=False,
            marker={
                "color": top["향상도"],
                "colorscale": [[0, "#9db9f6"], [1, "#6050c6"]],
                "showscale": False,
                "line": {"width": 0},
            },
            hovertemplate=(
                "<b>%{y}</b><br>향상도 <b>%{x:.2f}배</b>"
                "<br>동시 등장 %{customdata[0]}일"
                "<br>지지도 %{customdata[1]:.2f}%"
                "<br>신뢰도 %{customdata[2]:.2f}%<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        template="plotly_white",
        height=max(385, 56 * len(top) + 95),
        margin=dict(l=24, r=85, t=30, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR, DM Sans, sans-serif", color="#415078", size=12),
        xaxis=dict(
            title="향상도 (배)",
            gridcolor="#edf0f7",
            zeroline=False,
            rangemode="tozero",
        ),
        yaxis=dict(title=None, automargin=True, tickfont=dict(size=11)),
        bargap=0.32,
        showlegend=False,
        hoverlabel=dict(bgcolor="white", font=dict(color="#25356b")),
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False, "toImageButtonOptions": {"filename": "급식_향상도_TOP10"}},
    )


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">MEAL LAB · ASSOCIATION ANALYTICS</div>
        <div class="hero-title">급식 규칙 찾기 🍱</div>
        <div class="hero-sub">
            함께 등장한 메뉴 사이의 숨은 관계를 찾아보세요.<br>
            하루 식단을 하나의 장바구니로 분석하고, 지지도·신뢰도·향상도를 한눈에 비교합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    meals = load_meals()
except Exception as exc:
    st.error("급식 데이터를 불러오지 못했어요. CSV 주소와 네트워크 연결을 확인해 주세요.")
    st.code(str(exc))
    if st.button("데이터 다시 불러오기"):
        load_meals.clear()
        st.rerun()
    st.stop()

if meals.empty:
    st.warning("CSV에서 날짜와 메뉴가 있는 중식 데이터를 찾지 못했어요.")
    st.stop()

with st.sidebar:
    st.markdown('<div class="side-brand">⚙️ 분석 설정</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="side-caption">선택하는 즉시 규칙 표와 그래프가 함께 바뀝니다.</div>',
        unsafe_allow_html=True,
    )
    min_day, max_day = meals["날짜"].min().date(), meals["날짜"].max().date()
    selected_dates = st.date_input(
        "분석 기간",
        value=(min_day, max_day),
        min_value=min_day,
        max_value=max_day,
        format="YYYY.MM.DD",
        help="이 기간에 해당하는 중식 날짜만 계산합니다.",
    )
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        # 날짜 범위 선택 중 한 날짜만 눌린 임시 상태에서는 전체 기간 유지.
        start_date, end_date = min_day, max_day

period = meals.loc[
    meals["날짜"].dt.date.between(start_date, end_date)
].copy()

if period.empty:
    st.warning("선택한 기간에 급식 데이터가 없어요. 왼쪽에서 기간을 바꿔 주세요.")
    st.stop()

baskets = period["메뉴목록"].tolist()
rules, singles, pairs = find_rules(baskets)
menu_options = ["전체 메뉴"] + sorted(singles)

with st.sidebar:
    st.divider()
    st.markdown("**규칙 필터**")
    chosen_menu = st.selectbox(
        "메뉴 선택",
        menu_options,
        help="조건이나 결과에 해당 메뉴가 등장하는 모든 규칙을 찾습니다.",
    )
    menu_role = st.radio(
        "메뉴가 등장하는 위치",
        ["조건 또는 결과", "조건에만", "결과에만"],
        horizontal=False,
        disabled=(chosen_menu == "전체 메뉴"),
    )
    sort_label = st.selectbox("정렬 기준", list(SORT_OPTIONS))
    min_cooccurrence = st.number_input(
        "최소 동시 등장 횟수",
        min_value=1,
        max_value=max(1, max(pairs.values(), default=1)),
        value=1,
        step=1,
        help="기본값 1은 한 번이라도 같이 나온 모든 메뉴 쌍을 보여 줍니다.",
    )
    min_confidence = st.slider(
        "최소 신뢰도 (%)", min_value=0, max_value=100, value=0, step=5
    )
    search_text = st.text_input(
        "메뉴 이름 추가 검색", placeholder="예: 김치, 치킨, 국"
    ).strip()
    st.divider()
    if st.button("🔄 CSV 최신 데이터 새로고침", use_container_width=True):
        load_meals.clear()
        st.rerun()
    st.caption("데이터 출처: GitHub의 dorim_meals.csv · 중식만 분석 · 1시간 캐시")

filtered = rules.copy()
if chosen_menu != "전체 메뉴":
    if menu_role == "조건에만":
        filtered = filtered.loc[filtered["조건"].eq(chosen_menu)]
    elif menu_role == "결과에만":
        filtered = filtered.loc[filtered["결과"].eq(chosen_menu)]
    else:
        filtered = filtered.loc[
            filtered["조건"].eq(chosen_menu) | filtered["결과"].eq(chosen_menu)
        ]
if search_text:
    filtered = filtered.loc[
        filtered["조건"].str.contains(search_text, case=False, regex=False)
        | filtered["결과"].str.contains(search_text, case=False, regex=False)
    ]
filtered = filtered.loc[
    (filtered["동시"] >= min_cooccurrence)
    & (filtered["신뢰도"] >= min_confidence)
]
filtered = filtered.sort_values(
    SORT_OPTIONS[sort_label] + ["조건", "결과"],
    ascending=[False, False, False, True, True],
    kind="stable",
).reset_index(drop=True)

st.caption(
    f"📅 분석 범위  {period['날짜'].min():%Y.%m.%d} — "
    f"{period['날짜'].max():%Y.%m.%d}  |  조건을 바꾸면 결과가 자동으로 갱신됩니다."
)

c1, c2, c3 = st.columns(3, gap="medium")
for target, label, value, unit in (
    (c1, "분석한 급식 일수", len(baskets), "일"),
    (c2, "등장한 메뉴 종류", len(singles), "종"),
    (c3, "함께 나온 메뉴 쌍", len(pairs), "쌍"),
):
    with target:
        st.markdown(
            '<div class="stat-card">'
            f'<div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value:,}<span class="stat-unit">{unit}</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )

left, right = st.columns([3, 1], vertical_alignment="center")
with left:
    section("📈 향상도 TOP 10", "현재 메뉴·횟수·신뢰도 필터에 해당하는 규칙 중 향상도가 높은 10개")
with right:
    st.caption(f"표시 중인 규칙: **{len(filtered):,}개** / 전체 {len(rules):,}개")

if filtered.empty:
    st.info("조건에 맞는 규칙이 없어요. 메뉴나 최소 동시 횟수·신뢰도를 완화해 보세요.")
else:
    draw_lift_chart(filtered)

section("📋 메뉴 연관 규칙", "각 메뉴 쌍을 A → B와 B → A 두 방향으로 계산했습니다. 표의 열 제목을 눌러 정렬할 수도 있어요.")

if not filtered.empty:
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        height=min(690, max(195, 43 * len(filtered) + 40)),
        column_config={
            "조건": st.column_config.TextColumn("조건", width="medium"),
            "결과": st.column_config.TextColumn("결과", width="medium"),
            "동시": st.column_config.NumberColumn("동시", format="%d", help="두 메뉴가 함께 나온 날짜 수"),
            "지지도": st.column_config.NumberColumn("지지도", format="%.2f%%", help="동시 등장 일수 ÷ 전체 급식 일수"),
            "신뢰도": st.column_config.NumberColumn("신뢰도", format="%.2f%%", help="동시 등장 일수 ÷ 조건 메뉴 등장 일수"),
            "향상도": st.column_config.NumberColumn("향상도", format="%.2f", help="신뢰도 ÷ 결과 메뉴 등장 비율"),
        },
    )
else:
    st.caption("표시할 규칙이 없습니다.")

st.download_button(
    "⬇️ 현재 규칙 CSV 다운로드",
    data=filtered.to_csv(index=False).encode("utf-8-sig"),
    file_name="급식_연관규칙.csv",
    mime="text/csv",
    disabled=filtered.empty,
)

st.markdown(
    """
    <div class="help-note">
        <b>📌 지표 읽는 법</b><br>
        <b>동시</b> = 두 메뉴가 함께 나온 날 수 &nbsp;·&nbsp;
        <b>지지도</b> = 전체 급식 중 두 메뉴가 함께 나온 비율 &nbsp;·&nbsp;
        <b>신뢰도</b> = 조건 메뉴가 나온 날 결과 메뉴도 나온 비율 &nbsp;·&nbsp;
        <b>향상도</b> = 두 메뉴가 무관하다고 가정할 때보다 얼마나 자주 함께 나왔는지<br>
        향상도 1 초과는 예상보다 함께 자주 나왔다는 뜻입니다. 단, 등장 횟수가 1~2회인 희귀 규칙은 과대평가될 수 있으니
        <b>동시 등장 횟수</b>도 함께 확인해 보세요. 연관성이 원인과 결과를 뜻하지는 않습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("🔎 날짜별로 원본 식단 확인하기"):
    picked = st.selectbox(
        "급식 날짜",
        options=period["날짜"].dt.date.tolist(),
        format_func=lambda day: day.strftime("%Y년 %m월 %d일"),
    )
    one_day = period.loc[period["날짜"].dt.date == picked].iloc[0]
    st.markdown("**분석에 실제로 사용한 메뉴**")
    st.write(" · ".join(one_day["메뉴목록"]))
    st.caption("괄호 속 부가 정보 제거 전 원본 메뉴: " + one_day["메뉴"])
