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

# 개선 프롬프트의 비교 기준
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

    # 원본 맨 위 10줄을 그대로 보여주기 위해 별도 보관
    movies_head10 = movies.head(10).copy()

    # 일별 표의 날짜로 기준 기간 계산
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

    # 영화코드 정렬이 숫자/문자 혼합에도 안정적으로 되도록 보조 열 생성
    movies["movieCd"] = movies["movieCd"].astype(str)
    movies["_movieCd_num"] = pd.to_numeric(movies["movieCd"], errors="coerce")

    movies = movies.sort_values(
        by=["_movieCd_num", "movieCd"],
        na_position="last",
        kind="stable",
    ).reset_index(drop=True)

    # 숫자형 열 정리
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

    # 영화별 표에 있는 영화를 모두 분할 대상으로 사용
    # 정렬 후 10편 단위로 앞 3편(index % 10 = 0,1,2)을 테스트로 둠
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
        transformers.append(
            ("num", numeric_pipe, numeric_features)
        )

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
        transformers.append(
            ("cat", categorical_pipe, categorical_features)
        )

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
            f"총 관객 수(total_audi)가 비어 있는 영화가 {missing_target}편 있어 "
            "모든 영화를 평가에 사용할 수 없습니다."
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

    # 0명인 영화가 있을 경우 MAPE 분모 문제를 피함
    nonzero = y_test != 0
    if nonzero.any():
        mape = np.mean(
            np.abs((y_test[nonzero].to_numpy() - pred[nonzero]) / y_test[nonzero].to_numpy())
        ) * 100
    else:
        mape = np.nan

    result = test_df[
        ["movieCd", "movieNm", TARGET]
    ].copy()

    result["predicted_audi"] = pred
    result["abs_error"] = np.abs(
        result[TARGET] - result["predicted_audi"]
    )

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

period_text = (
    f"{period_start:%Y-%m-%d} ~ {period_end:%Y-%m-%d}"
)

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
st.write(
    "체크한 변수들만 사용해 새 다중 회귀 모델을 학습합니다. "
    "숫자형 변수의 빈칸은 중앙값으로, 장르·국가의 빈칸은 최빈값으로 보완합니다."
)

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

st.caption(
    "R²는 1에 가까울수록 실제값을 잘 설명합니다. "
    "MAE는 테스트 영화 한 편당 예측이 실제 총 관객 수에서 평균적으로 얼마나 빗나갔는지를 뜻합니다."
)


# ------------------------------------------------------------
# 실제값 vs 예측값 Plotly 산점도
# ------------------------------------------------------------
st.subheader("테스트 영화: 실제 총 관객 수 vs 예측 총 관객 수")

result = selected_eval["results"].copy()

# 예측값이 1,000명 미만이면 로그축에서 바닥(1,000명)에 붙여 표시
under_1000 = result["predicted_audi"] < 1000
under_1000_count = int(under_1000.sum())

result["plot_predicted_audi"] = result["predicted_audi"].clip(lower=1000)

# 로그축을 위해 실제값도 0 이하가 있을 경우 최소 1명으로만 안전 처리
result["plot_actual_audi"] = result[TARGET].clip(lower=1)

st.write(
    f"예측 관객 수가 **1,000명보다 작게 나온 영화는 {under_1000_count:,}편**입니다. "
    "이 영화들은 그래프의 1,000명 선에 붙여 표시합니다."
)

positive_values = pd.concat(
    [
        result["plot_actual_audi"],
        result["plot_predicted_audi"],
    ],
    ignore_index=True,
)

axis_min = max(1, float(positive_values[positive_values > 0].min()))
axis_max = max(
    float(result["plot_actual_audi"].max()),
    float(result["plot_predicted_audi"].max()),
    1000.0,
)

# 대각선 범위
diag_min = max(1, min(axis_min, 1000))
diag_max = axis_max

fig = go.Figure()

normal = result[~under_1000]
low = result[under_1000]

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
                normal["abs_error"].to_numpy(),
            ],
            axis=-1,
        ) if len(normal) else None,
        hovertemplate=(
            "영화명: %{customdata[0]}<br>"
            "영화코드: %{customdata[1]}<br>"
            "실제: %{customdata[2]:,.0f}명<br>"
            "예측: %{customdata[3]:,.0f}명<br>"
            "절대 오차: %{customdata[4]:,.0f}명"
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
                    low["abs_error"].to_numpy(),
                ],
                axis=-1,
            ),
            hovertemplate=(
                "영화명: %{customdata[0]}<br>"
                "영화코드: %{customdata[1]}<br>"
                "실제: %{customdata[2]:,.0f}명<br>"
                "원래 예측: %{customdata[3]:,.0f}명<br>"
                "그래프 표시 위치: 1,000명<br>"
                "절대 오차: %{customdata[4]:,.0f}명"
                "<extra></extra>"
            ),
        )
    )

# 실제값 = 예측값 대각선
fig.add_trace(
    go.Scatter(
        x=[diag_min, diag_max],
        y=[diag_min, diag_max],
        mode="lines",
        name="실제값 = 예측값",
        hoverinfo="skip",
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
fig.update_yaxes(type="log", range=[3, np.log10(diag_max) + 0.1])

st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# 테스트 영화 오차 표
# ------------------------------------------------------------
with st.expander("테스트 영화별 예측 결과 보기"):
    table = result[
        [
            "movieCd",
            "movieNm",
            TARGET,
            "predicted_audi",
            "abs_error",
        ]
    ].copy()

    table.columns = [
        "영화코드",
        "영화명",
        "실제 총 관객 수",
        "예측 총 관객 수",
        "절대 오차",
    ]

    for col in ["실제 총 관객 수", "예측 총 관객 수", "절대 오차"]:
        table[col] = table[col].round(0).astype("int64")

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )
