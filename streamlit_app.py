import hmac
import html
import json
import re
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Hello, Teacher! · 자기소개",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PALETTE = {
    "Cobalt": "#2F5BFF",
    "Tangerine": "#FF7A45",
    "Bubblegum": "#FF6FAE",
    "Lime": "#B6F03C",
    "Lemon": "#FFE14D",
    "Lilac": "#B69CFF",
    "Mint": "#5EE3C1",
}

DEFAULTS = {
    "name": "김하늘",
    "nickname": "HANEUL SSAEM",
    "handle": "@haneul.class",
    "date": "2026년 3월 2일 · 새 학기 첫날",
    "title1_top": "HELLO,",
    "title1_bottom": "I'm Teacher",
    "title1_color": "Lemon",
    "body1": (
        "안녕하세요! 올해 여러분과 함께할 ==담임 선생님== 김하늘이에요. "
        "저는 **작은 질문 하나가 큰 배움을 만든다**고 믿어요. "
        "교실이 ==실수해도 괜찮은 곳==, 서로의 이야기에 ==귀 기울이는 곳==이 되었으면 해요. "
        "1년 동안 ==재밌게 배우고 크게 웃어요!=="
    ),
    "title2_top": "WHAT I",
    "title2_bottom": "LOVE?",
    "title2_color": "Bubblegum",
    "list2": (
        "🎨 | 수채화 그리기 | 주말마다 작은 그림 한 장\n"
        "📚 | 그림책 모으기 | 교실 책장에 몰래 채워둘게요\n"
        "🍪 | 쿠키 굽기 | 칭찬 스티커 10개면 쿠키 파티!"
    ),
    "title3": "Student says",
    "body3": "“선생님 수업은 시간이 너무 빨리 가요. 매일 기다려져요!”",
    "title4": "MY MOTTO",
    "title4_color": "Mint",
    "body4": "천천히 가도 괜찮아, ==함께 가면== 멀리 갈 수 있어.",
    "title5": "CONTACT ME",
    "body5": "궁금한 건 언제든 **교무실 3층** 또는 알림장으로 편하게 물어봐 주세요.",
}

PROFILE_PATH = Path(__file__).with_name("profile.json")


def load_profile():
    """저장된 profile.json 을 읽고, 빠진 항목은 기본값으로 채운다."""
    profile = dict(DEFAULTS)
    if PROFILE_PATH.exists():
        saved = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        profile.update({k: v for k, v in saved.items() if k in DEFAULTS})
    return profile


def current_profile():
    return {key: st.session_state[key] for key in DEFAULTS}


