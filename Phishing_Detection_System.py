import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import re
import os
import json
import pickle
from collections import Counter

# ── PAGE CONFIG  (must be the very first Streamlit call) ────────────────────
st.set_page_config(
    page_title="PhishGuard AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── SVG ICON LIBRARY ─────────────────────────────────────────────────────────
def icon(name: str, size: int = 15, color: str = "currentColor") -> str:
    lib = {
        "shield":       f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        "cpu":          f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/></svg>',
        "database":     f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
        "bar-chart":    f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
        "layers":       f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
        "alert-circle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
        "check-circle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
        "mail":         f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>',
        "zap":          f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
        "refresh":      f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>',
    }
    return lib.get(name, "")


# ── GLOBAL CSS ────────────────────────────────────────────────────────────────
STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }

.stApp { background: #ffffff; }

/* ── SIDEBAR — layout/width controlled by JS (pg-sb-style in <head>) ── */

/* Constrain every element inside the sidebar to the sidebar's own width */
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] > div * {
    max-width: 100% !important;
    box-sizing: border-box !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    width: 100% !important;
}
/* Override the shared .block-container rule inside sidebar */
section[data-testid="stSidebar"] .block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0 !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    width: 100% !important;
    max-width: 100% !important;
    overflow: hidden !important;
}

/* Hide Streamlit's native sidebar collapse/expand controls */
button[data-testid="baseButton-headerNoPadding"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
button[kind="headerNoPadding"],
section[data-testid="stSidebar"] button[data-testid^="baseButton"],
.st-emotion-cache-1rs6os {
    display: none !important;
    visibility: hidden !important;
}


/* ── MAIN BLOCK ──────────────────────────────────────────────────────── */
.block-container {
    padding-top: 20px !important;
    padding-bottom: 20px !important;
    max-width: 840px !important;
    margin: 0 auto !important;
    transition: padding 0.32s ease;
}

/* ── BUTTONS ─────────────────────────────────────────────────────────── */
/* Primary — Analyse Email */
[data-testid="baseButton-primary"] {
    background: #111827 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 20px !important;
    transition: background 0.18s ease, box-shadow 0.18s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
}
[data-testid="baseButton-primary"]:hover {
    background: #2563eb !important;
    box-shadow: 0 3px 10px rgba(37,99,235,0.25) !important;
}

/* Secondary — Clear Chat */
[data-testid="baseButton-secondary"] {
    background: #ffffff !important;
    color: #374151 !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 9px !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 10px 20px !important;
    transition: border-color 0.18s ease, background 0.18s ease !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: #d1d5db !important;
    background: #f9fafb !important;
}

/* ── TEXT AREA ───────────────────────────────────────────────────────── */
.stTextArea textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 16px !important;
    border: 1.5px solid #e5e7eb !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    color: #111827 !important;
    background: #ffffff !important;
    resize: none !important;
    line-height: 1.6 !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.09) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #9ca3af !important; }

/* ── INPUT SECTION DIVIDER ───────────────────────────────────────────── */
.input-divider {
    height: 1px;
    background: #e5e7eb;
    margin: 20px 0 18px;
}

/* ── CHAT SCROLL AREA ────────────────────────────────────────────────── */
.chat-scroll {
    max-height: calc(100vh - 320px);
    overflow-y: auto;
    padding: 8px 0 16px;
    scroll-behavior: smooth;
}
.chat-scroll::-webkit-scrollbar { width: 5px; }
.chat-scroll::-webkit-scrollbar-track { background: transparent; }
.chat-scroll::-webkit-scrollbar-thumb {
    background: #e5e7eb;
    border-radius: 99px;
}

/* ── CHAT MESSAGE BUBBLES ────────────────────────────────────────────── */
.msg-wrap {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 22px;
}
.msg-wrap.msg-user { flex-direction: row-reverse; }

