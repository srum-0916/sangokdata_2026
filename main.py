"""뇌졸중 예측 실습실 — 1단계: 데이터 소개 화면.

실행: streamlit run main.py
필요 패키지: streamlit, pandas, plotly, scikit-learn
"""

import pandas as pd
import streamlit as st


DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
EXPECTED_COLUMNS = [
    "id",
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "ever_married",
    "work_type",
    "Residence_type",
    "avg_glucose_level",
    "bmi",
    "smoking_status",
    "stroke",
]


st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
      /* 전체 화면과 글꼴 */
      .stApp {
        background: #f6f8fc;
        color: #192b42;
      }
      .block-container {
        max-width: 1190px;
        padding-top: 2.1rem;
        padding-bottom: 4rem;
      }
      html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: "Pretendard", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
      }
      #MainMenu, footer {visibility: hidden;}

      /* 머리말 */
      .hero {
        background: linear-gradient(112deg, #16304f 0%, #14556d 58%, #137c89 100%);
        padding: 2.25rem 2.4rem;
        border-radius: 24px;
        color: white;
        box-shadow: 0 12px 30px rgba(18, 55, 78, .12);
        margin-bottom: 1.65rem;
      }
      .hero .eyebrow {
        display: inline-block;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .15em;
        color: #a4f3ec;
        margin-bottom: .7rem;
      }
      .hero h1 {
        font-size: clamp(1.75rem, 3vw, 2.5rem);
        letter-spacing: -.055em;
        font-weight: 850;
        margin: 0 0 .8rem 0;
        line-height: 1.25;
        color: #ffffff !important;
      }
      .hero p {
        max-width: 750px;
        color: #d7e9f0;
        margin: 0;
        line-height: 1.85;
        font-size: .99rem;
      }
      .section-kicker {
        color: #138e96;
        font-weight: 800;
        font-size: .74rem;
        letter-spacing: .17em;
        padding-top: .4rem;
      }
      .section-heading {
        color: #1e3149;
        font-weight: 800;
        font-size: 1.5rem;
        letter-spacing: -.04em;
        margin: .15rem 0 .55rem;
      }
      .section-description {
        color: #62758b;
        font-size: .92rem;
        margin: 0 0 .9rem;
        line-height: 1.7;
      }
      /* 메트릭 카드 */
      .metric-card {
        background: #ffffff;
        border: 1px solid #e3eaf1;
        border-radius: 18px;
        padding: 1.35rem 1.25rem 1.25rem;
        min-height: 146px;
        box-shadow: 0 5px 19px rgba(35, 66, 95, .045);
        position: relative;
        overflow: hidden;
        margin-bottom: .4rem;
      }
      .metric-card:before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--accent, #14b8a6);
      }
      .metric-title {
        color: #687b91;
        font-size: .85rem;
        font-weight: 700;
        margin-bottom: .55rem;
      }
      .metric-value {
        color: #20344e;
        font-size: clamp(1.55rem, 2.3vw, 2.15rem);
        font-weight: 800;
        line-height: 1.2;
        letter-spacing: -.04em;
      }
      .metric-foot {
        color: #8191a4;
        font-size: .75rem;
        margin-top: .6rem;
      }
      /* 데이터 표 및 버튼 */
      div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #e3eaf1;
        background: #fff;
      }
      div[data-testid="stDownloadButton"] button {
        border-radius: 12px;
        border-color: #c8e4e4;
        color: #137b82;
        font-weight: 700;
        background: #fff;
      }
      div[data-testid="stDownloadButton"] button:hover {
        background: #edfbfa;
        border-color: #5dbbbb;
      }
      div[data-testid="stTextArea"] textarea {
        background: #fff;
        border-radius: 12px;
        border: 1px solid #dbe6ef;
      }
      hr {border-color: #e4eaf1 !important;}
      @media (max-width: 760px) {
        .block-container { padding-top: 1.1rem; }
        .hero { padding: 1.7rem 1.45rem; border-radius: 18px; }
        .metric-card { min-height: 128px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    """원본 CSV를 UTF-8로 읽고 1시간 동안 캐시한다."""
    return pd.read_csv(DATA_URL, encoding="utf-8")


def value_kind(series, column):
    """숫자 자료는 형태를, 범주 자료는 실제 값의 종류를 소개한다."""
    if column == "id":
        return "식별번호 (숫자)"

    values = series.dropna()
    distinct_count = values.nunique()

    if column in {"hypertension", "heart_disease", "stroke"}:
        return "0 / 1"

    if pd.api.types.is_numeric_dtype(series):
        return f"숫자형 · 고유 값 {distinct_count:,}개"

    distinct_values = [str(value) for value in values.drop_duplicates().tolist()]
    if len(distinct_values) <= 8:
        return " / ".join(distinct_values)
    return f"범주형 · {len(distinct_values)}종"


def section(kicker, title, description):
    st.markdown(f'<div class="section-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-heading">{title}</div>', unsafe_allow_html=True)
    if description:
        st.markdown(f'<div class="section-description">{description}</div>', unsafe_allow_html=True)


def metric_card(title, value, foot, accent):
    st.markdown(
        f"""
        <div class="metric-card" style="--accent: {accent}">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">🧠 STROKE PREDICTION LAB · 01 DATA OVERVIEW</div>
      <h1>뇌졸중 예측 실습실</h1>
      <p>
        데이터를 먼저 이해하는 것부터 시작해요. 사람들의 나이, 건강 정보, 생활 습관과
        뇌졸중 발생 여부가 담긴 데이터를 살펴보고, 열의 의미와 비어 있는 값을 확인해 봅시다.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("데이터를 불러오는 중이에요..."):
    try:
        df = load_data()
    except Exception as error:
        st.error("CSV 데이터를 불러오지 못했어요. 인터넷 연결과 데이터 주소를 확인해 주세요.")
        with st.expander("오류 자세히 보기"):
            st.code(str(error))
        st.stop()

missing_columns = [name for name in EXPECTED_COLUMNS if name not in df.columns]
if missing_columns:
    st.error("데이터의 열 구성이 예상과 달라요: " + ", ".join(missing_columns))
    st.stop()

person_count = len(df)
column_count = len(df.columns)
stroke_count = int(pd.to_numeric(df["stroke"], errors="coerce").eq(1).sum())
stroke_ratio = (stroke_count / person_count * 100) if person_count else 0.0

section("01 / DATA SNAPSHOT", "데이터 한눈에 보기", "전체 데이터를 기준으로 자동 계산한 숫자입니다.")
col1, col2, col3, col4 = st.columns(4, gap="medium")
with col1:
    metric_card("👥 전체 사람 수", f"{person_count:,}명", "CSV의 전체 행 수", "#2cb8a7")
with col2:
    metric_card("▦ 열 개수", f"{column_count:,}개", "데이터 항목의 수", "#4c8dd9")
with col3:
    metric_card("🧠 뇌졸중 발생", f"{stroke_count:,}명", "stroke = 1인 사람", "#eb9673")
with col4:
    metric_card("◉ 발생 비율", f"{stroke_ratio:.2f}%", "전체 사람 수 대비", "#a68be8")

st.write("")
st.divider()
section(
    "02 / COLUMN DICTIONARY",
    "열 살펴보기",
    "<b>‘우리말 뜻’ 칸만 직접 수정</b>할 수 있어요. 교재를 보고 채워 넣으세요. "
    "‘값의 종류’는 숫자형 여부 또는 실제 범주값을 보여 줍니다.",
)

# 작성한 뜻은 Streamlit 세션 동안 보관된다. 다른 열은 수정 불가.
if "korean_meanings" not in st.session_state:
    st.session_state.korean_meanings = {name: "" for name in df.columns}

schema = pd.DataFrame(
    {
        "열 이름": df.columns,
        "우리말 뜻": [st.session_state.korean_meanings.get(name, "") for name in df.columns],
        "값의 종류": [value_kind(df[name], name) for name in df.columns],
        "빈 값 개수": [int(df[name].isna().sum()) for name in df.columns],
    }
)

edited_schema = st.data_editor(
    schema,
    hide_index=True,
    use_container_width=True,
    num_rows="fixed",
    disabled=["열 이름", "값의 종류", "빈 값 개수"],
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름", width="medium"),
        "우리말 뜻": st.column_config.TextColumn(
            "우리말 뜻 ✏️", help="교재를 보고 직접 입력하는 칸입니다.", width="medium"
        ),
        "값의 종류": st.column_config.TextColumn("값의 종류", width="large"),
        "빈 값 개수": st.column_config.NumberColumn("빈 값 개수", format="%d", width="small"),
    },
    key="stroke_column_dictionary_editor",
)

# 사용자가 작성한 내용을 다음 재실행에서도 기본값으로 사용한다.
st.session_state.korean_meanings = {
    str(name): "" if pd.isna(meaning) else str(meaning)
    for name, meaning in zip(edited_schema["열 이름"], edited_schema["우리말 뜻"])
}

st.download_button(
    label="📥 작성한 열 설명표 CSV로 저장",
    data=edited_schema.rename(columns={"우리말 뜻 ✏️": "우리말 뜻"}).to_csv(index=False).encode("utf-8-sig"),
    file_name="stroke_column_dictionary.csv",
    mime="text/csv",
    use_container_width=False,
)

missing_total = int(df.isna().sum().sum())
if missing_total > 0:
    st.info(f"💡 전체 데이터에 빈 값이 {missing_total:,}개 있어요. 분석 전 결측치를 확인해야 해요.")

st.write("")
st.divider()
section(
    "03 / RAW DATA PREVIEW",
    "원본 데이터 미리 보기",
    "원본 CSV에서 처음 다섯 행을 그대로 가져왔어요. 비어 있는 셀은 채우거나 삭제하지 않았습니다.",
)
st.dataframe(df.head(5), hide_index=True, use_container_width=True)

st.write("")
st.divider()
section(
    "04 / SOURCE NOTE",
    "데이터 출처 기록하기",
    "아래 칸은 비워 두었어요. 교재에 나온 데이터 출처를 직접 적어 보세요.",
)
st.text_area(
    "데이터 출처",
    key="stroke_source_note",
    placeholder="교재에 나온 데이터 출처를 여기에 입력하세요.",
    height=115,
    label_visibility="collapsed",
)
