import html
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import pytz
import requests
import streamlit as st


# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="BoxOffice Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. DESIGN SYSTEM
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #F4F7FB;
        --surface: #FFFFFF;
        --surface-soft: #F8FAFC;
        --text: #0F172A;
        --text-sub: #64748B;
        --line: #E7ECF3;
        --blue: #3182F6;
        --blue-dark: #1B64DA;
        --red: #FF5A65;
        --green: #10B981;
        --gold: #F5B700;
        --shadow: 0 14px 40px rgba(15, 23, 42, 0.07);
    }

    /* ---------- App shell ---------- */
    .stApp {
        background:
            radial-gradient(circle at 10% -10%, rgba(49,130,246,.09), transparent 28%),
            radial-gradient(circle at 95% 3%, rgba(139,92,246,.06), transparent 24%),
            var(--bg);
    }

    [data-testid="stHeader"] {
        background: rgba(244,247,251,.72);
        backdrop-filter: blur(14px);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1280px;
        padding-top: 2.1rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: rgba(255,255,255,.94);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    html, body, [class*="css"] {
        font-family:
            Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI",
            "Noto Sans KR", sans-serif;
    }

    /* ---------- Sidebar ---------- */
    .sidebar-brand {
        padding: 0.25rem 0 1.3rem;
    }

    .sidebar-brand .logo {
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        color: var(--text);
    }

    .sidebar-brand .desc {
        color: var(--text-sub);
        font-size: .86rem;
        margin-top: .25rem;
        line-height: 1.55;
    }

    .sidebar-date {
        margin-top: .75rem;
        padding: 1rem 1.05rem;
        border: 1px solid #DFE8F5;
        background: linear-gradient(135deg, #F8FBFF 0%, #EEF5FF 100%);
        border-radius: 18px;
    }

    .sidebar-date .label {
        color: #7190B9;
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .06em;
        text-transform: uppercase;
    }

    .sidebar-date .value {
        color: #174EA6;
        font-size: 1.05rem;
        font-weight: 850;
        margin-top: .2rem;
    }

    /* ---------- Hero ---------- */
    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 28px;
        padding: 2.25rem 2.45rem;
        background:
            radial-gradient(circle at 82% 18%, rgba(91,157,255,.34), transparent 26%),
            radial-gradient(circle at 72% 115%, rgba(117,74,255,.32), transparent 32%),
            linear-gradient(135deg, #0B1220 0%, #111F3A 48%, #153F7B 100%);
        box-shadow: 0 28px 60px rgba(22,50,92,.22);
        margin-bottom: 1.4rem;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        right: -80px;
        top: -90px;
        border: 1px solid rgba(255,255,255,.12);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        right: 25px;
        top: -65px;
        border: 1px solid rgba(255,255,255,.08);
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: .45rem;
        padding: .45rem .75rem;
        border-radius: 999px;
        background: rgba(255,255,255,.10);
        border: 1px solid rgba(255,255,255,.12);
        color: #CFE2FF;
        font-size: .78rem;
        font-weight: 800;
        letter-spacing: .03em;
        backdrop-filter: blur(8px);
    }

    .hero-title {
        color: white;
        font-size: clamp(2.15rem, 4vw, 4rem);
        font-weight: 950;
        letter-spacing: -.065em;
        line-height: 1.02;
        margin: 1rem 0 .6rem;
        max-width: 850px;
    }

    .hero-sub {
        color: #BFD0EA;
        font-size: 1rem;
        line-height: 1.7;
        max-width: 760px;
    }

    .hero-date {
        display: inline-block;
        margin-top: 1.35rem;
        color: white;
        font-weight: 800;
        font-size: .9rem;
    }

    /* ---------- Section header ---------- */
    .section-head {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 1rem;
        margin: 2.15rem 0 1rem;
    }

    .section-eyebrow {
        color: var(--blue);
        font-size: .76rem;
        font-weight: 900;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .22rem;
    }

    .section-title {
        color: var(--text);
        font-size: 1.45rem;
        font-weight: 900;
        letter-spacing: -.035em;
        margin: 0;
    }

    .section-caption {
        color: var(--text-sub);
        font-size: .86rem;
        margin-top: .25rem;
    }

    /* ---------- KPI cards ---------- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .9rem;
        margin-top: .2rem;
    }

    .kpi-card {
        background: rgba(255,255,255,.92);
        border: 1px solid rgba(226,232,240,.9);
        border-radius: 20px;
        padding: 1.18rem 1.25rem;
        box-shadow: 0 10px 30px rgba(15,23,42,.045);
    }

    .kpi-label {
        color: var(--text-sub);
        font-size: .78rem;
        font-weight: 750;
        margin-bottom: .55rem;
    }

    .kpi-value {
        color: var(--text);
        font-size: 1.55rem;
        font-weight: 900;
        letter-spacing: -.04em;
    }

    .kpi-note {
        color: #94A3B8;
        font-size: .72rem;
        margin-top: .35rem;
    }

    /* ---------- Podium ---------- */
    .podium-card {
        height: 100%;
        border: 1px solid var(--line);
        background: rgba(255,255,255,.96);
        border-radius: 24px;
        padding: 1.25rem 1.25rem 1.15rem;
        box-shadow: var(--shadow);
        transition: transform .18s ease, box-shadow .18s ease;
    }

    .podium-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 45px rgba(15,23,42,.10);
    }

    .podium-card.first {
        background:
            radial-gradient(circle at 90% 0%, rgba(49,130,246,.13), transparent 35%),
            linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
        border-color: #CFE0FF;
    }

    .rank-chip {
        display: inline-flex;
        width: 38px;
        height: 38px;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 950;
        background: #EEF4FF;
        color: var(--blue);
        margin-bottom: .9rem;
    }

    .rank-chip.gold {
        background: #FFF7D6;
        color: #A56D00;
    }

    .podium-name {
        color: var(--text);
        font-size: 1.14rem;
        font-weight: 900;
        letter-spacing: -.035em;
        line-height: 1.35;
        min-height: 3.05rem;
    }

    .podium-meta {
        color: var(--text-sub);
        font-size: .76rem;
        margin-top: .38rem;
    }

    .podium-number {
        color: var(--text);
        font-size: 1.45rem;
        font-weight: 900;
        letter-spacing: -.04em;
        margin-top: 1rem;
    }

    .podium-label {
        color: #94A3B8;
        font-size: .73rem;
        margin-top: .12rem;
    }

    /* ---------- Chart containers ---------- */
    .chart-shell {
        background: rgba(255,255,255,.96);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: .75rem 1rem .35rem;
        box-shadow: var(--shadow);
    }

    /* ---------- Table ---------- */
    .table-wrap {
        width: 100%;
        overflow-x: auto;
        border-radius: 22px;
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
        background: white;
    }

    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background: #FFFFFF;
        min-width: 880px;
    }

    .custom-table th {
        background: #F8FAFC;
        color: #64748B;
        padding: 15px 14px;
        text-align: center;
        font-size: .76rem;
        font-weight: 850;
        letter-spacing: .015em;
        border-bottom: 1px solid var(--line);
        white-space: nowrap;
    }

    .custom-table td {
        padding: 15px 14px;
        text-align: center;
        border-bottom: 1px solid #EFF3F8;
        color: #1E293B;
        font-size: .87rem;
        white-space: nowrap;
    }

    .custom-table tbody tr:last-child td {
        border-bottom: none;
    }

    .custom-table tbody tr {
        transition: background .14s ease;
    }

    .custom-table tbody tr:hover td {
        background: #F8FBFF;
    }

    .movie-cell {
        text-align: left !important;
        min-width: 230px;
    }

    .movie-name {
        font-weight: 800;
        color: #172033;
    }

    .million-badge {
        display: inline-block;
        margin-left: .38rem;
        padding: .15rem .4rem;
        border-radius: 999px;
        background: #FFF4CC;
        color: #8B6500;
        font-size: .66rem;
        font-weight: 850;
        vertical-align: 1px;
    }

    .rank-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 31px;
        height: 31px;
        border-radius: 10px;
        background: #F1F5F9;
        color: #475569;
        font-weight: 900;
    }

    .rank-number.top {
        background: #EAF2FF;
        color: #1F6FEB;
    }

    .trend-up, .trend-down, .trend-new, .trend-flat {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 46px;
        padding: .28rem .47rem;
        border-radius: 999px;
        font-size: .7rem;
        font-weight: 850;
    }

    .trend-up   { color: #E5484D; background: #FFF0F0; }
    .trend-down { color: #2574D9; background: #EDF5FF; }
    .trend-new  { color: #7C3AED; background: #F4EEFF; }
    .trend-flat { color: #94A3B8; background: #F1F5F9; }

    /* ---------- Footer note ---------- */
    .soft-note {
        margin-top: 1rem;
        padding: .9rem 1rem;
        border-radius: 16px;
        background: #EEF5FF;
        color: #4A6A95;
        font-size: .8rem;
        line-height: 1.65;
        border: 1px solid #DCEAFF;
    }

    /* ---------- Native widgets ---------- */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] input {
        border-radius: 13px !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    /* ---------- Responsive ---------- */
    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            padding: 1.7rem 1.45rem;
            border-radius: 23px;
        }

        .kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 620px) {
        .hero-title {
            font-size: 2.15rem;
        }

        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. DATA
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_boxoffice_data(target_date: str, api_key: str):
    """KOBIS 일별 박스오피스 TOP 10 조회."""
    url = (
        "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
        "boxoffice/searchDailyBoxOfficeList.json"
    )

    try:
        response = requests.get(
            url,
            params={"key": api_key, "targetDt": target_date},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 API 오류")
            return None, f"KOBIS API 오류: {message}"

        movie_list = (
            data.get("boxOfficeResult", {})
            .get("dailyBoxOfficeList", [])
        )

        if not movie_list:
            return None, "empty"

        return pd.DataFrame(movie_list), None

    except requests.RequestException:
        return None, "영화진흥위원회 서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요."
    except ValueError:
        return None, "서버 응답을 읽는 중 문제가 발생했어요."
    except Exception as exc:
        return None, f"예상하지 못한 오류가 발생했어요: {exc}"


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    numeric_cols = [
        "rank",
        "rankInten",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "salesAmt",
        "salesAcc",
    ]

    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0)

    result["isMillion"] = result["audiAcc"] >= 1_000_000
    result["movieNmDisplay"] = result["movieNm"].astype(str)
    return result


# =========================================================
# 4. FORMATTERS
# =========================================================
def won_short(value: float) -> str:
    value = float(value)
    if value >= 100_000_000:
        return f"{value / 100_000_000:.1f}억"
    if value >= 10_000:
        return f"{value / 10_000:.0f}만"
    return f"{value:,.0f}"


def person_short(value: float) -> str:
    value = float(value)
    if value >= 10_000:
        return f"{value / 10_000:.1f}만"
    return f"{value:,.0f}"


def trend_badge(rank_inten, old_new) -> str:
    if str(old_new).upper() == "NEW":
        return "<span class='trend-new'>NEW</span>"

    try:
        n = int(rank_inten)
    except (TypeError, ValueError):
        n = 0

    if n > 0:
        return f"<span class='trend-up'>▲ {n}</span>"
    if n < 0:
        return f"<span class='trend-down'>▼ {abs(n)}</span>"
    return "<span class='trend-flat'>—</span>"


def rank_badge(rank: int) -> str:
    cls = "rank-number top" if int(rank) <= 3 else "rank-number"
    return f"<span class='{cls}'>{int(rank)}</span>"


def section_header(eyebrow: str, title: str, caption: str = ""):
    st.markdown(
        f"""
        <div class="section-head">
            <div>
                <div class="section-eyebrow">{html.escape(eyebrow)}</div>
                <div class="section-title">{html.escape(title)}</div>
                <div class="section-caption">{html.escape(caption)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_podium_card(row: pd.Series, rank: int):
    name = html.escape(str(row["movieNmDisplay"]))
    open_dt = html.escape(str(row.get("openDt", "-")))
    audience = int(row["audiCnt"])
    accumulated = int(row["audiAcc"])
    is_million = bool(row["isMillion"])

    first_cls = " first" if rank == 1 else ""
    chip_cls = "rank-chip gold" if rank == 1 else "rank-chip"
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
    trophy = " · 100만+ 흥행작" if is_million else ""

    st.markdown(
        f"""
        <div class="podium-card{first_cls}">
            <div class="{chip_cls}">{medal}</div>
            <div class="podium-name">{name}</div>
            <div class="podium-meta">개봉 {open_dt}{trophy}</div>
            <div class="podium-number">{audience:,}<span style="font-size:.78rem;font-weight:750;color:#94A3B8;"> 명</span></div>
            <div class="podium-label">선택 날짜 일일 관객수</div>
            <div style="height:.6rem"></div>
            <div style="color:#64748B;font-size:.78rem;">누적 <b style="color:#334155;">{accumulated:,}명</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 5. CHARTS
# =========================================================
def make_audience_chart(df: pd.DataFrame):
    chart_df = df.head(5).copy()
    chart_df["label"] = chart_df["movieNmDisplay"].str.slice(0, 18)
    chart_df = chart_df.iloc[::-1]

    colors = [
        "#A9C8FF" if int(rank) != 1 else "#3182F6"
        for rank in chart_df["rank"]
    ]

    fig = go.Figure(
        go.Bar(
            x=chart_df["audiCnt"],
            y=chart_df["label"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"{int(v):,}명" for v in chart_df["audiCnt"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x:,.0f}명<extra></extra>",
        )
    )

    fig.update_layout(
        height=390,
        margin=dict(l=8, r=72, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor="#EEF2F7",
            zeroline=False,
            showticklabels=False,
            title=None,
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=12, color="#334155"),
            automargin=True,
        ),
        font=dict(
            family='Pretendard, "Noto Sans KR", sans-serif',
            color="#334155",
        ),
        bargap=0.36,
    )
    return fig


def make_share_chart(df: pd.DataFrame):
    chart_df = df.head(5).copy()
    other = max(int(df["audiCnt"].sum() - chart_df["audiCnt"].sum()), 0)

    labels = chart_df["movieNmDisplay"].tolist()
    values = chart_df["audiCnt"].astype(int).tolist()

    if other > 0:
        labels.append("6~10위")
        values.append(other)

    colors = [
        "#3182F6",
        "#6EA8FF",
        "#9BC2FF",
        "#BDD6FF",
        "#D8E7FF",
        "#E9EEF5",
    ][: len(labels)]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.68,
            sort=False,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=3)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:,.0f}명 · %{percent}<extra></extra>",
        )
    )

    top1_share = values[0] / sum(values) * 100 if sum(values) else 0

    fig.add_annotation(
        x=0.5,
        y=0.53,
        text=f"<b>{top1_share:.1f}%</b>",
        showarrow=False,
        font=dict(size=27, color="#0F172A"),
    )
    fig.add_annotation(
        x=0.5,
        y=0.40,
        text="1위 점유율",
        showarrow=False,
        font=dict(size=11, color="#94A3B8"),
    )

    fig.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=20, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.02,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#64748B"),
        ),
        font=dict(family='Pretendard, "Noto Sans KR", sans-serif'),
    )
    return fig


