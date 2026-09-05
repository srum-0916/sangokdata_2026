import colorsys
import html
import random
import re
import textwrap
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import pytz
import requests
import streamlit as st


# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="BoxOffice Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. DESIGN SYSTEM + MOTION
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --bg: #F4F7FB;
        --surface: #FFFFFF;
        --surface-soft: #F8FAFC;
        --text: #0F172A;
        --text-sub: #64748B;
        --line: #E5EAF1;
        --blue: #3182F6;
        --blue-2: #6EA8FF;
        --purple: #8B5CF6;
        --red: #EF4444;
        --green: #10B981;
        --gold: #F5B700;
        --shadow: 0 16px 44px rgba(15, 23, 42, 0.07);
    }

    @keyframes heroFloatA {
        0%, 100% { transform: translate3d(0,0,0) scale(1); }
        50% { transform: translate3d(-34px,20px,0) scale(1.08); }
    }

    @keyframes heroFloatB {
        0%, 100% { transform: translate3d(0,0,0) scale(1); }
        50% { transform: translate3d(30px,-16px,0) scale(.94); }
    }

    @keyframes beamSweep {
        0% { transform: translateX(-160%) rotate(12deg); opacity: 0; }
        16% { opacity: .58; }
        58% { opacity: .18; }
        100% { transform: translateX(230%) rotate(12deg); opacity: 0; }
    }

    @keyframes livePulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(105,169,255,.42); }
        50% { box-shadow: 0 0 0 10px rgba(105,169,255,0); }
    }

    @keyframes fadeRise {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes borderFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes softGlow {
        0%, 100% {
            box-shadow: 0 17px 45px rgba(15,23,42,.08), 0 0 0 rgba(49,130,246,0);
        }
        50% {
            box-shadow: 0 25px 62px rgba(15,23,42,.10), 0 0 36px rgba(49,130,246,.10);
        }
    }

    @keyframes tickerMove {
        from { transform: translateX(0); }
        to { transform: translateX(-50%); }
    }

    /* ---------- APP ---------- */
    .stApp {
        background:
            radial-gradient(circle at 8% -10%, rgba(49,130,246,.10), transparent 28%),
            radial-gradient(circle at 98% 2%, rgba(139,92,246,.07), transparent 24%),
            var(--bg);
    }

    [data-testid="stHeader"] {
        background: rgba(244,247,251,.70);
        backdrop-filter: blur(16px);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1280px;
        padding-top: 1.8rem;
        padding-bottom: 5rem;
    }

    [data-testid="stSidebar"] {
        background: rgba(255,255,255,.94);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.4rem;
    }

    html, body, [class*="css"] {
        font-family:
            Pretendard, -apple-system, BlinkMacSystemFont,
            "Segoe UI", "Noto Sans KR", sans-serif;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    /* ---------- SIDEBAR ---------- */
    .sidebar-brand {
        padding: .25rem 0 1.25rem;
    }

    .sidebar-logo {
        color: var(--text);
        font-size: 1.35rem;
        font-weight: 950;
        letter-spacing: -.045em;
    }

    .sidebar-desc {
        color: #7B8798;
        font-size: .82rem;
        line-height: 1.65;
        margin-top: .38rem;
    }

    .sidebar-card {
        margin-top: .8rem;
        padding: 1rem;
        border-radius: 18px;
        background:
            radial-gradient(circle at 100% 0%, rgba(49,130,246,.10), transparent 38%),
            linear-gradient(135deg, #F9FBFF, #EDF5FF);
        border: 1px solid #DCE9FB;
    }

    .sidebar-card-label {
        color: #7E9DC8;
        font-size: .68rem;
        font-weight: 950;
        letter-spacing: .08em;
    }

    .sidebar-card-value {
        margin-top: .18rem;
        color: #1759B3;
        font-size: 1rem;
        font-weight: 900;
    }

    /* ---------- HERO ---------- */
    .hero {
        position: relative;
        isolation: isolate;
        overflow: hidden;
        min-height: 340px;
        display: flex;
        align-items: center;
        padding: 2.55rem 2.6rem;
        border-radius: 30px;
        color: white;
        background:
            radial-gradient(circle at 84% 18%, rgba(67,146,255,.30), transparent 27%),
            radial-gradient(circle at 68% 116%, rgba(132,76,255,.28), transparent 34%),
            linear-gradient(135deg, #09111F 0%, #10203C 50%, #123F79 100%);
        box-shadow: 0 30px 70px rgba(22,50,92,.24);
        transition:
            transform .35s cubic-bezier(.2,.8,.2,1),
            box-shadow .35s cubic-bezier(.2,.8,.2,1);
    }

    .hero:hover {
        transform: translateY(-4px);
        box-shadow: 0 39px 88px rgba(22,50,92,.31);
    }

    .hero-content {
        position: relative;
        z-index: 8;
        width: 100%;
        animation: fadeRise .7s ease both;
    }

    .hero-grid {
        position: absolute;
        inset: 0;
        z-index: 1;
        pointer-events: none;
        opacity: .22;
        background-image:
            linear-gradient(rgba(255,255,255,.052) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.052) 1px, transparent 1px);
        background-size: 38px 38px;
        mask-image: linear-gradient(to bottom, rgba(0,0,0,.75), transparent 95%);
    }

    .hero-orb {
        position: absolute;
        border-radius: 999px;
        z-index: 2;
        pointer-events: none;
        mix-blend-mode: screen;
        filter: blur(7px);
    }

    .hero-orb.a {
        width: 350px;
        height: 350px;
        top: -125px;
        right: -65px;
        background: radial-gradient(circle, rgba(60,146,255,.62), rgba(60,146,255,0) 70%);
        animation: heroFloatA 7s ease-in-out infinite;
    }

    .hero-orb.b {
        width: 320px;
        height: 320px;
        right: 18%;
        bottom: -200px;
        background: radial-gradient(circle, rgba(146,82,255,.47), rgba(146,82,255,0) 70%);
        animation: heroFloatB 8.5s ease-in-out infinite;
    }

    .hero-beam {
        position: absolute;
        z-index: 3;
        width: 190px;
        height: 165%;
        top: -32%;
        left: 0;
        pointer-events: none;
        filter: blur(5px);
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255,255,255,.03) 24%,
            rgba(255,255,255,.22) 50%,
            rgba(255,255,255,.03) 76%,
            transparent 100%
        );
        animation: beamSweep 6.8s ease-in-out infinite;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: .48rem;
        padding: .46rem .72rem;
        border-radius: 999px;
        color: #CDE1FF;
        background: rgba(255,255,255,.09);
        border: 1px solid rgba(255,255,255,.11);
        backdrop-filter: blur(12px);
        font-size: .72rem;
        font-weight: 900;
        letter-spacing: .07em;
    }

    .hero-kicker::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #70AFFF;
        animation: livePulse 1.8s ease-in-out infinite;
    }

    .hero-title {
        margin-top: 1rem;
        color: white;
        font-size: clamp(2.25rem, 4.25vw, 4.2rem);
        line-height: 1.01;
        font-weight: 950;
        letter-spacing: -.067em;
        max-width: 920px;
    }

    .hero-sub {
        color: #BFD0E9;
        font-size: .98rem;
        line-height: 1.72;
        max-width: 760px;
        margin-top: .68rem;
    }

    .hero-date {
        display: inline-block;
        color: white;
        font-size: .82rem;
        font-weight: 850;
        margin-top: 1rem;
    }

    .hero-mini-stats {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin-top: 1.25rem;
    }

    .hero-chip {
        display: inline-flex;
        align-items: center;
        padding: .45rem .66rem;
        border-radius: 999px;
        color: rgba(255,255,255,.92);
        background: rgba(255,255,255,.08);
        border: 1px solid rgba(255,255,255,.11);
        backdrop-filter: blur(14px);
        font-size: .72rem;
        font-weight: 820;
        transition:
            transform .2s ease,
            background .2s ease,
            border-color .2s ease;
    }

    .hero-chip:hover {
        transform: translateY(-2px) scale(1.025);
        background: rgba(255,255,255,.14);
        border-color: rgba(255,255,255,.20);
    }

    /* ---------- TICKER ---------- */
    .ticker-shell {
        position: relative;
        overflow: hidden;
        margin-top: .9rem;
        border-radius: 16px;
        background: rgba(255,255,255,.78);
        border: 1px solid #E3EAF4;
        backdrop-filter: blur(14px);
        box-shadow: 0 10px 26px rgba(15,23,42,.04);
    }

    .ticker-shell::before,
    .ticker-shell::after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        width: 70px;
        z-index: 3;
        pointer-events: none;
    }

    .ticker-shell::before {
        left: 0;
        background: linear-gradient(90deg, #F7F9FC, transparent);
    }

    .ticker-shell::after {
        right: 0;
        background: linear-gradient(-90deg, #F7F9FC, transparent);
    }

    .ticker-track {
        display: flex;
        width: max-content;
        animation: tickerMove 24s linear infinite;
    }

    .ticker-shell:hover .ticker-track {
        animation-play-state: paused;
    }

    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: .55rem;
        padding: .8rem 1.05rem;
        color: #4B5B71;
        font-size: .75rem;
        font-weight: 800;
        white-space: nowrap;
    }

    .ticker-rank {
        color: var(--blue);
        font-weight: 950;
    }

    .ticker-dot {
        width: 4px;
        height: 4px;
        border-radius: 999px;
        background: #C7D2E0;
    }

    /* ---------- SECTION ---------- */
    .section-head {
        margin: 2.4rem 0 1rem;
        animation: fadeRise .55s ease both;
    }

    .section-eyebrow {
        color: var(--blue);
        font-size: .70rem;
        font-weight: 950;
        letter-spacing: .09em;
        text-transform: uppercase;
    }

    .section-title {
        color: var(--text);
        font-size: 1.48rem;
        font-weight: 950;
        letter-spacing: -.04em;
        margin-top: .18rem;
    }

    .section-caption {
        color: #8090A4;
        font-size: .79rem;
        margin-top: .28rem;
    }

    /* ---------- KPI ---------- */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0,1fr));
        gap: .9rem;
        margin-top: 1rem;
        animation: fadeRise .6s ease both;
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
        padding: 1.18rem 1.22rem;
        border-radius: 20px;
        background: rgba(255,255,255,.94);
        border: 1px solid #E3EAF2;
        box-shadow: 0 10px 30px rgba(15,23,42,.04);
        transition:
            transform .24s cubic-bezier(.2,.8,.2,1),
            box-shadow .24s ease,
            border-color .24s ease;
    }

    .kpi-card::after {
        content: "";
        position: absolute;
        width: 95px;
        height: 240%;
        left: -135px;
        top: -70%;
        transform: rotate(17deg);
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,.85),
            transparent
        );
        opacity: 0;
        transition: left .6s ease, opacity .15s ease;
        pointer-events: none;
    }

    .kpi-card:hover {
        transform: translateY(-7px);
        border-color: #C6DCFF;
        box-shadow: 0 23px 54px rgba(49,130,246,.11);
    }

    .kpi-card:hover::after {
        left: 120%;
        opacity: .64;
    }

    .kpi-label {
        color: #718096;
        font-size: .74rem;
        font-weight: 800;
    }

    .kpi-value {
        color: var(--text);
        font-size: 1.55rem;
        font-weight: 950;
        letter-spacing: -.045em;
        margin-top: .45rem;
    }

    .kpi-note {
        color: #9BA7B6;
        font-size: .68rem;
        margin-top: .22rem;
    }

    /* ---------- PODIUM ---------- */
    .podium-card {
        position: relative;
        overflow: hidden;
        height: 100%;
        padding: 1.25rem;
        border-radius: 24px;
        background: rgba(255,255,255,.97);
        border: 1px solid #E4EAF2;
        box-shadow: var(--shadow);
        transition:
            transform .26s cubic-bezier(.2,.8,.2,1),
            box-shadow .26s ease,
            border-color .26s ease;
    }

    .podium-card::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
            120deg,
            transparent 28%,
            rgba(255,255,255,0) 41%,
            rgba(255,255,255,.66) 50%,
            rgba(255,255,255,0) 59%,
            transparent 72%
        );
        transform: translateX(-125%);
        transition: transform .8s cubic-bezier(.2,.8,.2,1);
        pointer-events: none;
    }

    .podium-card:hover {
        transform: translateY(-9px) scale(1.012);
        border-color: #BFD7FF;
        box-shadow: 0 28px 64px rgba(34,83,150,.14);
    }

    .podium-card:hover::after {
        transform: translateX(125%);
    }

    .podium-card.first {
        background:
            radial-gradient(circle at 92% 0%, rgba(49,130,246,.13), transparent 36%),
            linear-gradient(180deg, #FFFFFF, #F8FBFF);
        border-color: #CFE0FF;
        animation: softGlow 4.8s ease-in-out infinite;
    }

    .rank-chip {
        display: inline-flex;
        width: 40px;
        height: 40px;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        background: #EEF4FF;
        color: #2D6FD1;
        font-size: 1rem;
        font-weight: 950;
        margin-bottom: .85rem;
    }

    .rank-chip.gold {
        background: #FFF5D4;
        color: #A36C00;
    }

    .podium-name {
        min-height: 3rem;
        color: #182236;
        font-size: 1.12rem;
        line-height: 1.35;
        font-weight: 950;
        letter-spacing: -.035em;
    }

    .podium-meta {
        color: #8996A7;
        font-size: .70rem;
        margin-top: .35rem;
    }

    .podium-number {
        color: #172033;
        font-size: 1.48rem;
        font-weight: 950;
        letter-spacing: -.04em;
        margin-top: 1rem;
    }

    .podium-label {
        color: #9AA6B5;
        font-size: .68rem;
        margin-top: .12rem;
    }

    /* ---------- INTERACTIVE PANEL ---------- */
    .interactive-shell {
        position: relative;
        border-radius: 27px;
        padding: 1px;
        margin: .4rem 0 .95rem;
        background: linear-gradient(
            115deg,
            #3182F6,
            #8B5CF6,
            #27C2FF,
            #3182F6
        );
        background-size: 300% 300%;
        animation: borderFlow 8s ease infinite;
        box-shadow: 0 20px 55px rgba(33,79,145,.10);
    }

    .interactive-inner {
        border-radius: 26px;
        padding: 1.12rem 1.15rem;
        background:
            radial-gradient(circle at 93% 0%, rgba(49,130,246,.08), transparent 30%),
            rgba(255,255,255,.985);
    }

    .panel-kicker {
        display: flex;
        align-items: center;
        gap: .45rem;
        color: #3182F6;
        font-size: .68rem;
        font-weight: 950;
        letter-spacing: .09em;
    }

    .panel-kicker::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #3182F6;
        box-shadow: 0 0 0 5px rgba(49,130,246,.09);
    }

    .panel-title {
        color: #111827;
        font-size: 1.14rem;
        font-weight: 950;
        letter-spacing: -.035em;
        margin-top: .25rem;
    }

    .panel-sub {
        color: #8391A4;
        font-size: .73rem;
        margin-top: .18rem;
    }

    /* ---------- FOCUS ---------- */
    .focus-card {
        position: relative;
        overflow: hidden;
        min-height: 250px;
        padding: 1.4rem;
        border-radius: 24px;
        color: white;
        background:
            radial-gradient(circle at 88% 5%, rgba(106,173,255,.34), transparent 30%),
            radial-gradient(circle at 0% 112%, rgba(139,92,246,.30), transparent 40%),
            linear-gradient(145deg, #101A2F 0%, #162D54 56%, #174D8E 100%);
        box-shadow: 0 23px 58px rgba(18,49,92,.21);
        transition: transform .25s ease, box-shadow .25s ease;
    }

    .focus-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 31px 72px rgba(18,49,92,.29);
    }

    .focus-rank {
        display: inline-flex;
        padding: .36rem .58rem;
        border-radius: 10px;
        color: #CFE2FF;
        background: rgba(255,255,255,.10);
        border: 1px solid rgba(255,255,255,.10);
        font-size: .68rem;
        font-weight: 900;
    }

    .focus-title {
        color: white;
        font-size: 1.55rem;
        line-height: 1.24;
        font-weight: 950;
        letter-spacing: -.045em;
        margin-top: .9rem;
    }

    .focus-meta {
        color: #AFC5E3;
        font-size: .70rem;
        margin-top: .36rem;
    }

    .focus-number {
        color: white;
        font-size: 2rem;
        font-weight: 950;
        letter-spacing: -.055em;
        margin-top: 1.1rem;
    }

    .focus-caption {
        color: #9DB6D9;
        font-size: .67rem;
    }

    .focus-track {
        width: 100%;
        height: 8px;
        overflow: hidden;
        border-radius: 999px;
        background: rgba(255,255,255,.10);
        margin-top: 1rem;
    }

    .focus-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #67A8FF, #9B7BFF);
        box-shadow: 0 0 18px rgba(104,168,255,.42);
        transition: width .7s cubic-bezier(.2,.8,.2,1);
    }

    .focus-track-label {
        display: flex;
        justify-content: space-between;
        gap: .5rem;
        color: #9DB6D9;
        font-size: .63rem;
        margin-top: .38rem;
    }

    /* ---------- DUEL ---------- */
    .duel-vs {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 54px;
        height: 54px;
        margin: .7rem auto 0;
        border-radius: 18px;
        color: white;
        background: linear-gradient(135deg, #3182F6, #8B5CF6);
        box-shadow: 0 12px 28px rgba(80,93,220,.25);
        font-weight: 950;
        transform: rotate(-4deg);
        transition: transform .2s ease;
    }

    .duel-vs:hover {
        transform: rotate(4deg) scale(1.08);
    }

    .duel-result {
        margin-top: .58rem;
        padding: .84rem .92rem;
        border-radius: 15px;
        background: #F7FAFF;
        border: 1px solid #E0EAF9;
        color: #56667C;
        font-size: .74rem;
        line-height: 1.65;
    }

    .duel-result b {
        color: #1F65C8;
    }

    /* ---------- RANKING ---------- */
    .ranking-panel {
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        border: 1px solid #E3EAF3;
        background: rgba(255,255,255,.98);
        box-shadow: 0 17px 48px rgba(15,23,42,.07);
        animation: fadeRise .55s ease both;
    }

    .ranking-panel::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        z-index: 4;
        background: linear-gradient(90deg, #3182F6, #6EA8FF, #8B5CF6);
    }

    .ranking-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.1rem .88rem;
        border-bottom: 1px solid #EDF1F6;
        background: linear-gradient(180deg, #FFFFFF, #FBFCFE);
    }

    .ranking-toolbar-left {
        display: flex;
        align-items: center;
        gap: .55rem;
    }

    .ranking-live {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #3182F6;
        animation: livePulse 1.8s ease-in-out infinite;
    }

    .ranking-toolbar-title {
        color: #152033;
        font-size: .84rem;
        font-weight: 950;
    }

    .ranking-toolbar-meta {
        color: #8A98AA;
        font-size: .68rem;
        font-weight: 700;
    }

    .ranking-scroll {
        width: 100%;
        overflow-x: auto;
        scrollbar-width: thin;
        scrollbar-color: #CBD5E1 transparent;
    }

    .ranking-scroll::-webkit-scrollbar {
        height: 8px;
    }

    .ranking-scroll::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 999px;
    }

    .custom-table {
        width: 100%;
        min-width: 950px;
        border-collapse: separate;
        border-spacing: 0;
        background: white;
        font-variant-numeric: tabular-nums;
    }

    .custom-table thead th {
        position: sticky;
        top: 0;
        z-index: 2;
        padding: 13px 14px;
        color: #7B8798;
        background: rgba(248,250,252,.97);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #E7EDF4;
        font-size: .66rem;
        font-weight: 950;
        letter-spacing: .055em;
        text-transform: uppercase;
        text-align: center;
        white-space: nowrap;
    }

    .custom-table thead th.movie-head {
        text-align: left;
    }

    .custom-table tbody tr {
        transition: transform .15s ease, filter .15s ease;
    }

    .custom-table tbody tr:hover {
        transform: translateX(4px);
        filter: saturate(1.04);
    }

    .custom-table tbody td {
        padding: 15px 14px;
        color: #344156;
        background: white;
        border-bottom: 1px solid #EEF2F7;
        font-size: .80rem;
        text-align: center;
        white-space: nowrap;
        transition: background .15s ease;
    }

    .custom-table tbody tr:last-child td {
        border-bottom: none;
    }

    .custom-table tbody tr:hover td {
        background: #F8FBFF;
    }

    .custom-table tbody tr.rank-row-1 td {
        background: linear-gradient(90deg, rgba(49,130,246,.05), white 48%);
    }

    .custom-table tbody tr.rank-row-1 td:first-child {
        box-shadow: inset 4px 0 0 #3182F6;
    }

    .rank-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 11px;
        color: #64748B;
        background: #F1F5F9;
        font-weight: 950;
        transition: transform .18s ease, box-shadow .18s ease;
    }

    .custom-table tbody tr:hover .rank-number {
        transform: scale(1.1) rotate(-2deg);
        box-shadow: 0 7px 16px rgba(15,23,42,.10);
    }

    .rank-number.first {
        color: #1C67D7;
        background: linear-gradient(135deg, #E7F0FF, #DCEAFF);
        box-shadow: inset 0 0 0 1px #C8DDFF;
    }

    .rank-number.second {
        color: #5A6677;
        background: linear-gradient(135deg, #F3F5F8, #E9EDF2);
    }

    .rank-number.third {
        color: #B3662D;
        background: linear-gradient(135deg, #FFF0E6, #FFE3D1);
    }

    .trend-up,
    .trend-down,
    .trend-new,
    .trend-flat {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 47px;
        padding: .29rem .46rem;
        border-radius: 999px;
        font-size: .63rem;
        line-height: 1;
        font-weight: 950;
        border: 1px solid transparent;
    }

    .trend-up {
        color: #D93E47;
        background: #FFF1F2;
        border-color: #FFE0E3;
    }

    .trend-down {
        color: #246CC7;
        background: #EDF5FF;
        border-color: #DBEAFE;
    }

    .trend-new {
        color: #7443C9;
        background: #F5F0FF;
        border-color: #E9DDFF;
    }

    .trend-flat {
        color: #8D99AA;
        background: #F4F6F8;
        border-color: #E8ECF1;
    }

    .movie-cell {
        min-width: 285px;
        max-width: 390px;
        text-align: left !important;
    }

    .movie-line {
        display: flex;
        align-items: center;
        gap: .44rem;
        min-width: 0;
    }

    .movie-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        color: #172033;
        font-weight: 950;
        letter-spacing: -.02em;
    }

    .million-badge {
        display: inline-flex;
        flex: 0 0 auto;
        padding: .18rem .4rem;
        border-radius: 999px;
        color: #896200;
        background: linear-gradient(135deg, #FFF7D6, #FFF1B8);
        border: 1px solid #F4DE8F;
        font-size: .58rem;
        font-weight: 950;
    }

    .audience-cell {
        min-width: 150px;
        text-align: right !important;
    }

    .audience-value {
        display: flex;
        align-items: baseline;
        justify-content: flex-end;
        gap: .2rem;
        color: #1E293B;
        font-weight: 950;
    }

    .audience-unit {
        color: #97A3B2;
        font-size: .62rem;
    }

    .share-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: .42rem;
        margin-top: .38rem;
    }

    .share-track {
        width: 72px;
        height: 5px;
        overflow: hidden;
        border-radius: 999px;
        background: #EDF2F7;
    }

    .share-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #7EB1FF, #3182F6);
        transition: width .65s cubic-bezier(.2,.8,.2,1);
    }

    .share-label {
        min-width: 34px;
        text-align: right;
        color: #98A4B3;
        font-size: .58rem;
        font-weight: 800;
    }

    .num-cell {
        text-align: right !important;
        font-weight: 780;
    }

    .screen-pill {
        display: inline-flex;
        min-width: 58px;
        justify-content: center;
        padding: .26rem .43rem;
        border-radius: 9px;
        color: #59687A;
        background: #F5F7FA;
        border: 1px solid #E8EDF3;
        font-weight: 850;
    }

    .ranking-footer {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        padding: .75rem 1.1rem;
        color: #94A0B0;
        background: #FBFCFE;
        border-top: 1px solid #EEF2F6;
        font-size: .63rem;
        font-weight: 650;
    }

    /* ---------- NOTES ---------- */
    .soft-note {
        margin-top: 1rem;
        padding: .9rem 1rem;
        border-radius: 16px;
        color: #526F95;
        background: #EEF5FF;
        border: 1px solid #DCEAFF;
        font-size: .74rem;
        line-height: 1.65;
    }

    /* ---------- NATIVE STREAMLIT ---------- */
    div[data-baseweb="select"] > div,
    div[data-testid="stDateInput"] input {
        border-radius: 13px !important;
    }

    [data-testid="stMetric"] {
        border-radius: 18px !important;
        transition:
            transform .2s ease,
            box-shadow .2s ease,
            border-color .2s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: #CFE0FF !important;
        box-shadow: 0 16px 34px rgba(15,23,42,.08);
    }

    .stButton > button {
        border-radius: 14px !important;
        font-weight: 850 !important;
        transition:
            transform .18s ease,
            box-shadow .18s ease,
            border-color .18s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        border-color: #9EC4FF !important;
        box-shadow: 0 10px 24px rgba(49,130,246,.13);
    }

    [data-testid="stTextInput"] input {
        border-radius: 14px !important;
    }

    [data-testid="stTextInput"] input:focus {
        box-shadow: 0 0 0 4px rgba(49,130,246,.10) !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    [data-testid="stPlotlyChart"] {
        overflow: hidden;
        border-radius: 18px;
    }

    /* ---------- RESPONSIVE ---------- */
    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero {
            min-height: 320px;
            padding: 1.8rem 1.45rem;
            border-radius: 24px;
        }

        .kpi-grid {
            grid-template-columns: repeat(2, minmax(0,1fr));
        }
    }

    @media (max-width: 620px) {
        .hero-title {
            font-size: 2.18rem;
        }

        .kpi-grid {
            grid-template-columns: 1fr;
        }

        .ranking-toolbar,
        .ranking-footer {
            align-items: flex-start;
            flex-direction: column;
        }

        .custom-table {
            min-width: 860px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .001ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .001ms !important;
        }
    }
    
    /* =====================================================
       ALWAYS-ON CINEMA MOTION
       ===================================================== */
    @keyframes ambientGradientDrift {
        0%   { background-position: 0% 0%, 100% 0%, 0 0; }
        50%  { background-position: 12% 8%, 88% 10%, 0 0; }
        100% { background-position: 0% 0%, 100% 0%, 0 0; }
    }

    @keyframes heroPulseDepth {
        0%, 100% {
            filter: saturate(1) brightness(1);
            box-shadow: 0 30px 70px rgba(22,50,92,.24);
        }
        50% {
            filter: saturate(1.08) brightness(1.025);
            box-shadow:
                0 36px 86px rgba(22,50,92,.30),
                0 0 55px rgba(49,130,246,.10);
        }
    }

    @keyframes starDrift {
        0% {
            transform: translate3d(0,0,0);
            opacity: .25;
        }
        50% {
            transform: translate3d(-18px,10px,0);
            opacity: .55;
        }
        100% {
            transform: translate3d(-36px,20px,0);
            opacity: .25;
        }
    }

    @keyframes laserFly1 {
        0% {
            transform: translateX(-140%) rotate(-7deg);
            opacity: 0;
        }
        8% { opacity: .75; }
        28% { opacity: .12; }
        40%, 100% {
            transform: translateX(260%) rotate(-7deg);
            opacity: 0;
        }
    }

    @keyframes laserFly2 {
        0%, 38% {
            transform: translateX(230%) rotate(8deg);
            opacity: 0;
        }
        46% { opacity: .55; }
        68% { opacity: .10; }
        80%, 100% {
            transform: translateX(-170%) rotate(8deg);
            opacity: 0;
        }
    }

    @keyframes cardFloatA {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
    }

    @keyframes cardFloatB {
        0%, 100% { transform: translateY(-2px); }
        50% { transform: translateY(3px); }
    }

    @keyframes cardFloatC {
        0%, 100% { transform: translateY(2px); }
        50% { transform: translateY(-3px); }
    }

    @keyframes shineText {
        0% {
            background-position: 200% center;
        }
        100% {
            background-position: -200% center;
        }
    }

    @keyframes sectionScan {
        0% {
            transform: translateX(-140%);
            opacity: 0;
        }
        15% {
            opacity: .8;
        }
        45%, 100% {
            transform: translateX(320%);
            opacity: 0;
        }
    }

    @keyframes rankScan {
        0% {
            transform: translateY(-120%);
            opacity: 0;
        }
        10% { opacity: .25; }
        45% { opacity: .10; }
        55%, 100% {
            transform: translateY(850%);
            opacity: 0;
        }
    }

    @keyframes pulseRing {
        0% {
            box-shadow: 0 0 0 0 rgba(49,130,246,.28);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(49,130,246,0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(49,130,246,0);
        }
    }

    @keyframes tableTopGlow {
        0%, 100% { opacity: .55; }
        50% { opacity: 1; }
    }

    /* 전체 배경이 아주 천천히 흐름 */
    .stApp {
        background-size: 120% 120%, 120% 120%, auto;
        animation: ambientGradientDrift 13s ease-in-out infinite;
    }

    /* 히어로는 마우스 없어도 호흡 */
    .hero {
        animation:
            heroPulseDepth 5.5s ease-in-out infinite,
            fadeRise .7s ease both;
    }

    /* 히어로 별가루 레이어 */
    .hero::before {
        content: "";
        position: absolute;
        inset: -10%;
        z-index: 2;
        pointer-events: none;
        opacity: .36;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(255,255,255,.80) 0 1px, transparent 1.7px),
            radial-gradient(circle at 27% 72%, rgba(255,255,255,.55) 0 1px, transparent 1.8px),
            radial-gradient(circle at 45% 34%, rgba(159,205,255,.85) 0 1px, transparent 1.7px),
            radial-gradient(circle at 63% 62%, rgba(255,255,255,.65) 0 1px, transparent 1.6px),
            radial-gradient(circle at 78% 26%, rgba(186,213,255,.90) 0 1px, transparent 1.9px),
            radial-gradient(circle at 91% 76%, rgba(255,255,255,.60) 0 1px, transparent 1.8px);
        background-size:
            180px 180px,
            230px 230px,
            260px 260px,
            210px 210px,
            320px 320px,
            280px 280px;
        animation: starDrift 10s linear infinite;
    }

    /* 삐슝 레이저 1 */
    .hero::after {
        content: "";
        position: absolute;
        z-index: 5;
        top: 18%;
        left: 0;
        width: 45%;
        height: 2px;
        pointer-events: none;
        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(101,171,255,.20),
                rgba(180,220,255,.95),
                rgba(101,171,255,.35),
                transparent
            );
        box-shadow:
            0 0 10px rgba(85,160,255,.65),
            0 0 24px rgba(85,160,255,.25);
        animation: laserFly1 7.5s ease-in-out infinite;
    }

    /* 추가 레이저는 hero-grid의 pseudo */
    .hero-grid::after {
        content: "";
        position: absolute;
        z-index: 5;
        top: 68%;
        right: 0;
        width: 38%;
        height: 1px;
        pointer-events: none;
        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(176,116,255,.18),
                rgba(211,180,255,.82),
                rgba(176,116,255,.30),
                transparent
            );
        box-shadow:
            0 0 9px rgba(167,112,255,.55),
            0 0 20px rgba(167,112,255,.22);
        animation: laserFly2 9s ease-in-out infinite;
    }

    /* KPI도 손 안 대도 살짝 부유 */
    .kpi-card:nth-child(1) {
        animation: cardFloatA 4.8s ease-in-out infinite;
    }

    .kpi-card:nth-child(2) {
        animation: cardFloatB 5.4s ease-in-out infinite;
        animation-delay: -.8s;
    }

    .kpi-card:nth-child(3) {
        animation: cardFloatC 5.0s ease-in-out infinite;
        animation-delay: -1.5s;
    }

    .kpi-card:nth-child(4) {
        animation: cardFloatA 5.8s ease-in-out infinite;
        animation-delay: -2.2s;
    }

    /* KPI 숫자에 계속 은은한 하이라이트 */
    .kpi-value {
        background:
            linear-gradient(
                110deg,
                #0F172A 0%,
                #0F172A 35%,
                #4E93F9 47%,
                #8B5CF6 52%,
                #0F172A 65%,
                #0F172A 100%
            );
        background-size: 260% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shineText 6.5s linear infinite;
    }

    /* TOP 3 서로 다른 박자로 부유 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .podium-card {
        animation:
            softGlow 4.8s ease-in-out infinite,
            cardFloatA 5.6s ease-in-out infinite;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .podium-card {
        animation: cardFloatB 6.2s ease-in-out infinite;
        animation-delay: -.9s;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(3) .podium-card {
        animation: cardFloatC 5.8s ease-in-out infinite;
        animation-delay: -1.7s;
    }

    /* 섹션 타이틀 밑으로 스캔 빛 */
    .section-head {
        position: relative;
        overflow: hidden;
        padding-bottom: .15rem;
    }

    .section-head::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: 0;
        width: 26%;
        height: 2px;
        border-radius: 999px;
        background:
            linear-gradient(
                90deg,
                transparent,
                #3182F6,
                #8B5CF6,
                transparent
            );
        box-shadow: 0 0 12px rgba(49,130,246,.35);
        animation: sectionScan 6.8s ease-in-out infinite;
    }

    /* 인터랙티브 박스 안쪽도 숨 쉬기 */
    .interactive-inner {
        position: relative;
        overflow: hidden;
    }

    .interactive-inner::after {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background:
            radial-gradient(circle at 8% 120%, rgba(49,130,246,.07), transparent 28%),
            radial-gradient(circle at 96% -20%, rgba(139,92,246,.08), transparent 26%);
        animation: heroFloatB 9s ease-in-out infinite;
    }

    /* focus card도 미세 호흡 */
    .focus-card {
        animation: cardFloatA 6.3s ease-in-out infinite;
    }

    /* VS 배지 자동 펄스 */
    .duel-vs {
        animation:
            pulseRing 2.7s ease-out infinite,
            cardFloatA 4.4s ease-in-out infinite;
    }

    /* 랭킹 패널 상단 광선 */
    .ranking-panel::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 34px;
        z-index: 3;
        pointer-events: none;
        background:
            linear-gradient(
                180deg,
                rgba(49,130,246,.10),
                rgba(49,130,246,0)
            );
        animation: tableTopGlow 3s ease-in-out infinite;
    }

    /* 랭킹 표를 가로지르는 레이더 스캔 */
    .ranking-scroll {
        position: relative;
    }

    .ranking-scroll::after {
        content: "";
        position: absolute;
        z-index: 8;
        top: 0;
        left: 0;
        right: 0;
        height: 30px;
        pointer-events: none;
        background:
            linear-gradient(
                180deg,
                transparent 0%,
                rgba(49,130,246,.035) 25%,
                rgba(49,130,246,.11) 50%,
                rgba(49,130,246,.035) 75%,
                transparent 100%
            );
        filter: blur(.2px);
        animation: rankScan 9.5s ease-in-out infinite;
    }

    /* LIVE 도트 추가 펄스 */
    .ranking-live {
        animation:
            livePulse 1.8s ease-in-out infinite,
            pulseRing 2.4s ease-out infinite;
    }

    /* top 3 랭크 숫자도 리듬 */
    .rank-number.first {
        animation: pulseRing 3.2s ease-out infinite;
    }

    .rank-number.second {
        animation: cardFloatB 4.8s ease-in-out infinite;
    }

    .rank-number.third {
        animation: cardFloatC 5.2s ease-in-out infinite;
    }

    /* 티커 속도와 움직임을 조금 더 영화관 전광판처럼 */
    .ticker-track {
        animation: tickerMove 20s linear infinite;
        will-change: transform;
    }

    /* hover가 들어오면 기존 상호작용은 애니메이션 위에 추가 */
    .kpi-card:hover {
        animation-play-state: paused;
        transform: translateY(-9px) scale(1.015);
    }

    .podium-card:hover,
    .focus-card:hover {
        animation-play-state: paused;
    }

    /* 그래프 영역에 아주 약한 pulse */
    [data-testid="stPlotlyChart"] {
        box-shadow: 0 0 0 rgba(49,130,246,0);
        transition: box-shadow .25s ease;
    }

    [data-testid="stPlotlyChart"]:hover {
        box-shadow: 0 18px 42px rgba(49,130,246,.08);
    }


    /* =====================================================
       SIDEBAR COMMAND CENTER
       ===================================================== */
    .sidebar-command {
        position: relative;
        overflow: hidden;
        margin-bottom: .9rem;
        padding: 1rem 1rem .92rem;
        border-radius: 20px;
        color: white;
        background:
            radial-gradient(circle at 95% 0%, rgba(102,178,255,.32), transparent 35%),
            radial-gradient(circle at 0% 120%, rgba(139,92,246,.24), transparent 40%),
            linear-gradient(145deg, #0D1728, #163665);
        box-shadow: 0 16px 34px rgba(25,57,105,.18);
    }
    .sidebar-command::after {
        content: "";
        position: absolute;
        width: 110px;
        height: 180%;
        left: -140px;
        top: -40%;
        transform: rotate(18deg);
        pointer-events: none;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.18), transparent);
        animation: beamSweep 7s ease-in-out infinite;
    }
    .sidebar-command-top {
        display: flex;
        align-items: center;
        gap: .5rem;
        color: #CDE2FF;
        font-size: .64rem;
        font-weight: 950;
        letter-spacing: .09em;
    }
    .sidebar-command-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #70AFFF;
        animation: livePulse 1.8s ease-in-out infinite;
    }
    .sidebar-command-title {
        margin-top: .4rem;
        color: white;
        font-size: 1.1rem;
        font-weight: 950;
        letter-spacing: -.04em;
    }
    .sidebar-command-sub {
        margin-top: .28rem;
        color: #AFC7E8;
        font-size: .69rem;
        line-height: 1.55;
    }
    [data-testid="stSidebar"] [data-baseweb="tab-list"] {
        gap: .2rem;
        padding: .24rem;
        margin-bottom: .75rem;
        border-radius: 15px;
        background: #F2F6FB;
        border: 1px solid #E4EAF2;
    }
    [data-testid="stSidebar"] [data-baseweb="tab"] {
        height: 38px;
        padding: 0 .45rem;
        border-radius: 11px;
        color: #718096;
        font-size: .66rem;
        font-weight: 850;
        transition: background .18s ease, color .18s ease, transform .18s ease, box-shadow .18s ease;
    }
    [data-testid="stSidebar"] [data-baseweb="tab"]:hover {
        color: #245FBD;
        background: rgba(255,255,255,.8);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] [aria-selected="true"] {
        color: #1759B3 !important;
        background: #FFFFFF !important;
        box-shadow: 0 6px 16px rgba(31,78,145,.09);
    }
    .side-section-label {
        margin: .15rem 0 .55rem;
        color: #8B98A9;
        font-size: .62rem;
        font-weight: 950;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .side-mini-card {
        margin-top: .62rem;
        padding: .82rem .86rem;
        border-radius: 16px;
        background: linear-gradient(145deg, #FBFCFF, #F3F7FC);
        border: 1px solid #E4EAF2;
        box-shadow: 0 8px 20px rgba(15,23,42,.035);
    }
    .side-mini-label {
        color: #8C99AA;
        font-size: .61rem;
        font-weight: 900;
        letter-spacing: .05em;
    }
    .side-mini-value {
        color: #172033;
        margin-top: .22rem;
        font-size: 1rem;
        font-weight: 950;
        letter-spacing: -.03em;
    }
    .side-mini-note {
        color: #98A5B5;
        margin-top: .18rem;
        font-size: .61rem;
        line-height: 1.5;
    }
    .side-feature-list {
        display: grid;
        gap: .46rem;
        margin-top: .55rem;
    }
    .side-feature {
        display: flex;
        align-items: center;
        gap: .55rem;
        padding: .66rem .72rem;
        border-radius: 13px;
        background: #F8FAFD;
        border: 1px solid #E8EDF4;
        color: #5B6B80;
        font-size: .67rem;
        font-weight: 760;
    }
    .side-feature-icon {
        display: inline-flex;
        width: 25px;
        height: 25px;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
        border-radius: 8px;
        background: #EAF2FF;
        color: #2563B9;
        font-size: .72rem;
    }
    .side-rank-card {
        margin-top: .62rem;
        padding: .92rem;
        border-radius: 17px;
        color: white;
        background:
            radial-gradient(circle at 92% 0%, rgba(115,181,255,.32), transparent 38%),
            linear-gradient(145deg, #10213B, #174C89);
        box-shadow: 0 12px 26px rgba(29,67,118,.17);
    }
    .side-rank-chip {
        display: inline-flex;
        padding: .27rem .42rem;
        border-radius: 8px;
        background: rgba(255,255,255,.10);
        border: 1px solid rgba(255,255,255,.10);
        color: #D5E7FF;
        font-size: .58rem;
        font-weight: 950;
    }
    .side-rank-name {
        margin-top: .58rem;
        color: #FFFFFF;
        font-size: .95rem;
        font-weight: 950;
        line-height: 1.32;
        letter-spacing: -.035em;
    }
    .side-rank-value {
        margin-top: .7rem;
        color: white;
        font-size: 1.3rem;
        font-weight: 950;
        letter-spacing: -.045em;
    }
    .side-rank-caption {
        color: #AFC8E8;
        margin-top: .1rem;
        font-size: .59rem;
    }
    .side-stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .5rem;
        margin-top: .6rem;
    }
    .side-stat {
        padding: .7rem;
        border-radius: 13px;
        background: #F8FAFD;
        border: 1px solid #E7EDF4;
    }
    .side-stat-label {
        color: #909DAC;
        font-size: .57rem;
        font-weight: 850;
    }
    .side-stat-value {
        color: #243147;
        margin-top: .17rem;
        font-size: .85rem;
        font-weight: 950;
    }
    .sidebar-tip {
        margin-top: .75rem;
        padding: .75rem .8rem;
        border-radius: 14px;
        color: #58749A;
        background: #EEF5FF;
        border: 1px solid #DCEAFF;
        font-size: .64rem;
        line-height: 1.62;
    }
    [data-testid="stSidebar"] .stButton > button {
        min-height: 38px;
        border-radius: 12px !important;
        font-size: .68rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stDateInput"] input {
        font-size: .76rem !important;
    }


    /* =====================================================
       EVERYTHING MOVES — ULTRA MOTION LAYER
       ===================================================== */

    @keyframes breatheScale {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.012); }
    }

    @keyframes gentleTilt {
        0%, 100% { transform: rotate(0deg) translateY(0); }
        50% { transform: rotate(.25deg) translateY(-2px); }
    }

    @keyframes glowSweep {
        0% {
            transform: translateX(-160%) skewX(-14deg);
            opacity: 0;
        }
        12% { opacity: .42; }
        52% { opacity: .10; }
        100% {
            transform: translateX(220%) skewX(-14deg);
            opacity: 0;
        }
    }

    @keyframes borderBreath {
        0%, 100% {
            border-color: rgba(49,130,246,.15);
            box-shadow: 0 0 0 rgba(49,130,246,0);
        }
        50% {
            border-color: rgba(49,130,246,.38);
            box-shadow: 0 0 24px rgba(49,130,246,.08);
        }
    }

    @keyframes inputGlow {
        0%, 100% {
            box-shadow: 0 0 0 rgba(49,130,246,0);
        }
        50% {
            box-shadow: 0 0 0 3px rgba(49,130,246,.055);
        }
    }

    @keyframes microFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-2px); }
    }

    @keyframes microFloatReverse {
        0%, 100% { transform: translateY(-1px); }
        50% { transform: translateY(2px); }
    }

    @keyframes badgePulse {
        0%, 100% {
            transform: scale(1);
            filter: brightness(1);
        }
        50% {
            transform: scale(1.04);
            filter: brightness(1.06);
        }
    }

    @keyframes progressGlow {
        0%, 100% {
            filter: brightness(1);
            box-shadow: 0 0 8px rgba(49,130,246,.12);
        }
        50% {
            filter: brightness(1.12);
            box-shadow: 0 0 18px rgba(49,130,246,.28);
        }
    }

    @keyframes rowWave {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(2px); }
    }

    @keyframes softBlink {
        0%, 100% { opacity: .72; }
        50% { opacity: 1; }
    }

    @keyframes sidebarGlow {
        0%, 100% {
            box-shadow: inset -1px 0 0 rgba(49,130,246,.04);
        }
        50% {
            box-shadow: inset -1px 0 0 rgba(49,130,246,.14);
        }
    }

    @keyframes iconNudge {
        0%, 100% { transform: translateY(0) rotate(0); }
        50% { transform: translateY(-2px) rotate(2deg); }
    }

    @keyframes tabPulse {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-1px); }
    }

    @keyframes chartBreath {
        0%, 100% {
            box-shadow: 0 0 0 rgba(49,130,246,0);
            transform: translateY(0);
        }
        50% {
            box-shadow: 0 18px 44px rgba(49,130,246,.055);
            transform: translateY(-1px);
        }
    }

    @keyframes noteGlow {
        0%, 100% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
    }

    @keyframes tableShimmer {
        0% {
            background-position: -200% center;
        }
        100% {
            background-position: 200% center;
        }
    }

    /* ---------- SIDEBAR WHOLE BODY ---------- */
    [data-testid="stSidebar"] {
        animation: sidebarGlow 4.8s ease-in-out infinite;
    }

    .sidebar-command {
        animation:
            breatheScale 5.2s ease-in-out infinite,
            borderBreath 6.5s ease-in-out infinite;
    }

    .sidebar-command-title {
        background:
            linear-gradient(
                110deg,
                #FFFFFF 0%,
                #FFFFFF 34%,
                #9FCCFF 47%,
                #C5B1FF 53%,
                #FFFFFF 66%,
                #FFFFFF 100%
            );
        background-size: 240% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shineText 7s linear infinite;
    }

    .sidebar-command-sub {
        animation: softBlink 4.5s ease-in-out infinite;
    }

    /* ---------- SIDEBAR TABS ---------- */
    [data-testid="stSidebar"] [data-baseweb="tab"] {
        animation: tabPulse 4s ease-in-out infinite;
    }

    [data-testid="stSidebar"] [data-baseweb="tab"]:nth-child(2) {
        animation-delay: -.8s;
    }

    [data-testid="stSidebar"] [data-baseweb="tab"]:nth-child(3) {
        animation-delay: -1.6s;
    }

    [data-testid="stSidebar"] [data-baseweb="tab"]:nth-child(4) {
        animation-delay: -2.4s;
    }

    [data-testid="stSidebar"] [aria-selected="true"] {
        animation:
            tabPulse 3.2s ease-in-out infinite,
            borderBreath 4.5s ease-in-out infinite;
    }

    /* ---------- SIDEBAR MINI CARDS ---------- */
    .side-mini-card,
    .side-stat,
    .side-feature,
    .sidebar-tip {
        position: relative;
        overflow: hidden;
    }

    .side-mini-card {
        animation: microFloat 5.2s ease-in-out infinite;
    }

    .side-stat:nth-child(1) {
        animation: microFloat 4.8s ease-in-out infinite;
    }

    .side-stat:nth-child(2) {
        animation: microFloatReverse 5.1s ease-in-out infinite;
    }

    .side-stat:nth-child(3) {
        animation: microFloat 5.5s ease-in-out infinite;
    }

    .side-stat:nth-child(4) {
        animation: microFloatReverse 4.9s ease-in-out infinite;
    }

    .side-feature:nth-child(1) {
        animation: microFloat 5.4s ease-in-out infinite;
    }

    .side-feature:nth-child(2) {
        animation: microFloatReverse 5.7s ease-in-out infinite;
    }

    .side-feature:nth-child(3) {
        animation: microFloat 6s ease-in-out infinite;
    }

    .side-feature-icon {
        animation: iconNudge 3.8s ease-in-out infinite;
    }

    .side-rank-card {
        animation:
            breatheScale 5.8s ease-in-out infinite,
            borderBreath 7s ease-in-out infinite;
    }

    .side-rank-chip {
        animation: badgePulse 3.8s ease-in-out infinite;
    }

    .side-rank-value {
        animation: shineText 7.5s linear infinite;
        background:
            linear-gradient(
                110deg,
                #FFFFFF 0%,
                #FFFFFF 36%,
                #9DC8FF 48%,
                #D3C0FF 52%,
                #FFFFFF 64%,
                #FFFFFF 100%
            );
        background-size: 250% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .sidebar-tip {
        background:
            linear-gradient(
                120deg,
                #EEF5FF,
                #F5F1FF,
                #EEF5FF
            );
        background-size: 220% 220%;
        animation: noteGlow 8s ease-in-out infinite;
    }

    /* ---------- NATIVE BUTTONS / INPUTS ---------- */
    .stButton > button {
        animation:
            microFloat 4.8s ease-in-out infinite,
            borderBreath 6s ease-in-out infinite;
    }

    [data-testid="stSidebar"] .stButton > button:nth-child(even) {
        animation-delay: -1s;
    }

    div[data-baseweb="select"] > div {
        animation: inputGlow 4.6s ease-in-out infinite;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input {
        animation: inputGlow 4.2s ease-in-out infinite;
    }

    [data-testid="stSlider"] {
        animation: microFloat 5.3s ease-in-out infinite;
    }

    [data-testid="stRadio"] {
        animation: microFloatReverse 5.6s ease-in-out infinite;
    }

    /* ---------- ALL LABELS / CAPTIONS ---------- */
    [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"] {
        animation: softBlink 5.5s ease-in-out infinite;
    }

    /* ---------- SECTION HEADERS ---------- */
    .section-title {
        background:
            linear-gradient(
                110deg,
                #0F172A 0%,
                #0F172A 38%,
                #3182F6 49%,
                #8B5CF6 53%,
                #0F172A 64%,
                #0F172A 100%
            );
        background-size: 250% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shineText 9s linear infinite;
    }

    .section-eyebrow {
        animation: badgePulse 4.4s ease-in-out infinite;
    }

    .section-caption {
        animation: softBlink 5.8s ease-in-out infinite;
    }

    /* ---------- HERO TEXT ---------- */
    .hero-title {
        animation:
            breatheScale 6s ease-in-out infinite,
            softBlink 4.8s ease-in-out infinite;
        transform-origin: left center;
    }

    .hero-sub {
        animation: softBlink 5.5s ease-in-out infinite;
    }

    .hero-date {
        animation: badgePulse 4.7s ease-in-out infinite;
    }

    .hero-chip:nth-child(1) {
        animation: microFloat 4.6s ease-in-out infinite;
    }

    .hero-chip:nth-child(2) {
        animation: microFloatReverse 5s ease-in-out infinite;
    }

    .hero-chip:nth-child(3) {
        animation: microFloat 5.4s ease-in-out infinite;
    }

    .hero-chip:nth-child(4) {
        animation: microFloatReverse 5.8s ease-in-out infinite;
    }

    /* ---------- KPI CONTENT ---------- */
    .kpi-label {
        animation: softBlink 5s ease-in-out infinite;
    }

    .kpi-note {
        animation: softBlink 6s ease-in-out infinite;
    }

    /* ---------- PODIUM INTERNAL ELEMENTS ---------- */
    .rank-chip {
        animation:
            badgePulse 3.8s ease-in-out infinite,
            pulseRing 5.2s ease-out infinite;
    }

    .podium-name {
        animation: softBlink 5.3s ease-in-out infinite;
    }

    .podium-number {
        background:
            linear-gradient(
                110deg,
                #172033 0%,
                #172033 36%,
                #3182F6 49%,
                #8B5CF6 53%,
                #172033 66%,
                #172033 100%
            );
        background-size: 260% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shineText 8s linear infinite;
    }

    /* ---------- INTERACTIVE PANEL ---------- */
    .panel-kicker {
        animation: badgePulse 4.2s ease-in-out infinite;
    }

    .panel-title {
        animation: softBlink 5.2s ease-in-out infinite;
    }

    .panel-sub {
        animation: softBlink 6.2s ease-in-out infinite;
    }

    /* ---------- PLOTLY CHARTS ---------- */
    [data-testid="stPlotlyChart"] {
        animation: chartBreath 6.5s ease-in-out infinite;
    }

    /* ---------- FOCUS CARD INTERNAL ---------- */
    .focus-rank {
        animation:
            badgePulse 4s ease-in-out infinite,
            pulseRing 5.4s ease-out infinite;
    }

    .focus-title {
        animation: softBlink 5.2s ease-in-out infinite;
    }

    .focus-number {
        background:
            linear-gradient(
                110deg,
                #FFFFFF 0%,
                #FFFFFF 36%,
                #A5D0FF 48%,
                #D6C1FF 52%,
                #FFFFFF 64%,
                #FFFFFF 100%
            );
        background-size: 250% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shineText 7.2s linear infinite;
    }

    .focus-fill {
        animation: progressGlow 3.8s ease-in-out infinite;
    }

    .focus-meta,
    .focus-caption,
    .focus-track-label {
        animation: softBlink 5.7s ease-in-out infinite;
    }

    /* ---------- DUEL ---------- */
    .duel-result {
        animation: microFloat 5.2s ease-in-out infinite;
    }

    .duel-result:nth-child(even) {
        animation: microFloatReverse 5.6s ease-in-out infinite;
    }

    /* ---------- METRICS ---------- */
    [data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        animation:
            microFloat 5.6s ease-in-out infinite,
            borderBreath 6.8s ease-in-out infinite;
    }

    [data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        top: -30%;
        bottom: -30%;
        width: 80px;
        left: -120px;
        pointer-events: none;
        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(255,255,255,.45),
                transparent
            );
        animation: glowSweep 7.8s ease-in-out infinite;
    }

    [data-testid="stMetricValue"] {
        animation: badgePulse 4.6s ease-in-out infinite;
    }

    [data-testid="stMetricLabel"] {
        animation: softBlink 5.5s ease-in-out infinite;
    }

    /* ---------- RANKING TABLE ---------- */
    .ranking-toolbar-title {
        animation: softBlink 4.6s ease-in-out infinite;
    }

    .ranking-toolbar-meta {
        animation: softBlink 5.8s ease-in-out infinite;
    }

    .custom-table thead th {
        background:
            linear-gradient(
                100deg,
                #F8FAFC 0%,
                #F8FAFC 40%,
                #EEF5FF 50%,
                #F8FAFC 60%,
                #F8FAFC 100%
            );
        background-size: 240% auto;
        animation: tableShimmer 12s linear infinite;
    }

    .custom-table tbody tr:nth-child(odd) {
        animation: rowWave 6s ease-in-out infinite;
    }

    .custom-table tbody tr:nth-child(even) {
        animation: rowWave 6.6s ease-in-out infinite reverse;
    }

    .movie-name {
        animation: softBlink 6s ease-in-out infinite;
    }

    .trend-up,
    .trend-down,
    .trend-new,
    .trend-flat,
    .million-badge,
    .screen-pill {
        animation: badgePulse 4.8s ease-in-out infinite;
    }

    .audience-value,
    .num-cell {
        animation: softBlink 5.8s ease-in-out infinite;
    }

    .share-fill {
        animation: progressGlow 4.2s ease-in-out infinite;
    }

    .ranking-footer span {
        animation: softBlink 6.2s ease-in-out infinite;
    }

    /* ---------- ALERT / INFO / NOTE ---------- */
    div[data-testid="stAlert"] {
        animation:
            microFloat 5.5s ease-in-out infinite,
            borderBreath 7s ease-in-out infinite;
    }

    .soft-note {
        background:
            linear-gradient(
                120deg,
                #EEF5FF,
                #F7F1FF,
                #EEF5FF
            );
        background-size: 240% 240%;
        animation:
            noteGlow 9s ease-in-out infinite,
            microFloat 6.2s ease-in-out infinite;
    }

    /* ---------- SCROLLBAR ---------- */
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb,
    .ranking-scroll::-webkit-scrollbar-thumb {
        animation: softBlink 4s ease-in-out infinite;
    }


    /* =====================================================
       HERO PREMIUM — CINEMA COMMAND STAGE
       ===================================================== */
    @keyframes heroRadarSpin {
        from { transform: translate(-50%, -50%) rotate(0deg); }
        to   { transform: translate(-50%, -50%) rotate(360deg); }
    }

    @keyframes heroRadarSpinReverse {
        from { transform: translate(-50%, -50%) rotate(360deg); }
        to   { transform: translate(-50%, -50%) rotate(0deg); }
    }

    @keyframes heroHaloPulse {
        0%, 100% { transform: translate(-50%, -50%) scale(.96); opacity: .52; }
        50%      { transform: translate(-50%, -50%) scale(1.06); opacity: .92; }
    }

    @keyframes heroRankFloat {
        0%, 100% { transform: translateY(0) rotate(-1.2deg); }
        50%      { transform: translateY(-9px) rotate(.8deg); }
    }

    @keyframes heroEdgeScan {
        0%   { transform: translateY(-145%); opacity: 0; }
        12%  { opacity: .72; }
        48%  { opacity: .12; }
        62%, 100% { transform: translateY(470%); opacity: 0; }
    }

    @keyframes heroGlassSweep {
        0%   { transform: translateX(-170%) skewX(-18deg); opacity: 0; }
        13%  { opacity: .75; }
        35%  { opacity: .10; }
        55%, 100% { transform: translateX(260%) skewX(-18deg); opacity: 0; }
    }

    @keyframes heroMarquee {
        from { transform: translateX(0); }
        to   { transform: translateX(-50%); }
    }

    @keyframes heroTitleGlow {
        0%, 100% {
            text-shadow: 0 0 0 rgba(105,169,255,0);
            filter: brightness(1);
        }
        50% {
            text-shadow:
                0 0 22px rgba(105,169,255,.22),
                0 0 48px rgba(139,92,246,.10);
            filter: brightness(1.07);
        }
    }

    @keyframes heroRankGlow {
        0%, 100% {
            filter: drop-shadow(0 0 8px rgba(110,168,255,.20));
        }
        50% {
            filter:
                drop-shadow(0 0 16px rgba(110,168,255,.48))
                drop-shadow(0 0 34px rgba(139,92,246,.22));
        }
    }

    @keyframes heroBarDance {
        0%, 100% { transform: scaleY(.45); opacity: .45; }
        50%      { transform: scaleY(1); opacity: 1; }
    }

    @keyframes heroDotTravel {
        0%   { left: 0%; opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { left: 100%; opacity: 0; }
    }

    @keyframes heroFrameBreath {
        0%, 100% {
            box-shadow:
                0 34px 80px rgba(7,19,42,.32),
                inset 0 1px 0 rgba(255,255,255,.09),
                inset 0 0 0 1px rgba(255,255,255,.035);
        }
        50% {
            box-shadow:
                0 42px 98px rgba(7,19,42,.40),
                0 0 60px rgba(49,130,246,.09),
                inset 0 1px 0 rgba(255,255,255,.13),
                inset 0 0 0 1px rgba(255,255,255,.05);
        }
    }

    .hero.hero-cinema {
        min-height: 465px;
        padding: 0;
        border-radius: 34px;
        background:
            radial-gradient(circle at 81% 28%, rgba(53,145,255,.25), transparent 25%),
            radial-gradient(circle at 68% 112%, rgba(135,78,255,.24), transparent 39%),
            radial-gradient(circle at 7% 0%, rgba(77,121,255,.10), transparent 31%),
            linear-gradient(135deg, #060B13 0%, #0B1424 34%, #102745 69%, #123C70 100%);
        border: 1px solid rgba(173,207,255,.12);
        box-shadow:
            0 34px 80px rgba(7,19,42,.32),
            inset 0 1px 0 rgba(255,255,255,.09),
            inset 0 0 0 1px rgba(255,255,255,.035);
        animation:
            heroFrameBreath 5.7s ease-in-out infinite,
            heroPulseDepth 7s ease-in-out infinite !important;
    }

    .hero.hero-cinema:hover {
        transform: translateY(-5px) scale(1.002);
        box-shadow:
            0 46px 105px rgba(7,19,42,.43),
            0 0 75px rgba(49,130,246,.12),
            inset 0 1px 0 rgba(255,255,255,.12);
    }

    .hero-cinema .hero-grid {
        opacity: .20;
        background-size: 36px 36px;
        mask-image: linear-gradient(90deg, rgba(0,0,0,.90), rgba(0,0,0,.32) 72%, transparent);
    }

    .hero-cinema-noise {
        position: absolute;
        inset: 0;
        z-index: 2;
        pointer-events: none;
        opacity: .16;
        background-image:
            radial-gradient(circle at 20% 35%, rgba(255,255,255,.28) 0 .7px, transparent .9px),
            radial-gradient(circle at 75% 12%, rgba(255,255,255,.20) 0 .7px, transparent .9px),
            radial-gradient(circle at 62% 76%, rgba(162,205,255,.24) 0 .8px, transparent 1px);
        background-size: 17px 17px, 23px 23px, 31px 31px;
        mix-blend-mode: screen;
    }

    .hero-cinema-scan {
        position: absolute;
        z-index: 5;
        left: 0;
        right: 0;
        top: 0;
        height: 96px;
        pointer-events: none;
        background: linear-gradient(
            180deg,
            transparent,
            rgba(103,172,255,.035) 35%,
            rgba(145,197,255,.13) 50%,
            rgba(103,172,255,.035) 65%,
            transparent
        );
        filter: blur(.2px);
        animation: heroEdgeScan 8.5s ease-in-out infinite;
    }

    .hero-corner-tl,
    .hero-corner-br {
        position: absolute;
        z-index: 7;
        width: 72px;
        height: 72px;
        pointer-events: none;
        opacity: .58;
    }

    .hero-corner-tl {
        top: 20px;
        left: 20px;
        border-left: 1px solid rgba(165,207,255,.48);
        border-top: 1px solid rgba(165,207,255,.48);
        border-radius: 11px 0 0 0;
    }

    .hero-corner-br {
        right: 20px;
        bottom: 20px;
        border-right: 1px solid rgba(181,157,255,.42);
        border-bottom: 1px solid rgba(181,157,255,.42);
        border-radius: 0 0 11px 0;
    }

    .hero-cinema-layout {
        position: relative;
        z-index: 10;
        display: grid;
        grid-template-columns: minmax(0, 1.42fr) minmax(310px, .78fr);
        gap: 2.1rem;
        width: 100%;
        min-height: 465px;
        padding: 2.5rem 2.55rem 4.15rem;
        align-items: center;
    }

    .hero-copy {
        position: relative;
        z-index: 4;
        min-width: 0;
    }

    .hero-topline {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: .55rem;
    }

    .hero-live-badge {
        display: inline-flex;
        align-items: center;
        gap: .38rem;
        padding: .43rem .65rem;
        border-radius: 999px;
        color: #CBE1FF;
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.10);
        backdrop-filter: blur(14px);
        font-size: .63rem;
        font-weight: 900;
        letter-spacing: .06em;
    }

    .hero-live-badge::before {
        content: "";
        width: 6px;
        height: 6px;
        border-radius: 999px;
        background: #63A7FF;
        box-shadow: 0 0 12px rgba(99,167,255,.65);
        animation: livePulse 1.7s ease-in-out infinite;
    }

    .hero-verified {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        padding: .42rem .62rem;
        border-radius: 999px;
        color: #C9B8FF;
        background: rgba(139,92,246,.075);
        border: 1px solid rgba(188,160,255,.13);
        font-size: .61rem;
        font-weight: 850;
        letter-spacing: .04em;
    }

    .hero-overline {
        display: flex;
        align-items: center;
        gap: .55rem;
        margin-top: 1.25rem;
        color: #78AFFF;
        font-size: .72rem;
        font-weight: 950;
        letter-spacing: .16em;
        text-transform: uppercase;
    }

    .hero-overline::after {
        content: "";
        position: relative;
        display: block;
        width: 112px;
        height: 1px;
        overflow: visible;
        background: linear-gradient(90deg, rgba(100,165,255,.62), transparent);
    }

    .hero-overline::before {
        content: "";
        position: absolute;
        width: 5px;
        height: 5px;
        margin-left: 148px;
        border-radius: 999px;
        background: #8CBFFF;
        box-shadow: 0 0 10px rgba(140,191,255,.75);
        animation: heroDotTravel 3.6s ease-in-out infinite;
    }

    .hero-title-v2 {
        max-width: 760px;
        margin-top: .55rem !important;
        animation: heroTitleGlow 5s ease-in-out infinite !important;
        transform-origin: left center;
    }

    .hero-title-small {
        display: block;
        color: #E5EEFA;
        font-size: clamp(1rem, 1.6vw, 1.35rem);
        line-height: 1.3;
        font-weight: 800;
        letter-spacing: -.03em;
        opacity: .78;
        margin-bottom: .22rem;
    }

    .hero-title-movie {
        display: block;
        max-width: 740px;
        overflow: hidden;
        text-overflow: ellipsis;
        color: #FFFFFF;
        font-size: clamp(2.4rem, 5vw, 4.65rem);
        line-height: .98;
        font-weight: 950;
        letter-spacing: -.07em;
        white-space: nowrap;
        background:
            linear-gradient(
                105deg,
                #FFFFFF 0%,
                #FFFFFF 30%,
                #A9D2FF 43%,
                #D8C8FF 50%,
                #FFFFFF 61%,
                #FFFFFF 100%
            );
        background-size: 260% auto;
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: shineText 6.8s linear infinite;
    }

    .hero-sub-v2 {
        max-width: 680px;
        margin-top: .82rem;
        color: #AFC1D9;
        font-size: .91rem;
        line-height: 1.72;
        letter-spacing: -.01em;
    }

    .hero-stat-deck {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .65rem;
        max-width: 720px;
        margin-top: 1.35rem;
    }

    .hero-stat-card {
        position: relative;
        overflow: hidden;
        min-height: 84px;
        padding: .78rem .86rem;
        border-radius: 17px;
        background:
            linear-gradient(145deg, rgba(255,255,255,.075), rgba(255,255,255,.035));
        border: 1px solid rgba(255,255,255,.105);
        backdrop-filter: blur(16px);
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,.07),
            0 12px 26px rgba(0,0,0,.08);
        transition: transform .22s ease, background .22s ease, border-color .22s ease;
    }

    .hero-stat-card::after {
        content: "";
        position: absolute;
        top: -30%;
        bottom: -30%;
        left: -100px;
        width: 70px;
        pointer-events: none;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.20), transparent);
        animation: heroGlassSweep 7s ease-in-out infinite;
    }

    .hero-stat-card:nth-child(2)::after { animation-delay: -2.2s; }
    .hero-stat-card:nth-child(3)::after { animation-delay: -4.4s; }

    .hero-stat-card:hover {
        transform: translateY(-4px);
        background: linear-gradient(145deg, rgba(255,255,255,.11), rgba(255,255,255,.05));
        border-color: rgba(173,210,255,.22);
    }

    .hero-stat-label {
        color: #849AB8;
        font-size: .61rem;
        font-weight: 850;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .hero-stat-value {
        margin-top: .27rem;
        color: #FFFFFF;
        font-size: 1.28rem;
        font-weight: 950;
        letter-spacing: -.045em;
    }

    .hero-stat-note {
        margin-top: .08rem;
        color: #7892B3;
        font-size: .58rem;
        font-weight: 650;
    }

    .hero-meta-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: .7rem;
        margin-top: 1rem;
        color: #8299B8;
        font-size: .64rem;
        font-weight: 760;
    }

    .hero-meta-date {
        display: inline-flex;
        align-items: center;
        gap: .38rem;
        color: #DCE9F8;
        font-weight: 850;
    }

    .hero-meta-dot {
        width: 4px;
        height: 4px;
        border-radius: 999px;
        background: #54779E;
    }

    /* ---------- RIGHT HOLOGRAPHIC RANK CORE ---------- */
    .hero-rank-zone {
        position: relative;
        z-index: 5;
        min-height: 340px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .hero-radar-ring {
        position: absolute;
        left: 50%;
        top: 50%;
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-radar-ring.one {
        width: 318px;
        height: 318px;
        border: 1px solid rgba(105,169,255,.16);
        border-left-color: rgba(119,185,255,.60);
        border-top-color: rgba(119,185,255,.32);
        animation: heroRadarSpin 13s linear infinite;
    }

    .hero-radar-ring.two {
        width: 260px;
        height: 260px;
        border: 1px dashed rgba(170,142,255,.19);
        border-right-color: rgba(190,164,255,.62);
        animation: heroRadarSpinReverse 9s linear infinite;
    }

    .hero-radar-ring.three {
        width: 208px;
        height: 208px;
        border: 1px solid rgba(115,179,255,.11);
        box-shadow:
            0 0 42px rgba(49,130,246,.08),
            inset 0 0 40px rgba(49,130,246,.035);
        animation: heroHaloPulse 4.3s ease-in-out infinite;
    }

    .hero-radar-cross {
        position: absolute;
        left: 50%;
        top: 50%;
        width: 310px;
        height: 310px;
        transform: translate(-50%, -50%);
        opacity: .15;
        pointer-events: none;
        background:
            linear-gradient(90deg, transparent 49.8%, #79B2FF 50%, transparent 50.2%),
            linear-gradient(transparent 49.8%, #79B2FF 50%, transparent 50.2%);
        mask-image: radial-gradient(circle, black 0 58%, transparent 59%);
    }

    .hero-rank-core {
        position: relative;
        z-index: 4;
        width: 235px;
        min-height: 270px;
        padding: 1.1rem 1.05rem 1rem;
        border-radius: 27px;
        background:
            radial-gradient(circle at 80% 3%, rgba(119,180,255,.18), transparent 31%),
            linear-gradient(155deg, rgba(14,35,66,.91), rgba(7,18,34,.86));
        border: 1px solid rgba(155,199,255,.18);
        box-shadow:
            0 26px 60px rgba(0,0,0,.28),
            0 0 58px rgba(49,130,246,.08),
            inset 0 1px 0 rgba(255,255,255,.08),
            inset 0 0 0 1px rgba(255,255,255,.025);
        backdrop-filter: blur(22px);
        animation: heroRankFloat 5s ease-in-out infinite;
    }

    .hero-rank-core::before {
        content: "";
        position: absolute;
        left: 13px;
        top: 13px;
        width: 34px;
        height: 34px;
        border-left: 1px solid rgba(128,188,255,.52);
        border-top: 1px solid rgba(128,188,255,.52);
        border-radius: 7px 0 0 0;
        opacity: .68;
    }

    .hero-rank-core::after {
        content: "";
        position: absolute;
        right: 13px;
        bottom: 13px;
        width: 34px;
        height: 34px;
        border-right: 1px solid rgba(177,144,255,.45);
        border-bottom: 1px solid rgba(177,144,255,.45);
        border-radius: 0 0 7px 0;
        opacity: .68;
    }

    .hero-rank-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: .5rem;
        color: #8198B8;
        font-size: .57rem;
        font-weight: 950;
        letter-spacing: .11em;
    }

    .hero-rank-live {
        display: inline-flex;
        align-items: center;
        gap: .28rem;
        color: #7DB4FF;
    }

    .hero-rank-live::before {
        content: "";
        width: 5px;
        height: 5px;
        border-radius: 999px;
        background: #6DB0FF;
        box-shadow: 0 0 10px rgba(109,176,255,.8);
        animation: livePulse 1.7s ease-in-out infinite;
    }

    .hero-rank-number {
        margin-top: .4rem;
        color: #FFFFFF;
        font-size: 5.7rem;
        line-height: .90;
        font-weight: 950;
        letter-spacing: -.095em;
        text-align: center;
        background:
            linear-gradient(180deg, #FFFFFF 0%, #CDE4FF 51%, #6AA8FF 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: heroRankGlow 3.8s ease-in-out infinite;
    }

    .hero-rank-divider {
        height: 1px;
        margin: .72rem 0 .65rem;
        background: linear-gradient(90deg, transparent, rgba(125,183,255,.38), transparent);
    }

    .hero-rank-movie {
        overflow: hidden;
        color: #F3F7FD;
        font-size: .88rem;
        font-weight: 950;
        line-height: 1.35;
        letter-spacing: -.025em;
        text-align: center;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .hero-rank-audience {
        margin-top: .3rem;
        color: #88A1C2;
        font-size: .59rem;
        font-weight: 750;
        text-align: center;
    }

    .hero-eq {
        height: 30px;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        gap: 5px;
        margin-top: .78rem;
    }

    .hero-eq span {
        width: 4px;
        height: 26px;
        border-radius: 999px;
        transform-origin: bottom;
        background: linear-gradient(180deg, #B5D7FF, #4E94F5);
        box-shadow: 0 0 8px rgba(78,148,245,.28);
        animation: heroBarDance 1.45s ease-in-out infinite;
    }

    .hero-eq span:nth-child(2) { animation-delay: -.95s; }
    .hero-eq span:nth-child(3) { animation-delay: -.35s; }
    .hero-eq span:nth-child(4) { animation-delay: -1.15s; }
    .hero-eq span:nth-child(5) { animation-delay: -.62s; }
    .hero-eq span:nth-child(6) { animation-delay: -.18s; }
    .hero-eq span:nth-child(7) { animation-delay: -.78s; }

    .hero-rank-trend {
        display: flex;
        justify-content: center;
        margin-top: .65rem;
    }

    .hero-rank-trend span {
        display: inline-flex;
        align-items: center;
        padding: .28rem .48rem;
        border-radius: 999px;
        color: #BBD7FB;
        background: rgba(101,164,255,.08);
        border: 1px solid rgba(101,164,255,.12);
        font-size: .56rem;
        font-weight: 900;
        letter-spacing: .04em;
    }

    /* ---------- BOTTOM MINI MARQUEE INSIDE HERO ---------- */
    .hero-bottom-rail {
        position: absolute;
        z-index: 12;
        left: 0;
        right: 0;
        bottom: 0;
        height: 45px;
        display: flex;
        align-items: center;
        overflow: hidden;
        border-top: 1px solid rgba(255,255,255,.07);
        background:
            linear-gradient(90deg, rgba(4,11,21,.88), rgba(13,31,56,.78), rgba(4,11,21,.88));
        backdrop-filter: blur(16px);
    }

    .hero-bottom-rail::before,
    .hero-bottom-rail::after {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        width: 78px;
        z-index: 3;
        pointer-events: none;
    }

    .hero-bottom-rail::before {
        left: 0;
        background: linear-gradient(90deg, #08111F, transparent);
    }

    .hero-bottom-rail::after {
        right: 0;
        background: linear-gradient(-90deg, #0B1A2D, transparent);
    }

    .hero-rail-track {
        display: flex;
        align-items: center;
        width: max-content;
        animation: heroMarquee 18s linear infinite;
        will-change: transform;
    }

    .hero-rail-item {
        display: inline-flex;
        align-items: center;
        gap: .52rem;
        padding: 0 1rem;
        color: #90A7C4;
        font-size: .61rem;
        font-weight: 800;
        white-space: nowrap;
    }

    .hero-rail-rank {
        color: #78AFFF;
        font-weight: 950;
    }

    .hero-rail-name {
        color: #DCE8F8;
    }

    .hero-rail-sep {
        width: 3px;
        height: 3px;
        border-radius: 999px;
        background: #49688E;
    }

    /* New hero should win over generic EVERYTHING-MOVES title rules */
    .hero.hero-cinema .hero-title-v2,
    .hero.hero-cinema .hero-title-small,
    .hero.hero-cinema .hero-title-movie {
        transform-origin: left center;
    }

    @media (max-width: 1050px) {
        .hero-cinema-layout {
            grid-template-columns: minmax(0, 1fr) 270px;
            gap: 1.15rem;
            padding-left: 2rem;
            padding-right: 1.6rem;
        }

        .hero-radar-ring.one { width: 276px; height: 276px; }
        .hero-radar-ring.two { width: 228px; height: 228px; }
        .hero-radar-ring.three { width: 182px; height: 182px; }
        .hero-radar-cross { width: 270px; height: 270px; }
        .hero-rank-core { width: 210px; }
        .hero-rank-number { font-size: 5rem; }
    }

    @media (max-width: 820px) {
        .hero.hero-cinema {
            min-height: auto;
        }

        .hero-cinema-layout {
            grid-template-columns: 1fr;
            min-height: auto;
            padding: 2rem 1.35rem 4.3rem;
        }

        .hero-rank-zone {
            min-height: 265px;
            margin-top: -.25rem;
        }

        .hero-radar-ring.one { width: 250px; height: 250px; }
        .hero-radar-ring.two { width: 205px; height: 205px; }
        .hero-radar-ring.three { width: 165px; height: 165px; }
        .hero-radar-cross { width: 242px; height: 242px; }
        .hero-rank-core { width: 205px; min-height: 220px; }
        .hero-rank-number { font-size: 4.5rem; }
        .hero-stat-deck { grid-template-columns: 1fr 1fr 1fr; }
    }

    @media (max-width: 560px) {
        .hero.hero-cinema {
            border-radius: 24px;
        }

        .hero-cinema-layout {
            padding: 1.45rem 1rem 4.1rem;
        }

        .hero-title-movie {
            font-size: 2.4rem;
            white-space: normal;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        .hero-stat-deck {
            grid-template-columns: 1fr;
        }

        .hero-stat-card {
            min-height: 68px;
        }

        .hero-rank-zone {
            min-height: 245px;
        }

        .hero-meta-row {
            gap: .45rem;
        }
    }


    /* =====================================================
       THEME STUDIO
       ===================================================== */
    .theme-studio-head {
        position: relative;
        overflow: hidden;
        margin-bottom: .7rem;
        padding: .85rem .88rem;
        border-radius: 16px;
        color: white;
        background:
            radial-gradient(circle at 95% 0%, rgba(255,255,255,.17), transparent 35%),
            linear-gradient(135deg, var(--theme-primary, #3182F6), var(--theme-secondary, #8B5CF6));
        box-shadow: 0 12px 28px rgba(15,23,42,.10);
    }

    .theme-studio-head::after {
        content: "";
        position: absolute;
        top: -40%;
        bottom: -40%;
        left: -90px;
        width: 60px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,.28), transparent);
        animation: glowSweep 6s ease-in-out infinite;
        pointer-events: none;
    }

    .theme-studio-kicker {
        color: rgba(255,255,255,.72);
        font-size: .58rem;
        font-weight: 950;
        letter-spacing: .10em;
    }

    .theme-studio-title {
        margin-top: .22rem;
        color: white;
        font-size: .98rem;
        font-weight: 950;
        letter-spacing: -.035em;
    }

    .theme-studio-sub {
        margin-top: .18rem;
        color: rgba(255,255,255,.72);
        font-size: .61rem;
        line-height: 1.5;
    }

    .palette-preview {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: .38rem;
        margin: .72rem 0 .45rem;
        padding: .48rem;
        border-radius: 15px;
        background: rgba(127,127,127,.06);
        border: 1px solid rgba(127,127,127,.12);
    }

    .palette-swatch {
        position: relative;
        height: 44px;
        overflow: hidden;
        border-radius: 11px;
        border: 1px solid rgba(255,255,255,.34);
        box-shadow: 0 7px 16px rgba(15,23,42,.10);
        animation: microFloat 5s ease-in-out infinite;
    }

    .palette-swatch:nth-child(2) { animation-delay: -.7s; }
    .palette-swatch:nth-child(3) { animation-delay: -1.4s; }
    .palette-swatch:nth-child(4) { animation-delay: -2.1s; }
    .palette-swatch:nth-child(5) { animation-delay: -2.8s; }

    .palette-code {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .35rem;
        margin-top: .45rem;
    }

    .palette-code-item {
        padding: .48rem .55rem;
        border-radius: 11px;
        background: rgba(127,127,127,.055);
        border: 1px solid rgba(127,127,127,.11);
        font-size: .58rem;
        font-weight: 800;
        line-height: 1.45;
    }

    .palette-code-item b {
        display: block;
        margin-bottom: .08rem;
        font-size: .52rem;
        letter-spacing: .06em;
        opacity: .62;
    }

    .theme-status {
        display: flex;
        align-items: center;
        gap: .5rem;
        margin-top: .65rem;
        padding: .62rem .68rem;
        border-radius: 13px;
        background: rgba(127,127,127,.055);
        border: 1px solid rgba(127,127,127,.11);
        font-size: .61rem;
        line-height: 1.55;
        font-weight: 750;
    }

    .theme-status-dot {
        width: 8px;
        height: 8px;
        flex: 0 0 auto;
        border-radius: 999px;
        background: var(--theme-primary, #3182F6);
        box-shadow: 0 0 14px var(--theme-primary, #3182F6);
        animation: livePulse 1.8s ease-in-out infinite;
    }

    [data-testid="stSidebar"] [data-testid="stColorPicker"] {
        animation: microFloat 5.2s ease-in-out infinite;
    }

    [data-testid="stSidebar"] [data-testid="stColorPicker"] button {
        border-radius: 12px !important;
        box-shadow: 0 6px 15px rgba(15,23,42,.08);
    }


    [data-testid="stSidebar"] [data-baseweb="tab"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
        padding-left: .20rem !important;
        padding-right: .20rem !important;
        font-size: .60rem !important;
    }

</style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. DATA
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def get_boxoffice_data(target_date: str, api_key: str):
    url = (
        "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
        "boxoffice/searchDailyBoxOfficeList.json"
    )

    try:
        response = requests.get(
            url,
            params={"key": api_key, "targetDt": target_date},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if "faultInfo" in data:
            message = data["faultInfo"].get("message", "알 수 없는 API 오류")
            return None, f"KOBIS API 오류: {message}"

        movie_list = data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])

        if not movie_list:
            return None, "empty"

        return pd.DataFrame(movie_list), None

    except requests.RequestException:
        return None, "영화진흥위원회 서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요."
    except ValueError:
        return None, "서버 응답을 읽는 중 문제가 발생했어요."
    except Exception as exc:
        return None, f"예상하지 못한 오류가 발생했어요: {exc}"


@st.cache_data(ttl=3600, show_spinner=False)
def get_week_boxoffice_data(end_date_str: str, api_key: str):
    end_date = datetime.strptime(end_date_str, "%Y%m%d").date()
    frames = []

    for offset in range(6, -1, -1):
        day = end_date - timedelta(days=offset)
        raw, error = get_boxoffice_data(day.strftime("%Y%m%d"), api_key)

        if raw is None or error:
            continue

        temp = raw.copy()

        for col in [
            "rank",
            "rankInten",
            "audiCnt",
            "audiAcc",
            "scrnCnt",
            "salesAmt",
            "salesAcc",
        ]:
            if col in temp.columns:
                temp[col] = pd.to_numeric(
                    temp[col],
                    errors="coerce",
                ).fillna(0)

        temp["movieNmDisplay"] = temp["movieNm"].astype(str)
        temp["date"] = pd.to_datetime(day)
        frames.append(temp)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    numeric_cols = [
        "rank",
        "rankInten",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "salesAmt",
        "salesAcc",
    ]

    for col in numeric_cols:
        if col in result.columns:
            result[col] = pd.to_numeric(
                result[col],
                errors="coerce",
            ).fillna(0)

    result["isMillion"] = result["audiAcc"] >= 1_000_000
    result["movieNmDisplay"] = result["movieNm"].astype(str)
    return result


# =========================================================
# 4. HELPERS
# =========================================================
def compact_html(markup: str) -> str:
    markup = textwrap.dedent(markup).strip()
    markup = re.sub(r">\s+<", "><", markup)
    return markup



def hex_to_rgb(hex_color: str):
    value = hex_color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        return (49, 130, 246)
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (49, 130, 246)


def rgb_to_hex(rgb):
    r, g, b = [max(0, min(255, int(round(v)))) for v in rgb]
    return f"#{r:02X}{g:02X}{b:02X}"


def mix_hex(color_a: str, color_b: str, amount: float) -> str:
    amount = max(0.0, min(1.0, float(amount)))
    a = hex_to_rgb(color_a)
    b = hex_to_rgb(color_b)
    mixed = tuple(a[i] * (1 - amount) + b[i] * amount for i in range(3))
    return rgb_to_hex(mixed)


def rgba_hex(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{max(0, min(1, alpha)):.3f})"


def color_luminance(hex_color: str) -> float:
    rgb = [c / 255.0 for c in hex_to_rgb(hex_color)]

    def linearize(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = [linearize(v) for v in rgb]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def auto_text_color(background: str) -> str:
    return "#F8FAFC" if color_luminance(background) < 0.38 else "#0F172A"


def hls_hex(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s)
    return rgb_to_hex((r * 255, g * 255, b * 255))


def make_random_palette():
    hue = random.random()
    dark = random.random() < 0.42

    primary = hls_hex(hue, 0.56, 0.88)
    secondary = hls_hex(hue + 0.13, 0.59, 0.83)
    accent = hls_hex(hue + 0.51, 0.58, 0.90)

    if dark:
        background = hls_hex(hue, 0.075, 0.30)
        surface = hls_hex(hue, 0.115, 0.25)
    else:
        background = hls_hex(hue, 0.965, 0.25)
        surface = "#FFFFFF"

    return {
        "theme_primary": primary,
        "theme_secondary": secondary,
        "theme_accent": accent,
        "theme_bg": background,
        "theme_surface": surface,
    }


def chart_theme_colors():
    if not st.session_state.get("theme_sync_charts", True):
        return {
            "primary": "#3182F6",
            "secondary": "#8B5CF6",
            "accent": "#16A3A3",
            "surface": "#FFFFFF",
            "background": "#F4F7FB",
            "text": "#334155",
            "muted": "#7A8799",
            "grid": "#EEF2F7",
        }

    primary = st.session_state.get("theme_primary", "#3182F6")
    secondary = st.session_state.get("theme_secondary", "#8B5CF6")
    accent = st.session_state.get("theme_accent", "#16A3A3")
    surface = st.session_state.get("theme_surface", "#FFFFFF")
    background = st.session_state.get("theme_bg", "#F4F7FB")
    text = auto_text_color(surface)
    muted = mix_hex(text, surface, 0.52)
    grid = mix_hex(surface, text, 0.11)

    return {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "surface": surface,
        "background": background,
        "text": text,
        "muted": muted,
        "grid": grid,
    }


def build_theme_css(
    primary: str,
    secondary: str,
    accent: str,
    background: str,
    surface: str,
    glow_strength: int,
) -> str:
    bg_text = auto_text_color(background)
    surface_text = auto_text_color(surface)

    muted = mix_hex(surface_text, surface, 0.52)
    muted_2 = mix_hex(surface_text, surface, 0.67)
    line = mix_hex(surface, surface_text, 0.12)
    soft = mix_hex(surface, primary, 0.075)
    soft_2 = mix_hex(surface, secondary, 0.075)

    hero_a = mix_hex(primary, "#030711", 0.80)
    hero_b = mix_hex(secondary, "#050813", 0.76)
    hero_c = mix_hex(primary, "#061225", 0.63)
    hero_surface = mix_hex(primary, "#07111F", 0.78)

    primary_soft = mix_hex(surface, primary, 0.16)
    secondary_soft = mix_hex(surface, secondary, 0.15)
    accent_soft = mix_hex(surface, accent, 0.15)

    glow = max(0, min(100, int(glow_strength)))
    glow_alpha = 0.035 + (glow / 100) * 0.25
    glow_alpha_soft = 0.02 + (glow / 100) * 0.13
    glow_px = 12 + int(glow * 0.32)

    bg_rgb = hex_to_rgb(background)
    surface_rgb = hex_to_rgb(surface)

    return f"""
    :root {{
        --theme-primary: {primary};
        --theme-secondary: {secondary};
        --theme-accent: {accent};
        --theme-bg: {background};
        --theme-surface: {surface};
        --theme-text: {surface_text};
        --theme-muted: {muted};
        --theme-line: {line};

        --blue: {primary} !important;
        --blue-2: {mix_hex(primary, secondary, .35)} !important;
        --purple: {secondary} !important;
        --green: {accent} !important;
        --bg: {background} !important;
        --surface: {surface} !important;
        --surface-soft: {soft} !important;
        --text: {surface_text} !important;
        --text-sub: {muted} !important;
        --line: {line} !important;
    }}

    .stApp {{
        color: {bg_text} !important;
        background:
            radial-gradient(circle at 7% -8%, {rgba_hex(primary, .16)}, transparent 30%),
            radial-gradient(circle at 97% 0%, {rgba_hex(secondary, .13)}, transparent 26%),
            radial-gradient(circle at 54% 105%, {rgba_hex(accent, .06)}, transparent 30%),
            {background} !important;
    }}

    [data-testid="stHeader"] {{
        background: rgba({bg_rgb[0]},{bg_rgb[1]},{bg_rgb[2]},.72) !important;
    }}

    [data-testid="stSidebar"] {{
        color: {surface_text} !important;
        background: rgba({surface_rgb[0]},{surface_rgb[1]},{surface_rgb[2]},.95) !important;
        border-right-color: {line} !important;
    }}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span:not(.sidebar-command-dot):not(.theme-status-dot) {{
        color: inherit;
    }}

    .sidebar-command {{
        background:
            radial-gradient(circle at 95% 0%, {rgba_hex(primary, .38)}, transparent 37%),
            radial-gradient(circle at 0% 120%, {rgba_hex(secondary, .30)}, transparent 42%),
            linear-gradient(145deg, {hero_a}, {hero_c}) !important;
        box-shadow:
            0 16px 38px {rgba_hex(primary, glow_alpha_soft)},
            inset 0 1px 0 rgba(255,255,255,.08) !important;
    }}

    .sidebar-command-dot,
    .ranking-live,
    .theme-status-dot {{
        background: {primary} !important;
        box-shadow: 0 0 {glow_px}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="tab-list"] {{
        background: {soft} !important;
        border-color: {line} !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="tab"] {{
        color: {muted} !important;
    }}

    [data-testid="stSidebar"] [aria-selected="true"] {{
        color: {primary} !important;
        background: {surface} !important;
        box-shadow: 0 7px 18px {rgba_hex(primary, .10)} !important;
    }}

    .side-mini-card,
    .side-stat,
    .side-feature,
    .sidebar-tip,
    .duel-result {{
        color: {surface_text} !important;
        background:
            linear-gradient(145deg, {surface}, {soft}) !important;
        border-color: {line} !important;
    }}

    .side-mini-label,
    .side-mini-note,
    .side-stat-label,
    .side-rank-caption,
    .section-caption,
    .panel-sub {{
        color: {muted_2} !important;
    }}

    .side-mini-value,
    .side-stat-value {{
        color: {surface_text} !important;
    }}

    .side-feature-icon {{
        color: {primary} !important;
        background: {primary_soft} !important;
    }}

    .side-rank-card {{
        background:
            radial-gradient(circle at 92% 0%, {rgba_hex(primary, .38)}, transparent 40%),
            linear-gradient(145deg, {hero_a}, {hero_c}) !important;
        box-shadow: 0 14px 32px {rgba_hex(primary, glow_alpha_soft)} !important;
    }}

    .theme-studio-head {{
        background:
            radial-gradient(circle at 95% 0%, rgba(255,255,255,.18), transparent 35%),
            linear-gradient(135deg, {primary}, {secondary}) !important;
        box-shadow: 0 14px 34px {rgba_hex(primary, glow_alpha_soft)} !important;
    }}

    .palette-code-item,
    .theme-status {{
        color: {surface_text} !important;
        background: {soft} !important;
        border-color: {line} !important;
    }}

    .section-eyebrow {{
        color: {primary} !important;
    }}

    .section-title {{
        background:
            linear-gradient(
                110deg,
                {surface_text} 0%,
                {surface_text} 35%,
                {primary} 47%,
                {secondary} 53%,
                {surface_text} 66%,
                {surface_text} 100%
            ) !important;
        background-size: 250% auto !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        color: transparent !important;
    }}

    .section-head::after {{
        background:
            linear-gradient(90deg, transparent, {primary}, {secondary}, transparent) !important;
        box-shadow: 0 0 {glow_px}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .kpi-card,
    .podium-card,
    .ranking-panel,
    [data-testid="stMetric"] {{
        color: {surface_text} !important;
        background:
            radial-gradient(circle at 100% 0%, {rgba_hex(primary, .055)}, transparent 34%),
            {surface} !important;
        border-color: {line} !important;
        box-shadow:
            0 16px 42px rgba(0,0,0,.055),
            0 0 {glow_px}px {rgba_hex(primary, glow_alpha_soft)} !important;
    }}

    .kpi-card:hover,
    .podium-card:hover,
    [data-testid="stMetric"]:hover {{
        border-color: {mix_hex(primary, surface, .30)} !important;
        box-shadow:
            0 24px 58px rgba(0,0,0,.09),
            0 0 {glow_px + 12}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .kpi-label,
    .kpi-note,
    .podium-meta,
    .podium-label {{
        color: {muted} !important;
    }}

    .kpi-value,
    .podium-number {{
        background:
            linear-gradient(
                110deg,
                {surface_text} 0%,
                {surface_text} 34%,
                {primary} 47%,
                {secondary} 53%,
                {surface_text} 66%,
                {surface_text} 100%
            ) !important;
        background-size: 260% auto !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        color: transparent !important;
    }}

    .podium-name,
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"] {{
        color: {surface_text} !important;
    }}

    .rank-chip {{
        color: {primary} !important;
        background: {primary_soft} !important;
    }}

    .rank-chip.gold {{
        color: {accent} !important;
        background: {accent_soft} !important;
    }}

    .interactive-shell {{
        background:
            linear-gradient(115deg, {primary}, {secondary}, {accent}, {primary}) !important;
        background-size: 300% 300% !important;
        box-shadow: 0 20px 55px {rgba_hex(primary, glow_alpha_soft)} !important;
    }}

    .interactive-inner {{
        color: {surface_text} !important;
        background:
            radial-gradient(circle at 93% 0%, {rgba_hex(primary, .09)}, transparent 30%),
            {surface} !important;
    }}

    .panel-kicker {{
        color: {primary} !important;
    }}

    .panel-kicker::before {{
        background: {primary} !important;
        box-shadow: 0 0 0 5px {rgba_hex(primary, .10)} !important;
    }}

    .panel-title {{
        color: {surface_text} !important;
    }}

    .focus-card {{
        background:
            radial-gradient(circle at 88% 5%, {rgba_hex(primary, .36)}, transparent 30%),
            radial-gradient(circle at 0% 112%, {rgba_hex(secondary, .32)}, transparent 40%),
            linear-gradient(145deg, {hero_a}, {hero_b}, {hero_c}) !important;
        box-shadow:
            0 25px 62px rgba(0,0,0,.20),
            0 0 {glow_px}px {rgba_hex(primary, glow_alpha_soft)} !important;
    }}

    .focus-fill,
    .share-fill {{
        background: linear-gradient(90deg, {primary}, {secondary}) !important;
        box-shadow: 0 0 {glow_px}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .duel-vs {{
        background: linear-gradient(135deg, {primary}, {secondary}) !important;
        box-shadow: 0 14px 32px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .ranking-panel::before {{
        background: linear-gradient(90deg, {primary}, {secondary}, {accent}) !important;
    }}

    .ranking-toolbar,
    .ranking-footer,
    .custom-table,
    .custom-table tbody td {{
        color: {surface_text} !important;
        background: {surface} !important;
        border-color: {line} !important;
    }}

    .custom-table thead th {{
        color: {muted} !important;
        background:
            linear-gradient(
                100deg,
                {soft} 0%,
                {soft} 40%,
                {soft_2} 50%,
                {soft} 60%,
                {soft} 100%
            ) !important;
        background-size: 240% auto !important;
        border-color: {line} !important;
    }}

    .custom-table tbody tr:hover td {{
        background: {soft} !important;
    }}

    .custom-table tbody tr.rank-row-1 td {{
        background:
            linear-gradient(90deg, {rgba_hex(primary, .09)}, {surface} 52%) !important;
    }}

    .custom-table tbody tr.rank-row-1 td:first-child {{
        box-shadow: inset 4px 0 0 {primary} !important;
    }}

    .movie-name,
    .audience-value,
    .num-cell,
    .ranking-toolbar-title {{
        color: {surface_text} !important;
    }}

    .rank-number.first {{
        color: {primary} !important;
        background: {primary_soft} !important;
        box-shadow: inset 0 0 0 1px {mix_hex(primary, surface, .45)} !important;
    }}

    .rank-number.second {{
        color: {secondary} !important;
        background: {secondary_soft} !important;
    }}

    .rank-number.third {{
        color: {accent} !important;
        background: {accent_soft} !important;
    }}

    .million-badge {{
        color: {accent} !important;
        background: {accent_soft} !important;
        border-color: {mix_hex(accent, surface, .48)} !important;
    }}

    .screen-pill {{
        color: {surface_text} !important;
        background: {soft} !important;
        border-color: {line} !important;
    }}

    .soft-note {{
        color: {surface_text} !important;
        background:
            linear-gradient(120deg, {soft}, {soft_2}, {soft}) !important;
        background-size: 240% 240% !important;
        border-color: {line} !important;
    }}

    div[data-baseweb="select"] > div,
    [data-testid="stTextInput"] input,
    [data-testid="stDateInput"] input {{
        color: {surface_text} !important;
        background: {surface} !important;
        border-color: {line} !important;
    }}

    /* ---------- PREMIUM HERO THEME ---------- */
    .hero.hero-cinema {{
        background:
            radial-gradient(circle at 81% 28%, {rgba_hex(primary, .31)}, transparent 27%),
            radial-gradient(circle at 68% 112%, {rgba_hex(secondary, .29)}, transparent 40%),
            radial-gradient(circle at 7% 0%, {rgba_hex(accent, .11)}, transparent 31%),
            linear-gradient(135deg, {hero_a} 0%, {hero_b} 36%, {hero_c} 72%, {hero_surface} 100%) !important;
        border-color: {rgba_hex(primary, .24)} !important;
        box-shadow:
            0 38px 90px rgba(0,0,0,.34),
            0 0 {glow_px + 18}px {rgba_hex(primary, glow_alpha_soft)},
            inset 0 1px 0 rgba(255,255,255,.10) !important;
    }}

    .hero-cinema-scan {{
        background:
            linear-gradient(
                180deg,
                transparent,
                {rgba_hex(primary, .04)} 35%,
                {rgba_hex(primary, .17)} 50%,
                {rgba_hex(primary, .04)} 65%,
                transparent
            ) !important;
    }}

    .hero-corner-tl {{
        border-left-color: {rgba_hex(primary, .60)} !important;
        border-top-color: {rgba_hex(primary, .60)} !important;
    }}

    .hero-corner-br {{
        border-right-color: {rgba_hex(secondary, .58)} !important;
        border-bottom-color: {rgba_hex(secondary, .58)} !important;
    }}

    .hero-live-badge {{
        color: {mix_hex("#FFFFFF", primary, .20)} !important;
        border-color: {rgba_hex(primary, .22)} !important;
    }}

    .hero-live-badge::before,
    .hero-rank-live::before {{
        background: {primary} !important;
        box-shadow: 0 0 {glow_px}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .hero-verified {{
        color: {mix_hex("#FFFFFF", secondary, .22)} !important;
        background: {rgba_hex(secondary, .10)} !important;
        border-color: {rgba_hex(secondary, .22)} !important;
    }}

    .hero-overline,
    .hero-rank-live,
    .hero-rail-rank {{
        color: {primary} !important;
    }}

    .hero-overline::after {{
        background: linear-gradient(90deg, {rgba_hex(primary, .78)}, transparent) !important;
    }}

    .hero-overline::before {{
        background: {primary} !important;
        box-shadow: 0 0 {glow_px}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .hero-title-movie {{
        background:
            linear-gradient(
                105deg,
                #FFFFFF 0%,
                #FFFFFF 29%,
                {mix_hex("#FFFFFF", primary, .36)} 42%,
                {mix_hex("#FFFFFF", secondary, .40)} 50%,
                #FFFFFF 62%,
                #FFFFFF 100%
            ) !important;
        background-size: 260% auto !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        color: transparent !important;
    }}

    .hero-stat-card {{
        border-color: {rgba_hex(primary, .18)} !important;
        background:
            linear-gradient(145deg, {rgba_hex(primary, .10)}, rgba(255,255,255,.035)) !important;
    }}

    .hero-stat-card:hover {{
        border-color: {rgba_hex(primary, .34)} !important;
        background:
            linear-gradient(145deg, {rgba_hex(primary, .16)}, {rgba_hex(secondary, .07)}) !important;
    }}

    .hero-radar-ring.one {{
        border-color: {rgba_hex(primary, .20)} !important;
        border-left-color: {rgba_hex(primary, .76)} !important;
        border-top-color: {rgba_hex(primary, .46)} !important;
    }}

    .hero-radar-ring.two {{
        border-color: {rgba_hex(secondary, .22)} !important;
        border-right-color: {rgba_hex(secondary, .80)} !important;
    }}

    .hero-radar-ring.three {{
        border-color: {rgba_hex(primary, .16)} !important;
        box-shadow:
            0 0 {glow_px + 20}px {rgba_hex(primary, glow_alpha_soft)},
            inset 0 0 40px {rgba_hex(primary, .05)} !important;
    }}

    .hero-radar-cross {{
        background:
            linear-gradient(90deg, transparent 49.8%, {primary} 50%, transparent 50.2%),
            linear-gradient(transparent 49.8%, {primary} 50%, transparent 50.2%) !important;
    }}

    .hero-rank-core {{
        background:
            radial-gradient(circle at 80% 3%, {rgba_hex(primary, .22)}, transparent 32%),
            linear-gradient(155deg, {mix_hex(hero_surface, primary, .12)}, {hero_a}) !important;
        border-color: {rgba_hex(primary, .28)} !important;
        box-shadow:
            0 28px 64px rgba(0,0,0,.30),
            0 0 {glow_px + 18}px {rgba_hex(primary, glow_alpha_soft)},
            inset 0 1px 0 rgba(255,255,255,.08) !important;
    }}

    .hero-rank-core::before {{
        border-left-color: {rgba_hex(primary, .68)} !important;
        border-top-color: {rgba_hex(primary, .68)} !important;
    }}

    .hero-rank-core::after {{
        border-right-color: {rgba_hex(secondary, .62)} !important;
        border-bottom-color: {rgba_hex(secondary, .62)} !important;
    }}

    .hero-rank-number {{
        background:
            linear-gradient(180deg, #FFFFFF 0%, {mix_hex("#FFFFFF", primary, .33)} 52%, {primary} 100%) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
        color: transparent !important;
    }}

    .hero-rank-divider {{
        background:
            linear-gradient(90deg, transparent, {rgba_hex(primary, .52)}, transparent) !important;
    }}

    .hero-eq span {{
        background: linear-gradient(180deg, {mix_hex("#FFFFFF", primary, .38)}, {primary}) !important;
        box-shadow: 0 0 {glow_px}px {rgba_hex(primary, glow_alpha)} !important;
    }}

    .hero-rank-trend span {{
        color: {mix_hex("#FFFFFF", primary, .24)} !important;
        background: {rgba_hex(primary, .11)} !important;
        border-color: {rgba_hex(primary, .20)} !important;
    }}

    .hero-bottom-rail {{
        background:
            linear-gradient(90deg, {hero_a}, {hero_b}, {hero_a}) !important;
        border-top-color: {rgba_hex(primary, .16)} !important;
    }}

    .hero-bottom-rail::before {{
        background: linear-gradient(90deg, {hero_a}, transparent) !important;
    }}

    .hero-bottom-rail::after {{
        background: linear-gradient(-90deg, {hero_a}, transparent) !important;
    }}

    .hero-rail-name {{
        color: {mix_hex("#FFFFFF", primary, .12)} !important;
    }}

    .hero-rail-sep {{
        background: {mix_hex(primary, hero_a, .45)} !important;
    }}
    """


def person_short(value: float) -> str:
    value = float(value)
    if value >= 10_000:
        return f"{value / 10_000:.1f}만"
    return f"{value:,.0f}"


def won_short(value: float) -> str:
    value = float(value)
    if value >= 100_000_000:
        return f"{value / 100_000_000:.1f}억"
    if value >= 10_000:
        return f"{value / 10_000:.0f}만"
    return f"{value:,.0f}"


def section_header(eyebrow: str, title: str, caption: str = ""):
    st.markdown(
        compact_html(
            f"""
            <div class="section-head">
                <div class="section-eyebrow">{html.escape(eyebrow)}</div>
                <div class="section-title">{html.escape(title)}</div>
                <div class="section-caption">{html.escape(caption)}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def metric_selector(label: str, options, default, key: str):
    if hasattr(st, "segmented_control"):
        value = st.segmented_control(
            label,
            options=options,
            default=default,
            key=key,
        )
        return value or default

    return st.radio(
        label,
        options=options,
        index=options.index(default),
        horizontal=True,
        key=key,
    )


def trend_badge(rank_inten, old_new) -> str:
    if str(old_new).upper() == "NEW":
        return "<span class='trend-new'>NEW</span>"

    try:
        n = int(rank_inten)
    except (TypeError, ValueError):
        n = 0

    if n > 0:
        return f"<span class='trend-up'>▲ {n}</span>"
    if n < 0:
        return f"<span class='trend-down'>▼ {abs(n)}</span>"

    return "<span class='trend-flat'>—</span>"


def rank_badge(rank: int) -> str:
    rank = int(rank)
    cls = "rank-number"

    if rank == 1:
        cls += " first"
    elif rank == 2:
        cls += " second"
    elif rank == 3:
        cls += " third"

    return f"<span class='{cls}'>{rank}</span>"


def render_ticker(df: pd.DataFrame):
    items = []

    for _, row in df.head(5).iterrows():
        items.append(
            f"<span class='ticker-item'>"
            f"<span class='ticker-rank'>#{int(row['rank'])}</span>"
            f"<span>{html.escape(str(row['movieNmDisplay']))}</span>"
            f"<span class='ticker-dot'></span>"
            f"<span>{int(row['audiCnt']):,}명</span>"
            f"</span>"
        )

    doubled = "".join(items + items)

    st.markdown(
        compact_html(
            f"""
            <div class="ticker-shell">
                <div class="ticker-track">{doubled}</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_podium_card(row: pd.Series, rank: int):
    name = html.escape(str(row["movieNmDisplay"]))
    audience = int(row["audiCnt"])
    accumulated = int(row["audiAcc"])
    open_dt = html.escape(str(row.get("openDt", "-")))

    first_cls = " first" if rank == 1 else ""
    chip_cls = "rank-chip gold" if rank == 1 else "rank-chip"
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
    million_text = " · 🏆 100만+" if bool(row["isMillion"]) else ""

    st.markdown(
        compact_html(
            f"""
            <div class="podium-card{first_cls}">
                <div class="{chip_cls}">{medal}</div>
                <div class="podium-name">{name}</div>
                <div class="podium-meta">개봉 {open_dt}{million_text}</div>
                <div class="podium-number">
                    {audience:,}
                    <span style="font-size:.76rem;font-weight:800;color:#96A2B1;"> 명</span>
                </div>
                <div class="podium-label">선택 날짜 일일 관객</div>
                <div style="height:.58rem"></div>
                <div style="color:#68788C;font-size:.73rem;">
                    누적 <b style="color:#334155;">{accumulated:,}명</b>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_focus_card(row: pd.Series, total_audience: int):
    movie_name = html.escape(str(row["movieNmDisplay"]))
    rank = int(row["rank"])
    audience = int(row["audiCnt"])
    accumulated = int(row["audiAcc"])
    share = audience / max(total_audience, 1) * 100

    if accumulated >= 1_000_000:
        progress_value = 100
        progress_label = "🏆 100만 관객 돌파"
    else:
        progress_value = min(accumulated / 1_000_000 * 100, 100)
        progress_label = f"100만까지 {1_000_000 - accumulated:,}명"

    st.markdown(
        compact_html(
            f"""
            <div class="focus-card">
                <div class="focus-rank">BOX OFFICE #{rank}</div>
                <div class="focus-title">{movie_name}</div>
                <div class="focus-meta">
                    TOP 10 점유율 {share:.1f}% · 스크린 {int(row['scrnCnt']):,}개
                </div>
                <div class="focus-number">
                    {audience:,}
                    <span style="font-size:.78rem;font-weight:800;color:#AFC5E3;"> 명</span>
                </div>
                <div class="focus-caption">선택 날짜 일일 관객</div>
                <div class="focus-track">
                    <div class="focus-fill" style="width:{progress_value:.1f}%"></div>
                </div>
                <div class="focus-track-label">
                    <span>{progress_label}</span>
                    <span>누적 {accumulated:,}명</span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


# =========================================================
# 5. CHARTS
# =========================================================
def make_dynamic_rank_chart(
    df: pd.DataFrame,
    metric_label: str,
    top_n: int,
):
    theme = chart_theme_colors()

    metric_map = {
        "관객수": ("audiCnt", "명", theme["primary"]),
        "누적 관객": ("audiAcc", "명", theme["secondary"]),
        "스크린": ("scrnCnt", "개", theme["accent"]),
        "매출": ("salesAmt", "원", mix_hex(theme["accent"], "#F59E0B", .46)),
    }

    col, unit, accent = metric_map[metric_label]

    chart_df = (
        df.sort_values(col, ascending=False)
        .head(int(top_n))
        .copy()
        .iloc[::-1]
    )

    labels = chart_df["movieNmDisplay"].str.slice(0, 20)

    colors = [
        accent if i == len(chart_df) - 1 else mix_hex(theme["surface"], accent, .22)
        for i in range(len(chart_df))
    ]

    text_values = []

    for value in chart_df[col]:
        if metric_label == "매출":
            text_values.append(f"{won_short(value)}원")
        else:
            text_values.append(f"{int(value):,}{unit}")

    fig = go.Figure(
        go.Bar(
            x=chart_df[col],
            y=labels,
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(width=0),
            ),
            text=text_values,
            textposition="outside",
            cliponaxis=False,
            customdata=chart_df[["rank", "movieNmDisplay"]].values,
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "박스오피스 #%{customdata[0]:.0f}<br>"
                + (
                    "%{x:,.0f}원"
                    if metric_label == "매출"
                    else f"%{{x:,.0f}}{unit}"
                )
                + "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        height=410,
        margin=dict(l=8, r=82, t=14, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hoverlabel=dict(
            bgcolor="#101827",
            bordercolor="#101827",
            font=dict(color="white", size=12),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=theme["grid"],
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=12, color=theme["text"]),
            automargin=True,
            fixedrange=True,
        ),
        font=dict(
            family='Pretendard, "Noto Sans KR", sans-serif',
            color=theme["text"],
        ),
        bargap=.36,
        transition=dict(duration=420, easing="cubic-in-out"),
    )

    return fig


def make_weekly_movie_chart(
    week_df: pd.DataFrame,
    movie_name: str,
    end_date,
):
    theme = chart_theme_colors()

    all_days = pd.DataFrame(
        {"date": pd.date_range(end=end_date, periods=7, freq="D")}
    )

    history = (
        week_df[week_df["movieNmDisplay"] == movie_name][
            ["date", "audiCnt", "rank"]
        ]
        .copy()
        .sort_values("date")
    )

    trend = all_days.merge(history, on="date", how="left")
    trend["audiCnt"] = trend["audiCnt"].fillna(0)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=trend["date"],
            y=trend["audiCnt"],
            mode="lines+markers",
            name="일일 관객",
            line=dict(
                color=theme["primary"],
                width=3,
                shape="spline",
            ),
            marker=dict(
                size=8,
                color="#FFFFFF",
                line=dict(
                    color=theme["primary"],
                    width=3,
                ),
            ),
            fill="tozeroy",
            fillcolor=rgba_hex(theme["primary"], .09),
            hovertemplate="<b>%{x|%m/%d}</b><br>%{y:,.0f}명<extra></extra>",
        )
    )

    rank_mask = trend["rank"].notna()

    if rank_mask.any():
        fig.add_trace(
            go.Scatter(
                x=trend.loc[rank_mask, "date"],
                y=trend.loc[rank_mask, "rank"],
                mode="lines+markers",
                name="순위",
                yaxis="y2",
                line=dict(
                    color=theme["secondary"],
                    width=2,
                    dash="dot",
                ),
                marker=dict(
                    size=8,
                    symbol="diamond",
                    color=theme["secondary"],
                ),
                hovertemplate=(
                    "<b>%{x|%m/%d}</b><br>"
                    "박스오피스 #%{y:.0f}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        height=360,
        margin=dict(l=18, r=22, t=16, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(
                size=10,
                color="#64748B",
            ),
        ),
        xaxis=dict(
            showgrid=False,
            tickformat="%m/%d",
            fixedrange=True,
            tickfont=dict(color=theme["muted"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=theme["grid"],
            zeroline=False,
            rangemode="tozero",
            fixedrange=True,
            tickfont=dict(color=theme["muted"]),
        ),
        yaxis2=dict(
            overlaying="y",
            side="right",
            range=[10.7, .3],
            tickmode="array",
            tickvals=[1, 3, 5, 7, 10],
            ticktext=["1위", "3위", "5위", "7위", "10위"],
            showgrid=False,
            fixedrange=True,
            tickfont=dict(
                color=theme["secondary"],
                size=10,
            ),
        ),
        font=dict(
            family='Pretendard, "Noto Sans KR", sans-serif',
            color=theme["text"],
        ),
    )

    return fig


def make_duel_radar(
    df: pd.DataFrame,
    movie_a: str,
    movie_b: str,
):
    theme = chart_theme_colors()

    a = df[df["movieNmDisplay"] == movie_a].iloc[0]
    b = df[df["movieNmDisplay"] == movie_b].iloc[0]

    specs = [
        ("일일 관객", "audiCnt"),
        ("누적 관객", "audiAcc"),
        ("스크린", "scrnCnt"),
        ("일일 매출", "salesAmt"),
    ]

    theta = []
    a_values = []
    b_values = []

    for label, col in specs:
        max_value = max(float(df[col].max()), 1.0)

        theta.append(label)
        a_values.append(float(a[col]) / max_value * 100)
        b_values.append(float(b[col]) / max_value * 100)

    theta.append("랭킹 파워")
    a_values.append((11 - int(a["rank"])) / 10 * 100)
    b_values.append((11 - int(b["rank"])) / 10 * 100)

    theta_closed = theta + [theta[0]]
    a_closed = a_values + [a_values[0]]
    b_closed = b_values + [b_values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=a_closed,
            theta=theta_closed,
            fill="toself",
            name=movie_a,
            line=dict(
                color=theme["primary"],
                width=3,
            ),
            fillcolor=rgba_hex(theme["primary"], .15),
            marker=dict(size=6),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=b_closed,
            theta=theta_closed,
            fill="toself",
            name=movie_b,
            line=dict(
                color=theme["secondary"],
                width=3,
            ),
            fillcolor=rgba_hex(theme["secondary"], .12),
            marker=dict(size=6),
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=36, r=36, t=44, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=.5,
            font=dict(size=10),
        ),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                showticklabels=False,
                gridcolor=theme["grid"],
                linecolor=theme["grid"],
            ),
            angularaxis=dict(
                gridcolor=theme["grid"],
                linecolor=theme["grid"],
                tickfont=dict(
                    size=11,
                    color=theme["muted"],
                ),
            ),
        ),
        font=dict(
            family='Pretendard, "Noto Sans KR", sans-serif',
            color=theme["text"],
        ),
    )

    return fig


def duel_summary(
    df: pd.DataFrame,
    movie_a: str,
    movie_b: str,
):
    a = df[df["movieNmDisplay"] == movie_a].iloc[0]
    b = df[df["movieNmDisplay"] == movie_b].iloc[0]

    diff = int(a["audiCnt"]) - int(b["audiCnt"])

    if diff > 0:
        return (
            f"<b>{html.escape(movie_a)}</b>가 오늘 일일 관객에서 "
            f"<b>{diff:,}명</b> 앞서고 있습니다."
        )

    if diff < 0:
        return (
            f"<b>{html.escape(movie_b)}</b>가 오늘 일일 관객에서 "
            f"<b>{abs(diff):,}명</b> 앞서고 있습니다."
        )

    return "두 영화의 오늘 일일 관객수는 정확히 같습니다."


# =========================================================
# 6. TABLE
# =========================================================
def make_rank_table(
    df: pd.DataFrame,
    selected_date,
    total_audience: int,
) -> str:
    rows = []
    share_base = max(total_audience, 1)

    for _, row in df.iterrows():
        rank = int(row["rank"])
        movie_name = html.escape(str(row["movieNmDisplay"]))
        audience = int(row["audiCnt"])
        accumulated = int(row["audiAcc"])
        screens = int(row["scrnCnt"])
        share = audience / share_base * 100
        share_width = min(max(share, 2.5), 100)

        million = (
            "<span class='million-badge'>🏆 100만+</span>"
            if bool(row["isMillion"])
            else ""
        )

        rows.append(
            f"<tr class='rank-row-{rank}'>"
            f"<td>{rank_badge(rank)}</td>"
            f"<td>{trend_badge(row.get('rankInten', 0), row.get('rankOldAndNew', ''))}</td>"
            f"<td class='movie-cell'>"
            f"<div class='movie-line'>"
            f"<span class='movie-name'>{movie_name}</span>"
            f"{million}"
            f"</div>"
            f"</td>"
            f"<td>{html.escape(str(row.get('openDt', '-')))}</td>"
            f"<td class='audience-cell'>"
            f"<div class='audience-value'>"
            f"{audience:,}<span class='audience-unit'>명</span>"
            f"</div>"
            f"<div class='share-row'>"
            f"<div class='share-track'>"
            f"<div class='share-fill' style='width:{share_width:.1f}%'></div>"
            f"</div>"
            f"<span class='share-label'>{share:.1f}%</span>"
            f"</div>"
            f"</td>"
            f"<td class='num-cell'>{accumulated:,}</td>"
            f"<td><span class='screen-pill'>{screens:,}</span></td>"
            f"</tr>"
        )

    date_label = selected_date.strftime("%Y.%m.%d")

    table_html = (
        "<div class='ranking-panel'>"
        "<div class='ranking-toolbar'>"
        "<div class='ranking-toolbar-left'>"
        "<span class='ranking-live'></span>"
        "<span class='ranking-toolbar-title'>Daily Box Office · Top 10</span>"
        "</div>"
        f"<div class='ranking-toolbar-meta'>{date_label} 기준 · {len(df)}편 표시</div>"
        "</div>"
        "<div class='ranking-scroll'>"
        "<table class='custom-table'>"
        "<thead>"
        "<tr>"
        "<th>Rank</th>"
        "<th>Trend</th>"
        "<th class='movie-head'>Movie</th>"
        "<th>Release</th>"
        "<th style='text-align:right;'>Daily audience</th>"
        "<th style='text-align:right;'>Total audience</th>"
        "<th>Screens</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</div>"
        "<div class='ranking-footer'>"
        "<span>순위 변동은 전일 대비 · 관객 비중은 원본 TOP 10 기준</span>"
        "<span>Source · KOBIS</span>"
        "</div>"
        "</div>"
    )

    return compact_html(table_html)


# =========================================================
# 7. MAIN
# =========================================================
def main():
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    yesterday = (now_kst - timedelta(days=1)).date()

    # ---------- Sidebar Control Center ----------
    theme_presets = {
        "Cinema Blue": {
            "theme_primary": "#3182F6",
            "theme_secondary": "#8B5CF6",
            "theme_accent": "#16A3A3",
            "theme_bg": "#F4F7FB",
            "theme_surface": "#FFFFFF",
        },
        "Neon Violet": {
            "theme_primary": "#7C3AED",
            "theme_secondary": "#EC4899",
            "theme_accent": "#22D3EE",
            "theme_bg": "#080A13",
            "theme_surface": "#111827",
        },
        "Cyber Lime": {
            "theme_primary": "#84CC16",
            "theme_secondary": "#22C55E",
            "theme_accent": "#06B6D4",
            "theme_bg": "#07110A",
            "theme_surface": "#0E1B11",
        },
        "Crimson Rush": {
            "theme_primary": "#EF4444",
            "theme_secondary": "#F97316",
            "theme_accent": "#FACC15",
            "theme_bg": "#12090A",
            "theme_surface": "#1F1113",
        },
        "Aurora": {
            "theme_primary": "#06B6D4",
            "theme_secondary": "#8B5CF6",
            "theme_accent": "#EC4899",
            "theme_bg": "#07111A",
            "theme_surface": "#0D1A27",
        },
        "Bubblegum": {
            "theme_primary": "#FF4D8D",
            "theme_secondary": "#8B5CF6",
            "theme_accent": "#22D3EE",
            "theme_bg": "#FFF4FA",
            "theme_surface": "#FFFFFF",
        },
    }

    for key, value in theme_presets["Cinema Blue"].items():
        st.session_state.setdefault(key, value)

    st.session_state.setdefault("theme_glow", 72)
    st.session_state.setdefault("theme_sync_charts", True)

    def apply_theme_preset(name: str):
        palette = theme_presets[name]
        for key, value in palette.items():
            st.session_state[key] = value

    def randomize_theme():
        palette = make_random_palette()
        for key, value in palette.items():
            st.session_state[key] = value

    def reset_theme():
        apply_theme_preset("Cinema Blue")
        st.session_state["theme_glow"] = 72
        st.session_state["theme_sync_charts"] = True

    def set_quick_date(days_back: int):
        st.session_state["selected_date"] = yesterday - timedelta(days=days_back)

    with st.sidebar:
        st.markdown(
            compact_html(
                """
                <div class="sidebar-command">
                    <div class="sidebar-command-top">
                        <span class="sidebar-command-dot"></span>
                        BOXOFFICE CONTROL
                    </div>
                    <div class="sidebar-command-title">🎬 Command Center</div>
                    <div class="sidebar-command-sub">
                        날짜부터 화면 모션, 분석 기본값까지<br>
                        여기서 대시보드 전체를 조종합니다.
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        side_tabs = st.tabs(["🗓️ 조회", "🎛️ 화면", "🎨 색상", "📊 분석", "⚡ 요약"])

        with side_tabs[0]:
            st.markdown(
                '<div class="side-section-label">Quick date</div>',
                unsafe_allow_html=True,
            )

            if "selected_date" not in st.session_state:
                st.session_state["selected_date"] = yesterday

            q1, q2, q3 = st.columns(3, gap="small")

            with q1:
                st.button(
                    "어제",
                    width="stretch",
                    on_click=set_quick_date,
                    args=(0,),
                    key="quick_yesterday",
                )

            with q2:
                st.button(
                    "-3일",
                    width="stretch",
                    on_click=set_quick_date,
                    args=(3,),
                    key="quick_3days",
                )

            with q3:
                st.button(
                    "-7일",
                    width="stretch",
                    on_click=set_quick_date,
                    args=(7,),
                    key="quick_7days",
                )

            selected_date = st.date_input(
                "조회 날짜",
                max_value=yesterday,
                key="selected_date",
                format="YYYY/MM/DD",
                help="당일 데이터는 집계 중일 수 있어 어제까지 조회합니다.",
            )

            st.markdown(
                compact_html(
                    f"""
                    <div class="side-mini-card">
                        <div class="side-mini-label">SELECTED</div>
                        <div class="side-mini-value">
                            {selected_date.strftime("%Y.%m.%d")}
                        </div>
                        <div class="side-mini-note">
                            이 날짜를 기준으로 모든 차트와 순위표가 갱신됩니다.
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="sidebar-tip">
                    💡 날짜를 바꾸면 포커스 차트도 선택 날짜를 마지막 날로 잡아
                    최근 7일 흐름을 다시 계산합니다.
                </div>
                """,
                unsafe_allow_html=True,
            )

        with side_tabs[1]:
            st.markdown(
                '<div class="side-section-label">Motion & layout</div>',
                unsafe_allow_html=True,
            )

            motion_mode = st.select_slider(
                "모션 강도",
                options=["OFF", "SOFT", "MAX"],
                value="MAX",
                key="motion_mode",
                help="OFF는 정지, SOFT는 절제된 모션, MAX는 시스템 모션 제한보다 우선하는 풀모션입니다.",
            )

            density_mode = st.radio(
                "화면 밀도",
                ["여유롭게", "컴팩트"],
                horizontal=True,
                key="density_mode",
            )

            show_hero = st.toggle(
                "시네마 히어로 표시",
                value=True,
                key="show_hero",
            )

            show_ticker = st.toggle(
                "자동 영화 티커 표시",
                value=True,
                key="show_ticker",
            )

            st.markdown(
                """
                <div class="side-feature-list">
                    <div class="side-feature">
                        <span class="side-feature-icon">✦</span>
                        모션 강도는 페이지 전체에 즉시 반영
                    </div>
                    <div class="side-feature">
                        <span class="side-feature-icon">◫</span>
                        히어로·티커를 발표 상황에 맞게 숨김
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        with side_tabs[2]:
            st.markdown(
                compact_html(
                    f"""
                    <div class="theme-studio-head">
                        <div class="theme-studio-kicker">LIVE THEME ENGINE</div>
                        <div class="theme-studio-title">🎨 Color Studio</div>
                        <div class="theme-studio-sub">
                            원하는 색을 찍으면 사이트 전체가 즉시 그 팔레트로 재도색됩니다.
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="side-section-label">Preset palette</div>',
                unsafe_allow_html=True,
            )

            pr1, pr2 = st.columns(2, gap="small")
            with pr1:
                st.button(
                    "🌊 Cinema",
                    width="stretch",
                    on_click=apply_theme_preset,
                    args=("Cinema Blue",),
                    key="preset_cinema",
                )
                st.button(
                    "💚 Cyber",
                    width="stretch",
                    on_click=apply_theme_preset,
                    args=("Cyber Lime",),
                    key="preset_cyber",
                )
                st.button(
                    "🌌 Aurora",
                    width="stretch",
                    on_click=apply_theme_preset,
                    args=("Aurora",),
                    key="preset_aurora",
                )

            with pr2:
                st.button(
                    "🟣 Violet",
                    width="stretch",
                    on_click=apply_theme_preset,
                    args=("Neon Violet",),
                    key="preset_violet",
                )
                st.button(
                    "🔥 Crimson",
                    width="stretch",
                    on_click=apply_theme_preset,
                    args=("Crimson Rush",),
                    key="preset_crimson",
                )
                st.button(
                    "🍬 Bubble",
                    width="stretch",
                    on_click=apply_theme_preset,
                    args=("Bubblegum",),
                    key="preset_bubble",
                )

            rr1, rr2 = st.columns(2, gap="small")
            with rr1:
                st.button(
                    "🎲 조화 랜덤",
                    width="stretch",
                    on_click=randomize_theme,
                    key="random_theme",
                )
            with rr2:
                st.button(
                    "↺ 기본값",
                    width="stretch",
                    on_click=reset_theme,
                    key="reset_theme",
                )

            st.markdown(
                '<div class="side-section-label" style="margin-top:.8rem;">Custom colors</div>',
                unsafe_allow_html=True,
            )

            theme_primary = st.color_picker(
                "메인 컬러",
                key="theme_primary",
                help="버튼, 랭크, 핵심 글로우, 차트의 중심색입니다.",
            )

            theme_secondary = st.color_picker(
                "서브 컬러",
                key="theme_secondary",
                help="그라데이션, 홀로그램, 보조 차트 색상입니다.",
            )

            theme_accent = st.color_picker(
                "강조 컬러",
                key="theme_accent",
                help="배지, 3순위 계열, 보조 포인트에 사용됩니다.",
            )

            theme_bg = st.color_picker(
                "전체 배경",
                key="theme_bg",
            )

            theme_surface = st.color_picker(
                "카드 / 패널",
                key="theme_surface",
            )

            st.markdown(
                compact_html(
                    f"""
                    <div class="palette-preview">
                        <div class="palette-swatch" style="background:{theme_primary};"></div>
                        <div class="palette-swatch" style="background:{theme_secondary};"></div>
                        <div class="palette-swatch" style="background:{theme_accent};"></div>
                        <div class="palette-swatch" style="background:{theme_bg};"></div>
                        <div class="palette-swatch" style="background:{theme_surface};"></div>
                    </div>

                    <div class="palette-code">
                        <div class="palette-code-item"><b>PRIMARY</b>{theme_primary}</div>
                        <div class="palette-code-item"><b>SECONDARY</b>{theme_secondary}</div>
                        <div class="palette-code-item"><b>ACCENT</b>{theme_accent}</div>
                        <div class="palette-code-item"><b>BACKGROUND</b>{theme_bg}</div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

            theme_glow = st.slider(
                "네온 글로우",
                min_value=0,
                max_value=100,
                key="theme_glow",
                help="0은 깔끔한 플랫, 100은 네온 폭발입니다.",
            )

            theme_sync_charts = st.toggle(
                "차트 색상도 팔레트와 동기화",
                key="theme_sync_charts",
            )

            surface_mode = "DARK" if color_luminance(theme_surface) < .38 else "LIGHT"
            st.markdown(
                compact_html(
                    f"""
                    <div class="theme-status">
                        <span class="theme-status-dot"></span>
                        <span>
                            <b>{surface_mode} SURFACE</b><br>
                            텍스트 대비는 선택한 카드색에 맞춰 자동 계산됩니다.
                        </span>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

        with side_tabs[3]:
            st.markdown(
                '<div class="side-section-label">Analysis defaults</div>',
                unsafe_allow_html=True,
            )

            sidebar_metric = st.selectbox(
                "기본 비교 지표",
                ["관객수", "누적 관객", "스크린", "매출"],
                index=0,
                key="sidebar_metric",
            )

            sidebar_top_n = st.slider(
                "기본 표시 영화 수",
                min_value=3,
                max_value=10,
                value=7,
                step=1,
                key="sidebar_top_n",
            )

            st.markdown(
                """
                <div class="side-feature-list">
                    <div class="side-feature">
                        <span class="side-feature-icon">↗</span>
                        본문에서 지표와 영화 수를 다시 조절 가능
                    </div>
                    <div class="side-feature">
                        <span class="side-feature-icon">◎</span>
                        MOVIE FOCUS로 최근 7일 흐름 추적
                    </div>
                    <div class="side-feature">
                        <span class="side-feature-icon">VS</span>
                        MOVIE DUEL로 두 작품 정규화 비교
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="sidebar-tip">
                    📊 이 탭은 분석실의 초기 세팅을 빠르게 정하는 프리셋입니다.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # 요약 탭은 데이터 로딩 후 아래에서 채웁니다.

    # ---------- Dynamic presentation overrides ----------
    override_rules = []

    if motion_mode == "OFF":
        override_rules.append(
            """
            *, *::before, *::after {
                animation: none !important;
                transition-duration: .01ms !important;
            }
            """
        )

    elif motion_mode == "SOFT":
        # 시스템의 prefers-reduced-motion 보다 사용자가 직접 고른 SOFT가 우선합니다.
        # animation shorthand를 !important로 다시 선언해 duration뿐 아니라
        # iteration-count까지 확실하게 복구합니다.
        override_rules.append(
            """
            .hero::after,
            .hero-grid::after,
            .ranking-scroll::after {
                display: none !important;
            }

            .stApp {
                animation: ambientGradientDrift 22s ease-in-out infinite !important;
            }

            .hero {
                animation: heroPulseDepth 11s ease-in-out infinite !important;
            }

            .hero::before {
                animation: starDrift 18s linear infinite !important;
            }

            .hero-orb.a {
                animation: heroFloatA 13s ease-in-out infinite !important;
            }

            .hero-orb.b {
                animation: heroFloatB 15s ease-in-out infinite !important;
            }

            .hero-beam {
                animation: beamSweep 13s ease-in-out infinite !important;
                opacity: .42;
            }

            .hero-kicker::before,
            .sidebar-command-dot {
                animation: livePulse 3.2s ease-in-out infinite !important;
            }

            .ticker-track {
                animation: tickerMove 38s linear infinite !important;
            }

            .kpi-card:nth-child(1) {
                animation: cardFloatA 10s ease-in-out infinite !important;
            }

            .kpi-card:nth-child(2) {
                animation: cardFloatB 11s ease-in-out infinite !important;
            }

            .kpi-card:nth-child(3) {
                animation: cardFloatC 10.5s ease-in-out infinite !important;
            }

            .kpi-card:nth-child(4) {
                animation: cardFloatA 12s ease-in-out infinite !important;
            }

            .kpi-value {
                animation: shineText 13s linear infinite !important;
            }

            .podium-card.first {
                animation:
                    softGlow 10s ease-in-out infinite,
                    cardFloatA 11s ease-in-out infinite !important;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(2) .podium-card {
                animation: cardFloatB 12s ease-in-out infinite !important;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(3) .podium-card {
                animation: cardFloatC 11.5s ease-in-out infinite !important;
            }

            .section-head::after {
                animation: sectionScan 13s ease-in-out infinite !important;
            }

            .interactive-shell {
                animation: borderFlow 15s ease infinite !important;
            }

            .interactive-inner::after {
                animation: heroFloatB 16s ease-in-out infinite !important;
            }

            .focus-card {
                animation: cardFloatA 12s ease-in-out infinite !important;
            }

            .duel-vs {
                animation:
                    pulseRing 5s ease-out infinite,
                    cardFloatA 9s ease-in-out infinite !important;
            }

            .ranking-panel::after {
                animation: tableTopGlow 6s ease-in-out infinite !important;
            }

            .ranking-live {
                animation:
                    livePulse 3.2s ease-in-out infinite,
                    pulseRing 4.5s ease-out infinite !important;
            }

            .rank-number.first {
                animation: pulseRing 6s ease-out infinite !important;
            }

            .rank-number.second {
                animation: cardFloatB 9s ease-in-out infinite !important;
            }

            .rank-number.third {
                animation: cardFloatC 10s ease-in-out infinite !important;
            }

            .sidebar-command::after {
                animation: beamSweep 13s ease-in-out infinite !important;
            }

            /* reduced-motion이 transition까지 .001ms로 만든 경우도 복구 */
            .hero,
            .kpi-card,
            .podium-card,
            .focus-card,
            .stButton > button,
            .custom-table tbody tr,
            .rank-number {
                transition-duration: .22s !important;
            }

            /* EVERYTHING MOVES — SOFT 감속 */
            [data-testid="stSidebar"],
            .sidebar-command,
            [data-testid="stSidebar"] [data-baseweb="tab"],
            .side-mini-card,
            .side-stat,
            .side-feature,
            .sidebar-tip,
            .stButton > button,
            div[data-baseweb="select"] > div,
            [data-testid="stTextInput"] input,
            [data-testid="stDateInput"] input,
            [data-testid="stSlider"],
            [data-testid="stRadio"],
            [data-testid="stPlotlyChart"],
            [data-testid="stMetric"],
            .soft-note,
            div[data-testid="stAlert"] {
                animation-duration: 12s !important;
            }

            .section-title,
            .kpi-value,
            .podium-number,
            .focus-number,
            .side-rank-value {
                animation-duration: 14s !important;
            }

            .custom-table tbody tr,
            .trend-up,
            .trend-down,
            .trend-new,
            .trend-flat,
            .million-badge,
            .screen-pill {
                animation-duration: 10s !important;
            }

            """
        )

    elif motion_mode == "MAX":
        # MAX는 사용자의 명시적 선택이므로 시스템 reduced-motion보다 강하게 우선합니다.
        override_rules.append(
            """

            /* EVERYTHING MOVES — MAX 강제 복구 */
            [data-testid="stSidebar"] {
                animation: sidebarGlow 4.8s ease-in-out infinite !important;
            }

            .sidebar-command {
                animation:
                    breatheScale 5.2s ease-in-out infinite,
                    borderBreath 6.5s ease-in-out infinite !important;
            }

            .sidebar-command-title {
                animation: shineText 7s linear infinite !important;
            }

            .sidebar-command-sub,
            .section-caption,
            .panel-sub,
            .focus-meta,
            .focus-caption,
            .ranking-toolbar-meta {
                animation: softBlink 5.5s ease-in-out infinite !important;
            }

            [data-testid="stSidebar"] [data-baseweb="tab"] {
                animation: tabPulse 4s ease-in-out infinite !important;
            }

            .side-mini-card,
            .side-feature,
            .sidebar-tip,
            .duel-result {
                animation: microFloat 5.2s ease-in-out infinite !important;
            }

            .side-stat:nth-child(odd) {
                animation: microFloat 4.9s ease-in-out infinite !important;
            }

            .side-stat:nth-child(even) {
                animation: microFloatReverse 5.1s ease-in-out infinite !important;
            }

            .side-feature-icon {
                animation: iconNudge 3.8s ease-in-out infinite !important;
            }

            .side-rank-card {
                animation:
                    breatheScale 5.8s ease-in-out infinite,
                    borderBreath 7s ease-in-out infinite !important;
            }

            .side-rank-chip,
            .rank-chip,
            .focus-rank,
            .million-badge,
            .screen-pill,
            .trend-up,
            .trend-down,
            .trend-new,
            .trend-flat {
                animation: badgePulse 4.2s ease-in-out infinite !important;
            }

            .side-rank-value,
            .section-title,
            .podium-number,
            .focus-number,
            .kpi-value {
                animation: shineText 7.5s linear infinite !important;
            }

            .stButton > button {
                animation:
                    microFloat 4.8s ease-in-out infinite,
                    borderBreath 6s ease-in-out infinite !important;
            }

            div[data-baseweb="select"] > div,
            [data-testid="stTextInput"] input,
            [data-testid="stDateInput"] input {
                animation: inputGlow 4.4s ease-in-out infinite !important;
            }

            [data-testid="stSlider"] {
                animation: microFloat 5.3s ease-in-out infinite !important;
            }

            [data-testid="stRadio"] {
                animation: microFloatReverse 5.6s ease-in-out infinite !important;
            }

            [data-testid="stWidgetLabel"],
            [data-testid="stCaptionContainer"],
            .kpi-label,
            .kpi-note,
            .podium-name,
            .panel-title,
            .movie-name,
            .audience-value,
            .num-cell,
            .ranking-footer span {
                animation: softBlink 5.7s ease-in-out infinite !important;
            }

            .hero-title {
                animation:
                    breatheScale 6s ease-in-out infinite,
                    softBlink 4.8s ease-in-out infinite !important;
            }

            .hero-sub {
                animation: softBlink 5.5s ease-in-out infinite !important;
            }

            .hero-date {
                animation: badgePulse 4.7s ease-in-out infinite !important;
            }

            .hero-chip:nth-child(odd) {
                animation: microFloat 4.8s ease-in-out infinite !important;
            }

            .hero-chip:nth-child(even) {
                animation: microFloatReverse 5.2s ease-in-out infinite !important;
            }

            .section-eyebrow {
                animation: badgePulse 4.4s ease-in-out infinite !important;
            }

            [data-testid="stPlotlyChart"] {
                animation: chartBreath 6.5s ease-in-out infinite !important;
            }

            .focus-fill,
            .share-fill {
                animation: progressGlow 4s ease-in-out infinite !important;
            }

            [data-testid="stMetric"] {
                animation:
                    microFloat 5.6s ease-in-out infinite,
                    borderBreath 6.8s ease-in-out infinite !important;
            }

            [data-testid="stMetric"]::after {
                animation: glowSweep 7.8s ease-in-out infinite !important;
            }

            [data-testid="stMetricValue"] {
                animation: badgePulse 4.6s ease-in-out infinite !important;
            }

            .custom-table thead th {
                animation: tableShimmer 12s linear infinite !important;
            }

            .custom-table tbody tr:nth-child(odd) {
                animation: rowWave 6s ease-in-out infinite !important;
            }

            .custom-table tbody tr:nth-child(even) {
                animation: rowWave 6.6s ease-in-out infinite reverse !important;
            }

            div[data-testid="stAlert"] {
                animation:
                    microFloat 5.5s ease-in-out infinite,
                    borderBreath 7s ease-in-out infinite !important;
            }

            .soft-note {
                animation:
                    noteGlow 9s ease-in-out infinite,
                    microFloat 6.2s ease-in-out infinite !important;
            }
            .hero::after,
            .hero-grid::after,
            .ranking-scroll::after {
                display: block !important;
            }

            .stApp {
                animation: ambientGradientDrift 13s ease-in-out infinite !important;
            }

            .hero {
                animation:
                    heroPulseDepth 5.5s ease-in-out infinite,
                    fadeRise .7s ease 1 both !important;
            }

            .hero::before {
                animation: starDrift 10s linear infinite !important;
            }

            .hero::after {
                animation: laserFly1 7.5s ease-in-out infinite !important;
            }

            .hero-grid::after {
                animation: laserFly2 9s ease-in-out infinite !important;
            }

            .hero-orb.a {
                animation: heroFloatA 7s ease-in-out infinite !important;
            }

            .hero-orb.b {
                animation: heroFloatB 8.5s ease-in-out infinite !important;
            }

            .hero-beam {
                animation: beamSweep 6.8s ease-in-out infinite !important;
                opacity: 1;
            }

            .hero-kicker::before {
                animation: livePulse 1.8s ease-in-out infinite !important;
            }

            .ticker-track {
                animation: tickerMove 20s linear infinite !important;
            }

            .section-head {
                animation: fadeRise .55s ease 1 both !important;
            }

            .section-head::after {
                animation: sectionScan 6.8s ease-in-out infinite !important;
            }

            .kpi-grid {
                animation: fadeRise .6s ease 1 both !important;
            }

            .kpi-card:nth-child(1) {
                animation: cardFloatA 4.8s ease-in-out infinite !important;
            }

            .kpi-card:nth-child(2) {
                animation: cardFloatB 5.4s ease-in-out infinite !important;
            }

            .kpi-card:nth-child(3) {
                animation: cardFloatC 5s ease-in-out infinite !important;
            }

            .kpi-card:nth-child(4) {
                animation: cardFloatA 5.8s ease-in-out infinite !important;
            }

            .kpi-value {
                animation: shineText 6.5s linear infinite !important;
            }

            .podium-card.first {
                animation:
                    softGlow 4.8s ease-in-out infinite,
                    cardFloatA 5.6s ease-in-out infinite !important;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(2) .podium-card {
                animation: cardFloatB 6.2s ease-in-out infinite !important;
            }

            div[data-testid="stHorizontalBlock"] > div:nth-child(3) .podium-card {
                animation: cardFloatC 5.8s ease-in-out infinite !important;
            }

            .interactive-shell {
                animation: borderFlow 8s ease infinite !important;
            }

            .interactive-inner::after {
                animation: heroFloatB 9s ease-in-out infinite !important;
            }

            .focus-card {
                animation: cardFloatA 6.3s ease-in-out infinite !important;
            }

            .duel-vs {
                animation:
                    pulseRing 2.7s ease-out infinite,
                    cardFloatA 4.4s ease-in-out infinite !important;
            }

            .ranking-panel {
                animation: fadeRise .55s ease 1 both !important;
            }

            .ranking-panel::after {
                animation: tableTopGlow 3s ease-in-out infinite !important;
            }

            .ranking-scroll::after {
                animation: rankScan 9.5s ease-in-out infinite !important;
            }

            .ranking-live {
                animation:
                    livePulse 1.8s ease-in-out infinite,
                    pulseRing 2.4s ease-out infinite !important;
            }

            .rank-number.first {
                animation: pulseRing 3.2s ease-out infinite !important;
            }

            .rank-number.second {
                animation: cardFloatB 4.8s ease-in-out infinite !important;
            }

            .rank-number.third {
                animation: cardFloatC 5.2s ease-in-out infinite !important;
            }

            .sidebar-command::after {
                animation: beamSweep 7s ease-in-out infinite !important;
            }

            .sidebar-command-dot {
                animation: livePulse 1.8s ease-in-out infinite !important;
            }

            /* MAX에서는 hover/버튼 전환 효과도 복구 */
            .hero,
            .kpi-card,
            .podium-card,
            .focus-card,
            .stButton > button,
            .custom-table tbody tr,
            .rank-number,
            .hero-chip {
                transition-duration: .22s !important;
            }
            """
        )


    # ---------- Premium hero motion profile ----------
    if motion_mode == "SOFT":
        override_rules.append(
            """
            .hero-cinema-scan { animation: heroEdgeScan 16s ease-in-out infinite !important; }
            .hero-live-badge::before,
            .hero-rank-live::before { animation: livePulse 3s ease-in-out infinite !important; }
            .hero-title-v2 { animation: heroTitleGlow 10s ease-in-out infinite !important; }
            .hero-title-movie { animation: shineText 13s linear infinite !important; }
            .hero-stat-card::after { animation: heroGlassSweep 14s ease-in-out infinite !important; }
            .hero-radar-ring.one { animation: heroRadarSpin 26s linear infinite !important; }
            .hero-radar-ring.two { animation: heroRadarSpinReverse 20s linear infinite !important; }
            .hero-radar-ring.three { animation: heroHaloPulse 9s ease-in-out infinite !important; }
            .hero-rank-core { animation: heroRankFloat 10s ease-in-out infinite !important; }
            .hero-rank-number { animation: heroRankGlow 8s ease-in-out infinite !important; }
            .hero-eq span { animation: heroBarDance 3s ease-in-out infinite !important; }
            .hero-rail-track { animation: heroMarquee 34s linear infinite !important; }
            """
        )

    elif motion_mode == "MAX":
        override_rules.append(
            """
            .hero.hero-cinema {
                animation:
                    heroFrameBreath 5.7s ease-in-out infinite,
                    heroPulseDepth 7s ease-in-out infinite !important;
            }
            .hero-cinema-scan { animation: heroEdgeScan 8.5s ease-in-out infinite !important; }
            .hero-live-badge::before,
            .hero-rank-live::before { animation: livePulse 1.7s ease-in-out infinite !important; }
            .hero-title-v2 { animation: heroTitleGlow 5s ease-in-out infinite !important; }
            .hero-title-movie { animation: shineText 6.8s linear infinite !important; }
            .hero-stat-card::after { animation: heroGlassSweep 7s ease-in-out infinite !important; }
            .hero-radar-ring.one { animation: heroRadarSpin 13s linear infinite !important; }
            .hero-radar-ring.two { animation: heroRadarSpinReverse 9s linear infinite !important; }
            .hero-radar-ring.three { animation: heroHaloPulse 4.3s ease-in-out infinite !important; }
            .hero-rank-core { animation: heroRankFloat 5s ease-in-out infinite !important; }
            .hero-rank-number { animation: heroRankGlow 3.8s ease-in-out infinite !important; }
            .hero-eq span { animation: heroBarDance 1.45s ease-in-out infinite !important; }
            .hero-rail-track { animation: heroMarquee 18s linear infinite !important; }
            """
        )

    if density_mode == "컴팩트":
        override_rules.append(
            """
            .section-head {
                margin-top: 1.65rem !important;
                margin-bottom: .7rem !important;
            }
            .custom-table tbody td {
                padding-top: 10px !important;
                padding-bottom: 10px !important;
            }
            .kpi-card,
            .podium-card {
                padding: .95rem !important;
            }
            """
        )

    if override_rules:
        st.markdown(
            "<style>" + "\n".join(override_rules) + "</style>",
            unsafe_allow_html=True,
        )

    # ---------- Live Theme Engine ----------
    theme_primary = st.session_state["theme_primary"]
    theme_secondary = st.session_state["theme_secondary"]
    theme_accent = st.session_state["theme_accent"]
    theme_bg = st.session_state["theme_bg"]
    theme_surface = st.session_state["theme_surface"]
    theme_glow = st.session_state["theme_glow"]

    st.markdown(
        "<style>"
        + build_theme_css(
            theme_primary,
            theme_secondary,
            theme_accent,
            theme_bg,
            theme_surface,
            theme_glow,
        )
        + "</style>",
        unsafe_allow_html=True,
    )

    # ---------- API key ----------
    if "KOBIS_KEY" not in st.secrets:
        st.error(
            "`.streamlit/secrets.toml` 또는 Streamlit Cloud Secrets에 "
            "`KOBIS_KEY`를 등록해 주세요."
        )
        return

    api_key = st.secrets["KOBIS_KEY"]
    target_dt = selected_date.strftime("%Y%m%d")

    # ---------- Current day ----------
    with st.spinner("박스오피스 데이터를 불러오는 중..."):
        df, error = get_boxoffice_data(target_dt, api_key)

    if error == "empty":
        st.warning(
            f"{selected_date.strftime('%Y년 %m월 %d일')} 데이터가 아직 없어요. "
            "다른 날짜를 선택해 주세요."
        )
        return

    if error:
        st.error(error)
        return

    df = preprocess(df)

    top1 = df.iloc[0]
    top1_name = html.escape(str(top1["movieNmDisplay"]))
    total_audience = int(df["audiCnt"].sum())
    top1_share = (
        int(top1["audiCnt"]) / total_audience * 100
        if total_audience
        else 0
    )
    new_count = int(
        (
            df.get(
                "rankOldAndNew",
                pd.Series(dtype=str),
            )
            .astype(str)
            .str.upper()
            == "NEW"
        ).sum()
    )
    screen_sum = int(df["scrnCnt"].sum())


    top2_name = (
        html.escape(str(df.iloc[1]["movieNmDisplay"]))
        if len(df) > 1
        else "-"
    )
    top3_name = (
        html.escape(str(df.iloc[2]["movieNmDisplay"]))
        if len(df) > 2
        else "-"
    )

    top1_old_new = str(top1.get("rankOldAndNew", "")).upper()
    top1_delta = int(top1.get("rankInten", 0))

    if top1_old_new == "NEW":
        top1_trend_text = "NEW ENTRY"
    elif top1_delta > 0:
        top1_trend_text = f"▲ {top1_delta} · RISING"
    elif top1_delta < 0:
        top1_trend_text = f"▼ {abs(top1_delta)} · MOVED"
    else:
        top1_trend_text = "— · HOLDING #1"

    # ---------- Sidebar summary tab ----------
    million_count = int(df["isMillion"].sum())
    rising_count = int((df["rankInten"] > 0).sum())

    with side_tabs[4]:
        st.markdown(
            '<div class="side-section-label">Today at a glance</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            compact_html(
                f"""
                <div class="side-rank-card">
                    <div class="side-rank-chip">🥇 BOX OFFICE #1</div>
                    <div class="side-rank-name">
                        {html.escape(str(top1["movieNmDisplay"]))}
                    </div>
                    <div class="side-rank-value">
                        {int(top1["audiCnt"]):,}
                        <span style="font-size:.66rem;color:#BFD5EF;">명</span>
                    </div>
                    <div class="side-rank-caption">선택 날짜 일일 관객</div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            compact_html(
                f"""
                <div class="side-stat-grid">
                    <div class="side-stat">
                        <div class="side-stat-label">TOP 10 관객</div>
                        <div class="side-stat-value">{person_short(total_audience)}명</div>
                    </div>
                    <div class="side-stat">
                        <div class="side-stat-label">1위 점유율</div>
                        <div class="side-stat-value">{top1_share:.1f}%</div>
                    </div>
                    <div class="side-stat">
                        <div class="side-stat-label">100만+ 작품</div>
                        <div class="side-stat-value">{million_count}편</div>
                    </div>
                    <div class="side-stat">
                        <div class="side-stat-label">순위 상승</div>
                        <div class="side-stat-value">{rising_count}편</div>
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="side-feature-list">
                <div class="side-feature">
                    <span class="side-feature-icon">🗓</span>
                    날짜 변경 시 모든 값 자동 갱신
                </div>
                <div class="side-feature">
                    <span class="side-feature-icon">⚡</span>
                    KOBIS API 응답은 1시간 캐시
                </div>
                <div class="side-feature">
                    <span class="side-feature-icon">↗</span>
                    본문에서 7일 추이와 영화 맞대결 지원
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="sidebar-tip">
                <b>Source</b> · 영화진흥위원회 KOBIS<br>
                <b>Scope</b> · 한국 일별 박스오피스 TOP 10
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------- Hero ----------
    if show_hero:
        rail_items = (
            f"<span class='hero-rail-item'><span class='hero-rail-rank'>#01</span><span class='hero-rail-name'>{top1_name}</span><span class='hero-rail-sep'></span><span>{int(top1['audiCnt']):,}명</span></span>"
            f"<span class='hero-rail-item'><span class='hero-rail-rank'>#02</span><span class='hero-rail-name'>{top2_name}</span></span>"
            f"<span class='hero-rail-item'><span class='hero-rail-rank'>#03</span><span class='hero-rail-name'>{top3_name}</span></span>"
            f"<span class='hero-rail-item'><span>KOBIS DAILY</span><span class='hero-rail-sep'></span><span>{selected_date.strftime('%Y.%m.%d')}</span></span>"
        )

        st.markdown(
            compact_html(
                f"""
                <div class="hero hero-cinema">
                    <div class="hero-grid"></div>
                    <div class="hero-orb a"></div>
                    <div class="hero-orb b"></div>
                    <div class="hero-beam"></div>
                    <div class="hero-cinema-noise"></div>
                    <div class="hero-cinema-scan"></div>
                    <div class="hero-corner-tl"></div>
                    <div class="hero-corner-br"></div>

                    <div class="hero-content hero-cinema-layout">
                        <div class="hero-copy">
                            <div class="hero-topline">
                                <div class="hero-kicker">KOREA DAILY BOX OFFICE</div>
                                <div class="hero-live-badge">LIVE RANKING</div>
                                <div class="hero-verified">✦ KOBIS VERIFIED</div>
                            </div>

                            <div class="hero-overline">NOW SHOWING · BOX OFFICE 01</div>

                            <div class="hero-title hero-title-v2">
                                <span class="hero-title-small">오늘 극장의 중심</span>
                                <span class="hero-title-movie">{top1_name}</span>
                            </div>

                            <div class="hero-sub-v2">
                                지금 한국 극장에서 가장 많은 관객이 선택한 작품.
                                오늘의 관객 흐름과 흥행 신호를 한 화면에서 읽어보세요.
                            </div>

                            <div class="hero-stat-deck">
                                <div class="hero-stat-card">
                                    <div class="hero-stat-label">Daily audience</div>
                                    <div class="hero-stat-value">{int(top1['audiCnt']):,}<span style="font-size:.63rem;color:#86A0C0;margin-left:.18rem;">명</span></div>
                                    <div class="hero-stat-note">오늘 관객수</div>
                                </div>

                                <div class="hero-stat-card">
                                    <div class="hero-stat-label">Market share</div>
                                    <div class="hero-stat-value">{top1_share:.1f}<span style="font-size:.63rem;color:#86A0C0;margin-left:.05rem;">%</span></div>
                                    <div class="hero-stat-note">TOP 10 관객 점유율</div>
                                </div>

                                <div class="hero-stat-card">
                                    <div class="hero-stat-label">Screens</div>
                                    <div class="hero-stat-value">{int(top1['scrnCnt']):,}<span style="font-size:.63rem;color:#86A0C0;margin-left:.18rem;">개</span></div>
                                    <div class="hero-stat-note">상영 스크린</div>
                                </div>
                            </div>

                            <div class="hero-meta-row">
                                <span class="hero-meta-date">◉ {selected_date.strftime('%Y.%m.%d')}</span>
                                <span class="hero-meta-dot"></span>
                                <span>누적 {int(top1['audiAcc']):,}명</span>
                                <span class="hero-meta-dot"></span>
                                <span>일일 매출 {won_short(top1.get('salesAmt', 0))}원</span>
                            </div>
                        </div>

                        <div class="hero-rank-zone">
                            <div class="hero-radar-ring one"></div>
                            <div class="hero-radar-ring two"></div>
                            <div class="hero-radar-ring three"></div>
                            <div class="hero-radar-cross"></div>

                            <div class="hero-rank-core">
                                <div class="hero-rank-head">
                                    <span>DAILY RANK</span>
                                    <span class="hero-rank-live">LIVE</span>
                                </div>

                                <div class="hero-rank-number">01</div>
                                <div class="hero-rank-divider"></div>
                                <div class="hero-rank-movie">{top1_name}</div>
                                <div class="hero-rank-audience">{int(top1['audiCnt']):,} audience today</div>

                                <div class="hero-eq">
                                    <span></span><span></span><span></span><span></span>
                                    <span></span><span></span><span></span>
                                </div>

                                <div class="hero-rank-trend">
                                    <span>{top1_trend_text}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="hero-bottom-rail">
                        <div class="hero-rail-track">
                            {rail_items}{rail_items}
                        </div>
                    </div>
                </div>
                """
            ),
            unsafe_allow_html=True,
        )

    if show_ticker:
        render_ticker(df)

    # ---------- KPI ----------
    st.markdown(
        compact_html(
            f"""
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">TOP 10 일일 관객</div>
                    <div class="kpi-value">{person_short(total_audience)}명</div>
                    <div class="kpi-note">상위 10편 관객수 합계</div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-label">1위 관객 점유율</div>
                    <div class="kpi-value">{top1_share:.1f}%</div>
                    <div class="kpi-note">{html.escape(str(top1['movieNmDisplay']))}</div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-label">신규 진입작</div>
                    <div class="kpi-value">{new_count}편</div>
                    <div class="kpi-note">TOP 10 기준 NEW</div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-label">TOP 10 스크린 합계</div>
                    <div class="kpi-value">{screen_sum:,}개</div>
                    <div class="kpi-note">영화별 스크린 수 합계</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    # ---------- Podium ----------
    section_header(
        "TOP MOVIES",
        "오늘 가장 많이 본 영화",
        "카드에 마우스를 올려보세요. 상위 3편은 살아있는 포디움처럼 반응합니다.",
    )

    p1, p2, p3 = st.columns([1.12, 1, 1], gap="medium")

    with p1:
        render_podium_card(df.iloc[0], 1)

    with p2:
        if len(df) > 1:
            render_podium_card(df.iloc[1], 2)

    with p3:
        if len(df) > 2:
            render_podium_card(df.iloc[2], 3)

    # ---------- Interactive explorer ----------
    section_header(
        "INTERACTIVE LAB",
        "숫자를 직접 만져보는 분석실",
        "지표와 영화 수를 바꾸면 그래프가 즉시 다시 정렬됩니다.",
    )

    st.markdown(
        compact_html(
            """
            <div class="interactive-shell">
                <div class="interactive-inner">
                    <div class="panel-kicker">LIVE EXPLORER</div>
                    <div class="panel-title">Top 10 Ranking Explorer</div>
                    <div class="panel-sub">
                        관객 · 누적 · 스크린 · 매출을 버튼 한 번으로 바꿔보세요.
                    </div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    c_metric, c_count = st.columns([1.65, 1], gap="medium")

    with c_metric:
        selected_metric = metric_selector(
            "비교 지표",
            ["관객수", "누적 관객", "스크린", "매출"],
            sidebar_metric,
            "metric_mode",
        )

    with c_count:
        top_n = st.slider(
            "표시할 영화 수",
            min_value=3,
            max_value=min(10, len(df)),
            value=min(sidebar_top_n, len(df)),
            step=1,
        )

    st.plotly_chart(
        make_dynamic_rank_chart(
            df,
            selected_metric,
            top_n,
        ),
        width="stretch",
        config={
            "displayModeBar": False,
            "scrollZoom": False,
        },
        key="dynamic_rank_chart",
    )

    # ---------- Focus ----------
    section_header(
        "MOVIE FOCUS",
        "한 편을 찍어서 7일 흐름 추적",
        "오늘 TOP 10 중 하나를 골라 최근 7일의 관객수와 순위 변화를 함께 확인합니다.",
    )

    movie_options = df["movieNmDisplay"].tolist()

    if (
        "focus_selector" not in st.session_state
        or st.session_state["focus_selector"] not in movie_options
    ):
        st.session_state["focus_selector"] = movie_options[0]

    focus_select_col, focus_button_col = st.columns([4, 1], gap="small")

    def pick_random_movie():
        st.session_state["focus_selector"] = random.choice(movie_options)

    with focus_button_col:
        st.button(
            "🎲 랜덤 픽",
            width="stretch",
            on_click=pick_random_movie,
        )

    with focus_select_col:
        focus_movie = st.selectbox(
            "포커스 영화",
            movie_options,
            key="focus_selector",
            label_visibility="collapsed",
        )

    focus_row = df[
        df["movieNmDisplay"] == focus_movie
    ].iloc[0]

    focus_card_col, focus_chart_col = st.columns(
        [1, 1.65],
        gap="medium",
    )

    with focus_card_col:
        render_focus_card(
            focus_row,
            total_audience,
        )

    with focus_chart_col:
        with st.spinner("최근 7일 흐름을 읽는 중..."):
            week_df = get_week_boxoffice_data(
                target_dt,
                api_key,
            )

        if week_df.empty:
            st.info("최근 7일 데이터를 불러오지 못했어요.")
        else:
            st.plotly_chart(
                make_weekly_movie_chart(
                    week_df,
                    focus_movie,
                    selected_date,
                ),
                width="stretch",
                config={"displayModeBar": False},
                key="weekly_movie_chart",
            )

    # ---------- Duel ----------
    section_header(
        "MOVIE DUEL",
        "영화 vs 영화",
        "두 작품을 직접 골라 관객·누적·스크린·매출·랭킹 파워를 레이더로 붙여봅니다.",
    )

    duel_a_col, duel_vs_col, duel_b_col = st.columns(
        [1, .18, 1],
        gap="small",
    )

    with duel_a_col:
        movie_a = st.selectbox(
            "A 영화",
            movie_options,
            index=0,
            key="duel_a",
        )

    with duel_vs_col:
        st.markdown(
            '<div class="duel-vs">VS</div>',
            unsafe_allow_html=True,
        )

    default_b = 1 if len(movie_options) > 1 else 0

    with duel_b_col:
        movie_b = st.selectbox(
            "B 영화",
            movie_options,
            index=default_b,
            key="duel_b",
        )

    if movie_a == movie_b and len(movie_options) > 1:
        st.info("서로 다른 영화를 골라보세요. 비교가 훨씬 재밌어집니다.")
    else:
        duel_chart_col, duel_info_col = st.columns(
            [1.55, 1],
            gap="medium",
        )

        with duel_chart_col:
            st.plotly_chart(
                make_duel_radar(
                    df,
                    movie_a,
                    movie_b,
                ),
                width="stretch",
                config={"displayModeBar": False},
                key="duel_radar",
            )

        with duel_info_col:
            row_a = df[
                df["movieNmDisplay"] == movie_a
            ].iloc[0]

            row_b = df[
                df["movieNmDisplay"] == movie_b
            ].iloc[0]

            st.markdown(
                compact_html(
                    f"""
                    <div class="interactive-shell">
                        <div class="interactive-inner">
                            <div class="panel-kicker">HEAD TO HEAD</div>
                            <div class="panel-title">오늘의 맞대결</div>
                            <div class="panel-sub">
                                레이더는 오늘 TOP 10 내부 최고값을 100으로 정규화합니다.
                            </div>

                            <div class="duel-result">
                                {duel_summary(df, movie_a, movie_b)}
                            </div>

                            <div class="duel-result">
                                <b>{html.escape(movie_a)}</b><br>
                                관객 {int(row_a['audiCnt']):,}명 ·
                                스크린 {int(row_a['scrnCnt']):,}개 ·
                                순위 #{int(row_a['rank'])}
                            </div>

                            <div class="duel-result">
                                <b>{html.escape(movie_b)}</b><br>
                                관객 {int(row_b['audiCnt']):,}명 ·
                                스크린 {int(row_b['scrnCnt']):,}개 ·
                                순위 #{int(row_b['rank'])}
                            </div>
                        </div>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

    # ---------- No.1 Snapshot ----------
    section_header(
        "NO.1 SNAPSHOT",
        f"1위 영화 상세 지표 · {top1['movieNmDisplay']}",
        "오늘의 1위 성적을 핵심 숫자로 빠르게 확인합니다.",
    )

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "일일 관객",
            f"{int(top1['audiCnt']):,}명",
            border=True,
            icon=":material/groups:",
        )

    with m2:
        st.metric(
            "누적 관객",
            f"{int(top1['audiAcc']):,}명",
            border=True,
            icon=":material/monitoring:",
        )

    with m3:
        st.metric(
            "스크린 수",
            f"{int(top1['scrnCnt']):,}개",
            border=True,
            icon=":material/theaters:",
        )

    with m4:
        st.metric(
            "일일 매출",
            f"{won_short(top1.get('salesAmt', 0))}원",
            border=True,
            icon=":material/payments:",
        )

    # ---------- Ranking ----------
    section_header(
        "FULL RANKING",
        "전체 박스오피스 순위",
        "검색하거나 필터를 눌러 필요한 영화만 즉시 좁혀보세요.",
    )

    search_col, filter_col = st.columns(
        [1.55, 1],
        gap="medium",
    )

    with search_col:
        rank_query = st.text_input(
            "영화 검색",
            placeholder="🔎 영화 제목을 입력하면 순위표가 바로 필터링됩니다",
            label_visibility="collapsed",
        )

    with filter_col:
        rank_filter = metric_selector(
            "순위표 필터",
            ["전체", "100만+", "NEW", "상승"],
            "전체",
            "rank_filter_mode",
        )

    filtered_df = df.copy()

    if rank_query.strip():
        filtered_df = filtered_df[
            filtered_df["movieNmDisplay"].str.contains(
                rank_query.strip(),
                case=False,
                regex=False,
            )
        ]

    if rank_filter == "100만+":
        filtered_df = filtered_df[
            filtered_df["isMillion"]
        ]

    elif rank_filter == "NEW":
        filtered_df = filtered_df[
            filtered_df["rankOldAndNew"]
            .astype(str)
            .str.upper()
            == "NEW"
        ]

    elif rank_filter == "상승":
        filtered_df = filtered_df[
            filtered_df["rankInten"] > 0
        ]

    if filtered_df.empty:
        st.info(
            "조건에 맞는 영화가 없습니다. 검색어나 필터를 바꿔보세요."
        )
    else:
        st.markdown(
            make_rank_table(
                filtered_df,
                selected_date,
                total_audience,
            ),
            unsafe_allow_html=True,
        )

    st.markdown(
        compact_html(
            """
            <div class="soft-note">
                🏆 <b>100만+</b> 배지는 누적 관객 100만 명 이상인 작품입니다.
                <b>NEW</b>는 TOP 10 신규 진입, ▲·▼는 전일 대비 순위 변화입니다.
                포커스 7일 그래프에서 0명으로 보이는 날짜는 해당 영화가
                그날 KOBIS TOP 10 목록에 없었을 수 있습니다.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
