import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# ------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------
st.set_page_config(
    page_title="영화 흥행 예측기",
    page_icon="🎬",
    layout="wide",
)

DAILY_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
MOVIES_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

TARGET = "total_audi"

FEATURE_INFO = {
    "first_scrn": ("첫 관측일 스크린수", "numeric"),
    "first_show": ("첫 관측일 상영횟수", "numeric"),
    "days_in_top10": ("10위권 체류일수", "numeric"),
    "peak": ("성수기 개봉 여부", "numeric"),
    "first_week_audi": ("첫 주 관객 수", "numeric"),
    "genre": ("장르", "categorical"),
    "nation": ("국가", "categorical"),
}

BASE_FEATURES = ["first_scrn", "first_show", "days_in_top10"]
PLUS_WEEK_FEATURES = BASE_FEATURES + ["first_week_audi"]


# ------------------------------------------------------------
# 데이터 불러오기
# ------------------------------------------------------------
@st.cache_data
def load_data():
    daily = pd.read_csv(
        DAILY_URL,
        encoding="utf-8",
        dtype={"영화코드": str},
    )

    movies = pd.read_csv(
        MOVIES_URL,
        encoding="utf-8",
        dtype={"movieCd": str},
    )

    # 원본 맨 위 10줄 보관
    movies_head10 = movies.head(10).copy()

    # 일별 데이터의 기간 계산
    daily["날짜_변환"] = pd.to_datetime(
        daily["날짜"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(8),
        format="%Y%m%d",
        errors="coerce",
    )

    valid_dates = daily["날짜_변환"].dropna()
    if valid_dates.empty:
        raise ValueError("kobis_daily.csv의 날짜 열을 읽을 수 없습니다.")

    period_start = valid_dates.min()
    period_end = valid_dates.max()

    # 영화코드 순 정렬
    movies["movieCd"] = movies["movieCd"].astype(str)
    movies["_movieCd_num"] = pd.to_numeric(movies["movieCd"], errors="coerce")

    movies = movies.sort_values(
        by=["_movieCd_num", "movieCd"],
        na_position="last",
        kind="stable",
    ).reset_index(drop=True)

    numeric_columns = [
        "first_scrn",
        "first_show",
        "peak",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]

    for col in numeric_columns:
        if col in movies.columns:
            movies[col] = pd.to_numeric(movies[col], errors="coerce")

    # 앞과 동일:
    # 영화코드 순 정렬 후 10편마다 앞 3편을 테스트용으로 분리
    movies["_row_no"] = np.arange(len(movies))
    movies["_is_test"] = (movies["_row_no"] % 10) < 3

    return daily, movies, movies_head10, period_start, period_end


try:
    daily, movies, movies_head10, period_start, period_end = load_data()
except Exception as e:
    st.error(f"데이터를 불러오거나 처리하는 중 오류가 발생했습니다.\n\n{e}")
    st.stop()


# ------------------------------------------------------------
# 모델 함수
# ------------------------------------------------------------
def build_model(feature_cols):
    numeric_features = [
        col for col in feature_cols
        if FEATURE_INFO[col][1] == "numeric"
    ]

    categorical_features = [
        col for col in feature_cols
        if FEATURE_INFO[col][1] == "categorical"
    ]

    transformers = []

    if numeric_features:
        numeric_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]
        )
        transformers.append(("num", numeric_pipe, numeric_features))

    if categorical_features:
        categorical_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                (
                    "onehot",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                ),
            ]
        )
        transformers.append(("cat", categorical_pipe, categorical_features))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("regression", LinearRegression()),
        ]
    )

    return model


def evaluate_model(feature_cols):
    if not feature_cols:
        return None

    if movies[TARGET].isna().any():
        missing_target = int(movies[TARGET].isna().sum())
        raise ValueError(
            f"총 관객 수(total_audi)가 비어 있는 영화가 {missing_target}편 있습니다."
        )

    train_df = movies.loc[~movies["_is_test"]].copy()
    test_df = movies.loc[movies["_is_test"]].copy()

    X_train = train_df[feature_cols]
    y_train = train_df[TARGET].astype(float)

    X_test = test_df[feature_cols]
    y_test = test_df[TARGET].astype(float)

    model = build_model(feature_cols)
    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    r2 = r2_score(y_test, pred)
    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))

    nonzero = y_test != 0
    if nonzero.any():
        mape = np.mean(
            np.abs(
                (y_test[nonzero].to_numpy() - pred[nonzero])
                / y_test[nonzero].to_numpy()
            )
        ) * 100
    else:
        mape = np.nan

    result = test_df[
        ["movieCd", "movieNm", "first_scrn", TARGET]
    ].copy()

    result["predicted_audi"] = pred

    # 요청한 오차 정의: 실제 총 관객 수 - 예측값
    result["error"] = result[TARGET] - result["predicted_audi"]
    result["abs_error"] = np.abs(result["error"])

    return {
        "model": model,
        "train_count": len(train_df),
        "test_count": len(test_df),
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "results": result,
    }