# =========================================================
# 6. TABLE
# =========================================================
def make_rank_table(df: pd.DataFrame) -> str:
    rows = []

    for _, row in df.iterrows():
        movie_name = html.escape(str(row["movieNmDisplay"]))
        million = (
            "<span class='million-badge'>🏆 100만+</span>"
            if bool(row["isMillion"])
            else ""
        )

        rows.append(
            f"""
            <tr>
                <td>{rank_badge(row["rank"])}</td>
                <td>{trend_badge(row.get("rankInten", 0), row.get("rankOldAndNew", ""))}</td>
                <td class="movie-cell">
                    <span class="movie-name">{movie_name}</span>{million}
                </td>
                <td>{html.escape(str(row.get("openDt", "-")))}</td>
                <td><b>{int(row["audiCnt"]):,}</b></td>
                <td>{int(row["audiAcc"]):,}</td>
                <td>{int(row["scrnCnt"]):,}</td>
            </tr>
            """
        )

    return f"""
    <div class="table-wrap">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>순위</th>
                    <th>변동</th>
                    <th style="text-align:left;">영화명</th>
                    <th>개봉일</th>
                    <th>일일 관객</th>
                    <th>누적 관객</th>
                    <th>스크린</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """


# =========================================================
# 7. MAIN APP
# =========================================================
def main():
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    yesterday = (now_kst - timedelta(days=1)).date()

    # ---------- Sidebar ----------
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="logo">🎬 BoxOffice Pro</div>
                <div class="desc">
                    KOBIS 데이터를 기반으로<br>
                    한국 일별 박스오피스를 빠르게 확인합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_date = st.date_input(
            "조회 날짜",
            value=yesterday,
            max_value=yesterday,
            format="YYYY/MM/DD",
            help="당일 데이터는 아직 집계 중일 수 있어 전날까지만 조회합니다.",
        )

        st.markdown(
            f"""
            <div class="sidebar-date">
                <div class="label">Selected date</div>
                <div class="value">{selected_date.strftime("%Y년 %m월 %d일")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
        st.caption("데이터 출처 · 영화진흥위원회 KOBIS")
        st.caption("캐시 · 1시간")

    # ---------- Secret check ----------
    if "KOBIS_KEY" not in st.secrets:
        st.error(
            "`.streamlit/secrets.toml`에 `KOBIS_KEY`가 없습니다. "
            "Streamlit Cloud의 Secrets 설정도 확인해 주세요."
        )
        return

    api_key = st.secrets["KOBIS_KEY"]
    target_dt = selected_date.strftime("%Y%m%d")

    # ---------- Load ----------
    with st.spinner("박스오피스 데이터를 불러오는 중..."):
        df, error = get_boxoffice_data(target_dt, api_key)

    if error == "empty":
        st.warning(
            f"{selected_date.strftime('%Y년 %m월 %d일')} 데이터가 아직 없어요. "
            "다른 날짜를 선택해 주세요."
        )
        return

    if error:
        st.error(error)
        return

    df = preprocess(df)

    top1 = df.iloc[0]
    top1_name = html.escape(str(top1["movieNmDisplay"]))
    total_audience = int(df["audiCnt"].sum())
    top1_share = (int(top1["audiCnt"]) / total_audience * 100) if total_audience else 0
    new_count = int((df.get("rankOldAndNew", pd.Series(dtype=str)).astype(str).str.upper() == "NEW").sum())
    screen_sum = int(df["scrnCnt"].sum())

    # ---------- Hero ----------
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">● KOREA DAILY BOX OFFICE</div>
            <div class="hero-title">
                오늘 극장의 중심은<br>{top1_name}
            </div>
            <div class="hero-sub">
                박스오피스 순위부터 관객 흐름, 스크린 점유까지.
                복잡한 숫자를 한 화면에서 가볍게 읽어보세요.
            </div>
            <div class="hero-date">
                {selected_date.strftime("%Y.%m.%d")} · Daily Top 10
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- KPI ----------
    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">TOP 10 일일 관객</div>
                <div class="kpi-value">{person_short(total_audience)}명</div>
                <div class="kpi-note">상위 10편 관객수 합계</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">1위 관객 점유율</div>
                <div class="kpi-value">{top1_share:.1f}%</div>
                <div class="kpi-note">{html.escape(str(top1["movieNmDisplay"]))}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">신규 진입작</div>
                <div class="kpi-value">{new_count}편</div>
                <div class="kpi-note">TOP 10 기준 NEW 표시</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">TOP 10 스크린 합계</div>
                <div class="kpi-value">{screen_sum:,}개</div>
                <div class="kpi-note">영화별 스크린 수 단순 합계</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Podium ----------
    section_header(
        "TOP MOVIES",
        "오늘 가장 많이 본 영화",
        "상위 3편을 한눈에 비교해 보세요.",
    )

    c1, c2, c3 = st.columns([1.12, 1, 1], gap="medium")
    with c1:
        render_podium_card(df.iloc[0], 1)
    with c2:
        if len(df) > 1:
            render_podium_card(df.iloc[1], 2)
    with c3:
        if len(df) > 2:
            render_podium_card(df.iloc[2], 3)

    # ---------- Charts ----------
    section_header(
        "AUDIENCE INSIGHT",
        "관객 흐름 한눈에 보기",
        "막대그래프는 규모, 도넛차트는 상위권 집중도를 보여줍니다.",
    )

    chart_left, chart_right = st.columns([1.55, 1], gap="medium")

    with chart_left:
        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-weight:900;color:#0F172A;padding:.55rem .2rem 0;'>TOP 5 일일 관객수</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            make_audience_chart(df),
            width="stretch",
            config={"displayModeBar": False},
            key="audience_bar",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_right:
        st.markdown('<div class="chart-shell">', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-weight:900;color:#0F172A;padding:.55rem .2rem 0;'>TOP 10 관객 비중</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            make_share_chart(df),
            width="stretch",
            config={"displayModeBar": False},
            key="share_donut",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- Top1 details ----------
    section_header(
        "NO.1 SNAPSHOT",
        f"1위 영화 상세 지표 · {top1['movieNmDisplay']}",
        "오늘 성적과 누적 흥행 규모를 빠르게 확인합니다.",
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            "일일 관객",
            f"{int(top1['audiCnt']):,}명",
            border=True,
            icon=":material/groups:",
        )
    with m2:
        st.metric(
            "누적 관객",
            f"{int(top1['audiAcc']):,}명",
            border=True,
            icon=":material/monitoring:",
        )
    with m3:
        st.metric(
            "스크린 수",
            f"{int(top1['scrnCnt']):,}개",
            border=True,
            icon=":material/theaters:",
        )
    with m4:
        sales = int(top1.get("salesAmt", 0))
        st.metric(
            "일일 매출",
            f"{won_short(sales)}원",
            border=True,
            icon=":material/payments:",
        )

    # ---------- Ranking table ----------
    section_header(
        "FULL RANKING",
        "전체 박스오피스 순위",
        "순위 변동, 개봉일, 일일·누적 관객, 스크린 수를 함께 볼 수 있습니다.",
    )

    st.markdown(make_rank_table(df), unsafe_allow_html=True)

    st.markdown(
        """
        <div class="soft-note">
            🏆 <b>100만+</b> 배지는 누적 관객 100만 명 이상인 작품을 뜻합니다.
            순위 변동은 전일 대비이며, <b>NEW</b>는 TOP 10 신규 진입작입니다.
            KOBIS 일별 박스오피스 API가 제공하는 상위 목록을 기준으로 표시합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
