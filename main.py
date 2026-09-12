from __future__ import annotations

import calendar
import html
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# Streamlit Cloud에 배포한 뒤 실제 주소를 입력하세요.
APP_URL = ""

SCHOOL_API_URL = "https://open.neis.go.kr/hub/schoolInfo"
MEAL_API_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"
KST = ZoneInfo("Asia/Seoul")
TODAY_KST = datetime.now(KST).date()

ALLERGY_NAMES = {
    1: "난류",
    2: "우유",
    3: "메밀",
    4: "땅콩",
    5: "대두",
    6: "밀",
    7: "고등어",
    8: "게",
    9: "새우",
    10: "돼지고기",
    11: "복숭아",
    12: "토마토",
    13: "아황산류",
    14: "호두",
    15: "닭고기",
    16: "쇠고기",
    17: "오징어",
    18: "조개류(굴·전복·홍합 포함)",
    19: "잣",
}

PAGE_CALENDAR = "🍱 급식 달력"
PAGE_DETAIL = "🔎 급식 상세"
PAGE_COMPARE = "🏫 학교 비교"
PAGE_OPTIONS = [PAGE_CALENDAR, PAGE_DETAIL, PAGE_COMPARE]


st.set_page_config(
    page_title="우리 학교 급식 탐험대",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_secret_key() -> str:
    """Streamlit Cloud Secrets에서 나이스 API 인증키를 안전하게 읽는다."""
    try:
        return str(st.secrets.get("SECRET_KEY", "")).strip()
    except Exception:
        # 로컬에 secrets.toml이 없어도 무인증 모드로 실행할 수 있다.
        return ""


# Streamlit Cloud의 Settings > Secrets에 아래 형식으로 등록하세요.
# SECRET_KEY = "여기에 API 키"
SECRET_KEY = load_secret_key()


def add_api_key(params: dict[str, Any]) -> dict[str, Any]:
    """인증키가 설정된 경우에만 나이스 API 요청 변수에 KEY를 추가한다."""
    if SECRET_KEY:
        return {**params, "KEY": SECRET_KEY}
    return params


def apply_styles() -> None:
    """앱 전체에 적용할 밝고 반응형인 스타일."""
    st.markdown(
        """
        <style>
        :root {
            --ink: #172033;
            --muted: #68758c;
            --line: #e8edf4;
            --brand: #5c67f2;
            --brand-soft: #eef0ff;
            --mint: #15a37d;
        }
        .stApp {
            background:
                radial-gradient(circle at 12% 0%, rgba(118, 217, 190, .16), transparent 30rem),
                radial-gradient(circle at 95% 8%, rgba(112, 127, 255, .14), transparent 32rem),
                #f7f9fc;
            color: var(--ink);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, .88);
            border-right: 1px solid var(--line);
        }
        .block-container { max-width: 1380px; padding-top: 2rem; padding-bottom: 4rem; }
        h1, h2, h3 { color: var(--ink); letter-spacing: -.025em; }
        .hero {
            padding: 1.55rem 1.7rem;
            border: 1px solid rgba(255,255,255,.78);
            border-radius: 24px;
            background: linear-gradient(115deg, rgba(255,255,255,.98), rgba(242,245,255,.9));
            box-shadow: 0 16px 48px rgba(36, 48, 92, .09);
            margin-bottom: 1rem;
        }
        .hero-kicker { color: var(--brand); font-weight: 800; font-size: .84rem; }
        .hero-title { margin: .18rem 0 .32rem; font-size: clamp(1.7rem, 4vw, 2.55rem); font-weight: 900; }
        .hero-copy { margin: 0; color: var(--muted); }
        .school-banner {
            display: flex; align-items: center; gap: .72rem;
            padding: .9rem 1.1rem; margin: .65rem 0 1rem;
            border-radius: 16px; background: #fff; border: 1px solid var(--line);
            box-shadow: 0 8px 26px rgba(39, 52, 90, .055);
        }
        .school-banner strong { color: var(--brand); }
        .soft-card {
            padding: 1rem; background: #fff; border: 1px solid var(--line);
            border-radius: 18px; box-shadow: 0 7px 22px rgba(31, 45, 78, .05);
        }
        .calendar-empty {
            min-height: 252px; padding: .8rem; border-radius: 17px;
            background: rgba(239, 243, 249, .62); color: #b8c0cd;
            border: 1px dashed #e3e8f0;
        }
        .calendar-empty span { font-size: .78rem; font-weight: 750; }
        .month-title { text-align: center; line-height: 1.1; }
        .month-title .year { color: #929cad; font-size: .72rem; font-weight: 800; letter-spacing: .08em; }
        .month-title .month { color: var(--ink); font-size: 1.72rem; font-weight: 950; margin-top: .15rem; }
        .month-stat {
            min-height: 94px; padding: .88rem 1rem; border-radius: 18px;
            background: rgba(255,255,255,.96); border: 1px solid var(--line);
            box-shadow: 0 7px 24px rgba(35, 48, 83, .055);
        }
        .month-stat .icon {
            display: inline-flex; align-items: center; justify-content: center;
            width: 1.75rem; height: 1.75rem; margin-bottom: .42rem;
            border-radius: 9px; background: var(--brand-soft); font-size: .88rem;
        }
        .month-stat .label { color: #8b95a7; font-size: .7rem; font-weight: 750; }
        .month-stat .value { color: var(--ink); font-size: 1.03rem; font-weight: 900; margin-top: .14rem; }
        .weekday-header {
            text-align: center; padding: .52rem .15rem; margin: .18rem 0 .35rem;
            border-radius: 12px; background: rgba(255,255,255,.72);
            color: #697489; font-size: .77rem; font-weight: 900;
            border: 1px solid rgba(232,237,244,.82);
        }
        .weekday-header.sun, .day-number.sun { color: #e25565; background-color: #fff1f3; }
        .weekday-header.sat, .day-number.sat { color: #4a75da; background-color: #eef4ff; }
        .day-number {
            display: inline-flex; align-items: center; min-width: 1.62rem; height: 1.62rem;
            padding: 0 .4rem; border-radius: 9px; font-size: .78rem;
            font-weight: 900; color: var(--muted); margin-bottom: .55rem;
            background: #f2f4f8;
        }
        .today-dot {
            display: inline-block; margin-left: .32rem; padding: .1rem .38rem;
            border-radius: 999px; background: #5c67f2; color: #fff;
            font-size: .58rem; vertical-align: middle; box-shadow: 0 3px 10px rgba(92,103,242,.22);
        }
        .meal-title { font-weight: 900; color: var(--ink); line-height: 1.35; margin-bottom: .38rem; letter-spacing: -.015em; }
        .meal-list { color: #5e6b80; font-size: .78rem; line-height: 1.45; min-height: 4.5rem; }
        .no-meal { color: #a1a9b6; font-size: .78rem; padding-top: .4rem; }
        .kcal-badge {
            display: inline-flex; gap: .33rem; align-items: center;
            margin-top: .55rem; border-radius: 999px; padding: .28rem .55rem;
            font-size: .7rem; font-weight: 850;
        }
        .level-low { color: #08765b; background: #e7f8f1; }
        .level-high { color: #9a5a00; background: #fff3d8; }
        .level-very-high { color: #b52d38; background: #ffe8eb; }
        .level-unknown { color: #64748b; background: #eef2f6; }
        .legend {
            display: flex; flex-wrap: wrap; align-items: center; gap: .42rem;
            color: var(--muted); font-size: .75rem; margin: .2rem 0 .85rem;
            padding: .65rem .8rem; border-radius: 14px; background: rgba(255,255,255,.72);
            border: 1px solid var(--line);
        }
        .legend-title { font-weight: 850; color: #515d72; margin-right: .12rem; }
        .legend-chip { padding: .2rem .45rem; border-radius: 999px; font-weight: 750; }
        .legend-low { color: #08765b; background: #e7f8f1; }
        .legend-high { color: #9a5a00; background: #fff3d8; }
        .legend-very-high { color: #b52d38; background: #ffe8eb; }
        .allergy-card {
            padding: 1rem 1.1rem; margin: .55rem 0; border-radius: 16px;
            background: #fff; border: 1px solid var(--line);
        }
        .allergy-card .food { font-size: 1rem; font-weight: 850; color: var(--ink); }
        .allergy-card .allergy { color: #6a7385; font-size: .86rem; margin-top: .35rem; }
        .allergy-card .raw { color: #a0a8b5; font-size: .72rem; margin-top: .25rem; }
        .insight-card {
            min-height: 116px; padding: 1rem; border-radius: 18px; color: #fff;
            background: linear-gradient(135deg, #5662ef, #7f87ff);
            box-shadow: 0 12px 30px rgba(84, 97, 238, .2);
        }
        .insight-card.green { background: linear-gradient(135deg, #079a74, #32bd98); }
        .insight-card.orange { background: linear-gradient(135deg, #e28230, #f3aa55); }
        .insight-label { font-size: .77rem; opacity: .87; }
        .insight-value { font-size: 1.13rem; font-weight: 900; margin-top: .42rem; line-height: 1.35; }
        div[data-testid="stMetric"] {
            padding: .95rem 1rem; border-radius: 17px; background: #fff;
            border: 1px solid var(--line); box-shadow: 0 7px 22px rgba(31,45,78,.05);
        }
        div[data-testid="stMetricValue"] { color: var(--ink); font-size: 1.3rem; }
        .stButton > button, .stLinkButton > a {
            border-radius: 12px; border-color: #dfe5ef; font-weight: 750;
        }
        .stButton > button:hover { border-color: var(--brand); color: var(--brand); }
        [class*="st-key-meal_"] button {
            min-height: 1.85rem; padding: .16rem .58rem;
            border-radius: 999px; font-size: .72rem; font-weight: 800;
            color: #667085; background: rgba(255, 255, 255, .9);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,.96); border-radius: 16px;
            box-shadow: 0 6px 22px rgba(34, 46, 77, .05);
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px); border-color: #d8def0;
            box-shadow: 0 11px 28px rgba(34, 46, 77, .09);
        }
        div[role="radiogroup"] {
            width: fit-content; padding: .28rem; margin-bottom: .8rem;
            border-radius: 15px; background: rgba(255,255,255,.86);
            border: 1px solid var(--line); box-shadow: 0 5px 18px rgba(34,46,77,.04);
        }
        @media (max-width: 780px) {
            .block-container { padding: 1.2rem .85rem 3rem; }
            .hero { padding: 1.2rem; border-radius: 19px; }
            .hero-title { font-size: 1.75rem; }
            .calendar-empty { min-height: 110px; }
            .month-stat { min-height: 84px; padding: .72rem; }
            .month-stat .value { font-size: .9rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "base_school": None,
        "school_results": [],
        "school_search_note": "",
        "compare_results": [],
        "compare_search_note": "",
        "comparison_schools": [],
        "selected_meal_date": TODAY_KST,
        "detail_date_picker": TODAY_KST,
        "active_page": PAGE_CALENDAR,
        "calendar_anchor": TODAY_KST.replace(day=1),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def safe_rows(payload: Any, root_key: str) -> tuple[list[dict[str, Any]], str | None]:
    """나이스의 성공/데이터 없음/오류 응답을 안전하게 분리한다."""
    if not isinstance(payload, dict):
        return [], "응답 형식을 확인할 수 없어요."

    result = payload.get("RESULT")
    if isinstance(result, dict):
        code = str(result.get("CODE", ""))
        if code == "INFO-200":
            return [], None
        if code and code != "INFO-000":
            return [], str(result.get("MESSAGE") or "나이스 API 요청을 처리하지 못했어요.")

    blocks = payload.get(root_key)
    if not isinstance(blocks, list):
        return [], None

    for block in blocks:
        if isinstance(block, dict) and isinstance(block.get("row"), list):
            return block["row"], None

    # 일부 오류는 head 안 RESULT에 들어온다.
    for block in blocks:
        if not isinstance(block, dict):
            continue
        for head in block.get("head", []) if isinstance(block.get("head"), list) else []:
            nested = head.get("RESULT") if isinstance(head, dict) else None
            if isinstance(nested, dict):
                code = str(nested.get("CODE", ""))
                if code == "INFO-200":
                    return [], None
                if code and code != "INFO-000":
                    return [], str(nested.get("MESSAGE") or "나이스 API 오류가 발생했어요.")
    return [], None


def expand_school_abbreviation(name: str) -> str:
    """학교명 끝의 흔한 줄임말만 정식 표현으로 바꾼다."""
    cleaned = re.sub(r"\s+", "", name.strip())
    if not cleaned:
        return cleaned
    formal_words = ("여자고등학교", "남자고등학교", "고등학교", "중학교", "초등학교")
    if any(word in cleaned for word in formal_words):
        return cleaned
    replacements = (
        ("여고", "여자고등학교"),
        ("남고", "남자고등학교"),
        ("고", "고등학교"),
        ("중", "중학교"),
        ("초", "초등학교"),
    )
    for short, full in replacements:
        if cleaned.endswith(short):
            return cleaned[: -len(short)] + full
    return cleaned


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def request_school_search(query: str) -> tuple[list[dict[str, str]], str | None]:
    params = add_api_key(
        {"Type": "json", "SCHUL_NM": query, "pSize": 100, "pIndex": 1}
    )
    try:
        response = requests.get(
            SCHOOL_API_URL,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        rows, error = safe_rows(response.json(), "schoolInfo")
    except (requests.RequestException, ValueError):
        return [], "학교 정보를 불러오지 못했어요. 잠시 후 다시 시도해 주세요."

    schools: list[dict[str, str]] = []
    for row in rows:
        school = {
            "name": str(row.get("SCHUL_NM", "")).strip(),
            "office_code": str(row.get("ATPT_OFCDC_SC_CODE", "")).strip(),
            "school_code": str(row.get("SD_SCHUL_CODE", "")).strip(),
            "region": str(row.get("LCTN_SC_NM", "지역 정보 없음")).strip(),
        }
        if school["name"] and school["office_code"] and school["school_code"]:
            schools.append(school)
    return schools, error


def search_schools(user_query: str) -> tuple[list[dict[str, str]], str, str | None]:
    query = user_query.strip()
    if not query:
        return [], "", "학교 이름을 입력해 주세요."

    schools, error = request_school_search(query)
    if schools or error:
        return schools, "", error

    expanded = expand_school_abbreviation(query)
    if expanded != re.sub(r"\s+", "", query):
        schools, error = request_school_search(expanded)
        note = f"'{query}' 대신 '{expanded}'로 다시 검색했어요."
        return schools, note, error
    return [], "", None


def school_label(school: dict[str, str]) -> str:
    return f"{school['name']} · {school.get('region', '지역 정보 없음')}"


def split_raw_menu(raw_menu: str) -> list[str]:
    normalized = re.sub(r"<br\s*/?>", "\n", raw_menu or "", flags=re.IGNORECASE)
    return [html.unescape(item).strip() for item in normalized.splitlines() if item.strip()]


def parse_menu_item(raw_item: str) -> dict[str, Any]:
    """메뉴명과 끝에 붙은 알레르기 번호를 분리한다."""
    allergy_numbers: list[int] = []
    matches = list(re.finditer(r"\(([\d\s.,]+)\)", raw_item))
    if matches:
        candidate = matches[-1]
        for number_text in re.findall(r"\d+", candidate.group(1)):
            number = int(number_text)
            if number in ALLERGY_NAMES and number not in allergy_numbers:
                allergy_numbers.append(number)
        name = (raw_item[: candidate.start()] + raw_item[candidate.end() :]).strip()
    else:
        name = raw_item.strip()
    name = re.sub(r"\s+", " ", name).strip()
    return {
        "name": name or raw_item.strip(),
        "raw": raw_item.strip(),
        "allergy_numbers": allergy_numbers,
        "allergy_names": [ALLERGY_NAMES[number] for number in allergy_numbers],
    }


def parse_calories(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"[\d,]+(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def calorie_level(calories: float | None) -> tuple[str, str]:
    if calories is None:
        return "정보 없음", "level-unknown"
    if calories < 900:
        return "낮음", "level-low"
    if calories < 1100:
        return "높음", "level-high"
    return "매우 높음", "level-very-high"


def format_kcal(calories: float | None) -> str:
    if calories is None:
        return "열량 정보 없음"
    if calories.is_integer():
        return f"{int(calories):,} kcal"
    return f"{calories:,.1f} kcal"


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def get_day_meal(office_code: str, school_code: str, ymd: str) -> dict[str, Any]:
    params = add_api_key(
        {
            "Type": "json",
            "ATPT_OFCDC_SC_CODE": office_code,
            "SD_SCHUL_CODE": school_code,
            "MMEAL_SC_CODE": "2",
            "MLSV_FROM_YMD": ymd,
            "MLSV_TO_YMD": ymd,
            "pSize": 1,
            "pIndex": 1,
        }
    )
    try:
        response = requests.get(MEAL_API_URL, params=params, timeout=10)
        response.raise_for_status()
        rows, error = safe_rows(response.json(), "mealServiceDietInfo")
    except (requests.RequestException, ValueError):
        return {"date": ymd, "meal": None, "error": "급식 정보를 불러오지 못했어요."}

    if error:
        return {"date": ymd, "meal": None, "error": error}
    if not rows:
        return {"date": ymd, "meal": None, "error": None}

    row = rows[0]
    raw_menu = str(row.get("DDISH_NM", "")).strip()
    raw_items = split_raw_menu(raw_menu)
    meal = {
        "date": str(row.get("MLSV_YMD", ymd)),
        "raw_menu": raw_menu,
        "items": [parse_menu_item(item) for item in raw_items],
        "calories": parse_calories(row.get("CAL_INFO")),
        "calorie_text": str(row.get("CAL_INFO", "")).strip(),
    }
    return {"date": ymd, "meal": meal, "error": None}


def dates_between(start_date: date, end_date: date, weekdays_only: bool = True) -> list[date]:
    days: list[date] = []
    current = start_date
    while current <= end_date:
        if not weekdays_only or current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def get_meals_for_period(
    school: dict[str, str], start_date: date, end_date: date
) -> tuple[dict[date, dict[str, Any]], int]:
    """날짜별 API 제한을 지키면서 기간 전체의 식단을 병렬 조회한다."""
    # 토요일에도 급식을 제공하는 학교가 있어 주말을 포함해 정확히 확인한다.
    query_dates = dates_between(start_date, end_date, weekdays_only=False)
    meals: dict[date, dict[str, Any]] = {}
    error_count = 0
    if not query_dates:
        return meals, error_count

    max_workers = min(6, len(query_dates))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_date = {
            executor.submit(
                get_day_meal,
                school["office_code"],
                school["school_code"],
                day.strftime("%Y%m%d"),
            ): day
            for day in query_dates
        }
        for future in as_completed(future_to_date):
            day = future_to_date[future]
            try:
                result = future.result()
            except Exception:
                error_count += 1
                continue
            if result.get("error"):
                error_count += 1
            if result.get("meal"):
                meals[day] = result["meal"]
    return meals, error_count


def month_bounds(anchor: date) -> tuple[date, date]:
    last_day = calendar.monthrange(anchor.year, anchor.month)[1]
    return anchor.replace(day=1), anchor.replace(day=last_day)


def shift_month(anchor: date, amount: int) -> date:
    month_index = anchor.year * 12 + (anchor.month - 1) + amount
    return date(month_index // 12, month_index % 12 + 1, 1)


def change_calendar_month(amount: int) -> None:
    st.session_state.calendar_anchor = shift_month(st.session_state.calendar_anchor, amount)


def select_meal_day(day: date) -> None:
    st.session_state.selected_meal_date = day
    st.session_state.detail_date_picker = day
    st.session_state.active_page = PAGE_DETAIL


def render_calorie_badge(calories: float | None) -> None:
    level, css_class = calorie_level(calories)
    st.markdown(
        f'<span class="kcal-badge {css_class}">{html.escape(format_kcal(calories))} · {level}</span>',
        unsafe_allow_html=True,
    )


def render_month_calendar(school: dict[str, str]) -> None:
    anchor = st.session_state.calendar_anchor
    nav_left, nav_title, nav_right = st.columns([1, 4, 1], vertical_alignment="center")
    with nav_left:
        st.button("← 이전 달", use_container_width=True, on_click=change_calendar_month, args=(-1,))
    with nav_title:
        st.markdown(
            "<div class='month-title'>"
            f"<div class='year'>{anchor.year} YEAR</div>"
            f"<div class='month'>{anchor.month}월</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with nav_right:
        st.button("다음 달 →", use_container_width=True, on_click=change_calendar_month, args=(1,))

    start_date, end_date = month_bounds(anchor)
    with st.spinner(f"{anchor.month}월 급식을 날짜별로 확인하고 있어요…"):
        meals, error_count = get_meals_for_period(school, start_date, end_date)

    if error_count:
        st.warning(f"일부 날짜({error_count}일)의 정보를 불러오지 못했어요. 잠시 후 다시 열면 채워질 수 있어요.")

    calorie_meals = [
        (meal_date, meal["calories"])
        for meal_date, meal in meals.items()
        if meal.get("calories") is not None
    ]
    average_calories = (
        sum(calories for _, calories in calorie_meals) / len(calorie_meals)
        if calorie_meals
        else None
    )
    highest_meal = max(calorie_meals, key=lambda item: item[1]) if calorie_meals else None

    summary_values = [
        ("🍱", "등록된 식단", f"{len(meals)}일" if meals else "아직 없음"),
        ("📊", "평균 열량", format_kcal(average_calories)),
        (
            "✨",
            "가장 높은 날",
            f"{highest_meal[0].day}일 · {format_kcal(highest_meal[1])}"
            if highest_meal
            else "정보 없음",
        ),
    ]
    summary_columns = st.columns(3)
    for column, (icon, label, value) in zip(summary_columns, summary_values):
        column.markdown(
            "<div class='month-stat'>"
            f"<div class='icon'>{icon}</div>"
            f"<div class='label'>{html.escape(label)}</div>"
            f"<div class='value'>{html.escape(value)}</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='legend'>"
        "<span class='legend-title'>열량 수준</span>"
        "<span class='legend-chip legend-low'>● 900 kcal 미만</span>"
        "<span class='legend-chip legend-high'>● 900~1099 kcal</span>"
        "<span class='legend-chip legend-very-high'>● 1100 kcal 이상</span>"
        "<span>빠른 구분용 표시이며 개인의 건강·섭취 판단 기준은 아닙니다.</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    weekday_names = [
        ("일", "sun"),
        ("월", ""),
        ("화", ""),
        ("수", ""),
        ("목", ""),
        ("금", ""),
        ("토", "sat"),
    ]
    header_columns = st.columns(7)
    for column, (name, tone) in zip(header_columns, weekday_names):
        column.markdown(
            f"<div class='weekday-header {tone}'>{name}</div>",
            unsafe_allow_html=True,
        )

    month_calendar = calendar.Calendar(firstweekday=6).monthdatescalendar(anchor.year, anchor.month)
    for week_index, week in enumerate(month_calendar):
        columns = st.columns(7, gap="small")
        for day_index, (column, day) in enumerate(zip(columns, week)):
            with column:
                if day.month != anchor.month:
                    st.markdown(
                        f"<div class='calendar-empty'><span>{day.day}</span></div>",
                        unsafe_allow_html=True,
                    )
                    continue

                meal = meals.get(day)
                with st.container(height=208, border=True):
                    today_badge = "<span class='today-dot'>오늘</span>" if day == TODAY_KST else ""
                    day_tone = "sun" if day_index == 0 else "sat" if day_index == 6 else ""
                    st.markdown(
                        f"<div class='day-number {day_tone}'>{day.day}{today_badge}</div>",
                        unsafe_allow_html=True,
                    )
                    if meal:
                        names = [item["name"] for item in meal["items"]]
                        representative = names[0] if names else "급식 메뉴"
                        remaining = names[1:4]
                        menu_preview = "<br>".join(f"· {html.escape(name)}" for name in remaining)
                        if len(names) > 4:
                            menu_preview += f"<br>· 외 {len(names) - 4}개"
                        st.markdown(
                            f"<div class='meal-title'>{html.escape(representative)}</div>"
                            f"<div class='meal-list'>{menu_preview or '메뉴를 눌러 확인하세요.'}</div>",
                            unsafe_allow_html=True,
                        )
                        render_calorie_badge(meal["calories"])
                    else:
                        st.markdown("<div class='no-meal'>급식 없음</div>", unsafe_allow_html=True)

                # 상세 버튼은 식단 카드와 분리해 날짜마다 같은 높이에 작게 배치한다.
                if meal:
                    _, button_column, _ = st.columns([1, 3, 1])
                    with button_column:
                        st.button(
                            "상세 보기",
                            key=f"meal_{anchor:%Y%m}_{week_index}_{day:%d}",
                            use_container_width=True,
                            on_click=select_meal_day,
                            args=(day,),
                        )


def render_detail_page(school: dict[str, str]) -> None:
    st.subheader("선택한 날의 급식")
    selected = st.date_input(
        "날짜",
        key="detail_date_picker",
        help="달력에서 날짜를 누르거나 여기서 직접 고를 수 있어요.",
    )
    if selected != st.session_state.selected_meal_date:
        st.session_state.selected_meal_date = selected

    with st.spinner("급식 상세 정보를 불러오고 있어요…"):
        result = get_day_meal(
            school["office_code"], school["school_code"], selected.strftime("%Y%m%d")
        )

    if result.get("error"):
        st.warning(result["error"])
        return
    meal = result.get("meal")
    if not meal:
        st.info(f"{selected:%Y년 %m월 %d일}에는 등록된 중식 급식이 없어요.")
        return

    left, middle, right = st.columns(3)
    left.metric("날짜", selected.strftime("%Y.%m.%d"))
    middle.metric("학교", school["name"])
    right.metric("총 열량", format_kcal(meal["calories"]))
    render_calorie_badge(meal["calories"])

    st.markdown("### 메뉴별 알레르기 정보")
    for item in meal["items"]:
        allergy_text = (
            " · ".join(item["allergy_names"])
            if item["allergy_names"]
            else "표시된 알레르기 정보 없음"
        )
        st.markdown(
            "<div class='allergy-card'>"
            f"<div class='food'>{html.escape(item['name'])}</div>"
            f"<div class='allergy'>알레르기: {html.escape(allergy_text)}</div>"
            f"<div class='raw'>원문 표기: {html.escape(item['raw'])}</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with st.expander("API가 제공한 원래 메뉴 전체 보기"):
        st.code("\n".join(split_raw_menu(meal["raw_menu"])), language=None)

    st.caption(
        "※ 실제 알레르기 여부와 식재료는 학교가 제공한 급식 정보를 기준으로 하며, "
        "심한 알레르기가 있는 경우 학교의 공식 정보를 다시 확인하세요."
    )


def comparison_rows(
    schools: list[dict[str, str]], start_date: date, end_date: date
) -> tuple[pd.DataFrame, dict[str, int]]:
    rows: list[dict[str, Any]] = []
    errors: dict[str, int] = {}
    for school in schools:
        meals, error_count = get_meals_for_period(school, start_date, end_date)
        errors[school["school_code"]] = error_count
        for meal_date, meal in meals.items():
            if meal["calories"] is None:
                continue
            rows.append(
                {
                    "학교": school["name"],
                    "지역": school["region"],
                    "학교 식별": school_label(school),
                    "날짜": pd.Timestamp(meal_date),
                    "칼로리": meal["calories"],
                }
            )
    return pd.DataFrame(rows), errors


def build_comparison_summary(data: pd.DataFrame) -> pd.DataFrame:
    summary_rows: list[dict[str, Any]] = []
    for school_name, group in data.groupby("학교 식별", sort=False):
        max_row = group.loc[group["칼로리"].idxmax()]
        min_row = group.loc[group["칼로리"].idxmin()]
        summary_rows.append(
            {
                "학교": school_name,
                "평균 칼로리": round(group["칼로리"].mean(), 1),
                "최고 열량일": f"{max_row['날짜']:%m.%d} · {max_row['칼로리']:,.1f} kcal",
                "최저 열량일": f"{min_row['날짜']:%m.%d} · {min_row['칼로리']:,.1f} kcal",
                "900 kcal 이상": int((group["칼로리"] >= 900).sum()),
                "1100 kcal 이상": int((group["칼로리"] >= 1100).sum()),
                "급식 일수": int(len(group)),
            }
        )
    return pd.DataFrame(summary_rows)


def render_insight_cards(summary: pd.DataFrame) -> None:
    if summary.empty:
        return
    hottest = summary.loc[summary["평균 칼로리"].idxmax(), "학교"]
    lightest = summary.loc[summary["평균 칼로리"].idxmin(), "학교"]
    most_very_high = summary.loc[summary["1100 kcal 이상"].idxmax()]
    cards = [
        ("🔥 평균 열량이 가장 높은 학교", hottest, ""),
        ("🌱 평균 열량이 가장 낮은 학교", lightest, "green"),
        (
            "⚡ 1100 kcal 이상 급식 최다",
            f"{most_very_high['학교']} · {int(most_very_high['1100 kcal 이상'])}일",
            "orange",
        ),
    ]
    columns = st.columns(3)
    for column, (label, value, css_class) in zip(columns, cards):
        column.markdown(
            f"<div class='insight-card {css_class}'>"
            f"<div class='insight-label'>{html.escape(label)}</div>"
            f"<div class='insight-value'>{html.escape(str(value))}</div></div>",
            unsafe_allow_html=True,
        )


def polish_comparison_chart(figure: Any, height: int = 440) -> Any:
    """비교 화면의 모든 Plotly 그래프에 같은 디자인을 적용한다."""
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=28, b=12),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard, Apple SD Gothic Neo, sans-serif", color="#354057"),
        legend_title_text="학교",
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
    )
    figure.update_xaxes(gridcolor="#edf0f5", zeroline=False)
    figure.update_yaxes(gridcolor="#edf0f5", zeroline=False)
    return figure


def build_calorie_band_counts(data: pd.DataFrame) -> pd.DataFrame:
    """학교별 열량 구간의 급식 일수를 빠짐없이 계산한다."""
    band_order = ["900 kcal 미만", "900~1099 kcal", "1100 kcal 이상"]
    school_order = list(dict.fromkeys(data["학교 식별"].tolist()))
    banded = data.copy()
    banded["열량 구간"] = pd.cut(
        banded["칼로리"],
        bins=[float("-inf"), 900, 1100, float("inf")],
        labels=band_order,
        right=False,
    )
    counts = (
        banded.groupby(["학교 식별", "열량 구간"], observed=False)
        .size()
        .rename("급식 일수")
        .reindex(
            pd.MultiIndex.from_product(
                [school_order, band_order], names=["학교 식별", "열량 구간"]
            ),
            fill_value=0,
        )
        .reset_index()
    )
    return counts


def build_daily_school_gap(data: pd.DataFrame) -> pd.DataFrame:
    """같은 날짜에 데이터가 있는 학교들의 최고·최저 열량 차이를 계산한다."""
    daily_gap = (
        data.groupby("날짜")
        .agg(
            최고_칼로리=("칼로리", "max"),
            최저_칼로리=("칼로리", "min"),
            비교_학교수=("학교 식별", "nunique"),
        )
        .reset_index()
    )
    daily_gap = daily_gap[daily_gap["비교_학교수"] >= 2].copy()
    daily_gap["학교 간 차이"] = daily_gap["최고_칼로리"] - daily_gap["최저_칼로리"]
    return daily_gap


def render_comparison_page(base_school: dict[str, str]) -> None:
    st.subheader("여러 학교의 급식 비교")
    st.caption("기준 학교는 자동으로 포함됩니다. 비교 학교를 두 곳 이상 추가하면 3개 학교를 한눈에 볼 수 있어요.")

    comparison_schools = [
        school
        for school in st.session_state.comparison_schools
        if school["school_code"] != base_school["school_code"]
    ]
    st.session_state.comparison_schools = comparison_schools

    with st.form("compare_search_form"):
        query = st.text_input("비교할 학교 검색", placeholder="예: 수도여고")
        submitted = st.form_submit_button("학교 찾기", use_container_width=True)
    if submitted:
        results, note, error = search_schools(query)
        st.session_state.compare_results = results
        st.session_state.compare_search_note = note
        if error:
            st.warning(error)

    if st.session_state.compare_search_note:
        st.caption(st.session_state.compare_search_note)

    results = st.session_state.compare_results
    if results:
        options = {school_label(school): school for school in results}
        selected_label = st.selectbox("검색 결과", options.keys(), key="compare_school_choice")
        if st.button("＋ 비교 학교에 추가", type="primary", use_container_width=True):
            selected_school = options[selected_label]
            existing_codes = {school["school_code"] for school in comparison_schools}
            if selected_school["school_code"] == base_school["school_code"]:
                st.info("기준 학교는 이미 비교에 포함되어 있어요.")
            elif selected_school["school_code"] in existing_codes:
                st.info("이미 추가한 학교예요.")
            else:
                st.session_state.comparison_schools.append(selected_school)
                st.rerun()
    elif submitted:
        st.info("검색된 학교가 없어요. 정식 학교명이나 지역과 함께 다시 검색해 보세요.")

    st.markdown("#### 현재 비교 학교")
    st.markdown(
        f"<div class='school-banner'>⭐ <div><strong>기준</strong><br>{html.escape(school_label(base_school))}</div></div>",
        unsafe_allow_html=True,
    )
    for index, school in enumerate(comparison_schools):
        col_school, col_remove = st.columns([5, 1], vertical_alignment="center")
        col_school.markdown(
            f"<div class='soft-card'>🏫 {html.escape(school_label(school))}</div>",
            unsafe_allow_html=True,
        )
        if col_remove.button("삭제", key=f"remove_school_{school['school_code']}_{index}"):
            st.session_state.comparison_schools = [
                item
                for item in st.session_state.comparison_schools
                if item["school_code"] != school["school_code"]
            ]
            st.rerun()

    all_schools = [base_school] + comparison_schools
    if len(all_schools) < 3:
        st.info(f"비교 학교를 {3 - len(all_schools)}곳 더 추가하면 3개 학교 비교가 완성돼요.")

    current_start, current_end = month_bounds(TODAY_KST.replace(day=1))
    selected_period = st.date_input(
        "비교 기간",
        value=(current_start, current_end),
        max_value=TODAY_KST + timedelta(days=366),
        key="compare_period",
    )
    if not isinstance(selected_period, (tuple, list)) or len(selected_period) != 2:
        st.info("비교할 시작일과 종료일을 모두 골라 주세요.")
        return
    start_date, end_date = selected_period
    if start_date > end_date:
        st.warning("시작일은 종료일보다 빠르게 골라 주세요.")
        return
    if (end_date - start_date).days > 61:
        st.warning("원활한 조회를 위해 비교 기간은 최대 62일까지 선택할 수 있어요.")
        return

    if not st.button("선택한 기간 비교하기", type="primary", use_container_width=True):
        st.caption("기간을 고른 뒤 버튼을 누르면 실제 급식 데이터를 불러옵니다.")
        return

    with st.spinner(f"{len(all_schools)}개 학교의 급식을 날짜별로 비교하고 있어요…"):
        data, errors = comparison_rows(all_schools, start_date, end_date)

    total_errors = sum(errors.values())
    if total_errors:
        st.warning(f"일부 요청({total_errors}건)은 불러오지 못했어요. 표시된 결과만으로 비교합니다.")
    if data.empty:
        st.info("선택한 기간에 비교할 수 있는 급식 열량 데이터가 없어요.")
        return

    summary = build_comparison_summary(data)
    render_insight_cards(summary)

    st.markdown("### 비교 요약")
    display_summary = summary.copy()
    display_summary["평균 칼로리"] = display_summary["평균 칼로리"].map(lambda value: f"{value:,.1f} kcal")
    st.dataframe(display_summary, hide_index=True, use_container_width=True)

    st.markdown("### 그래프로 비교하기")
    st.caption("탭을 바꾸면 변화·평균·분포·구간 구성·날짜별 차이를 서로 다른 관점에서 볼 수 있어요.")
    trend_tab, average_tab, distribution_tab, band_tab, heatmap_tab, gap_tab = st.tabs(
        ["📈 날짜별 변화", "📊 학교별 평균", "📦 전체 분포", "🎨 구간 구성", "🗓️ 히트맵", "↔️ 학교 간 차이"]
    )

    with trend_tab:
        st.markdown("#### 날짜별 급식 열량 변화")
        st.caption("날짜가 지나면서 각 학교의 급식 열량이 어떻게 달라졌는지 확인해요.")
        line_figure = px.line(
            data.sort_values("날짜"),
            x="날짜",
            y="칼로리",
            color="학교 식별",
            markers=True,
            labels={"학교 식별": "학교", "칼로리": "열량(kcal)"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        line_figure.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>날짜 %{x|%Y-%m-%d}<br>%{y:,.1f} kcal<extra></extra>"
        )
        line_figure.update_layout(hovermode="x unified")
        line_figure.update_xaxes(showgrid=False)
        st.plotly_chart(polish_comparison_chart(line_figure, 480), use_container_width=True)

    with average_tab:
        st.markdown("#### 학교별 평균 열량")
        st.caption("조회 기간 전체의 평균을 비교해 학교별 차이를 간단히 확인해요.")
        bar_figure = px.bar(
            summary.sort_values("평균 칼로리"),
            x="평균 칼로리",
            y="학교",
            orientation="h",
            text="평균 칼로리",
            color="평균 칼로리",
            color_continuous_scale=["#68cbb1", "#7e87fb", "#ef8a70"],
            labels={"평균 칼로리": "평균 열량(kcal)"},
        )
        bar_figure.update_traces(
            texttemplate="%{text:,.1f} kcal",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>평균 %{x:,.1f} kcal<extra></extra>",
        )
        bar_figure.update_layout(showlegend=False, coloraxis_showscale=False)
        bar_figure.update_yaxes(title=None)
        st.plotly_chart(
            polish_comparison_chart(bar_figure, max(360, 82 * len(summary))),
            use_container_width=True,
        )

    with distribution_tab:
        st.markdown("#### 학교별 급식 열량 분포")
        st.caption("상자의 위치와 길이로 평소 범위와 날짜별 퍼짐 정도를 함께 비교해요.")
        box_figure = px.box(
            data,
            x="칼로리",
            y="학교 식별",
            color="학교 식별",
            orientation="h",
            points="all",
            hover_data={"날짜": "|%Y-%m-%d", "학교 식별": False},
            labels={"학교 식별": "학교", "칼로리": "열량(kcal)"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        box_figure.update_traces(jitter=0.28, marker_size=6)
        box_figure.update_layout(showlegend=False)
        box_figure.update_yaxes(title=None)
        st.plotly_chart(
            polish_comparison_chart(box_figure, max(380, 86 * len(summary))),
            use_container_width=True,
        )

    with band_tab:
        st.markdown("#### 열량 구간별 급식 일수")
        st.caption("각 학교의 식단이 세 열량 구간에 며칠씩 포함되었는지 비교해요.")
        band_counts = build_calorie_band_counts(data)
        band_figure = px.bar(
            band_counts,
            x="학교 식별",
            y="급식 일수",
            color="열량 구간",
            barmode="stack",
            text="급식 일수",
            category_orders={
                "열량 구간": ["900 kcal 미만", "900~1099 kcal", "1100 kcal 이상"]
            },
            color_discrete_map={
                "900 kcal 미만": "#36b998",
                "900~1099 kcal": "#f2b457",
                "1100 kcal 이상": "#eb6b78",
            },
            labels={"학교 식별": "학교", "급식 일수": "급식 일수", "열량 구간": "열량 구간"},
        )
        band_figure.update_traces(
            texttemplate="%{text}일",
            textposition="inside",
            hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y}일<extra></extra>",
        )
        band_figure.update_layout(legend_title_text="열량 구간")
        band_figure.update_xaxes(tickangle=-12)
        st.plotly_chart(polish_comparison_chart(band_figure, 460), use_container_width=True)

    with heatmap_tab:
        st.markdown("#### 날짜와 학교별 열량 히트맵")
        st.caption("색이 진한 칸을 따라가면 어느 학교의 어느 날짜가 상대적으로 높았는지 빠르게 찾을 수 있어요.")
        heatmap_data = data.pivot_table(
            index="학교 식별", columns="날짜", values="칼로리", aggfunc="mean"
        ).sort_index(axis=1)
        heatmap_data.columns = [column.strftime("%m.%d") for column in heatmap_data.columns]
        heatmap_figure = px.imshow(
            heatmap_data,
            aspect="auto",
            color_continuous_scale=["#e9f8f3", "#fff0c8", "#f27f87"],
            labels={"x": "날짜", "y": "학교", "color": "열량(kcal)"},
        )
        heatmap_figure.update_traces(
            hovertemplate="<b>%{y}</b><br>날짜 %{x}<br>%{z:,.1f} kcal<extra></extra>"
        )
        heatmap_figure.update_layout(coloraxis_colorbar=dict(title="kcal"))
        heatmap_figure.update_yaxes(title=None)
        st.plotly_chart(
            polish_comparison_chart(heatmap_figure, max(380, 82 * len(summary))),
            use_container_width=True,
        )

    with gap_tab:
        st.markdown("#### 날짜별 학교 간 열량 차이")
        st.caption("같은 날 급식이 등록된 학교 중 가장 높은 값과 낮은 값의 차이를 보여 줘요.")
        daily_gap = build_daily_school_gap(data)
        if daily_gap.empty:
            st.info("같은 날짜에 두 학교 이상의 데이터가 있어야 학교 간 차이를 계산할 수 있어요.")
        else:
            gap_figure = px.bar(
                daily_gap,
                x="날짜",
                y="학교 간 차이",
                color="학교 간 차이",
                color_continuous_scale=["#8fdac6", "#7f89f4", "#ed7180"],
                labels={"학교 간 차이": "최고−최저 차이(kcal)"},
                custom_data=["최고_칼로리", "최저_칼로리", "비교_학교수"],
            )
            gap_figure.update_traces(
                hovertemplate=(
                    "<b>%{x|%Y-%m-%d}</b><br>학교 간 차이 %{y:,.1f} kcal"
                    "<br>최고 %{customdata[0]:,.1f} · 최저 %{customdata[1]:,.1f} kcal"
                    "<br>비교 학교 %{customdata[2]}곳<extra></extra>"
                )
            )
            gap_figure.update_layout(coloraxis_showscale=False)
            gap_figure.update_xaxes(showgrid=False)
            st.plotly_chart(polish_comparison_chart(gap_figure, 440), use_container_width=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🏫 기준 학교 찾기")
        st.caption("학교 이름과 지역을 확인한 뒤 선택하세요.")
        if SECRET_KEY:
            st.caption("🔐 나이스 API 인증키 연결됨")
        else:
            st.caption("🔓 API 인증키 미설정 · 무인증 조회 모드")
        with st.form("base_school_search_form"):
            query = st.text_input("학교 이름", placeholder="예: 수도여고")
            submitted = st.form_submit_button("검색", use_container_width=True)
        if submitted:
            results, note, error = search_schools(query)
            st.session_state.school_results = results
            st.session_state.school_search_note = note
            if error:
                st.warning(error)

        if st.session_state.school_search_note:
            st.caption(st.session_state.school_search_note)

        results = st.session_state.school_results
        if results:
            options = {school_label(school): school for school in results}
            selected_label = st.selectbox("검색 결과", options.keys(), key="base_school_choice")
            if st.button("이 학교를 기준으로 설정", type="primary", use_container_width=True):
                chosen = options[selected_label]
                previous = st.session_state.base_school
                st.session_state.base_school = chosen
                if not previous or previous.get("school_code") != chosen["school_code"]:
                    st.session_state.selected_meal_date = TODAY_KST
                    st.session_state.detail_date_picker = TODAY_KST
                    st.session_state.calendar_anchor = TODAY_KST.replace(day=1)
                st.rerun()
        elif submitted:
            st.info("검색된 학교가 없어요. 학교 이름을 조금 다르게 입력해 보세요.")

        if st.session_state.base_school:
            st.success(f"기준 학교\n\n{school_label(st.session_state.base_school)}")

        st.divider()
        st.markdown("### 🔗 친구에게 공유하기")
        if APP_URL.strip():
            st.code(APP_URL.strip(), language=None)
            st.link_button("앱 열기", APP_URL.strip(), use_container_width=True)
        else:
            st.caption("배포 후 APP_URL에 Streamlit Cloud 주소를 입력하면 친구들과 바로 공유할 수 있어요.")


def main() -> None:
    apply_styles()
    init_state()
    render_sidebar()

    st.markdown(
        "<section class='hero'>"
        "<div class='hero-kicker'>SCHOOL LUNCH EXPLORER</div>"
        "<div class='hero-title'>우리 학교 급식 탐험대 🍱</div>"
        "<p class='hero-copy'>월간 식단부터 알레르기 정보, 다른 학교와의 열량 비교까지 한곳에서 확인해요.</p>"
        "</section>",
        unsafe_allow_html=True,
    )

    base_school = st.session_state.base_school
    if not base_school:
        st.info("왼쪽에서 학교를 검색하고 기준 학교를 먼저 선택해 주세요.")
        st.markdown(
            "<div class='soft-card'><b>사용 순서</b><br><br>"
            "① 학교명 검색 → ② 지역을 확인해 기준 학교 선택 → "
            "③ 급식 달력·상세 정보·학교 비교 이용</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"<div class='school-banner'>🏫 <div>현재 기준 학교<br>"
        f"<strong>{html.escape(school_label(base_school))}</strong></div></div>",
        unsafe_allow_html=True,
    )

    active_page = st.radio(
        "화면 선택",
        PAGE_OPTIONS,
        horizontal=True,
        key="active_page",
        label_visibility="collapsed",
    )

    if active_page == PAGE_CALENDAR:
        render_month_calendar(base_school)
    elif active_page == PAGE_DETAIL:
        render_detail_page(base_school)
    else:
        render_comparison_page(base_school)


if __name__ == "__main__":
    main()