def save_profile():
    PROFILE_PATH.write_text(
        json.dumps(current_profile(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    st.session_state.saved_flash = True


def revert_to_saved():
    st.session_state.update(load_profile())


# 방문자는 항상 저장된 내용을 보고, 편집 중인 관리자는 자기 세션의 입력값을 유지한다.
for key, value in load_profile().items():
    st.session_state.setdefault(key, value)


def admin_password():
    try:
        return st.secrets.get("admin_password", "")
    except FileNotFoundError:  # secrets.toml 이 아예 없는 경우
        return ""


def check_password():
    expected = admin_password()
    typed = st.session_state.get("password_input", "")
    st.session_state.is_admin = bool(expected) and hmac.compare_digest(typed, expected)
    st.session_state.password_failed = not st.session_state.is_admin
    st.session_state.password_input = ""


def logout():
    st.session_state.is_admin = False


# ---------- 사이드바 편집기 ----------
def render_login():
    st.markdown("### 🔒 편집 모드")
    if not admin_password():
        st.warning("비밀번호가 설정되지 않았어요. Secrets에 `admin_password` 를 추가해 주세요.")
        return
    st.text_input("비밀번호", type="password", key="password_input", on_change=check_password)
    if st.session_state.get("password_failed"):
        st.error("비밀번호가 맞지 않아요.")


def render_editor():
    st.markdown("### ✏️ 자기소개 편집하기")
    st.caption("`==문장==` 은 형광펜 하이라이트, `**문장**` 은 굵게 표시돼요.")

    color_names = list(PALETTE)

    with st.expander("👤 기본 정보", expanded=True):
        st.text_input("이름", key="name")
        st.text_input("영문 닉네임", key="nickname")
        st.text_input("SNS 핸들", key="handle")
        st.text_input("날짜 · 한 줄 메모", key="date")

    with st.expander("① 메인 인사 (왼쪽 위)", expanded=True):
        st.text_input("타이틀 윗줄", key="title1_top")
        st.text_input("타이틀 아랫줄 (외곽선 글씨)", key="title1_bottom")
        st.selectbox("타이틀 밑줄 색", color_names, key="title1_color")
        st.text_area("내용", key="body1", height=180)

    with st.expander("② 좋아하는 것 (오른쪽 위)"):
        st.text_input("타이틀 윗줄 (외곽선 글씨)", key="title2_top")
        st.text_input("타이틀 아랫줄", key="title2_bottom")
        st.selectbox("타이틀 밑줄 색", color_names, key="title2_color")
        st.text_area(
            "목록 — 한 줄에 하나씩 `이모지 | 제목 | 설명`",
            key="list2",
            height=130,
        )

    with st.expander("③ 한마디 카드 (오른쪽 가운데)"):
        st.text_input("타이틀", key="title3")
        st.text_area("내용", key="body3", height=90)

    with st.expander("④ 좌우명 (왼쪽 아래)"):
        st.text_input("타이틀", key="title4")
        st.selectbox("타이틀 밑줄 색", color_names, key="title4_color")
        st.text_area("내용", key="body4", height=90)

    with st.expander("⑤ 연락처 (오른쪽 아래)"):
        st.text_input("타이틀", key="title5")
        st.text_area("내용", key="body5", height=90)

    st.button("💾 저장하기", on_click=save_profile, type="primary", width="stretch")
    if st.session_state.pop("saved_flash", False):
        st.success("저장했어요! 이제 사이트에 접속하면 이 내용이 보여요.")
    st.download_button(
        "⬇️ profile.json 내려받기",
        json.dumps(current_profile(), ensure_ascii=False, indent=2),
        file_name="profile.json",
        mime="application/json",
        width="stretch",
    )
    st.button("↺ 저장된 내용으로 되돌리기", on_click=revert_to_saved, width="stretch")
    st.button("🔓 편집 모드 나가기", on_click=logout, width="stretch")


with st.sidebar:
    if st.session_state.get("is_admin"):
        render_editor()
    else:
        render_login()


# ---------- 텍스트 변환 ----------
HIGHLIGHTS = ["hl-peach", "hl-blue", "hl-lime", "hl-pink", "hl-lemon"]


def rich(text):
    """사용자 입력을 안전하게 escape 한 뒤 ==하이라이트== / **굵게** 를 적용한다."""
    safe = html.escape(text).replace("$", "&#36;")
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    counter = iter(range(10_000))
    safe = re.sub(
        r"==(.+?)==",
        lambda m: f'<mark class="{HIGHLIGHTS[next(counter) % len(HIGHLIGHTS)]}">{m.group(1)}</mark>',
        safe,
    )
    return safe.replace("\n", "<br>")


def esc(text):
    return html.escape(text).replace("$", "&#36;")


def playlist_rows(raw):
    thumbs = ["#FFE14D", "#FF6FAE", "#5EE3C1", "#B69CFF", "#FF7A45", "#2F5BFF"]
    rows = []
    for i, line in enumerate(l for l in raw.splitlines() if l.strip()):
        parts = [p.strip() for p in line.split("|")]
        parts += [""] * (3 - len(parts))
        emoji, title, desc = parts[:3]
        star = "★" if i % 2 == 0 else "☆"
        rows.append(
            f'<div class="track">'
            f'<div class="thumb" style="background:{thumbs[i % len(thumbs)]}">{esc(emoji)}</div>'
            f'<div class="track-text"><div class="track-title">{esc(title)}</div>'
            f'<div class="track-desc">{esc(desc)}</div></div>'
            f'<div class="track-star">{star}</div></div>'
        )
    return "".join(rows)


# ---------- 3D 선생님 캐릭터 (SVG) ----------
TEACHER_SVG = """
<svg class="teacher" viewBox="0 0 420 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="안경을 쓴 귀여운 선생님 캐릭터">
<defs>
<radialGradient id="skin" cx="42%" cy="35%" r="70%"><stop offset="0" stop-color="#FFEBDD"/><stop offset=".55" stop-color="#FAC9AE"/><stop offset="1" stop-color="#E9997B"/></radialGradient>
<radialGradient id="skinS" cx="40%" cy="30%" r="80%"><stop offset="0" stop-color="#FAD0B8"/><stop offset="1" stop-color="#DE8C6E"/></radialGradient>
<radialGradient id="hair" cx="38%" cy="25%" r="85%"><stop offset="0" stop-color="#7A4E3B"/><stop offset=".5" stop-color="#4A2C20"/><stop offset="1" stop-color="#2A1812"/></radialGradient>
<linearGradient id="cardi" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFB0CB"/><stop offset=".5" stop-color="#FF6FAE"/><stop offset="1" stop-color="#E0457F"/></linearGradient>
<linearGradient id="shirt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#DCE4FF"/></linearGradient>
<radialGradient id="iris" cx="45%" cy="35%" r="70%"><stop offset="0" stop-color="#8A5A44"/><stop offset=".6" stop-color="#3A2018"/><stop offset="1" stop-color="#1A0E0A"/></radialGradient>
<linearGradient id="book" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6F93FF"/><stop offset="1" stop-color="#2F5BFF"/></linearGradient>
<radialGradient id="apple" cx="35%" cy="30%" r="75%"><stop offset="0" stop-color="#FF9A8A"/><stop offset=".5" stop-color="#F2383A"/><stop offset="1" stop-color="#A5141E"/></radialGradient>
<radialGradient id="bg" cx="50%" cy="35%" r="75%"><stop offset="0" stop-color="#E9F0FF"/><stop offset="1" stop-color="#BFD0FF"/></radialGradient>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="10" stdDeviation="9" flood-color="#1B2A6B" flood-opacity=".22"/></filter>
<filter id="paper" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="3" dy="6" stdDeviation="6" flood-color="#000" flood-opacity=".18"/></filter>
</defs>
<path filter="url(#paper)" d="M72 120 L150 58 L205 72 L262 40 L352 96 L360 190 L392 250 L372 360 L398 430 L338 520 L96 522 L40 452 L62 360 L28 270 L58 196 Z" fill="url(#bg)" stroke="#fff" stroke-width="12" stroke-linejoin="round"/>
<g fill="#fff" opacity=".7"><circle cx="96" cy="150" r="3"/><circle cx="330" cy="140" r="4"/><circle cx="350" cy="330" r="3"/><circle cx="80" cy="400" r="4"/></g>
<g filter="url(#soft)">
<path d="M88 212 Q82 92 210 82 Q338 92 332 212 L340 330 Q322 356 290 338 L130 338 Q98 356 80 330 Z" fill="url(#hair)"/>
<path d="M98 530 Q92 400 140 356 Q210 322 280 356 Q328 400 322 530 Z" fill="url(#cardi)"/>
<path d="M176 346 L210 420 L244 346 Q210 336 176 346 Z" fill="url(#shirt)"/>
<path d="M176 346 L196 372 L210 356 L224 372 L244 346" fill="none" stroke="#fff" stroke-width="7" stroke-linejoin="round"/>
<circle cx="210" cy="440" r="6" fill="#FFE14D"/><circle cx="210" cy="474" r="6" fill="#FFE14D"/><circle cx="210" cy="508" r="6" fill="#FFE14D"/>
<path d="M132 380 Q150 372 160 390" stroke="#fff" stroke-opacity=".45" stroke-width="6" fill="none" stroke-linecap="round"/>
<rect x="190" y="300" width="40" height="50" rx="16" fill="url(#skinS)"/>
<circle cx="110" cy="222" r="18" fill="url(#skinS)"/><circle cx="310" cy="222" r="18" fill="url(#skinS)"/>
<circle cx="110" cy="244" r="5" fill="#FFE14D"/><circle cx="310" cy="244" r="5" fill="#FFE14D"/>
<ellipse cx="210" cy="212" rx="102" ry="96" fill="url(#skin)"/>
<ellipse cx="178" cy="160" rx="34" ry="14" fill="#fff" opacity=".35"/>
<path d="M106 206 Q100 104 210 100 Q320 104 314 206 Q298 160 262 146 Q248 178 210 172 Q176 166 164 142 Q128 164 106 206 Z" fill="url(#hair)"/>
<path d="M150 124 Q190 104 240 112" stroke="#fff" stroke-opacity=".35" stroke-width="8" fill="none" stroke-linecap="round"/>
<path d="M270 128 l6 12 13 2 -9 9 2 13 -12 -6 -12 6 2 -13 -9 -9 13 -2 Z" fill="#FFE14D" stroke="#F2B400" stroke-width="2" stroke-linejoin="round"/>
<ellipse cx="170" cy="226" rx="17" ry="21" fill="url(#iris)"/><ellipse cx="250" cy="226" rx="17" ry="21" fill="url(#iris)"/>
<circle cx="176" cy="217" r="6.5" fill="#fff"/><circle cx="256" cy="217" r="6.5" fill="#fff"/>
<circle cx="164" cy="236" r="3" fill="#fff" opacity=".8"/><circle cx="244" cy="236" r="3" fill="#fff" opacity=".8"/>
<path d="M150 196 Q168 186 186 194" stroke="#3A2018" stroke-width="4" fill="none" stroke-linecap="round"/>
<path d="M234 194 Q252 186 270 196" stroke="#3A2018" stroke-width="4" fill="none" stroke-linecap="round"/>
<circle cx="170" cy="226" r="33" fill="#fff" fill-opacity=".14" stroke="#2F5BFF" stroke-width="5.5"/>
<circle cx="250" cy="226" r="33" fill="#fff" fill-opacity=".14" stroke="#2F5BFF" stroke-width="5.5"/>
<path d="M203 222 Q210 214 217 222" stroke="#2F5BFF" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M150 208 L160 200" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".8"/><path d="M230 208 L240 200" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".8"/>
<ellipse cx="138" cy="266" rx="18" ry="10" fill="#FF7FA0" opacity=".5"/><ellipse cx="282" cy="266" rx="18" ry="10" fill="#FF7FA0" opacity=".5"/>
<ellipse cx="210" cy="252" rx="4" ry="3" fill="#E08D70"/>
<path d="M194 270 Q210 290 226 270 Q210 276 194 270 Z" fill="#E6505A" stroke="#B83240" stroke-width="2.5" stroke-linejoin="round"/>
<g transform="rotate(-8 210 470)">
<rect x="140" y="420" width="140" height="100" rx="10" fill="url(#book)"/>
<rect x="140" y="420" width="16" height="100" rx="6" fill="#1D3FC4"/>
<rect x="170" y="440" width="92" height="30" rx="8" fill="#fff"/>
<text x="216" y="462" text-anchor="middle" font-family="Archivo Black, sans-serif" font-size="17" fill="#2F5BFF">ABC</text>
<path d="M176 490 h70" stroke="#FFE14D" stroke-width="7" stroke-linecap="round"/>
<path d="M150 428 h120" stroke="#fff" stroke-opacity=".35" stroke-width="4" stroke-linecap="round"/>
</g>
<ellipse cx="138" cy="470" rx="22" ry="20" fill="url(#skin)"/><ellipse cx="284" cy="452" rx="22" ry="20" fill="url(#skin)"/>
</g>
<g filter="url(#soft)" transform="translate(318 380)">
<circle cx="30" cy="36" r="30" fill="url(#apple)"/><circle cx="50" cy="36" r="28" fill="url(#apple)"/>
<path d="M40 12 Q42 0 48 -6" stroke="#6B3A1E" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M44 4 Q62 -10 72 4 Q58 14 44 4 Z" fill="#7BD34A"/>
<ellipse cx="26" cy="26" rx="8" ry="5" fill="#fff" opacity=".55"/>
</g>
</svg>
"""

STAR = '<svg viewBox="0 0 24 24"><path d="M12 2l2.9 6.2 6.8.8-5 4.7 1.3 6.7L12 17l-6 3.4 1.3-6.7-5-4.7 6.8-.8Z"/></svg>'

DOODLE_BURST = """<svg class="doodle burst" viewBox="0 0 120 90"><g stroke="#111" stroke-width="4" stroke-linecap="round" fill="none"><path d="M20 60 L30 20"/><path d="M42 58 L58 12"/><path d="M62 64 L92 26"/><path d="M72 76 L108 60"/></g></svg>"""
DOODLE_HEART = """<svg class="doodle heart" viewBox="0 0 60 56"><path d="M30 50 C6 34 2 18 12 10 C20 4 28 8 30 16 C33 8 42 4 50 10 C60 20 52 36 30 50 Z" fill="none" stroke="#111" stroke-width="3.5" stroke-linejoin="round"/></svg>"""
DOODLE_ARROW = """<svg class="doodle arrow" viewBox="0 0 90 120"><path d="M22 112 C6 90 30 72 44 86 C56 98 34 110 30 90 C26 64 50 36 70 16" fill="none" stroke="#111" stroke-width="3.5" stroke-linecap="round"/><path d="M52 16 L72 12 L70 32" fill="none" stroke="#111" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""
DOODLE_CLIPS = """<svg class="doodle clips" viewBox="0 0 110 180"><g fill="none" stroke="#111" stroke-width="3.5" stroke-linejoin="round"><path d="M10 40 L60 30 L62 42 L14 50 Z"/><path d="M70 10 L84 60 L94 58 L80 8 Z"/><path d="M8 90 L66 76 L68 88 L12 100 Z"/><path d="M30 130 L60 170 L70 162 L40 122 Z"/></g></svg>"""
DOODLE_HI = """<svg class="doodle hi" viewBox="0 0 110 60"><g fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"><path d="M14 12 V50 M14 32 Q28 20 34 34 V50"/><path d="M50 30 V50"/><circle cx="50" cy="18" r="2.5" fill="#111"/><path d="M64 14 V38"/><circle cx="64" cy="48" r="2.5" fill="#111"/><path d="M80 20 Q96 30 80 44 M90 12 Q108 30 90 52"/></g></svg>"""

# ---------- 스타일 ----------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Instrument+Serif:ital@0;1&family=Space+Grotesk:wght@400;500;700&family=Black+Han+Sans&family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
:root{
  --cobalt:#2F5BFF; --tangerine:#FF7A45; --pink:#FF6FAE; --lime:#B6F03C; --lemon:#FFE14D; --lilac:#B69CFF; --mint:#5EE3C1;
  --ink:#16161D; --muted:#5E5E6B; --paper:#FBFAF6;
}
.stApp{
  background-color:var(--paper);
  background-image:
    radial-gradient(rgba(0,0,0,.035) 1px, transparent 1px),
    radial-gradient(rgba(0,0,0,.025) 1px, transparent 1px);
  background-size:7px 7px, 13px 13px;
  background-position:0 0, 3px 5px;
}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem; padding-bottom:3rem; max-width:1240px;}
.page{position:relative; color:var(--ink); font-family:'Space Grotesk','Noto Sans KR',sans-serif; font-size:14.5px; line-height:1.62;}
.page *{box-sizing:border-box;}
.topline{text-align:center; font-size:13px; letter-spacing:.02em; margin-bottom:26px;}
.topline b{font-weight:700;} .topline small{display:block; font-size:10.5px; color:var(--muted); letter-spacing:.14em; text-transform:uppercase;}
.grid{display:grid; grid-template-columns:1fr 1.3fr 1fr; gap:28px; align-items:start;}
.col{position:relative; display:flex; flex-direction:column; gap:22px; z-index:2;}
/* 타이틀 */
.title{font-family:'Archivo Black','Black Han Sans',sans-serif; font-size:clamp(34px,3.6vw,50px); line-height:1.02; letter-spacing:-.01em; margin:0; word-break:keep-all;}
.title .hl{color:var(--cobalt); background:linear-gradient(transparent 55%, var(--hl) 55%, var(--hl) 92%, transparent 92%); padding:0 .08em; -webkit-box-decoration-break:clone; box-decoration-break:clone;}
.title .outline{display:inline-block; color:#fff; -webkit-text-stroke:2px var(--ink); paint-order:stroke fill; text-shadow:3px 3px 0 var(--hl);}
.title-row{display:flex; align-items:flex-start; justify-content:space-between; gap:12px;}
.bar{width:9px; min-width:9px; height:74px; background:var(--cobalt); border-radius:2px; margin-top:6px;}
.meta{display:flex; justify-content:space-between; gap:10px; font-size:12.5px; color:var(--muted); margin:10px 0 6px;}
.meta b{color:var(--ink);}
.body{text-align:justify; word-break:keep-all; font-family:'Noto Sans KR','Space Grotesk',sans-serif; font-size:14px;}
.body b{font-weight:900;}
mark{padding:1px 4px; border-radius:3px; color:inherit;}
.hl-peach{background:#FFC7AE;} .hl-blue{background:#BFD0FF;} .hl-lime{background:#DDF9A0;} .hl-pink{background:#FFC6DF;} .hl-lemon{background:#FFF0A0;}
.liked{display:flex; justify-content:space-between; align-items:center; font-size:13px; margin-top:10px;}
.liked .heart{color:var(--pink); font-size:18px;}
.big-letter{font-family:'Archivo Black',sans-serif; font-size:52px; line-height:1; color:var(--ink);}
.big-letter span{color:var(--cobalt);} .big-letter i{font-family:'Instrument Serif',serif; font-style:normal; font-size:44px;}
/* 가운데 캐릭터 */
.center{position:relative; min-height:560px; display:flex; justify-content:center; z-index:1;}
.teacher{width:100%; max-width:470px; height:auto; animation:bob 5s ease-in-out infinite;}
@keyframes bob{0%,100%{transform:translateY(0) rotate(-.6deg);}50%{transform:translateY(-8px) rotate(.6deg);}}
.sticker{position:absolute; width:34px; height:34px; filter:drop-shadow(0 3px 3px rgba(0,0,0,.2));}
.sticker path{fill:var(--c); stroke:#fff; stroke-width:1.6; stroke-linejoin:round;}
.s1{top:30%; left:2%; --c:var(--lemon);} .s2{bottom:12%; left:4%; --c:var(--lime); width:28px; height:28px;}
.s3{top:4%; right:12%; --c:var(--tangerine); width:26px; height:26px;} .s4{bottom:22%; right:0; --c:var(--lilac);}
.tape{position:absolute; width:90px; height:26px; background:rgba(94,227,193,.75); top:2%; left:18%; transform:rotate(-14deg); border-radius:2px; box-shadow:0 2px 4px rgba(0,0,0,.08);}
.tape.t2{background:rgba(255,111,174,.7); top:auto; bottom:4%; left:auto; right:20%; transform:rotate(10deg); width:80px;}
.name-tag{position:absolute; bottom:7%; left:50%; transform:translateX(-50%) rotate(-3deg); background:var(--lemon); border:2.5px solid var(--ink); border-radius:999px; padding:6px 18px; font-family:'Archivo Black','Black Han Sans',sans-serif; font-size:15px; box-shadow:4px 4px 0 var(--ink); white-space:nowrap; z-index:3;}
.doodle{position:absolute; pointer-events:none;}
.burst{width:84px; top:-4%; left:28%;} .heart{width:40px; top:44%; right:-4%;} .arrow{width:58px; bottom:14%; right:-10%;}
.clips{width:74px; top:44%; left:-12%;} .hi{width:88px; top:-2%; right:2%;}
/* 오른쪽 */
.caption-sm{font-size:12.5px; color:var(--muted); margin-top:8px;}
.caption-sm b{color:var(--ink);}
.track{display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px dashed rgba(0,0,0,.12);}
.thumb{width:46px; height:46px; min-width:46px; border-radius:10px; display:grid; place-items:center; font-size:22px; border:2px solid var(--ink); box-shadow:3px 3px 0 var(--ink);}
.track-text{flex:1; min-width:0;}
.track-title{font-weight:700; font-size:14.5px; line-height:1.2;}
.track-desc{font-size:11px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); font-family:'Noto Sans KR',sans-serif;}
.track-star{color:var(--cobalt); font-size:18px;}
.quote{display:flex; gap:10px; background:#fff; border:2px solid var(--ink); border-radius:14px; padding:14px 16px; box-shadow:5px 5px 0 var(--lilac); position:relative;}
.quote .num{font-family:'Archivo Black',sans-serif; color:var(--tangerine);}
.quote .who{font-weight:700;}
.quote p{margin:2px 0 0; font-family:'Gowun Dodum','Noto Sans KR',sans-serif; font-size:14px;}
.pantone{text-align:right;}
.pantone .lbl{font-size:13px;} .pantone .lbl b{font-weight:700;}
.dots{display:flex; justify-content:flex-end; gap:8px; margin-top:8px;}
.dot{display:flex; flex-direction:column; align-items:center; gap:4px; font-family:'Instrument Serif',serif; font-style:italic; font-size:10.5px; color:var(--muted);}
.dot span{width:24px; height:24px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 0 1.5px var(--ink);}
.small-title{font-family:'Archivo Black','Black Han Sans',sans-serif; font-size:22px; line-height:1.1; margin:0 0 6px;}
.small-title .hl{background:linear-gradient(transparent 55%, var(--hl) 55%, var(--hl) 92%, transparent 92%); padding:0 .06em;}
.kicker{font-family:'Space Grotesk',sans-serif; font-size:12px; letter-spacing:.14em; text-transform:uppercase; font-weight:700;}
.kicker span{color:var(--cobalt);}
.posted{font-size:13px; letter-spacing:.12em;} .posted b{font-family:'Archivo Black',sans-serif; letter-spacing:0; font-size:15px;}
.pager{display:flex; justify-content:space-between; font-size:13px; max-width:180px;}
.pager b{text-decoration:underline; text-decoration-color:var(--tangerine); text-decoration-thickness:3px;}
.foot{text-align:center; font-size:12.5px; margin-top:34px; line-height:1.7;}
.foot i{font-family:'Instrument Serif',serif; font-size:16px;}
.foot .nick{color:var(--cobalt); font-weight:700; letter-spacing:.14em;}
.foot small{letter-spacing:.3em; color:var(--muted);}
.chips{display:flex; flex-wrap:wrap; gap:6px; margin-top:4px;}
.chip{font-size:11px; font-weight:700; padding:3px 10px; border-radius:999px; border:1.5px solid var(--ink);}
@media (max-width: 900px){
  .grid{grid-template-columns:1fr;}
  .center{order:-1; min-height:auto;}
  .clips,.arrow{display:none;}
}
</style>
"""


def title_block(top, bottom, color, outline_first=False, bar=False):
    hl = PALETTE[color]
    top_html = f'<span class="outline">{esc(top)}</span>' if outline_first else f'<span class="hl">{esc(top)}</span>'
    bottom_html = f'<span class="hl">{esc(bottom)}</span>' if outline_first else f'<span class="outline">{esc(bottom)}</span>'
    bar_html = '<div class="bar"></div>' if bar else ""
    return (
        f'<div class="title-row" style="--hl:{hl}">'
        f'<h1 class="title">{top_html}<br>{bottom_html}</h1>{bar_html}</div>'
    )


s = st.session_state
dots = "".join(
    f'<div class="dot"><span style="background:{PALETTE[n]}"></span>{n}</div>'
    for n in ["Cobalt", "Tangerine", "Bubblegum", "Lime"]
)
stars = "".join(f'<div class="sticker s{i}">{STAR}</div>' for i in range(1, 5))

page = f"""
<div class="page">
<div class="topline">Self-Introduction on <b>Classroom</b><small>page one</small></div>
<div class="grid">
<div class="col">
<div>
{title_block(s.title1_top, s.title1_bottom, s.title1_color, bar=True)}
<div class="meta"><span>{esc(s.date)}</span><b>New Semester</b></div>
<div class="body">{rich(s.body1)}</div>
<div class="liked"><span>Liked by <b>28 students</b></span><span class="heart">♥</span></div>
</div>
<div class="big-letter"><span>A</span><i>a.</i></div>
<div>
<div class="small-title" style="--hl:{PALETTE[s.title4_color]}"><span class="hl">{esc(s.title4)}</span></div>
<div class="body">{rich(s.body4)}</div>
</div>
<div class="posted">POSTED ON <b>{esc(s.handle)}</b></div>
<div class="pager"><span>01 02 <b>03</b></span><span>( + )</span></div>
</div>
<div class="center">
{DOODLE_BURST}{DOODLE_HI}{DOODLE_CLIPS}{DOODLE_HEART}{DOODLE_ARROW}
<div class="tape"></div><div class="tape t2"></div>
{TEACHER_SVG}
{stars}
<div class="name-tag">✏️ {esc(s.name)} 선생님</div>
</div>
<div class="col">
<div>
{title_block(s.title2_top, s.title2_bottom, s.title2_color, outline_first=True)}
<div class="caption-sm">Connected by <b>Classroom Diary</b> ©<br>From {esc(s.name)}'s <b>favorite things</b>:</div>
{playlist_rows(s.list2)}
</div>
<div class="quote"><span class="num">01</span><div><span class="who">{esc(s.title3)}:</span><p>{rich(s.body3)}</p></div></div>
<div class="big-letter" style="text-align:right"><span>E</span><i>e.</i></div>
<div class="pantone"><div class="lbl">Pantone <b>Feels</b></div><div class="dots">{dots}</div></div>
<div>
<div class="kicker">{esc(s.title5)} <span>· ANYTIME</span></div>
<div class="body" style="text-align:right">{rich(s.body5)}</div>
<div class="chips" style="justify-content:flex-end"><span class="chip" style="background:var(--lime)">#친절</span><span class="chip" style="background:var(--lilac)">#호기심</span><span class="chip" style="background:var(--lemon)">#웃음</span></div>
</div>
</div>
</div>
<div class="foot">Handscripted by <i>{esc(s.name)}</i><br>better known as <span class="nick">{esc(s.nickname)}</span><br><small>( 2026 / Class&amp;Folio )</small></div>
</div>
"""

# 빈 줄이 있으면 마크다운이 HTML 블록을 끊으므로 줄바꿈을 모두 제거해서 렌더링한다.
st.markdown(CSS, unsafe_allow_html=True)
st.markdown("".join(line.strip() for line in page.splitlines()), unsafe_allow_html=True)
