import math

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

APP_TITLE = "영화 유형 나누기"
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 영화 유형 나누기")
st.caption(
    "영화의 규모와 흥행 지속성을 나타내는 속성을 골라 K-평균으로 3가지 유형으로 묶습니다."
)

@st.cache_data
def load_and_prepare():
    df = pd.read_csv(DATA_URL, encoding="utf-8")

    required_cols = [
        "movieCd", "movieNm", "openDt", "genre", "nation",
        "first_scrn", "first_show", "first_date", "peak",
        "first_week_audi", "total_audi", "days_in_top10",
    ]

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"필요한 열이 없습니다: {', '.join(missing)}")

    total_count = len(df)

    for col in ["first_scrn", "first_week_audi", "total_audi", "days_in_top10"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

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

    grouped_count = len(valid)

    return valid, total_count, grouped_count


try:
    df, total_count, grouped_count = load_and_prepare()
except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다.\n\n{e}")
    st.stop()


FEATURES = {
    "log_first_scrn": "스크린 수(상용로그)",
    "log_total_audi": "누적 관객(상용로그)",
    "days_in_top10": "10위권 일수",
    "longrun_index": "롱런 지수",
}

st.write(
    f"전체 영화 **{total_count:,}편** 중 조건을 만족해 유형을 묶은 영화는 "
    f"**{grouped_count:,}편**입니다."
)

st.subheader("묶는 데 사용할 속성 선택")

selected_features = st.multiselect(
    "두 개 이상의 속성을 골라 주세요.",
    options=list(FEATURES.keys()),
    default=list(FEATURES.keys()),
    format_func=lambda x: FEATURES[x],
)

if len(selected_features) < 2:
    st.warning("K-평균 군집화를 하려면 속성을 두 개 이상 선택해야 합니다.")
    st.stop()

X = df[selected_features].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10,
)

df["cluster_raw"] = kmeans.fit_predict(X_scaled)

cluster_order = (
    df.groupby("cluster_raw")["total_audi"]
    .mean()
    .sort_values(ascending=False)
    .index
    .tolist()
)

cluster_label_map = {
    cluster_order[0]: "㉮",
    cluster_order[1]: "㉯",
    cluster_order[2]: "㉰",
}

df["묶음"] = df["cluster_raw"].map(cluster_label_map)
CLUSTER_ORDER = ["㉮", "㉯", "㉰"]

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
    category_orders={"묶음": CLUSTER_ORDER},
    hover_name="movieNm",
    hover_data={
        "묶음": True,
        "movieCd": True,
        "total_audi": ":,.0f",
        x_feature: ":.3f" if x_feature.startswith("log_") else ":.2f",
        y_feature: ":.3f" if y_feature.startswith("log_") else ":.2f",
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

st.subheader("3차원 산점도")

if len(selected_features) < 3:
    st.info(
        "3차원 산점도를 보려면 묶는 데 사용할 속성을 세 개 이상 선택해 주세요."
    )
else:
    axis3_col1, axis3_col2, axis3_col3 = st.columns(3)

    with axis3_col1:
        x3 = st.selectbox(
            "3D x축",
            options=selected_features,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="x_3d",
        )

    y3_options = [f for f in selected_features if f != x3]

    with axis3_col2:
        y3 = st.selectbox(
            "3D y축",
            options=y3_options,
            index=0,
            format_func=lambda x: FEATURES[x],
            key="y_3d",
        )

    z3_options = [f for f in selected_features if f not in {x3, y3}]

    with axis3_col3:
        z3 = st.selectbox(
            "3D z축",
            options=z3_options,
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
        category_orders={"묶음": CLUSTER_ORDER},
        hover_name="movieNm",
        hover_data={
            "묶음": True,
            "movieCd": True,
            "total_audi": ":,.0f",
        },
        labels={
            x3: FEATURES[x3],
            y3: FEATURES[y3],
            z3: FEATURES[z3],
            "묶음": "묶음",
            "movieCd": "영화코드",
            "total_audi": "누적 관객",
        },
    )

    fig3d.update_traces(marker=dict(size=3))
    fig3d.update_layout(
        legend_title_text="묶음",
        margin=dict(l=0, r=0, t=20, b=0),
        height=650,
    )

    st.plotly_chart(fig3d, use_container_width=True)

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
    .reindex(CLUSTER_ORDER)
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

st.subheader("묶음별 누적 관객 상위 5편")

cols = st.columns(3)

for i, cluster_name in enumerate(CLUSTER_ORDER):
    top5 = (
        df[df["묶음"] == cluster_name]
        .sort_values("total_audi", ascending=False)
        .head(5)
    )

    with cols[i]:
        st.markdown(f"### {cluster_name}")
        for rank, (_, row) in enumerate(top5.iterrows(), start=1):
            st.write(
                f"{rank}. **{row['movieNm']}** "
                f"— {row['total_audi']:,.0f}명"
            )

st.caption(
    "※ 스크린 수와 누적 관객은 군집화할 때 상용로그 값으로 사용하고, "
    "묶음별 평균 표에는 원래 단위의 평균을 표시합니다. "
    "롱런 지수는 누적 관객 ÷ 첫 주 관객이며 최대 20으로 제한합니다."
)
