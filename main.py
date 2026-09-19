import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
APP_TITLE = "영화 유형 나누기"
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 유형 나누기")
st.caption(
    "영화의 규모와 흥행 지속성을 나타내는 속성을 골라 "
    "K-평균으로 영화 유형을 나눠 봅니다."
)


# ------------------------------------------------------------
# 데이터 불러오기 및 속성 만들기
# ------------------------------------------------------------
@st.cache_data
def load_and_prepare():
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    required_cols = [
        "movieCd",
        "movieNm",
        "openDt",
        "genre",
        "nation",
        "first_scrn",
        "first_show",
        "first_date",
        "peak",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"필요한 열이 없습니다: {', '.join(missing)}")

    total_count = len(df)

    for col in [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
        "peak",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 기본 네 속성 계산에 필요한 값이 없는 영화 제외
    valid = df[
        df["first_scrn"].notna()
        & df["total_audi"].notna()
        & df["days_in_top10"].notna()
        & df["first_week_audi"].notna()
        & (df["first_week_audi"] != 0)
        & (df["first_scrn"] > 0)
        & (df["total_audi"] > 0)
    ].copy()

    valid["log_first_scrn"] = valid["first_scrn"].map(math.log10)
    valid["log_total_audi"] = valid["total_audi"].map(math.log10)

    valid["longrun_index"] = (
        valid["total_audi"] / valid["first_week_audi"]
    ).clip(upper=20)

    # 5차원 시각화용 추가 속성
    valid["log_first_show"] = valid["first_show"].apply(
        lambda x: math.log10(x) if pd.notna(x) and x > 0 else float("nan")
    )

    valid["log_first_week_audi"] = valid["first_week_audi"].apply(
        lambda x: math.log10(x) if pd.notna(x) and x > 0 else float("nan")
    )

    grouped_count = len(valid)

    return valid, total_count, grouped_count


try:
    df, total_count, grouped_count = load_and_prepare()
except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다.\n\n{e}")
    st.stop()


# ------------------------------------------------------------
# 속성 정의
# ------------------------------------------------------------
FEATURES = {
    "log_first_scrn": "스크린 수(상용로그)",
    "log_total_audi": "누적 관객(상용로그)",
    "days_in_top10": "10위권 일수",
    "longrun_index": "롱런 지수",
}

FIFTH_FEATURES = {
    "log_first_show": "첫 관측일 상영횟수(상용로그)",
    "log_first_week_audi": "첫 주 관객 수(상용로그)",
    "peak": "성수기 개봉 여부",
}

CLUSTER_SYMBOLS = ["㉮", "㉯", "㉰", "㉱", "㉲", "㉳", "㉴"]

st.write(
    f"전체 영화 **{total_count:,}편** 중 조건을 만족해 유형을 묶은 영화는 "
    f"**{grouped_count:,}편**입니다."
)


# ------------------------------------------------------------
# 군집화 설정
# ------------------------------------------------------------
st.subheader("군집화 설정")

setting_col1, setting_col2 = st.columns([2, 1])

with setting_col1:
    selected_features = st.multiselect(
        "묶는 데 사용할 속성",
        options=list(FEATURES.keys()),
        default=list(FEATURES.keys()),
        format_func=lambda x: FEATURES[x],
        help="두 개 이상의 속성을 선택해 주세요.",
    )

with setting_col2:
    cluster_count = st.slider(
        "묶음 수",
        min_value=2,
        max_value=7,
        value=3,
        step=1,
    )

if len(selected_features) < 2:
    st.warning("K-평균 군집화를 하려면 속성을 두 개 이상 선택해야 합니다.")
    st.stop()

if len(df) < cluster_count:
    st.warning("영화 수보다 묶음 수가 많습니다.")
    st.stop()


# ------------------------------------------------------------
# 선택 속성 표준화 + KMeans
# ------------------------------------------------------------
X = df[selected_features].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(
    n_clusters=cluster_count,
    random_state=42,
    n_init=10,
)

df["cluster_raw"] = kmeans.fit_predict(X_scaled)


# ------------------------------------------------------------
# 누적 관객 평균이 큰 묶음부터 ㉮, ㉯, ...
# ------------------------------------------------------------
cluster_order = (
    df.groupby("cluster_raw")["total_audi"]
    .mean()
    .sort_values(ascending=False)
    .index
    .tolist()
)

cluster_label_map = {
    raw_cluster: CLUSTER_SYMBOLS[i]
    for i, raw_cluster in enumerate(cluster_order)
}

df["묶음"] = df["cluster_raw"].map(cluster_label_map)
ACTIVE_CLUSTER_SYMBOLS = CLUSTER_SYMBOLS[:cluster_count]

st.write(
    f"현재 **{len(selected_features)}개 속성**을 사용해 "
    f"영화를 **{cluster_count}개 묶음**으로 나눴습니다."
)


# ------------------------------------------------------------
# 2차원 산점도
# ------------------------------------------------------------
st.subheader("2차원 산점도")

axis_col1, axis_col2 = st.columns(2)

with axis_col1:
    x_feature = st.selectbox(
        "가로축",
        options=selected_features,
        index=0,
        format_func=lambda x: FEATURES[x],
        key="x_2d",
    )

with axis_col2:
    y_options = [f for f in selected_features if f != x_feature]
    y_feature = st.selectbox(
        "세로축",
        options=y_options,
        index=0,
        format_func=lambda x: FEATURES[x],
        key="y_2d",
    )

fig2d = px.scatter(
    df,
    x=x_feature,
    y=y_feature,
    color="묶음",
    category_orders={"묶음": ACTIVE_CLUSTER_SYMBOLS},
    hover_name="movieNm",
    hover_data={
        "묶음": True,
        "movieCd": True,
        "total_audi": ":,.0f",
    },
    labels={
        x_feature: FEATURES[x_feature],
        y_feature: FEATURES[y_feature],
        "묶음": "묶음",
        "movieCd": "영화코드",
        "total_audi": "누적 관객",
    },
)

fig2d.update_traces(marker=dict(size=7))
fig2d.update_layout(
    legend_title_text="묶음",
    margin=dict(l=20, r=20, t=20, b=20),
)

st.plotly_chart(fig2d, use_container_width=True)


# ------------------------------------------------------------
# 3차원 산점도
# ------------------------------------------------------------
st.subheader("3차원 산점도")

if len(selected_features) < 3:
    st.info("3차원 산점도를 보려면 속성을 세 개 이상 선택해 주세요.")
else:
    c1, c2, c3 = st.columns(3)

    with c1:
        x3 = st.selectbox(
            "3D x축",
            selected_features,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="x_3d",
        )

    y3_options = [f for f in selected_features if f != x3]

    with c2:
        y3 = st.selectbox(
            "3D y축",
            y3_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="y_3d",
        )

    z3_options = [f for f in selected_features if f not in {x3, y3}]

    with c3:
        z3 = st.selectbox(
            "3D z축",
            z3_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="z_3d",
        )

    fig3d = px.scatter_3d(
        df,
        x=x3,
        y=y3,
        z=z3,
        color="묶음",
        category_orders={"묶음": ACTIVE_CLUSTER_SYMBOLS},
        hover_name="movieNm",
        hover_data={
            "묶음": True,
            "total_audi": ":,.0f",
        },
        labels={
            x3: FEATURES[x3],
            y3: FEATURES[y3],
            z3: FEATURES[z3],
            "묶음": "묶음",
        },
    )

    fig3d.update_traces(marker=dict(size=3))
    fig3d.update_layout(height=650)

    st.plotly_chart(fig3d, use_container_width=True)


# ------------------------------------------------------------
# 4차원 산점도
# ------------------------------------------------------------
st.subheader("4차원 산점도")
st.caption("x·y·z 세 축에 더해 네 번째 속성을 점 크기로 표현합니다.")

if len(selected_features) < 4:
    st.info("4차원 산점도를 보려면 네 속성을 모두 선택해 주세요.")
else:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        x4 = st.selectbox(
            "4D x축",
            selected_features,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="x_4d",
        )

    with c2:
        y4_options = [f for f in selected_features if f != x4]
        y4 = st.selectbox(
            "4D y축",
            y4_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="y_4d",
        )

    with c3:
        z4_options = [f for f in selected_features if f not in {x4, y4}]
        z4 = st.selectbox(
            "4D z축",
            z4_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="z_4d",
        )

    with c4:
        size4_options = [
            f for f in selected_features if f not in {x4, y4, z4}
        ]
        size4 = st.selectbox(
            "4번째 차원 · 점 크기",
            size4_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="size_4d",
        )

    size_min = df[size4].min()
    df["_size_4d"] = (
        df[size4] - size_min + 0.1
        if size_min <= 0
        else df[size4]
    )

    fig4d = px.scatter_3d(
        df,
        x=x4,
        y=y4,
        z=z4,
        size="_size_4d",
        size_max=18,
        color="묶음",
        category_orders={"묶음": ACTIVE_CLUSTER_SYMBOLS},
        hover_name="movieNm",
        hover_data={
            "묶음": True,
            size4: ":.3f",
            "_size_4d": False,
        },
        labels={
            x4: FEATURES[x4],
            y4: FEATURES[y4],
            z4: FEATURES[z4],
            size4: FEATURES[size4],
            "묶음": "묶음",
        },
    )

    fig4d.update_layout(height=700)
    st.plotly_chart(fig4d, use_container_width=True)


# ------------------------------------------------------------
# 5차원 산점도
# x + y + z + 점 크기 + 점 색 = 숫자 5차원
# 묶음은 점 모양으로 별도 표현
# ------------------------------------------------------------
st.subheader("🔥 5차원 산점도")
st.caption(
    "x·y·z = 공간 위치, **점 크기 = 4번째 차원**, "
    "**점 색의 연속적인 변화 = 5번째 차원**입니다. "
    "영화 묶음은 점 모양으로 따로 구분합니다."
)

if len(selected_features) < 4:
    st.info(
        "5차원 산점도를 보려면 군집화 속성 네 개를 모두 선택해 주세요."
    )
else:
    c1, c2, c3 = st.columns(3)

    with c1:
        x5 = st.selectbox(
            "5D x축",
            selected_features,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="x_5d",
        )

    with c2:
        y5_options = [f for f in selected_features if f != x5]
        y5 = st.selectbox(
            "5D y축",
            y5_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="y_5d",
        )

    with c3:
        z5_options = [f for f in selected_features if f not in {x5, y5}]
        z5 = st.selectbox(
            "5D z축",
            z5_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="z_5d",
        )

    c4, c5 = st.columns(2)

    with c4:
        size5_options = [
            f for f in selected_features
            if f not in {x5, y5, z5}
        ]

        size5 = st.selectbox(
            "4번째 차원 · 점 크기",
            size5_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="size_5d",
        )

    with c5:
        color5 = st.selectbox(
            "5번째 차원 · 점 색",
            options=list(FIFTH_FEATURES.keys()),
            index=0,
            format_func=lambda x: FIFTH_FEATURES[x],
            key="color_5d",
        )

    five_df = df[df[color5].notna()].copy()

    size_min_5 = five_df[size5].min()
    five_df["_size_5d"] = (
        five_df[size5] - size_min_5 + 0.1
        if size_min_5 <= 0
        else five_df[size5]
    )

    fig5d = px.scatter_3d(
        five_df,
        x=x5,
        y=y5,
        z=z5,
        size="_size_5d",
        size_max=20,
        color=color5,
        symbol="묶음",
        category_orders={"묶음": ACTIVE_CLUSTER_SYMBOLS},
        hover_name="movieNm",
        hover_data={
            "묶음": True,
            "movieCd": True,
            "total_audi": ":,.0f",
            size5: ":.3f",
            color5: ":.3f",
            "_size_5d": False,
        },
        labels={
            x5: FEATURES[x5],
            y5: FEATURES[y5],
            z5: FEATURES[z5],
            size5: FEATURES[size5],
            color5: FIFTH_FEATURES[color5],
            "묶음": "묶음",
            "movieCd": "영화코드",
            "total_audi": "누적 관객",
        },
        color_continuous_scale="Turbo",
    )

    fig5d.update_layout(
        height=760,
        margin=dict(l=0, r=0, t=20, b=0),
        scene=dict(
            xaxis_title=FEATURES[x5],
            yaxis_title=FEATURES[y5],
            zaxis_title=FEATURES[z5],
        ),
    )

    st.plotly_chart(fig5d, use_container_width=True)

    st.markdown(
        f"""
**현재 5차원 표현**
- x축: **{FEATURES[x5]}**
- y축: **{FEATURES[y5]}**
- z축: **{FEATURES[z5]}**
- 점 크기: **{FEATURES[size5]}**
- 점 색: **{FIFTH_FEATURES[color5]}**
- 점 모양: **영화 묶음(㉮·㉯·㉰ …)**
"""
    )


# ------------------------------------------------------------
# 묶음별 특징
# ------------------------------------------------------------
st.subheader("묶음별 특징")

summary = (
    df.groupby("묶음")
    .agg(
        영화_편수=("movieCd", "count"),
        평균_스크린_수=("first_scrn", "mean"),
        평균_누적_관객=("total_audi", "mean"),
        평균_10위권_일수=("days_in_top10", "mean"),
        평균_롱런_지수=("longrun_index", "mean"),
    )
    .reindex(ACTIVE_CLUSTER_SYMBOLS)
    .reset_index()
)

summary.columns = [
    "묶음",
    "영화 편수",
    "평균 스크린 수",
    "평균 누적 관객",
    "평균 10위권 일수",
    "평균 롱런 지수",
]

summary["영화 편수"] = summary["영화 편수"].astype(int)
summary["평균 스크린 수"] = summary["평균 스크린 수"].round(1)
summary["평균 누적 관객"] = summary["평균 누적 관객"].round(0).astype(int)
summary["평균 10위권 일수"] = summary["평균 10위권 일수"].round(1)
summary["평균 롱런 지수"] = summary["평균 롱런 지수"].round(2)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# 묶음별 누적 관객 상위 5편
# ------------------------------------------------------------
st.subheader("묶음별 누적 관객 상위 5편")

for start in range(0, cluster_count, 3):
    row_symbols = ACTIVE_CLUSTER_SYMBOLS[start:start + 3]
    cols = st.columns(len(row_symbols))

    for col, cluster_name in zip(cols, row_symbols):
        top5 = (
            df[df["묶음"] == cluster_name]
            .sort_values("total_audi", ascending=False)
            .head(5)
        )

        with col:
            st.markdown(f"### {cluster_name}")
            for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                st.write(
                    f"{rank}. **{row['movieNm']}** "
                    f"— {row['total_audi']:,.0f}명"
                )


# ------------------------------------------------------------
# 묶음 수 비교 - 엘보 방법
# ------------------------------------------------------------
st.subheader("묶음 수 비교")

inertia_rows = []

for k in range(1, 8):
    elbow_model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10,
    )

    elbow_model.fit(X_scaled)

    inertia_rows.append(
        {
            "묶음 수": k,
            "중심에서 떨어진 거리 제곱합": elbow_model.inertia_,
        }
    )

