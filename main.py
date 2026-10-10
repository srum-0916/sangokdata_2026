"""뇌졸중 예측 실습실 · 데이터 소개.

실행: streamlit run main.py
페이지: pages/1_탐색.py
설치: pip install -r requirements.txt
"""

import pandas as pd
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
EXPECTED_COLUMNS = [
    "id", "gender", "age", "hypertension", "heart_disease",
    "ever_married", "work_type", "Residence_type", "avg_glucose_level",
    "bmi", "smoking_status", "stroke",
]

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 각 페이지에서 같은 UI가 보이도록 스타일을 독립적으로 포함한다.
st.markdown(
    r"""<style>
:root {
  --ink: #eaf5ff;
  --muted: #8fa6bc;
  --mint: #29e8cf;
  --lilac: #ad9bff;
  --pink: #ff7899;
  --line: rgba(168, 201, 232, .13);
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: "Pretendard", "Inter", "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}
.stApp {
  background:
    radial-gradient(ellipse 70% 42% at 85% -7%, rgba(39, 228, 206, .11) 0%, transparent 75%),
    radial-gradient(ellipse 55% 36% at -14% 48%, rgba(136, 117, 252, .08) 0%, transparent 80%),
    #07111f;
  color: #eaf5ff;
}
[data-testid="stHeader"] {background: rgba(7,17,31,.75) !important; backdrop-filter: blur(10px)}
.main .block-container, [data-testid="stMainBlockContainer"] {
  max-width: 1320px;
  padding-top: 2.0rem;
  padding-bottom: 5rem;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0c1a2a 0%, #091321 100%);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {border-radius: 11px;}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {background: rgba(41,232,207,.08);}
#MainMenu, footer {visibility:hidden;}
/* Navigation / brand */
.brand {display:flex; align-items:center; gap:11px; margin:0 0 24px;}
.brand-mark {height:39px; width:39px; display:grid; place-items:center; border:1px solid rgba(41,232,207,.47); border-radius:13px; color:var(--mint); background:rgba(41,232,207,.08); font-size:21px;}
.brand-name {font-weight:900; font-size:15px; letter-spacing:.13em; color:white;}
.brand-small {font-size:10px; letter-spacing:.22em; color:#83a3b4; margin-top:2px;}
.side-kicker {font-size:10px; font-weight:800; letter-spacing:.17em; color:var(--mint); margin:10px 0 8px;}
.side-line {font-size:12px; color:#8ca5ba; line-height:1.9;}
/* Rich hero */
.lab-hero {
  position:relative; overflow:hidden;
  padding:40px 46px 38px;
  border:1px solid rgba(71,234,215,.21);
  border-radius:27px;
  background:
    radial-gradient(circle at 90% 50%, rgba(64,248,223,.17), transparent 32%),
    radial-gradient(circle at 44% -100%, rgba(158,132,255,.14), transparent 70%),
    linear-gradient(118deg, #101f33, #0a2032 58%, #092a34);
  box-shadow: 0 18px 70px rgba(0,0,0,.24), inset 0 1px rgba(255,255,255,.045);
  margin-bottom:32px;
}
.lab-hero:before {
  content:""; pointer-events:none; position:absolute; inset:0;
  opacity:.14;
  background-image: linear-gradient(rgba(142,223,230,.25) 1px, transparent 1px), linear-gradient(90deg, rgba(142,223,230,.25) 1px, transparent 1px);
  background-size:32px 32px;
  mask-image:linear-gradient(to left,#000,transparent 70%);
}
.lab-hero:after {
  content:""; position:absolute; pointer-events:none;
  width:225px; height:225px; border-radius:50%; right:7%; top:50%; transform:translateY(-50%);
  border:1px solid rgba(69,243,221,.23);
  box-shadow:0 0 0 27px rgba(41,232,207,.04),0 0 0 55px rgba(41,232,207,.025),0 0 80px rgba(41,232,207,.11);
}
.lab-hero > * {position:relative; z-index:1;}
.hero-eyebrow {display:flex;align-items:center;gap:10px;color:#8aefdf;font-weight:800;letter-spacing:.18em;font-size:11px;margin-bottom:16px;}
.live-dot {width:7px;height:7px;display:inline-block;border-radius:50%;background:var(--mint);box-shadow:0 0 10px var(--mint);animation:livepulse 2.5s ease-in-out infinite;}
@keyframes livepulse {0%,100%{opacity:1}50%{opacity:.35}}
.lab-hero h1 {font-size:clamp(2rem,4.4vw,3.55rem);letter-spacing:-.07em;font-weight:900;margin:0 0 14px;line-height:1.24;color:#fff;}