# ------------------------------------------------------------
# 화면 상단
# ------------------------------------------------------------
st.title("🎬 영화 흥행 예측기")
st.caption(
    "KOBIS 영화별 집계 데이터로 총 관객 수(total_audi)를 예측하는 다중 회귀 모델입니다."
)

period_text = f"{period_start:%Y-%m-%d} ~ {period_end:%Y-%m-%d}"

st.info(
    "⚠️ 이 데이터의 변수들은 사후에 집계된 값을 포함합니다. "
    "따라서 이 앱의 점수는 실제 개봉 전에 흥행을 예측하는 성능을 뜻하지 않습니다."
)

meta1, meta2, meta3 = st.columns(3)
meta1.metric("기준 기간", period_text)
meta2.metric("영화별 표 전체 영화", f"{len(movies):,}편")
meta3.metric("분할 규칙", "10편마다 앞 3편 테스트")

st.subheader("영화별 표의 맨 위 10줄")
st.dataframe(
    movies_head10,
    use_container_width=True,
    hide_index=True,
)


# ------------------------------------------------------------
# 기본 모델 vs 첫 주 관객 추가 모델
# ------------------------------------------------------------
st.subheader("기본 모델과 첫 주 관객 추가 모델 비교")

try:
    base_eval = evaluate_model(BASE_FEATURES)
    plus_eval = evaluate_model(PLUS_WEEK_FEATURES)
except Exception as e:
    st.error(f"모델 평가 중 오류가 발생했습니다.\n\n{e}")
    st.stop()

left, right = st.columns(2)

with left:
    st.markdown("#### 기본 변수 3개")
    st.caption("첫 관측 스크린수 + 첫 관측 상영횟수 + 10위권 체류일수")
    st.metric("R² 점수", f"{base_eval['r2']:.3f}")
    st.metric("평균 절대 오차(MAE)", f"{base_eval['mae']:,.0f}명")

with right:
    st.markdown("#### 기본 변수 + 첫 주 관객")
    st.caption("기본 변수 3개 + 첫 주 관객 수")
    st.metric("R² 점수", f"{plus_eval['r2']:.3f}")
    st.metric("평균 절대 오차(MAE)", f"{plus_eval['mae']:,.0f}명")


# ------------------------------------------------------------
# 변수 선택
# ------------------------------------------------------------
st.subheader("내가 사용할 변수 고르기")

selected_features = []

checkbox_cols = st.columns(3)
feature_keys = list(FEATURE_INFO.keys())

for i, feature in enumerate(feature_keys):
    label, _ = FEATURE_INFO[feature]
    default_value = feature in BASE_FEATURES

    with checkbox_cols[i % 3]:
        checked = st.checkbox(
            f"{label} ({feature})",
            value=default_value,
            key=f"feature_{feature}",
        )

    if checked:
        selected_features.append(feature)

if not selected_features:
    st.warning("변수를 하나 이상 선택해 주세요.")
    st.stop()


# ------------------------------------------------------------
# 선택한 모델 평가
# ------------------------------------------------------------
try:
    selected_eval = evaluate_model(selected_features)
except Exception as e:
    st.error(f"선택한 모델을 평가하는 중 오류가 발생했습니다.\n\n{e}")
    st.stop()

st.subheader("선택한 모델의 평가 결과")

m1, m2, m3, m4 = st.columns(4)
m1.metric("학습에 쓴 영화", f"{selected_eval['train_count']:,}편")
m2.metric("점수를 평가한 영화", f"{selected_eval['test_count']:,}편")
m3.metric("R² 점수", f"{selected_eval['r2']:.3f}")
m4.metric("평균 절대 오차", f"{selected_eval['mae']:,.0f}명")

e1, e2 = st.columns(2)
e1.metric("RMSE", f"{selected_eval['rmse']:,.0f}명")

if np.isfinite(selected_eval["mape"]):
    e2.metric("평균 절대 백분율 오차", f"{selected_eval['mape']:.1f}%")
