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
            min-height: 220px; padding: .75rem; border-radius: 15px;
            background: rgba(242, 245, 249, .78); color: #a0a9b8;
        }
        .day-number { font-size: .82rem; font-weight: 850; color: var(--muted); margin-bottom: .5rem; }
        .today-dot {
            display: inline-block; margin-left: .3rem; padding: .1rem .4rem;
            border-radius: 999px; background: var(--brand-soft); color: var(--brand);
            font-size: .63rem; vertical-align: middle;
        }
        .meal-title { font-weight: 850; color: var(--ink); line-height: 1.35; margin-bottom: .34rem; }
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
        .legend { color: var(--muted); font-size: .8rem; margin: -.25rem 0 .85rem; }
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
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255,255,255,.96); border-radius: 16px;
            box-shadow: 0 6px 22px rgba(34, 46, 77, .05);
        }
        @media (max-width: 780px) {
            .block-container { padding: 1.2rem .85rem 3rem; }
            .hero { padding: 1.2rem; border-radius: 19px; }
            .hero-title { font-size: 1.75rem; }
            .calendar-empty { min-height: 110px; }
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
    try:
        response = requests.get(
            SCHOOL_API_URL,
            params={"Type": "json", "SCHUL_NM": query, "pSize": 5},
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
    params = {
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": office_code,
        "SD_SCHUL_CODE": school_code,
        "MMEAL_SC_CODE": "2",
        "MLSV_FROM_YMD": ymd,
        "MLSV_TO_YMD": ymd,
        "pSize": 1,
        "pIndex": 1,
    }
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
            f"<h2 style='text-align:center;margin:.2rem 0'>{anchor.year}년 {anchor.month}월</h2>",
            unsafe_allow_html=True,
        )
    with nav_right:
        st.button("다음 달 →", use_container_width=True, on_click=change_calendar_month, args=(1,))

    st.markdown(
        "<div class='legend'>열량 수준: 🟢 900 kcal 미만 · 🟠 900~1099 kcal · 🔴 1100 kcal 이상 &nbsp; "
        "※ 빠른 구분용 표시이며 개인의 건강·섭취 판단 기준은 아닙니다.</div>",
        unsafe_allow_html=True,
    )

    start_date, end_date = month_bounds(anchor)
    with st.spinner(f"{anchor.month}월 급식을 날짜별로 확인하고 있어요…"):
        meals, error_count = get_meals_for_period(school, start_date, end_date)

    if error_count:
        st.warning(f"일부 날짜({error_count}일)의 정보를 불러오지 못했어요. 잠시 후 다시 열면 채워질 수 있어요.")

    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    header_columns = st.columns(7)
    for column, name in zip(header_columns, weekday_names):
        column.markdown(
            f"<div style='text-align:center;font-weight:850;color:#657086;padding:.25rem'>{name}</div>",
            unsafe_allow_html=True,
        )

    month_calendar = calendar.Calendar(firstweekday=0).monthdatescalendar(anchor.year, anchor.month)
    for week_index, week in enumerate(month_calendar):
        columns = st.columns(7, gap="small")
        for column, day in zip(columns, week):
            with column:
                if day.month != anchor.month:
                    st.markdown("<div class='calendar-empty'></div>", unsafe_allow_html=True)
                    continue

                with st.container(height=238, border=True):
                    today_badge = "<span class='today-dot'>오늘</span>" if day == TODAY_KST else ""
                    st.markdown(
                        f"<div class='day-number'>{day.day}{today_badge}</div>",
                        unsafe_allow_html=True,
                    )
                    meal = meals.get(day)
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
                        st.button(
                            "자세히",
                            key=f"meal_{anchor:%Y%m}_{week_index}_{day:%d}",
                            use_container_width=True,
                            on_click=select_meal_day,
                            args=(day,),
                        )
                    else:
                        st.markdown("<div class='no-meal'>급식 없음</div>", unsafe_allow_html=True)


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

    st.markdown("### 일자별 급식 칼로리")
    line_figure = px.line(
        data.sort_values("날짜"),
        x="날짜",
        y="칼로리",
        color="학교 식별",
        markers=True,
        labels={"학교 식별": "학교", "칼로리": "칼로리(kcal)"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    line_figure.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>날짜 %{x|%Y-%m-%d}<br>%{y:,.1f} kcal<extra></extra>"
    )
    line_figure.update_layout(
        height=470,
        hovermode="x unified",
        legend_title_text="학교",
        margin=dict(l=10, r=10, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    line_figure.update_xaxes(showgrid=False)
    line_figure.update_yaxes(gridcolor="#e8edf4")
    st.plotly_chart(line_figure, use_container_width=True)

    st.markdown("### 학교별 평균 칼로리")
    bar_figure = px.bar(
        summary.sort_values("평균 칼로리"),
        x="평균 칼로리",
        y="학교",
        orientation="h",
        text="평균 칼로리",
        color="평균 칼로리",
        color_continuous_scale=["#68cbb1", "#7e87fb", "#ef8a70"],
        labels={"평균 칼로리": "평균 칼로리(kcal)"},
    )
    bar_figure.update_traces(
        texttemplate="%{text:,.1f} kcal",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>평균 %{x:,.1f} kcal<extra></extra>",
    )
    bar_figure.update_layout(
        height=max(340, 80 * len(summary)),
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=10, r=70, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    bar_figure.update_xaxes(gridcolor="#e8edf4")
    bar_figure.update_yaxes(title=None)
    st.plotly_chart(bar_figure, use_container_width=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🏫 기준 학교 찾기")
        st.caption("학교 이름과 지역을 확인한 뒤 선택하세요.")
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