inertia_df = pd.DataFrame(inertia_rows)

inertia_df["앞 값에서 줄어든 양"] = (
    inertia_df["중심에서 떨어진 거리 제곱합"].shift(1)
    - inertia_df["중심에서 떨어진 거리 제곱합"]
)

fig_elbow = go.Figure()

fig_elbow.add_trace(
    go.Scatter(
        x=inertia_df["묶음 수"],
        y=inertia_df["중심에서 떨어진 거리 제곱합"],
        mode="lines+markers",
        hovertemplate=(
            "묶음 수: %{x}<br>"
            "거리 제곱합: %{y:,.2f}"
            "<extra></extra>"
        ),
    )
)

fig_elbow.add_vline(
    x=cluster_count,
    line_width=2,
    line_dash="dash",
    annotation_text=f"현재 선택: {cluster_count}",
    annotation_position="top",
)

fig_elbow.update_layout(
    xaxis_title="묶음 수",
    yaxis_title="중심에서 떨어진 거리의 제곱합",
    xaxis=dict(
        tickmode="array",
        tickvals=list(range(1, 8)),
    ),
    showlegend=False,
)

st.plotly_chart(fig_elbow, use_container_width=True)


# ------------------------------------------------------------
# 엘보 표
# ------------------------------------------------------------
display_inertia = inertia_df.copy()