else:
    e2.metric("평균 절대 백분율 오차", "계산 불가")


# ------------------------------------------------------------
# 산점도 상세 분석
# ------------------------------------------------------------
st.subheader("테스트 영화: 실제 총 관객 수 vs 예측 총 관객 수")

result = selected_eval["results"].copy()

# 대각선 기준:
# 아래 = 예측 < 실제
# 위   = 예측 > 실제
below_diagonal_count = int((result["predicted_audi"] < result[TARGET]).sum())
above_diagonal_count = int((result["predicted_audi"] > result[TARGET]).sum())
on_diagonal_count = int(np.isclose(result["predicted_audi"], result[TARGET]).sum())

negative_count = int((result["predicted_audi"] < 0).sum())
min_prediction = float(result["predicted_audi"].min())

# 1,000명 미만 예측은 그래프 바닥에 표시
under_1000 = result["predicted_audi"] < 1000
under_1000_count = int(under_1000.sum())

result["plot_predicted_audi"] = result["predicted_audi"].clip(lower=1000)
result["plot_actual_audi"] = result[TARGET].clip(lower=1)

axis_max = max(
    float(result["plot_actual_audi"].max()),
    float(result["plot_predicted_audi"].max()),
    1000.0,
)

fig = go.Figure()

normal = result[~under_1000]
low = result[under_1000]

if len(normal):
    fig.add_trace(
        go.Scatter(
            x=normal["plot_actual_audi"],
            y=normal["plot_predicted_audi"],
            mode="markers",
            name="예측 1,000명 이상",
            customdata=np.stack(
                [
                    normal["movieNm"].astype(str),
                    normal["movieCd"].astype(str),
                    normal[TARGET].to_numpy(),
                    normal["predicted_audi"].to_numpy(),
                    normal["error"].to_numpy(),
                ],
                axis=-1,
            ),
            hovertemplate=(
                "영화명: %{customdata[0]}<br>"
                "영화코드: %{customdata[1]}<br>"
                "실제: %{customdata[2]:,.0f}명<br>"
                "예측: %{customdata[3]:,.0f}명<br>"
                "오차(실제-예측): %{customdata[4]:+,.0f}명"
                "<extra></extra>"
            ),
        )
    )

if len(low):
    fig.add_trace(
        go.Scatter(
            x=low["plot_actual_audi"],
            y=low["plot_predicted_audi"],
            mode="markers",
            name="예측 1,000명 미만 → 바닥 표시",
            customdata=np.stack(
                [
                    low["movieNm"].astype(str),
                    low["movieCd"].astype(str),
                    low[TARGET].to_numpy(),
                    low["predicted_audi"].to_numpy(),
                    low["error"].to_numpy(),
                ],
                axis=-1,
            ),
            hovertemplate=(
                "영화명: %{customdata[0]}<br>"
                "영화코드: %{customdata[1]}<br>"
                "실제: %{customdata[2]:,.0f}명<br>"
                "원래 예측: %{customdata[3]:,.0f}명<br>"
                "그래프 표시 위치: 1,000명<br>"
                "오차(실제-예측): %{customdata[4]:+,.0f}명"
                "<extra></extra>"
            ),
        )
    )

fig.add_trace(
    go.Scatter(
        x=[1, axis_max],
        y=[1, axis_max],
        mode="lines",
        name="실제값 = 예측값",
        hoverinfo="skip",
        line=dict(dash="dash"),
    )
)

fig.update_layout(
    xaxis_title="실제 총 관객 수",
    yaxis_title="예측 총 관객 수",
    hovermode="closest",
    legend_title_text="",
    margin=dict(l=20, r=20, t=20, b=20),
)

fig.update_xaxes(type="log")
fig.update_yaxes(
    type="log",
    range=[3, np.log10(axis_max) + 0.1],
)

scatter_col, detail_col = st.columns([3, 1])

with scatter_col:
    st.plotly_chart(fig, use_container_width=True)

with detail_col:
    st.markdown("#### 산점도 읽기")
    st.metric(
        "대각선보다 아래",
        f"{below_diagonal_count:,}편",
        help="예측값이 실제값보다 작은 영화입니다.",
    )
    st.metric(
        "대각선보다 위",
        f"{above_diagonal_count:,}편",
        help="예측값이 실제값보다 큰 영화입니다.",
    )

    if on_diagonal_count:
        st.caption(f"대각선과 거의 같은 점: {on_diagonal_count:,}편")

    st.metric(
        "음수로 예측된 영화",
        f"{negative_count:,}편",
    )
    st.metric(
        "가장 작은 예측값",
        f"{min_prediction:,.0f}명",
    )
    st.metric(
        "1,000명 미만 예측",
        f"{under_1000_count:,}편",
        help="로그축 표시를 위해 1,000명 위치에 붙여 표시합니다.",
    )