.msg-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    font-size: 11px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    letter-spacing: 0.3px;
}
.msg-user-av  { background: #2563eb; color: #fff; }
.msg-bot-av   { background: #111827; color: #fff; }

.msg-bubble {
    max-width: 82%;
    border-radius: 14px;
    font-size: 16px;
    line-height: 1.65;
}
.msg-user-bubble {
    background: #f3f4f6;
    color: #111827;
    padding: 13px 17px;
    border-bottom-right-radius: 4px;
    white-space: pre-wrap;
    word-break: break-word;
}
.msg-bot-bubble {
    background: transparent;
    border-bottom-left-radius: 4px;
    width: 100%;
    max-width: 100%;
}

/* ── RESULT CARDS ────────────────────────────────────────────────────── */
.result-card {
    border-radius: 13px;
    padding: 16px 20px;
    margin-top: 2px;
}
.result-phishing   { background: #fef2f2; border: 1px solid #fecaca; }
.result-legitimate { background: #f0fdf4; border: 1px solid #bbf7d0; }

.result-verdict {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
    line-height: 1.3;
}
.verdict-phishing   { color: #dc2626; }
.verdict-legitimate { color: #16a34a; }

.result-detail {
    font-size: 15px;
    color: #4b5563;
    line-height: 1.65;
}

/* ── WELCOME SCREEN ──────────────────────────────────────────────────── */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 24px 48px;
    text-align: center;
}
.welcome-icon-wrap {
    width: 62px;
    height: 62px;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 22px;
}
.welcome-title {
    font-size: 32px;
    font-weight: 600;
    color: #111827;
    letter-spacing: -0.6px;
    margin-bottom: 10px;
    line-height: 1.2;
}
.welcome-sub {
    font-size: 17px;
    color: #6b7280;
    max-width: 420px;
    line-height: 1.65;
    margin: 0 auto 32px;
}
.hint-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    justify-content: center;
    max-width: 640px;
}
.hint-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 15px;
    color: #374151;
    line-height: 1.5;
    text-align: left;
    max-width: 195px;
    cursor: default;
    transition: border-color 0.15s ease;
}
.hint-card:hover { border-color: #d1d5db; }
.hint-card-icon  { margin-bottom: 7px; display: block; }

/* ── SIDEBAR COMPONENTS ─────────────────────────────────────────────── */
.sb-header {
    padding: 20px 18px 18px;
    border-bottom: 1px solid #e5e7eb;
}
.sb-brand-row {
    display: flex;
    align-items: center;
    gap: 11px;
}
.sb-brand-icon {
    width: 38px;
    height: 38px;
    background: #111827;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.sb-brand-name {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.3px;
    line-height: 1.2;
}
.sb-brand-sub {
    font-size: 12px;
    color: #9ca3af;
    font-weight: 400;
    margin-top: 1px;
}
.sb-section {
    padding: 14px 14px 16px;
    border-bottom: 1px solid #e5e7eb;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
}
.sb-section-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 15px;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 13px;
    user-select: none;
}
.sb-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 4px 0;
    gap: 8px;
}
.sb-key {
    font-size: 13px;
    color: #6b7280;
    font-weight: 400;
    flex-shrink: 0;
}
.sb-val {
    font-size: 13px;
    color: #111827;
    font-weight: 600;
    text-align: right;
    max-width: 58%;
    line-height: 1.4;
}
.badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 11px;
    font-weight: 600;
}
.badge-blue  { background: #dbeafe; color: #1d4ed8; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-gray  { background: #f3f4f6; color: #374151; }

/* Metric bars */
.metric-block { margin-bottom: 14px; width: 100%; box-sizing: border-box; }
.metric-block:last-child { margin-bottom: 0; }
.metric-label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 7px;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
}
.metric-name { font-size: 13px; color: #374151; font-weight: 500; min-width: 0; flex: 1; }
.metric-pct  { font-size: 13px; color: #2563eb;  font-weight: 700; flex-shrink: 0; padding-left: 6px; }
.metric-track {
    height: 9px;
    width: 100%;
    background: #e5e7eb;
    border-radius: 99px;
    overflow: hidden;
    box-sizing: border-box;
    display: block;
}
.metric-fill {
    height: 9px;
    border-radius: 99px;
    background: linear-gradient(90deg, #60a5fa, #2563eb);
    display: block;
    min-width: 4px;
}

/* Pipeline tags */
.pipeline-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 2px;
}
.pipeline-tag {
    font-size: 11px;
    color: #374151;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 3px 8px;
    font-weight: 500;
}

/* Warning override */
.stAlert {
    border-radius: 10px !important;
    font-size: 14px !important;
    color: #111827 !important;
}
div[data-testid="stAlert"],
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] * {
    color: #111827 !important;
}

@media (max-width: 768px) {
    .hint-row   { flex-direction:column !important; gap:8px !important; }
    .hint-card  { width:100% !important; max-width:100% !important; font-size:13px !important; padding:12px 14px !important; }
    .welcome-wrap       { padding:24px 16px !important; }
    .welcome-icon-wrap  { width:54px !important; height:54px !important; }
    .welcome-title      { font-size:22px !important; }
    .welcome-sub        { font-size:14px !important; }
    .main .block-container { padding-left:12px !important; padding-right:12px !important; }
    .result-card    { padding:16px 14px !important; }
    .result-verdict { font-size:15px !important; }
    .result-detail  { font-size:13px !important; }
    .msg-user, .msg-bot { max-width:95% !important; font-size:14px !important; }
    .stTextArea textarea { font-size:14px !important; }
    #pg-hb { top:10px !important; }
}

@media (max-width: 480px) {
    .welcome-title { font-size:19px !important; }
    .welcome-sub   { font-size:13px !important; }
    div[data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
    div[data-testid="column"]            { min-width:100% !important; width:100% !important; }
    .stButton > button                   { width:100% !important; }
}
</style>
"""


# ── HAMBURGER BUTTON  (injected into parent document via JS) ─────────────────
HAMBURGER_HTML = """
<!DOCTYPE html><html><body style="margin:0;padding:0;overflow:hidden;">
<script>
(function () {
    var pdoc   = window.parent;
    var doc    = pdoc.document;
    var SB_W   = 285;
    var SB_C   = 52;
    var BG     = '#f7f7f8';   // same colour for both open and closed
    var OPEN_K = '__pgSidebarOpen';
    var INIT_K = '__pgHamburgerReady';

    // ── Style element in <head> — injected immediately ─────────────────────
    var styleEl = doc.getElementById('pg-sb-style');
    if (!styleEl) {
        styleEl = doc.createElement('style');
        styleEl.id = 'pg-sb-style';
        doc.head.appendChild(styleEl);
    }

    if (pdoc[OPEN_K] === undefined) pdoc[OPEN_K] = true;

    var TR = 'min-width .3s cubic-bezier(.4,0,.2,1),max-width .3s cubic-bezier(.4,0,.2,1)';

    function isMobile() { return pdoc.innerWidth <= 768; }

    function applyCSS(open) {
        var mobile = isMobile();
        var w = open ? SB_W : (mobile ? 0 : SB_C);
        // Head CSS — higher cascade priority than any body stylesheet
        styleEl.textContent = [
            'section[data-testid="stSidebar"]{',
            '  display:block!important;visibility:visible!important;',
            '  min-width:' + w + 'px!important;max-width:' + w + 'px!important;width:' + w + 'px!important;',
            '  background-color:' + BG + '!important;',
            '  border-right:' + (w > 0 ? '1px solid #e5e7eb' : 'none') + '!important;',
            '  overflow:hidden!important;',
            '  transform:translateX(0)!important;',
            '  transition:' + TR + '!important;',
            '}',
            'section[data-testid="stSidebar"] div,',
            'section[data-testid="stSidebar"] section{',
            '  max-width:' + w + 'px!important;',
            '  box-sizing:border-box!important;',
            '}',
            'section[data-testid="stSidebar"]>div{',
            '  opacity:' + (open ? '1' : '0') + '!important;',
            '  transition:opacity .2s ease!important;',
            '  pointer-events:' + (open ? 'auto' : 'none') + '!important;',
            '}'
        ].join('');

        var sb = doc.querySelector('[data-testid="stSidebar"]');
        if (!sb) return;

        sb.style.setProperty('display',         'block',          'important');
        sb.style.setProperty('visibility',      'visible',        'important');
        sb.style.setProperty('min-width',        w + 'px',        'important');
        sb.style.setProperty('max-width',        w + 'px',        'important');
        sb.style.setProperty('width',            w + 'px',        'important');
        sb.style.setProperty('background-color', BG,              'important');
        sb.style.setProperty('overflow',         'hidden',        'important');
        sb.style.setProperty('transform',        'translateX(0)', 'important');

        // Mobile: open = fixed overlay so main content stays full-width
        if (mobile && open) {
            sb.style.setProperty('position', 'fixed',  'important');
            sb.style.setProperty('top',      '0',      'important');
            sb.style.setProperty('left',     '0',      'important');
            sb.style.setProperty('height',   '100vh',  'important');
            sb.style.setProperty('z-index',  '9999',   'important');
        } else {
            sb.style.removeProperty('position');
            sb.style.removeProperty('height');
            sb.style.removeProperty('z-index');
        }

        // Backdrop — tap outside to close on mobile
        var bd = doc.getElementById('pg-bd');
        if (mobile && open && !bd) {
            bd = doc.createElement('div');
            bd.id = 'pg-bd';
            bd.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;' +
                               'background:rgba(0,0,0,0.45);z-index:9998;transition:opacity .2s;';
            bd.onclick = function () { pdoc.pgToggle(); };
            doc.body.appendChild(bd);
        } else if ((!mobile || !open) && bd) {
            bd.parentNode.removeChild(bd);
        }

        var el = sb.firstElementChild;
        for (var i = 0; i < 3 && el; i++) {
            el.style.setProperty('max-width',  w + 'px',       'important');
            el.style.setProperty('width',      '100%',         'important');
            el.style.setProperty('overflow',   'hidden',       'important');
            el.style.setProperty('box-sizing', 'border-box',   'important');
            if (i === 0) {
                el.style.setProperty('opacity',        open ? '1' : '0',    'important');
                el.style.setProperty('pointer-events', open ? 'auto' : 'none', 'important');
            }
            el = el.firstElementChild;
        }
    }

    var BTN  = 34;
    var MENU = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>';

    // Open: button at top-right of sidebar   Closed desktop: centred in 52px strip   Closed mobile: floating at left:12px
    function btnLeft(open) {
        if (open) return SB_W - BTN - 9;
        return isMobile() ? 12 : Math.round((SB_C - BTN) / 2);
    }

    function positionBtn(open) {
        var btn = doc.getElementById('pg-hb');
        if (btn) btn.style.left = btnLeft(open) + 'px';
    }

    // Expose toggle on parent window
    pdoc.pgToggle = function () {
        pdoc[OPEN_K] = !pdoc[OPEN_K];
        applyCSS(pdoc[OPEN_K]);
        positionBtn(pdoc[OPEN_K]);
    };

    applyCSS(pdoc[OPEN_K]);
    setTimeout(function () { applyCSS(pdoc[OPEN_K]); }, 300);
    setTimeout(function () { applyCSS(pdoc[OPEN_K]); }, 800);

    if (pdoc[INIT_K]) return;
    pdoc[INIT_K] = true;

    // ── Create fixed-position button ──────────────────────────────────────
    function createBtn() {
        if (doc.getElementById('pg-hb')) return;
        var btn = doc.createElement('button');
        btn.id        = 'pg-hb';
        btn.title     = 'Toggle sidebar';
        btn.innerHTML = MENU;
        btn.style.cssText = [
            'position:fixed',
            'top:8px',
            'left:' + btnLeft(pdoc[OPEN_K]) + 'px',
            'z-index:999999',
            'width:' + BTN + 'px',
            'height:' + BTN + 'px',
            'border:1px solid #e5e7eb',
            'border-radius:8px',
            'background:#ffffff',
            'cursor:pointer',
            'display:flex',
            'align-items:center',
            'justify-content:center',
            'box-shadow:0 1px 4px rgba(0,0,0,0.09)',
            'padding:0',
            'outline:none',
            'transition:left .3s cubic-bezier(.4,0,.2,1),box-shadow .18s,border-color .18s'
        ].join(';');
        btn.onmouseenter = function () {
            btn.style.boxShadow   = '0 2px 8px rgba(0,0,0,0.14)';
            btn.style.borderColor = '#d1d5db';
        };
        btn.onmouseleave = function () {
            btn.style.boxShadow   = '0 1px 4px rgba(0,0,0,0.09)';
            btn.style.borderColor = '#e5e7eb';
        };
        btn.onclick = function () { pdoc.pgToggle(); };
        doc.body.appendChild(btn);
    }

    // ── Hide Streamlit's native collapse button ───────────────────────────
    function hideNativeToggle() {
        ['[data-testid="collapsedControl"]',
         '[data-testid="stSidebarCollapsedControl"]',
         'button[data-testid="baseButton-headerNoPadding"]'
        ].forEach(function (s) {
            doc.querySelectorAll(s).forEach(function (el) {
                el.style.setProperty('display', 'none', 'important');
            });
        });
    }

    // ── MutationObserver ─────────────────────────────────────────────────
    var raf = null;
    new MutationObserver(function () {
        if (raf) return;
        raf = pdoc.requestAnimationFrame(function () {
            raf = null;
            applyCSS(pdoc[OPEN_K]);
            createBtn();
            positionBtn(pdoc[OPEN_K]);
            hideNativeToggle();
            var chat = doc.getElementById('pg-chat-scroll');
            if (chat) chat.scrollTop = chat.scrollHeight;
        });
    }).observe(doc.body, { childList: true, subtree: true });

    // ── Resize listener — re-apply on orientation change / window resize ──
    pdoc.addEventListener('resize', function () {
        applyCSS(pdoc[OPEN_K]);
        positionBtn(pdoc[OPEN_K]);
    });

    if (doc.readyState === 'loading') {
        doc.addEventListener('DOMContentLoaded', createBtn);
    } else {
        setTimeout(createBtn, 100);
    }
})();
</script>
</body></html>
"""


# ── MODEL LOADING  (cached — loads pre-trained pickles, runs in ~1 second) ────
@st.cache_resource(show_spinner=False)
def load_resources():
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer

    for corpus in ["stopwords", "punkt", "punkt_tab",
                   "wordnet", "omw-1.4",
                   "averaged_perceptron_tagger",
                   "averaged_perceptron_tagger_eng"]:
        nltk.download(corpus, quiet=True)

    base_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base_dir, "model.pkl"),  "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(base_dir, "tfidf.pkl"),  "rb") as f:
        tfidf = pickle.load(f)
    with open(os.path.join(base_dir, "meta.json"),  "r") as f:
        meta = json.load(f)

    return {
        "model":          model,
        "vectorizer":     tfidf,
        "stop_words":     set(stopwords.words("english")),
        "frequent_words": set(meta["frequent_words"]),
        "rare_words":     set(meta["rare_words"]),
        "stemmer":        PorterStemmer(),
        "lemmatizer":     WordNetLemmatizer(),
        "metrics":        meta["metrics"],
        "stats":          meta["stats"],
    }


# ── PREDICT ───────────────────────────────────────────────────────────────────
def predict_email(text: str, res: dict):
    from nltk.tokenize import word_tokenize

    sw  = res["stop_words"]
    fw  = res["frequent_words"]
    rw  = res["rare_words"]
    stm = res["stemmer"]
    lem = res["lemmatizer"]

    t = str(text)
    t = re.sub(r"<[^>]+>",                   " ", t)
    t = re.sub(r"https?://\S+|www\.\S+",     " ", t)
    t = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", " ", t)
    t = re.sub(r"[^\w\s]",                    " ", t)
    t = re.sub(r"\d+",                        " ", t)
    t = re.sub(r"[^a-zA-Z\s]",               " ", t)
    t = re.sub(r"\s+",                        " ", t).strip().lower()
    t = " ".join(w for w in t.split() if w not in sw)
    t = " ".join(w for w in t.split() if w not in fw)
    t = " ".join(w for w in t.split() if w not in rw)

    tokens    = word_tokenize(t)
    tokens    = [stm.stem(w)        for w in tokens]
    tokens    = [lem.lemmatize(w)   for w in tokens]
    processed = " ".join(tokens)

    vec   = res["vectorizer"].transform([processed])
    pred  = res["model"].predict(vec)[0]
    proba = res["model"].predict_proba(vec)[0]
    return int(pred), proba


# ── BUILD RESULT HTML ─────────────────────────────────────────────────────────
def build_result(pred: int, proba) -> str:
    if pred == 1:
        return (
            '<div class="result-card result-phishing">'
            f'<div class="result-verdict verdict-phishing">'
            f'{icon("alert-circle", 18, "#dc2626")} Phishing Email Detected'
            '</div>'
            '<div class="result-detail">This email exhibits characteristics commonly '
            'associated with phishing attempts — deceptive language, urgency cues, or '
            'suspicious content patterns. Do not click links or share personal information.'
            '</div>'
            '</div>'
        )
    return (
        '<div class="result-card result-legitimate">'
        f'<div class="result-verdict verdict-legitimate">'
        f'{icon("check-circle", 18, "#16a34a")} Legitimate Email'
        '</div>'
        '<div class="result-detail">This email does not exhibit typical phishing patterns. '
        'It appears to be a legitimate communication based on the language and content '
        'features analysed by the model.'
        '</div>'
        '</div>'
    )


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def render_sidebar(res: dict) -> None:
    m = res["metrics"]
    s = res["stats"]

    with st.sidebar:
        # Model Information
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-section-title">
                {icon("cpu", 15, "#9ca3af")} &nbsp; Model Information
            </div>
            <div class="sb-row">
                <span class="sb-key">Algorithm</span>
                <span class="sb-val">Multinomial Naive Bayes</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Training Split</span>
                <span class="sb-val">80% Train &nbsp;/&nbsp; 20% Test</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Training Samples</span>
                <span class="sb-val">{s["train"]:,} emails</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Testing Samples</span>
                <span class="sb-val">{s["test"]:,} emails</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Task Type</span>
                <span class="sb-val">Binary Classification</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Dataset Info
        st.markdown(f"""
        <div class="sb-section">
            <div class="sb-section-title">
                {icon("database", 15, "#9ca3af")} &nbsp; Dataset
            </div>
            <div class="sb-row">
                <span class="sb-key">Total Entries</span>
                <span class="sb-val">{s["total"]:,} emails</span>
            </div>
            <div class="sb-row">
                <span class="sb-key">Source</span>
                <span class="sb-val">Kaggle</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Performance Metrics — compact single-line HTML to avoid Markdown code-block misparse
        _perf_icon = icon("bar-chart", 15, "#9ca3af")
        _mhtml = ""
        for _label, _key in [
            ("Accuracy",  "accuracy"),
            ("Precision", "precision"),
            ("Recall",    "recall"),
            ("F1-Score",  "f1"),
        ]:
            _v = m[_key]
            _mhtml += (
                f'<div style="margin-bottom:14px;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;">'
                f'<span style="font-size:13px;color:#374151;font-weight:500;flex:1;min-width:0;">{_label}</span>'
                f'<span style="font-size:13px;color:#2563eb;font-weight:700;padding-left:6px;flex-shrink:0;">{_v}%</span>'
                f'</div>'
                f'<div style="height:9px;width:100%;background:#e5e7eb;border-radius:99px;overflow:hidden;">'
                f'<div style="height:9px;width:{_v}%;min-width:4px;background:linear-gradient(90deg,#60a5fa,#2563eb);border-radius:99px;"></div>'
                f'</div>'
                f'</div>'
            )
        st.markdown(
            '<div style="padding:14px 16px 18px 16px;border-bottom:1px solid #e5e7eb;box-sizing:border-box;">'
            '<div class="sb-section-title">' + _perf_icon + ' &nbsp; Performance Metrics</div>'
            + _mhtml +
            '</div>',
            unsafe_allow_html=True
        )

        # Preprocessing Pipeline
        st.markdown(f"""
        <div class="sb-section" style="border-bottom:none;">
            <div class="sb-section-title">
                {icon("layers", 15, "#9ca3af")} &nbsp; Preprocessing Pipeline
            </div>
            <div class="pipeline-tags">
                <span class="pipeline-tag">HTML Removal</span>
                <span class="pipeline-tag">URL Removal</span>
                <span class="pipeline-tag">Lowercase</span>
                <span class="pipeline-tag">Stop Words</span>
                <span class="pipeline-tag">Frequent Words</span>
                <span class="pipeline-tag">Rare Words</span>
                <span class="pipeline-tag">Tokenization</span>
                <span class="pipeline-tag">Stemming</span>
                <span class="pipeline-tag">Lemmatization</span>
                <span class="pipeline-tag">TF-IDF</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── WELCOME SCREEN ────────────────────────────────────────────────────────────
def render_welcome() -> None:
    st.markdown(f"""
    <div class="welcome-wrap">
        <div class="welcome-icon-wrap">{icon("shield", 30, "#374151")}</div>
        <div class="welcome-title">Ready when you are.</div>
        <div class="welcome-sub">
            Paste any email subject line or body text below to instantly
            detect whether it is a phishing attempt or a legitimate email.
        </div>
        <div class="hint-row">
            <div class="hint-card">
                <span class="hint-card-icon">{icon("mail", 15, "#6b7280")}</span>
                Paste a suspicious email you received
            </div>
            <div class="hint-card">
                <span class="hint-card-icon">{icon("check-circle", 15, "#6b7280")}</span>
                Test with a known legitimate email
            </div>
            <div class="hint-card">
                <span class="hint-card-icon">{icon("zap", 15, "#6b7280")}</span>
                Try a bank alert or promotional email
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    st.markdown(STYLES, unsafe_allow_html=True)

    # Inject hamburger button (JS runs in parent document, persists across reruns)
    components.html(HAMBURGER_HTML, height=0, scrolling=False)

    # Session state
    if "messages"  not in st.session_state:
        st.session_state.messages  = []
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

    # Load model once (cached)
    with st.spinner("Setting up PhishGuard AI — please wait on first launch..."):
        res = load_resources()

    # Sidebar
    render_sidebar(res)

    # ── Welcome or conversation ───────────────────────────────────────────
    if not st.session_state.messages:
        render_welcome()
    else:
        msgs_html = '<div class="chat-scroll" id="pg-chat-scroll">'
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
                msgs_html += (
                    '<div class="msg-wrap msg-user">'
                    f'<div class="msg-bubble msg-user-bubble">{content}</div>'
                    '<div class="msg-avatar msg-user-av">You</div>'
                    '</div>'
                )
            else:
                msgs_html += (
                    '<div class="msg-wrap msg-bot">'
                    '<div class="msg-avatar msg-bot-av">AI</div>'
                    f'<div class="msg-bubble msg-bot-bubble">{msg["content"]}</div>'
                    '</div>'
                )
        msgs_html += '</div>'
        st.markdown(msgs_html, unsafe_allow_html=True)

    # ── Input section ─────────────────────────────────────────────────────
    st.markdown('<div class="input-divider"></div>', unsafe_allow_html=True)

    email_input = st.text_area(
        label="",
        placeholder="Paste email subject or body text here to analyse...",
        height=110,
        key=f"email_input_{st.session_state.input_key}",
        label_visibility="collapsed",
    )

    col_pred, col_gap, col_ref = st.columns([5, 0.25, 2])

    with col_pred:
        predict_btn = st.button(
            "Analyse Email",
            use_container_width=True,
            type="primary",
        )
    with col_ref:
        refresh_btn = st.button(
            "Clear Chat",
            use_container_width=True,
            type="secondary",
        )

    # ── Actions ───────────────────────────────────────────────────────────
    if refresh_btn:
        st.session_state.messages  = []
        st.session_state.input_key += 1
        st.rerun()

    if predict_btn:
        if not email_input or not email_input.strip():
            st.warning("Please paste some email text before clicking Analyse Email.")
        else:
            with st.spinner("Analysing email..."):
                pred, proba = predict_email(email_input.strip(), res)

            result_html = build_result(pred, proba)

            st.session_state.messages.append(
                {"role": "user",      "content": email_input.strip()})
            st.session_state.messages.append(
                {"role": "assistant", "content": result_html})

            st.session_state.input_key += 1
            st.rerun()


if __name__ == "__main__":
    main()