display_inertia["중심에서 떨어진 거리 제곱합"] = (
    display_inertia["중심에서 떨어진 거리 제곱합"].round(2)
)

display_inertia["앞 값에서 줄어든 양"] = (
    display_inertia["앞 값에서 줄어든 양"].round(2)
)

display_inertia["앞 값에서 줄어든 양"] = (
    display_inertia["앞 값에서 줄어든 양"]
    .apply(lambda x: "" if pd.isna(x) else f"{x:,.2f}")
)

display_inertia["중심에서 떨어진 거리 제곱합"] = (
    display_inertia["중심에서 떨어진 거리 제곱합"]
    .map(lambda x: f"{x:,.2f}")
)

st.dataframe(
    display_inertia,
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# 실루엣 점수
# ------------------------------------------------------------
current_silhouette = silhouette_score(
    X_scaled,
    df["cluster_raw"],
)

st.write(
    f"현재 선택한 **{cluster_count}개 묶음의 실루엣 점수는 "
    f"{current_silhouette:.3f}**입니다. "
    "실루엣 점수는 -1에서 1 사이이며, "
    "1에 가까울수록 묶음이 더 뚜렷하게 나뉜다는 뜻입니다."
)

st.caption(
    "※ 스크린 수와 누적 관객은 상용로그 값으로 군집화하고, "
    "10위권 일수는 그대로 사용합니다. "
    "롱런 지수는 누적 관객 ÷ 첫 주 관객이며 최대 20입니다. "
    "선택한 군집화 속성은 K-평균에 넣기 전에 표준화합니다."
)
