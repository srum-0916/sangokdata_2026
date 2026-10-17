"""💝 두근두근 연구소 · 내가 만든 모델 소개.

이 페이지는 데이터를 읽거나 외부로 전송하지 않습니다.
사용자가 입력한 내용은 현재 Streamlit 세션 안에서만 화면에 표시합니다.
"""

import html

import pandas as pd
import streamlit as st


QUESTIONS = [
    ("무슨 데이터입니까", "사용한 데이터의 내용과 대상을 소개해 줘~! 🍓"),
    ("무엇을 보고 맞힙니까", "모델이 참고한 속성들을 적어 줘~! 🔍"),
    ("무엇을 고쳤습니까", "전처리에서 바꾼 점을 적어 줘~! 🫧"),
    ("이 모델을 검진센터가 사용해도 됩니까", "성능과 한계를 고려해 이유를 적어 줘~! 🏥"),
    ("이 모델이 못 하는 것 한 가지", "이 모델로는 알 수 없는 것을 한 가지 적어 줘~! 🌷"),
]
METRICS = ["정확도", "재현율", "F1", "찾아낸 환자", "헛짚은 사람"]
NAV_ITEMS = [
    ("main.py", "🏠 데이터 소개"),
    ("pages/1_탐색.py", "🔎 탐색 놀이터"),
    ("pages/2_분류_모델.py", "🧸 분류 모델 연구실"),
    ("pages/3_채점표.py", "💌 채점표 연구실"),
    ("pages/4_전처리.py", "🫧 전처리 실험실"),
    ("pages/5_내가_만든_모델_소개.py", "💝 내 모델 소개"),
]

st.set_page_config(
    page_title="내가 만든 모델 소개 💝 | 두근두근 연구소",
    page_icon="💝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
[data-testid="stSidebarNav"] {display:none!important}
[data-testid="stAppViewContainer"] {
  background:radial-gradient(circle at 8% 5%, #ffe4ee 0, transparent 31%),
             radial-gradient(circle at 88% 11%, #eee4ff 0, transparent 34%),
             radial-gradient(circle at 70% 93%, #e0fff4 0, transparent 35%), #fffafd!important;
}
[data-testid="stSidebar"] {background:linear-gradient(160deg,#ffeff7,#f1edff 63%,#edfff7)!important;border-right:2px solid white!important}
[data-testid="stSidebar"] p {color:#725d85!important}
[data-testid="stMainBlockContainer"] {max-width:1120px;padding-top:1.7rem;padding-bottom:5rem}
h1,h2,h3 {color:#665078!important;letter-spacing:-.035em!important}
[data-testid="stPageLink"] a {
  background:rgba(255,255,255,.78)!important;border:1.5px solid #f1d8e9!important;
  border-radius:15px!important;margin:3px 0!important;padding:7px 10px!important;
  transition:transform .18s, background .18s!important
}
[data-testid="stPageLink"] a:hover {background:#fff!important;transform:translateX(3px)!important}
[data-testid="stTextArea"] textarea, [data-testid="stDataEditor"] {
  border:2px solid #f4d9e9!important;border-radius:17px!important;
  background:white!important;box-shadow:0 5px 16px rgba(183,120,166,.07)!important
}
[data-testid="stTabs"] button {font-weight:800!important;color:#7c6496!important}
[data-testid="stTabs"] button[aria-selected="true"] {color:#df699f!important}
.sweet-hero {
  padding:34px 38px;border-radius:30px;background:linear-gradient(108deg,#ffd7e8,#eee0ff 72%,#dffbf0);
  border:3px solid #fff;box-shadow:0 9px 0 #f9e2ed;margin-bottom:35px;position:relative;overflow:hidden
}
.sweet-tag {color:#a36f9d;font-size:12px;letter-spacing:.08em;font-weight:900}
.sweet-hero h1 {font-size:clamp(2rem,4vw,3.1rem)!important;margin:13px 0 10px!important}
.sweet-hero p {color:#856e94;font-size:14px;font-weight:700;line-height:1.85}
.sweet-card {background:#fff;border:2px solid #f5e0ef;border-radius:22px;
  box-shadow:0 6px 0 #fbeaf2;padding:19px 22px;margin:13px 0 24px}
.sweet-card h3 {margin:0 0 9px!important;color:#745b8a!important}
.sweet-card p {color:#8c789d;line-height:1.8;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}
.sweet-note {padding:13px 16px;border-radius:17px;background:#fff5d9;
  color:#927846;font-weight:700;margin:16px 0}
.sweet-brand {font-size:20px;font-weight:900;color:#765b91;margin-bottom:6px}
.sweet-sub {color:#a88eaa;font-size:12px;line-height:1.8;margin-bottom:17px}
.sweet-footer {text-align:center;color:#ad92ac;font-size:12px;padding-top:35px}
@media(max-width:750px) {.sweet-hero{padding:25px 22px}}
</style>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="sweet-brand">🌷 두근두근 연구소 💗</div>', unsafe_allow_html=True)
    st.markdown('<div class="sweet-sub">SWEET DATA LAB ♡<br>만든 모델을 글로 정리하는 마지막 연구 노트야~! 🎀</div>', unsafe_allow_html=True)
    st.markdown("### 🎨 연구실 이동하기 💗")
    for path, label in NAV_ITEMS:
        st.page_link(path, label=label, use_container_width=True)
    st.divider()
    st.caption("🧸 이 페이지는 CSV를 읽지 않아! 적은 내용은 파일로 저장하거나 전송하지 않아. 💌")

st.markdown(
    '<div class="sweet-hero"><div class="sweet-tag">💌 FINAL REPORT · SWEET DATA LAB</div>'
    '<h1>💝 내가 만든 모델 소개 ♡</h1>'
    '<p>내가 직접 만든 AI 모델을 예쁘게 소개해 보자아~! 🎀<br>'
    '앞 페이지에서 살펴본 결과를 손으로 옮겨 적고, 한 장으로 모아서 확인할 수 있어. ✨</p></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sweet-note">🍯 여기는 데이터 분석을 다시 하지 않는 작성 공간이야! '
    '탭을 바꿔도 지금 세션에서 적은 글을 모아 볼 수 있어. '
    '새로 접속하거나 세션이 종료되면 입력 내용이 사라질 수 있어. 💗</div>',
    unsafe_allow_html=True,
)

entry_tab, report_tab = st.tabs(["✏️ 채워 넣기 💗", "📜 한 장으로 모아 보기 💌"])

with entry_tab:
    st.subheader("🌷 내 모델 이야기 다섯 가지")
    st.caption("각 질문 아래 여러 줄로 자유롭게 적어 줘~! 아직 몰라도 빈칸으로 두면 돼. 🧸")
    for index, (question, hint) in enumerate(QUESTIONS, start=1):
        st.text_area(
            f"{index}. {question} 💕",
            key=f"model_intro_answer_{index}",
            height=105,
            placeholder=hint,
        )

    st.divider()
    st.subheader("🍰 고치기 전과 고친 뒤 성적표")
    st.caption("전처리·채점표 페이지에서 확인한 숫자를 직접 옮겨 적어 줘~! 자동 입력은 하지 않아. 💞")
    if "model_intro_metric_rows" not in st.session_state:
        st.session_state["model_intro_metric_rows"] = pd.DataFrame({
            "지표": METRICS,
            "고치기 전": [""] * len(METRICS),
            "고친 뒤": [""] * len(METRICS),
        })
    edited_metrics = st.data_editor(
        st.session_state["model_intro_metric_rows"],
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["지표"],
        column_config={
            "지표": st.column_config.TextColumn("지표 💗"),
            "고치기 전": st.column_config.TextColumn("고치기 전 🍓"),
            "고친 뒤": st.column_config.TextColumn("고친 뒤 🫧"),
        },
        key="model_intro_metric_editor",
    )

with report_tab:
    st.subheader("💝 나의 모델 소개 · 한 장 모아 보기")
    st.caption("내가 적은 다섯 가지 이야기와 성적표를 순서대로 모았어~! 🌸")
    for index, (question, _) in enumerate(QUESTIONS, start=1):
        answer = st.session_state.get(f"model_intro_answer_{index}", "")
        shown = html.escape(answer.strip()) if isinstance(answer, str) and answer.strip() else "아직 적지 않았어요 💌"
        st.markdown(
            f'<div class="sweet-card"><h3>{index}. {html.escape(question)} 💗</h3>'
            f'<p>{shown}</p></div>',
            unsafe_allow_html=True,
        )
    st.subheader("📋 고치기 전 · 고친 뒤 비교표 💕")
    preview = edited_metrics.copy()
    for col in ("고치기 전", "고친 뒤"):
        preview[col] = preview[col].apply(
            lambda value: "적지 않았어요 💌" if pd.isna(value) or not str(value).strip() else str(value)
        )
    st.table(preview.set_index("지표"))
    st.info("🌼 이 한 장은 화면에서만 볼 수 있어. 따로 저장하거나 어디로 보내지 않아~! 💗")

st.markdown('<div class="sweet-footer">🎀 두근두근 연구소 ♡ 나만의 연구 이야기를 완성해 보자아~! 💕</div>', unsafe_allow_html=True)