st.caption(
    "대각선 아래 점은 실제 관객 수가 예측보다 많았던 영화이고, "
    "대각선 위 점은 예측 관객 수가 실제보다 많았던 영화입니다."
)


# ------------------------------------------------------------
# 절대오차 상위 8편 분석
# ------------------------------------------------------------
st.subheader("예측이 가장 크게 빗나간 8편")

top8 = (
    result.nlargest(8, "abs_error")
    .copy()
    .sort_values("error")
)

total_abs_error = float(result["abs_error"].sum())
top8_abs_error = float(top8["abs_error"].sum())

if total_abs_error > 0:
    top8_share = top8_abs_error / total_abs_error * 100
else:
    top8_share = 0.0

st.write(
    f"절대오차가 큰 8편의 절대오차 합은 **{top8_abs_error:,.0f}명**이고, "
    f"테스트용 영화 전체 절대오차 합 **{total_abs_error:,.0f}명**의 "
    f"**{top8_share:.1f}%**입니다."
)

# 막대 라벨: 영화명 + 첫 관측일 스크린 수
top8["bar_label"] = top8.apply(
    lambda row: (
        f"{row['movieNm']} · 첫 스크린 "
        f"{int(row['first_scrn']):,}개"
        if pd.notna(row["first_scrn"])
        else f"{row['movieNm']} · 첫 스크린 정보 없음"
    ),
    axis=1,
)

# 양수(실제 > 예측) / 음수(예측 > 실제) 색상 구분
bar_colors = np.where(
    top8["error"] >= 0,
    "#2E86DE",
    "#E74C3C",
)

bar_fig = go.Figure()

bar_fig.add_trace(
    go.Bar(
        x=top8["error"],
        y=top8["bar_label"],
        orientation="h",
        marker_color=bar_colors,
        text=top8["error"].map(lambda x: f"{x:+,.0f}명"),
        textposition="outside",
        customdata=np.stack(
            [
                top8["movieNm"].astype(str),
                top8["first_scrn"].fillna(-1).to_numpy(),
                top8[TARGET].to_numpy(),
                top8["predicted_audi"].to_numpy(),
                top8["error"].to_numpy(),
                top8["abs_error"].to_numpy(),
            ],
            axis=-1,
        ),
        hovertemplate=(
            "영화명: %{customdata[0]}<br>"
            "첫 관측일 스크린 수: %{customdata[1]:,.0f}개<br>"
            "실제 총 관객 수: %{customdata[2]:,.0f}명<br>"
            "예측 총 관객 수: %{customdata[3]:,.0f}명<br>"
            "오차(실제-예측): %{customdata[4]:+,.0f}명<br>"
            "절대오차: %{customdata[5]:,.0f}명"
            "<extra></extra>"
        ),
    )
)

bar_fig.add_vline(
    x=0,
    line_width=2,
    line_dash="solid",
)

bar_fig.update_layout(
    xaxis_title="오차 = 실제 총 관객 수 - 예측 총 관객 수",
    yaxis_title="",
    showlegend=False,
    margin=dict(l=20, r=90, t=20, b=20),
    height=500,
)

st.plotly_chart(bar_fig, use_container_width=True)

st.caption(
    "오른쪽 막대는 실제 관객 수가 예측보다 많았던 영화, "
    "왼쪽 막대는 예측 관객 수가 실제보다 많았던 영화입니다."
)


# ------------------------------------------------------------
# 테스트 영화 오차 표
# ------------------------------------------------------------
with st.expander("테스트 영화별 예측 결과 보기"):
    table = result[
        [
            "movieCd",
            "movieNm",
            "first_scrn",
            TARGET,
            "predicted_audi",
            "error",
            "abs_error",
        ]
    ].copy()

    table.columns = [
        "영화코드",
        "영화명",
        "첫 관측일 스크린 수",
        "실제 총 관객 수",
        "예측 총 관객 수",
        "오차(실제-예측)",
        "절대오차",
    ]

    for col in [
        "실제 총 관객 수",
        "예측 총 관객 수",
        "오차(실제-예측)",
        "절대오차",
    ]:
        table[col] = table[col].round(0).astype("int64")

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )
