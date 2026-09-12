import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# 0. 기본 설정
# ============================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)

REQUIRED_COLUMNS = [
    "movieCd",
    "movieNm",
    "openDt",
    "genre",
    "nation",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10",
]


# ============================================================
# 1. 데이터 불러오기 / 전처리
# ============================================================
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # BOM 및 열 이름 공백 제거
    df.columns = (
        df.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    # 필요한 열 확인
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "CSV에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    # 개봉일: 20260805 -> datetime
    df["openDt"] = pd.to_datetime(
        df["openDt"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True),
        format="%Y%m%d",
        errors="coerce",
    )

    # genre가 "액션|스릴러"처럼 | 로 여러 개 적힌 경우
    # 첫 번째 장르만 사용
    def get_first_genre(value):
        if pd.isna(value):
            return "정보 없음"

        text = str(value).strip()

        if text == "":
            return "정보 없음"

        return text.split("|")[0].strip() or "정보 없음"

    df["genre_main"] = df["genre"].apply(get_first_genre)

    # 제작 국가 정리
    df["nation_clean"] = (
        df["nation"]
        .fillna("정보 없음")
        .astype(str)
        .str.strip()
        .replace("", "정보 없음")
    )

    # 영화명 정리
    df["movieNm"] = (
        df["movieNm"]
        .fillna("제목 없음")
        .astype(str)
        .str.strip()
    )

    # 숫자 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce",
        )

    return df


# ============================================================
# 2. 공통 함수
# ============================================================
def show_insight(text):
    st.info(
        "💡 이 그래프로 알 수 있는 것: "
        + text
    )


def format_people(value):
    if pd.isna(value):
        return "알 수 없음"
    return f"{int(round(value)):,}명"


def make_histogram_insight(df, bins=20):
    """
    총 관객이 가장 많이 몰린 구간과
    총 관객 1위 영화를 자동으로 계산합니다.
    """
    valid = (
        df[["movieNm", "total_audi"]]
        .dropna(subset=["total_audi"])
        .query("total_audi >= 0")
        .copy()
    )

    if valid.empty:
        return (
            "총 관객 데이터가 없어 "
            "분포를 계산할 수 없습니다."
        )

    # 총 관객 1위 영화
    top_row = valid.loc[
        valid["total_audi"].idxmax()
    ]

    top_movie = top_row["movieNm"]
    top_audience = top_row["total_audi"]

    # pandas.cut으로 20개 구간 생성
    # 중복 경계가 생기는 특수 상황도 안전하게 처리
    try:
        groups = pd.cut(
            valid["total_audi"],
            bins=bins,
            include_lowest=True,
            duplicates="drop",
        )

        counts = groups.value_counts(
            sort=False
        )

        busiest_interval = counts.idxmax()

        lower = max(
            0,
            int(round(busiest_interval.left)),
        )
        upper = max(
            lower,
            int(round(busiest_interval.right)),
        )

        range_text = (
            f"약 {lower:,}명~{upper:,}명"
        )

    except Exception:
        range_text = (
            "관객 수가 비교적 낮은 구간"
        )

    return (
        f"가장 많은 영화가 {range_text}에 몰려 있으며, "
        f"총 관객이 가장 많은 영화는 "
        f"「{top_movie}」"
        f"({format_people(top_audience)})입니다."
    )


# ============================================================
# 그래프 1
# 장르별 영화 편수 - 도넛 그래프
# ============================================================
def render_graph_1(df):
    st.subheader(
        "1. 장르별 영화 편수"
    )

    genre_counts = (
        df["genre_main"]
        .value_counts()
        .rename_axis("장르")
        .reset_index(name="영화 편수")
    )

    fig = px.pie(
        genre_counts,
        names="장르",
        values="영화 편수",
        hole=0.5,
        title="장르별 영화 편수 분포",
    )

    fig.update_traces(
        textinfo="label+percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value:,}편<br>"
            "비율: %{percent}"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        legend_title_text="장르",
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    show_insight(
        "장르별 영화 편수를 비교해 "
        "어떤 장르의 영화가 이 기간 박스오피스 TOP 10에 "
        "더 많이 등장했는지 확인할 수 있습니다."
    )


# ============================================================
# 그래프 2
# 장르 > 영화 - 트리맵
# 칸 크기: total_audi
# ============================================================
def render_graph_2(df):
    st.subheader(
        "2. 장르 안의 영화별 총 관객"
    )

    tree_df = (
        df[
            [
                "genre_main",
                "movieNm",
                "total_audi",
            ]
        ]
        .dropna(subset=["total_audi"])
        .query("total_audi > 0")
        .copy()
    )

    if tree_df.empty:
        st.warning(
            "트리맵을 그릴 수 있는 "
            "총 관객 데이터가 없습니다."
        )
        return

    fig = px.treemap(
        tree_df,
        path=[
            "genre_main",
            "movieNm",
        ],
        values="total_audi",
        title="장르 → 영화 트리맵",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,.0f}명"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=70,
            b=10,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    show_insight(
        "장르 안에서 어떤 영화가 큰 관객 규모를 차지했는지 "
        "칸의 크기를 통해 비교할 수 있습니다."
    )


# ============================================================
# 그래프 3
# total_audi 히스토그램
# ============================================================
def render_graph_3(df):
    st.subheader(
        "3. 영화별 총 관객 분포"
    )

    hist_df = (
        df[
            [
                "movieNm",
                "total_audi",
            ]
        ]
        .dropna(subset=["total_audi"])
        .query("total_audi >= 0")
        .copy()
    )

    if hist_df.empty:
        st.warning(
            "히스토그램을 그릴 수 있는 "
            "총 관객 데이터가 없습니다."
        )
        return

    fig = px.histogram(
        hist_df,
        x="total_audi",
        nbins=20,
        title="총 관객 히스토그램",
        labels={
            "total_audi": "총 관객",
            "count": "영화 편수",
        },
    )

    fig.update_layout(
        xaxis_title="총 관객",
        yaxis_title="영화 편수",
        bargap=0.04,
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    fig.update_xaxes(
        tickformat=",",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    # 요구사항:
    # - 대부분의 영화가 어느 구간에 몰리는지
    # - 가장 관객이 많은 영화 이름
    show_insight(
        make_histogram_insight(
            df,
            bins=20,
        )
    )


# ============================================================
# 그래프 4
# first_scrn vs total_audi 산점도
# 색: 장르
# ============================================================
def render_graph_4(df):
    st.subheader(
        "4. 개봉일 스크린수와 총 관객의 관계"
    )

    scatter_df = (
        df[
            [
                "movieNm",
                "genre_main",
                "first_scrn",
                "total_audi",
            ]
        ]
        .dropna(
            subset=[
                "first_scrn",
                "total_audi",
            ]
        )
        .copy()
    )

    if scatter_df.empty:
        st.warning(
            "산점도를 그릴 수 있는 "
            "데이터가 없습니다."
        )
        return

    fig = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre_main",
        hover_name="movieNm",
        hover_data={
            "genre_main": True,
            "first_scrn": ":,.0f",
            "total_audi": ":,.0f",
        },
        title="개봉일 스크린수와 총 관객",
        labels={
            "first_scrn": "개봉일 스크린수",
            "total_audi": "총 관객",
            "genre_main": "장르",
        },
    )

    fig.update_traces(
        marker=dict(
            size=9,
            opacity=0.78,
        ),
    )

    fig.update_layout(
        xaxis_title="개봉일 스크린수",
        yaxis_title="총 관객",
        legend_title_text="장르",
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    fig.update_yaxes(
        tickformat=",",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    show_insight(
        "개봉일 스크린수가 많은 영화가 "
        "최종적으로도 많은 관객을 모으는 경향이 있는지와 "
        "그 관계가 장르별로 어떻게 다른지 확인할 수 있습니다."
    )


# ============================================================
# 그래프 5
# 영화가 10편 이상인 장르만
# 장르별 total_audi 박스플롯
# ============================================================
def render_graph_5(df):
    st.subheader(
        "5. 장르별 총 관객 분포"
    )

    # 장르별 전체 영화 수를 먼저 계산
    genre_movie_counts = (
        df["genre_main"]
        .value_counts()
    )

    eligible_genres = (
        genre_movie_counts[
            genre_movie_counts >= 10
        ]
        .index
        .tolist()
    )

    if not eligible_genres:
        st.warning(
            "영화가 10편 이상인 장르가 없습니다."
        )
        return

    box_df = (
        df[
            df["genre_main"].isin(
                eligible_genres
            )
        ][
            [
                "movieNm",
                "genre_main",
                "total_audi",
            ]
        ]
        .dropna(subset=["total_audi"])
        .copy()
    )

    if box_df.empty:
        st.warning(
            "박스플롯을 그릴 수 있는 "
            "총 관객 데이터가 없습니다."
        )
        return

    # 중앙값이 큰 장르부터 보기 좋게 정렬
    genre_order = (
        box_df
        .groupby("genre_main")[
            "total_audi"
        ]
        .median()
        .sort_values(
            ascending=False
        )
        .index
        .tolist()
    )

    fig = px.box(
        box_df,
        x="genre_main",
        y="total_audi",
        color="genre_main",
        points="outliers",
        hover_name="movieNm",
        hover_data={
            "genre_main": True,
            "total_audi": ":,.0f",
        },
        category_orders={
            "genre_main": genre_order
        },
        title=(
            "영화가 10편 이상인 장르의 "
            "총 관객 박스플롯"
        ),
        labels={
            "genre_main": "장르",
            "total_audi": "총 관객",
        },
    )

    fig.update_layout(
        xaxis_title="장르",
        yaxis_title="총 관객",
        showlegend=False,
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    fig.update_yaxes(
        tickformat=",",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    show_insight(
        "영화가 10편 이상인 장르들의 "
        "총 관객 중앙값과 분포 범위를 비교하고, "
        "유난히 관객이 많은 이상치 영화도 확인할 수 있습니다."
    )


# ============================================================
# 그래프 6
# 그래프 4의 버블 그래프 버전
# 크기: first_week_audi
# ============================================================
def render_graph_6(df):
    st.subheader(
        "6. 개봉일 스크린수·총 관객·첫 주 관객의 관계"
    )

    bubble_df = (
        df[
            [
                "movieNm",
                "genre_main",
                "first_scrn",
                "first_week_audi",
                "total_audi",
            ]
        ]
        .dropna(
            subset=[
                "first_scrn",
                "first_week_audi",
                "total_audi",
            ]
        )
        .query("first_week_audi >= 0")
        .copy()
    )

    if bubble_df.empty:
        st.warning(
            "버블 그래프를 그릴 수 있는 "
            "데이터가 없습니다."
        )
        return

    fig = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre_main",
        hover_name="movieNm",
        hover_data={
            "genre_main": True,
            "first_scrn": ":,.0f",
            "first_week_audi": ":,.0f",
            "total_audi": ":,.0f",
        },
        size_max=55,
        title=(
            "개봉일 스크린수와 총 관객 "
            "(버블 크기 = 첫 주 관객)"
        ),
        labels={
            "first_scrn": "개봉일 스크린수",
            "first_week_audi": "첫 주 관객",
            "total_audi": "총 관객",
            "genre_main": "장르",
        },
    )

    fig.update_layout(
        xaxis_title="개봉일 스크린수",
        yaxis_title="총 관객",
        legend_title_text="장르",
        margin=dict(
            l=20,
            r=20,
            t=70,
            b=20,
        ),
    )

    fig.update_yaxes(
        tickformat=",",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    show_insight(
        "스크린수와 총 관객의 관계에 "
        "첫 주 관객 규모까지 함께 비교해 "
        "초기 흥행이 큰 영화가 최종 흥행으로 이어졌는지 살펴볼 수 있습니다."
    )


# ============================================================
# 그래프 7
# nation -> genre 선버스트
# 크기: 영화 편수
# ============================================================
def render_graph_7(df):
    st.subheader(
        "7. 제작 국가와 장르의 구성"
    )

    sunburst_df = (
        df
        .groupby(
            [
                "nation_clean",
                "genre_main",
            ],
            as_index=False,
        )
        .size()
        .rename(
            columns={
                "nation_clean": "제작 국가",
                "genre_main": "장르",
                "size": "영화 편수",
            }
        )
    )

    if sunburst_df.empty:
        st.warning(
            "선버스트 그래프를 그릴 수 있는 "
            "데이터가 없습니다."
        )
        return

    fig = px.sunburst(
        sunburst_df,
        path=[
            "제작 국가",
            "장르",
        ],
        values="영화 편수",
        title="제작 국가 → 장르 선버스트",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 편수: %{value:,}편"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        margin=dict(
            l=10,
            r=10,
            t=70,
            b=10,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displaylogo": False},
    )

    show_insight(
        "어느 제작 국가의 영화가 많이 포함되었고 "
        "각 국가 안에서 어떤 장르가 많이 나타났는지 "
        "계층적으로 확인할 수 있습니다."
    )


# ============================================================
# 3. 앱 본문
# ============================================================
st.title(
    "🎬 영화 데이터 그래프 도감 2 - 분포와 관계"
)

st.caption(
    "1년간 박스오피스 TOP 10에 진입한 영화 가운데 "
    "이 기간에 개봉한 영화들의 분포와 변수 사이의 관계를 살펴봅니다."
)

try:
    data = load_data()

except Exception as e:
    st.error(
        "데이터를 불러오지 못했습니다. "
        "인터넷 연결 또는 CSV 주소를 확인해 주세요."
    )
    st.exception(e)
    st.stop()


# ------------------------------------------------------------
# 그래프 구역 1
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_1(data)

st.divider()


# ------------------------------------------------------------
# 그래프 구역 2
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_2(data)

st.divider()


# ------------------------------------------------------------
# 그래프 구역 3
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_3(data)

st.divider()


# ------------------------------------------------------------
# 그래프 구역 4
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_4(data)

st.divider()


# ------------------------------------------------------------
# 그래프 구역 5
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_5(data)

st.divider()


# ------------------------------------------------------------
# 그래프 구역 6
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_6(data)

st.divider()


# ------------------------------------------------------------
# 그래프 구역 7
# ------------------------------------------------------------
with st.container(border=True):
    render_graph_7(data)
