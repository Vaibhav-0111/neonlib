"""
app.py
Layer : Presentation Layer ONLY
Rule  : Calls auth.py and services.py.  NEVER calls database.py directly.
        Contains zero business logic.
"""

import streamlit as st
from database import initialize_database
import auth
import services
import database as db
from utils import fmt_date, days_until_due, pw_score

# ── page config (must be first Streamlit call) ────────────────
st.set_page_config(
    page_title="NeonLib",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()

# ── theme bootstrap ───────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

DARK = st.session_state["theme"] == "dark"


# ══════════════════════════════════════════════════════════════
# CSS  — injected once, switches on DARK flag
# ══════════════════════════════════════════════════════════════
def _css():
    if DARK:
        # ── dark palette ──────────────────────────────────────
        BG    = "#030712";  CARD  = "#0d1117";  CARD2 = "#111827"
        SB    = "linear-gradient(180deg,#080e1a,#0a0f1e)"
        TXT   = "#e2e8f0";  MUT   = "#64748b";  HEAD  = "#ffffff"
        BDR   = "rgba(0,245,255,.13)";  SB_BDR = "rgba(0,245,255,.18)"
        INP   = "rgba(13,17,23,.97)";   INP_BDR= "rgba(0,245,255,.22)"
        FOCUS = "#00f5ff"
        A1="#00f5ff"; A2="#ff00ff"; A3="#00ff88"
        A4="#ff6b35"; A5="#ffd700"; A6="#7b2fff"
        FONT  = "'Rajdhani',sans-serif"
        HFONT = "'Orbitron',monospace"
        MFONT = "'Share Tech Mono',monospace"
        BRAD  = "6px";  IBRAD = "6px";  LS = "2px";  LLS = "1px"
        GLOW  = True
    else:
        # ── light palette ─────────────────────────────────────
        BG    = "#f1f5f9";  CARD  = "#ffffff";  CARD2 = "#f8faff"
        SB    = "linear-gradient(180deg,#e8eeff,#dde5ff)"
        TXT   = "#1e293b";  MUT   = "#64748b";  HEAD  = "#0f172a"
        BDR   = "rgba(99,102,241,.18)"; SB_BDR = "rgba(99,102,241,.3)"
        INP   = "rgba(255,255,255,.98)";INP_BDR= "rgba(99,102,241,.3)"
        FOCUS = "#6366f1"
        A1="#6366f1"; A2="#a855f7"; A3="#10b981"
        A4="#f97316"; A5="#eab308"; A6="#8b5cf6"
        FONT  = "'Inter',sans-serif"
        HFONT = "'Inter',sans-serif"
        MFONT = "'Inter',sans-serif"
        BRAD  = "8px";  IBRAD = "10px"; LS = ".3px"; LLS = "0"
        GLOW  = False

    def glow(color, spread=10, alpha="66"):
        return f"text-shadow:0 0 {spread}px {color},0 0 {spread*2}px {color}{alpha};" if GLOW else ""
    def shadow(color, blur=8):
        return f"box-shadow:0 0 {blur}px {color};" if GLOW else f"box-shadow:0 2px 8px rgba(0,0,0,.07);"
    def cshadow():
        return "box-shadow:0 2px 10px rgba(0,0,0,.4);" if GLOW else "box-shadow:0 2px 12px rgba(99,102,241,.07);"
    def chover():
        return f"box-shadow:0 0 22px {A1}18,0 8px 32px rgba(0,0,0,.4);" if GLOW else "box-shadow:0 4px 22px rgba(99,102,241,.13);"

    # ── scan-line animation colour ─────────────────────────────
    SC = A1

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── root tokens ── */
:root{{
  --a1:{A1}; --a2:{A2}; --a3:{A3}; --a4:{A4}; --a5:{A5}; --a6:{A6};
  --bg:{BG}; --card:{CARD}; --card2:{CARD2};
  --txt:{TXT}; --mut:{MUT}; --bdr:{BDR};
}}

/* ── app background ── */
.stApp{{
  background:{BG}!important;
  background-image:
    radial-gradient(ellipse 80% 50% at 50% -20%,{A1}0a 0%,transparent 60%),
    radial-gradient(ellipse 60% 40% at 90% 80%,{A2}07 0%,transparent 50%)!important;
  font-family:{FONT}!important;
  color:{TXT}!important;
  transition:background .4s,color .4s;
}}

/* ── sidebar ── */
[data-testid="stSidebar"]{{
  background:{SB}!important;
  border-right:1px solid {SB_BDR}!important;
  transition:all .4s;
}}
[data-testid="stSidebar"]::before{{
  content:''; position:absolute; top:0;left:0;right:0; height:2px;
  background:linear-gradient(90deg,transparent,{SC},transparent);
  animation:scan 3s ease-in-out infinite;
}}
@keyframes scan{{0%,100%{{opacity:.3}}50%{{opacity:1}}}}

/* ── typography ── */
h1,h2,h3{{font-family:{HFONT}!important;letter-spacing:{LS}!important;color:{HEAD}!important;}}

/* ── neon text helpers ── */
.nc{{color:{A1};{glow(A1)}}}
.nm{{color:{A2};{glow(A2)}}}
.ng{{color:{A3};{glow(A3)}}}
.no{{color:{A4};{glow(A4)}}}
.ny{{color:{A5};{glow(A5)}}}
.np{{color:{A6};{glow(A6)}}}

/* ── cards ── */
.card{{
  background:{CARD}; border:1px solid {BDR}; border-radius:14px;
  padding:1.4rem; margin:.7rem 0; position:relative; overflow:hidden;
  transition:all .3s; animation:fadeUp .5s ease both; {cshadow()}
}}
.card::before{{
  content:''; position:absolute; top:0;left:0;right:0; height:1px;
  background:linear-gradient(90deg,transparent,{A1},transparent);
  opacity:{".6" if GLOW else ".3"};
}}
.card:hover{{border-color:{A1}{"66" if GLOW else "40"};{chover()} transform:translateY(-2px);}}
.card-m{{border-color:{A2}{"22" if GLOW else "2e"}!important;}}
.card-m::before{{background:linear-gradient(90deg,transparent,{A2},transparent)!important;}}
.card-g{{border-color:{A3}{"22" if GLOW else "2e"}!important;}}
.card-g::before{{background:linear-gradient(90deg,transparent,{A3},transparent)!important;}}
.card-o{{border-color:{A4}{"33" if GLOW else "2e"}!important;}}
.card-o::before{{background:linear-gradient(90deg,transparent,{A4},transparent)!important;}}

/* ── metric cards ── */
.met{{
  background:{CARD2}; border:1px solid {BDR}; border-radius:16px;
  padding:1.25rem 1rem; text-align:center; position:relative;
  overflow:hidden; animation:fadeUp .6s ease both; transition:all .3s;
  {cshadow()}
}}
.met:hover{{transform:translateY(-3px);}}
.met .mv{{font-family:{HFONT};font-size:1.9rem;font-weight:900;line-height:1;margin-bottom:.25rem;}}
.met .ml{{font-family:{MFONT};font-size:.7rem;color:{MUT};letter-spacing:{"2px" if GLOW else ".3px"};text-transform:uppercase;}}
.met::after{{content:'';position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:60%;height:2px;border-radius:1px;}}
.mc1::after{{background:{A1};{shadow(A1)}}}
.mc2::after{{background:{A2};{shadow(A2)}}}
.mc3::after{{background:{A3};{shadow(A3)}}}
.mc4::after{{background:{A4};{shadow(A4)}}}
.mc5::after{{background:{A5};{shadow(A5)}}}
.mc6::after{{background:{A6};{shadow(A6)}}}

/* ── buttons ── */
.stButton>button{{
  background:transparent!important; border:1px solid {A1}!important;
  color:{A1}!important; font-family:{MFONT}!important;
  letter-spacing:{LLS}!important; text-transform:{"uppercase" if GLOW else "none"}!important;
  font-size:{".78rem" if GLOW else ".87rem"}!important;
  padding:.52rem 1.4rem!important; border-radius:{BRAD}!important;
  transition:all .25s!important; font-weight:{"400" if GLOW else "500"}!important;
}}
.stButton>button:hover{{
  background:{A1}14!important;
  {f"box-shadow:0 0 20px {A1}4d!important;" if GLOW else f"box-shadow:0 4px 12px rgba(99,102,241,.2)!important;"}
  transform:translateY(-1px)!important;
}}

/* ── inputs ── */
.stTextInput>div>div>input,
.stTextArea textarea,
.stSelectbox>div>div>div,
.stNumberInput>div>div>input{{
  background:{INP}!important; border:1px solid {INP_BDR}!important;
  color:{TXT}!important; font-family:{FONT}!important;
  border-radius:{IBRAD}!important; font-size:.95rem!important; transition:all .2s!important;
}}
.stTextInput>div>div>input:focus,.stTextArea textarea:focus{{
  border-color:{FOCUS}!important;
  {f"box-shadow:0 0 12px {FOCUS}26!important;" if GLOW else f"box-shadow:0 0 0 3px {FOCUS}1a!important;"}
}}
.stTextInput label,.stSelectbox label,.stNumberInput label,.stTextArea label{{
  color:{A1}!important; font-family:{MFONT}!important;
  font-size:{".78rem" if GLOW else ".84rem"}!important;
  letter-spacing:{LLS}!important; font-weight:{"400" if GLOW else "500"}!important;
}}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"]{{background:transparent!important;border-bottom:1px solid {BDR}!important;gap:.4rem!important;}}
.stTabs [data-baseweb="tab"]{{background:transparent!important;color:{MUT}!important;font-family:{MFONT}!important;letter-spacing:{"1px" if GLOW else "0"}!important;border:none!important;padding:.58rem 1.1rem!important;transition:color .2s!important;}}
.stTabs [aria-selected="true"]{{color:{A1}!important;border-bottom:2px solid {A1}!important;{glow(A1, 8, "80")}}}

/* ── hr ── */
hr{{border:none!important;height:1px!important;background:linear-gradient(90deg,transparent,{A1}4d,transparent)!important;margin:1.5rem 0!important;}}

/* ── alerts ── */
.stSuccess{{background:{A3}14!important;border:1px solid {A3}4d!important;border-radius:8px!important;}}
.stError  {{background:#ff2d5514!important;border:1px solid #ff2d5540!important;border-radius:8px!important;}}
.stWarning{{background:{A5}14!important;border:1px solid {A5}40!important;border-radius:8px!important;}}
.stInfo   {{background:{A1}0f!important;border:1px solid {A1}33!important;border-radius:8px!important;}}

/* ── scrollbar ── */
::-webkit-scrollbar{{width:5px;height:5px;}}
::-webkit-scrollbar-track{{background:{BG};}}
::-webkit-scrollbar-thumb{{background:{A1}4d;border-radius:3px;}}
::-webkit-scrollbar-thumb:hover{{background:{A1};}}

/* ── animations ── */
@keyframes fadeUp  {{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes slideIn {{from{{opacity:0;transform:translateX(-22px)}}to{{opacity:1;transform:translateX(0)}}}}
@keyframes glowPulse{{
  0%,100%{{{glow(A1,10,"66")}}}
  50%{{{glow(A1,20,"99")}}}
}}
@keyframes floatY{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-5px)}}}}
@keyframes ndot{{0%{{transform:scale(0);opacity:0}}60%{{transform:scale(1.3)}}100%{{transform:scale(1);opacity:1}}}}

.afloat{{animation:floatY 4s ease-in-out infinite;}}
.aglow {{animation:glowPulse 2.5s ease-in-out infinite;}}

/* ── progress bar ── */
.pbar{{height:4px;background:{CARD2};border-radius:2px;overflow:hidden;margin-top:.5rem;}}
.pbar-inner{{height:100%;border-radius:2px;background:linear-gradient(90deg,{A1},{A2});{shadow(A1,6)} transition:width .5s ease;}}

/* ── pw strength ── */
.pw-bar{{height:5px;border-radius:3px;transition:all .35s;margin-top:5px;}}
.pw1{{background:#ff2d55;width:25%;}}
.pw2{{background:{A5};width:50%;}}
.pw3{{background:{A4};width:75%;}}
.pw4{{background:{A3};{shadow(A3,6)} width:100%;}}

/* ── badges ── */
.b-ov{{background:#ff2d5526;border:1px solid #ff2d5566;color:#ff2d55;font-family:{MFONT};font-size:.68rem;padding:2px 8px;border-radius:20px;}}
.b-ok{{background:{A3}1a;border:1px solid {A3}4d;color:{A3};font-family:{MFONT};font-size:.68rem;padding:2px 8px;border-radius:20px;}}
.b-ad{{background:{A2}1a;border:1px solid {A2}55;color:{A2};font-family:{MFONT};font-size:.7rem;padding:2px 9px;border-radius:20px;}}
.b-st{{background:{A1}1a;border:1px solid {A1}44;color:{A1};font-family:{MFONT};font-size:.7rem;padding:2px 9px;border-radius:20px;}}
.b-pe{{background:{A5}1a;border:1px solid {A5}55;color:{A5};font-family:{MFONT};font-size:.68rem;padding:2px 8px;border-radius:20px;}}
.b-ap{{background:{A3}1a;border:1px solid {A3}44;color:{A3};font-family:{MFONT};font-size:.68rem;padding:2px 8px;border-radius:20px;}}
.b-rj{{background:#ff2d5526;border:1px solid #ff2d5544;color:#ff2d55;font-family:{MFONT};font-size:.68rem;padding:2px 8px;border-radius:20px;}}
.ndot{{display:inline-block;width:8px;height:8px;border-radius:50%;background:#ff2d55;{shadow("#ff2d55",5)} animation:ndot .4s ease;vertical-align:middle;margin-left:4px;}}

/* ── book cards ── */
.bcard{{background:{CARD};border:1px solid {BDR};border-radius:14px;padding:1.1rem;position:relative;overflow:hidden;transition:all .3s;{cshadow()}}}
.bcard:hover{{border-color:{A1}{"55" if GLOW else "38"};transform:translateY(-3px);{chover()}}}
.dot-g{{position:absolute;top:.9rem;right:.9rem;width:9px;height:9px;border-radius:50%;background:{A3};{shadow(A3,7)}}}
.dot-r{{position:absolute;top:.9rem;right:.9rem;width:9px;height:9px;border-radius:50%;background:#ff2d55;{shadow("#ff2d55",7)}}}

/* ── sidebar logo ── */
.sb-logo{{font-family:{HFONT};font-size:1.35rem;font-weight:900;color:{A1};{glow(A1,18,"99")} text-align:center;padding:1rem 0 .25rem;letter-spacing:{"3px" if GLOW else ".5px"};animation:glowPulse 3s infinite;}}
.sb-sub {{font-family:{MFONT};font-size:.6rem;color:{MUT};text-align:center;letter-spacing:{"4px" if GLOW else "1px"};text-transform:uppercase;margin-bottom:1rem;}}

/* ── hide streamlit chrome ── */
#MainMenu,footer,header{{visibility:hidden;}}
.block-container{{padding-top:1.5rem!important;}}
</style>
""", unsafe_allow_html=True)


_css()


# ══════════════════════════════════════════════════════════════
# THEME-AWARE HELPER TOKENS  (used by all page functions)
# ══════════════════════════════════════════════════════════════
def _a(k="1"):
    """Return theme-correct accent colour by key."""
    dark  = {"1":"#00f5ff","2":"#ff00ff","3":"#00ff88","4":"#ff6b35","5":"#ffd700","6":"#7b2fff",
             "t":"#e2e8f0","m":"#64748b","bg":"#0d1117","bg2":"#111827"}
    light = {"1":"#6366f1","2":"#a855f7","3":"#10b981","4":"#f97316","5":"#eab308","6":"#8b5cf6",
             "t":"#1e293b","m":"#64748b","bg":"#ffffff","bg2":"#f8faff"}
    return (dark if DARK else light).get(k, "#00f5ff")

def _glow(c, s=10):
    return f"text-shadow:0 0 {s}px {c},0 0 {s*2}px {c}66;" if DARK else ""

def _sh(c, b=8):
    return f"box-shadow:0 0 {b}px {c};" if DARK else ""

def _cshadow():
    return "box-shadow:0 2px 10px rgba(0,0,0,.35);" if DARK else "box-shadow:0 2px 12px rgba(99,102,241,.07);"


# ══════════════════════════════════════════════════════════════
# REUSABLE HTML COMPONENTS
# ══════════════════════════════════════════════════════════════

def metric_card(value, label, ac="1", icon=""):
    c = _a(ac)
    return (f'<div class="met mc{ac}">'
            f'<div class="mv" style="color:{c};">{icon} {value}</div>'
            f'<div class="ml">{label}</div>'
            f'</div>')


def section_title(title, sub="", ac="1"):
    c = _a(ac)
    hf = "Orbitron" if DARK else "Inter"
    mf = "Share Tech Mono" if DARK else "Inter"
    ls = "2.5px" if DARK else ".3px"
    gw = _glow(c, 14)
    sub_html = f'<p style="font-family:{mf},monospace;color:#64748b;font-size:.72rem;letter-spacing:2px;margin:4px 0 0;">{sub}</p>' if sub else ""
    return (f'<div style="margin:1.5rem 0 .9rem;animation:slideIn .4s ease;">'
            f'<h2 style="font-family:{hf},sans-serif;color:{c};{gw}font-size:1.22rem;font-weight:700;letter-spacing:{ls};margin:0;">{title}</h2>'
            f'{sub_html}</div>')


def stars(rating: int) -> str:
    c = _a("5")
    return "".join([f'<span style="color:{c};">★</span>' if i < rating
                    else f'<span style="color:#64748b;">☆</span>'
                    for i in range(5)])


def pbar(pct: float, color: str | None = None) -> str:
    c = color or _a("1")
    sh = f"box-shadow:0 0 6px {c};" if DARK else ""
    return (f'<div class="pbar">'
            f'<div class="pbar-inner" style="width:{pct:.0f}%;background:{c};{sh}"></div>'
            f'</div>')


def pw_strength_widget(password: str):
    """Renders live password strength bar + checklist below a text_input."""
    score = pw_score(password)
    labels = {0: ("", ""), 1: ("pw1", "WEAK"), 2: ("pw2", "FAIR"),
              3: ("pw3", "GOOD"), 4: ("pw4", "STRONG")}
    cls, lbl = labels.get(score, ("", ""))
    colors = {1: "#ff2d55", 2: _a("5"), 3: _a("4"), 4: _a("3")}
    col = colors.get(score, "#64748b")
    bar = f'<div class="pw-bar {cls}"></div>' if score else ""
    checks = [("8+ chars", len(password) >= 8),
              ("Uppercase", any(c.isupper() for c in password)),
              ("Number",    any(c.isdigit() for c in password)),
              ("Special @#$!", any(c in "@#$%^&*!_-" for c in password))]
    chk_html = "".join([
        f'<span style="color:{_a("3") if ok else "#64748b"};font-size:.72rem;margin-right:10px;">{"✓" if ok else "○"} {t}</span>'
        for t, ok in checks])
    lbl_html = f'<span style="color:{col};font-family:Share Tech Mono,monospace;font-size:.68rem;letter-spacing:2px;margin-left:8px;">{lbl}</span>' if lbl else ""
    mf = "Share Tech Mono" if DARK else "Inter"
    st.markdown(
        f'<div style="margin:0 0 .8rem;">'
        f'<div style="display:flex;align-items:center;"><span style="font-size:.7rem;color:#64748b;font-family:{mf},monospace;">STRENGTH</span>{lbl_html}</div>'
        f'{bar}<div style="margin-top:5px;line-height:2;">{chk_html}</div></div>',
        unsafe_allow_html=True)


def status_badge(status: str) -> str:
    cls = {"pending": "b-pe", "approved": "b-ap", "rejected": "b-rj",
           "overdue": "b-ov", "ok": "b-ok", "admin": "b-ad", "student": "b-st"}
    return f'<span class="{cls.get(status, "b-ok")}">{status.upper()}</span>'


def row_line(left, mid="", right="", bg=None, border=None):
    """Generic single-row info line used in lists."""
    bg_  = bg     or _a("bg2")
    bdr_ = border or f"{_a('1')}12"
    return (f'<div style="background:{bg_};border:1px solid {bdr_};border-radius:7px;'
            f'padding:.45rem 1rem;margin:.25rem 0;display:flex;justify-content:space-between;'
            f'align-items:center;font-size:.72rem;">'
            f'<span style="color:{_a("t")};">{left}</span>'
            f'{"<span style=\\'color:" + _a("1") + ";\\'>" + mid + "</span>" if mid else ""}'
            f'{"<span>" + right + "</span>" if right else ""}'
            f'</div>')


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
def sidebar() -> str:
    with st.sidebar:
        logo = (f'NEON<span style="color:{_a("2")}">LIB</span>' if DARK
                else f'<span style="color:{_a("1")}">Neon</span><span style="color:{_a("2")}">Lib</span>')
        st.markdown(f'<div class="sb-logo">{logo}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-sub">Library OS v3.0</div>', unsafe_allow_html=True)

        # ── theme toggle ──────────────────────────────────────
        if st.button("☀️  Light" if DARK else "🌙  Dark",
                     use_container_width=True, key="_theme"):
            st.session_state["theme"] = "light" if DARK else "dark"
            st.rerun()

        st.markdown("---")

        if not auth.is_logged_in():
            page = st.radio("_nav", ["LOGIN", "REGISTER"],
                            format_func=lambda x: {"LOGIN": "🔐  Login",
                                                   "REGISTER": "📝  Register"}[x],
                            label_visibility="collapsed")
            st.markdown("---")
            st.markdown(f'<div style="font-size:.63rem;color:#1e3a4a;text-align:center;line-height:2;">'
                        f'DEFAULT ADMIN<br><span style="color:#2d5a6b;">admin@library.com</span>'
                        f'<br><span style="color:#2d5a6b;">Admin@123</span></div>',
                        unsafe_allow_html=True)
            return page

        # ── logged-in ─────────────────────────────────────────
        u = auth.current_user()
        color   = u.get("avatar_color", _a("1"))
        unread  = db.count_unread_notifications(u["user_id"])
        pending = db.count_pending_requests() if u["role"] == "admin" else 0

        st.markdown(
            f'<div style="background:{_a("bg2")};border:1px solid {_a("1")}22;'
            f'border-radius:12px;padding:.9rem;margin-bottom:1rem;text-align:center;">'
            f'<div style="width:50px;height:50px;border-radius:50%;background:{color};'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-weight:900;font-size:1.2rem;color:#000;'
            f'{_sh(color, 14)}margin-bottom:.5rem;animation:floatY 4s ease-in-out infinite;">'
            f'{u["name"][0].upper()}</div>'
            f'<div style="font-weight:600;font-size:.95rem;color:{_a("t")};">{u["name"]}</div>'
            f'<div style="font-size:.62rem;color:#64748b;">{u["email"]}</div><br>'
            f'{status_badge(u["role"])}</div>',
            unsafe_allow_html=True)

        reddot  = "  🔴" if pending > 0 else ""
        ndot_   = "  🔴" if unread  > 0 else ""
        pages = {
            "DASH":   "🏠  Dashboard",
            "BOOKS":  "📚  Books",
            "LOANS":  "🔄  Issue / Return",
            "REQS":   f"📬  Book Requests{reddot}",
            "NOTIFS": f"🔔  Notifications{ndot_}",
            "WISH":   "♥   Wishlist",
            "HIST":   "📖  Reading History",
            "PROF":   "👤  My Profile",
        }
        if u["role"] == "admin":
            pages["USERS"] = "👥  All Users"

        page = st.radio("_nav", list(pages.keys()),
                        format_func=lambda x: pages[x],
                        label_visibility="collapsed")
        st.markdown("---")
        if st.button("⏻  LOGOUT", use_container_width=True):
            auth.logout_user()
            st.rerun()
        return page


# ══════════════════════════════════════════════════════════════
# PAGE: LOGIN
# ══════════════════════════════════════════════════════════════
def page_login():
    st.markdown(section_title("ACCESS TERMINAL", "AUTHENTICATE TO ENTER THE SYSTEM"), unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        # decorative header card
        st.markdown(
            f'<div style="background:{_a("bg")};border:1px solid {_a("1")}3a;border-radius:16px;'
            f'padding:1.8rem 2rem 1rem;{_sh(_a("1"), 30) if DARK else "box-shadow:0 4px 24px rgba(99,102,241,.1);"}">'
            f'<div style="text-align:center;margin-bottom:1.4rem;">'
            f'<div style="font-size:2.4rem;color:{_a("1")};{"animation:glowPulse 2.5s infinite;" if DARK else ""}">{"◈" if DARK else "🔐"}</div>'
            f'<div style="font-size:.7rem;color:#64748b;letter-spacing:{"4px" if DARK else "1px"};margin-top:.4rem;">IDENTITY VERIFICATION</div>'
            f'</div></div>',
            unsafe_allow_html=True)

        email = st.text_input("EMAIL ADDRESS", placeholder="user@library.com")
        pw    = st.text_input("ACCESS CODE", type="password", placeholder="••••••••")

        # ── live password strength on login page ──────────────
        if pw:
            pw_strength_widget(pw)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("AUTHENTICATE →", use_container_width=True):
            ok, msg, ud = auth.login_user(email, pw)
            if ok:
                auth.save_session(ud)
                st.success(msg)
                st.rerun()
            else:
                st.error(f"⛔ {msg}")

        st.markdown(
            f'<div style="font-size:.63rem;color:#1e3a4a;text-align:center;'
            f'margin-top:.9rem;padding-top:.7rem;border-top:1px solid {_a("1")}0d;">'
            f'HINT: admin@library.com / Admin@123</div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: REGISTER
# ══════════════════════════════════════════════════════════════
def page_register():
    st.markdown(section_title("CREATE PROFILE", "NEW USER REGISTRATION", "2"), unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        st.markdown(
            f'<div style="background:{_a("bg")};border:1px solid {_a("2")}30;border-radius:16px;'
            f'padding:1.4rem 2rem .5rem;{"box-shadow:0 4px 20px rgba(168,85,247,.07);" if not DARK else ""}">'
            f'<div style="text-align:center;margin-bottom:.9rem;">'
            f'<div style="font-size:1.9rem;color:{_a("2")};{_glow(_a("2"), 16)}">{"◉" if DARK else "✨"}</div>'
            f'<div style="font-size:.7rem;color:#64748b;letter-spacing:{"3px" if DARK else "1px"};">REGISTER NEW USER</div>'
            f'</div></div>',
            unsafe_allow_html=True)

        name = st.text_input("FULL NAME", placeholder="Alex Mercer")
        email = st.text_input("EMAIL ADDRESS", placeholder="alex@library.com")
        pw    = st.text_input("CREATE PASSWORD", type="password")
        if pw:
            pw_strength_widget(pw)
        conf = st.text_input("CONFIRM PASSWORD", type="password")
        if conf:
            ok_match = conf == pw
            mc = _a("3") if ok_match else "#ff2d55"
            mt = "✓ Passwords match" if ok_match else "⚠ Passwords do not match"
            st.markdown(f'<span style="color:{mc};font-size:.78rem;">{mt}</span>',
                        unsafe_allow_html=True)
        role = st.selectbox("ACCOUNT TYPE", ["student", "admin"])
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CREATE ACCOUNT →", use_container_width=True):
            if pw != conf:
                st.error("⛔ Passwords do not match.")
            else:
                ok, msg = auth.register_user(name, email, pw, role)
                st.success(f"✅ {msg}") if ok else st.error(f"⛔ {msg}")
        st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════
def page_dash():
    u = auth.current_user()
    if u["role"] == "admin":
        _admin_dash(u)
    else:
        _student_dash(u)


def _admin_dash(u):
    st.markdown(section_title("ADMIN DASHBOARD", "SYSTEM OVERVIEW & ANALYTICS"), unsafe_allow_html=True)
    s = services.library_stats()
    pend = db.count_pending_requests()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.markdown(metric_card(s["total_books"],       "TOTAL BOOKS",  "1","📚"), unsafe_allow_html=True)
    c2.markdown(metric_card(s["total_users"],       "USERS",        "2","👥"), unsafe_allow_html=True)
    c3.markdown(metric_card(s["total_issued"],      "ACTIVE LOANS", "4","🔄"), unsafe_allow_html=True)
    c4.markdown(metric_card(s["unique_authors"],    "AUTHORS",      "3","✍"), unsafe_allow_html=True)
    c5.markdown(metric_card(s["unique_categories"], "CATEGORIES",   "5","🗂"), unsafe_allow_html=True)
    c6.markdown(metric_card(pend, "PENDING REQS",   "4" if pend else "6","📬"), unsafe_allow_html=True)

    st.markdown("---")
    cl, cr = st.columns([1.2, 1])

    with cl:
        st.markdown(section_title("TOP BORROWED BOOKS", "O(n log n) Timsort", "5"), unsafe_allow_html=True)
        rank_c = [_a("5"), "#c0c0c0", "#cd7f32"]
        top = s["top_books"]
        for i, book in enumerate(top):
            rc = rank_c[i] if i < 3 else "#64748b"
            pct = min(100, book["borrow_count"] / max(1, top[0]["borrow_count"]) * 100)
            avg_r, rc_n = db.get_book_avg_rating(book["book_id"])
            st.markdown(
                f'<div class="card" style="padding:.9rem;margin:.35rem 0;">'
                f'<div style="display:flex;align-items:center;gap:.9rem;">'
                f'<div style="font-size:1.3rem;color:{rc};min-width:2rem;text-align:center;'
                f'font-weight:900;{_glow(rc, 9)}">#{i+1}</div>'
                f'<div style="flex:1;">'
                f'<div style="font-weight:700;color:{_a("t")};font-size:.9rem;">{book["title"]}</div>'
                f'<div style="font-size:.7rem;color:#64748b;">{book["author"]} · {book["category"]}</div>'
                f'{f"<div style=\\'font-size:.7rem;margin-top:2px;\\'>{stars(int(avg_r))} {avg_r}/5 ({rc_n})</div>" if avg_r else ""}'
                f'{pbar(pct, rc)}'
                f'</div>'
                f'<div style="color:{rc};font-size:1.05rem;font-weight:700;min-width:2.5rem;text-align:right;">{book["borrow_count"]}</div>'
                f'</div></div>',
                unsafe_allow_html=True)

    with cr:
        st.markdown(section_title("RECENT LOANS", "", "4"), unsafe_allow_html=True)
        for row in list(db.get_all_issued_books())[:5]:
            d = days_until_due(row["due_date"])
            badge = f'<span class="b-ov">OVERDUE {abs(d)}d</span>' if d < 0 else f'<span class="b-ok">{d}d left</span>'
            st.markdown(
                f'<div style="background:{_a("bg2")};border:1px solid {_a("4")}1f;border-radius:8px;'
                f'padding:.55rem 1rem;margin:.28rem 0;">'
                f'<span style="color:{_a("t")};font-weight:600;font-size:.88rem;">{row["title"]}</span>'
                f'<span style="color:#64748b;font-size:.78rem;"> → {row["borrower_name"]}</span>'
                f'<span style="float:right;">{badge}</span></div>',
                unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(section_title("AUTHORS", "SET O(1) dedup", "3"), unsafe_allow_html=True)
        tags = "".join([
            f'<span style="display:inline-block;background:{_a("3")}14;border:1px solid {_a("3")}2e;'
            f'color:{_a("3")};font-size:.67rem;padding:3px 9px;border-radius:20px;margin:3px;">{a}</span>'
            for a in sorted(list(s["authors_set"]))[:18]])
        st.markdown(f'<div style="line-height:2.2;">{tags}</div>', unsafe_allow_html=True)


def _student_dash(u):
    st.markdown(section_title(f"WELCOME BACK, {u['name'].upper()}", "YOUR LIBRARY DASHBOARD"), unsafe_allow_html=True)
    issued   = services.student_issued_books(u["user_id"])
    _, total_fine = services.student_fines(u["user_id"])
    wishlist = list(db.get_wishlist(u["user_id"]))
    history  = db.get_reading_history(u["user_id"])
    unread   = db.count_unread_notifications(u["user_id"])

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(metric_card(len(issued),          "ACTIVE LOANS","1","📖"), unsafe_allow_html=True)
    c2.markdown(metric_card(f"₹{total_fine:.0f}", "FINE",        "4" if total_fine else "3","⚠️"), unsafe_allow_html=True)
    c3.markdown(metric_card(len(wishlist),        "WISHLIST",    "2","♥"), unsafe_allow_html=True)
    c4.markdown(metric_card(len(history),         "BOOKS READ",  "5","📚"), unsafe_allow_html=True)
    c5.markdown(metric_card(unread,               "NOTIFS",      "4" if unread else "1","🔔"), unsafe_allow_html=True)

    st.markdown("---")
    if issued:
        st.markdown(section_title("ACTIVE LOANS",""), unsafe_allow_html=True)
        for b in issued:
            days = b["days_left"]
            badge = f'<span class="b-ov">OVERDUE {abs(days)}d · ₹{b["fine"]:.0f}</span>' if b["is_overdue"] else f'<span class="b-ok">{days}d left</span>'
            pct_ = max(0, min(100, ((7 - max(0, days)) / 7) * 100)) if not b["is_overdue"] else 100
            bc   = "#ff2d55" if b["is_overdue"] else _a("1")
            st.markdown(
                f'<div class="card {"card-o" if b["is_overdue"] else ""}">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                f'<div>'
                f'<div style="font-weight:700;color:{_a("t")};font-size:.98rem;">{b["title"]}</div>'
                f'<div style="font-size:.7rem;color:#64748b;">{b["author"]} · {b["book_id"]}</div>'
                f'<div style="font-size:.7rem;color:#64748b;">DUE: {fmt_date(b["due_date"])}</div>'
                f'</div>{badge}</div>'
                f'{pbar(pct_, bc)}</div>',
                unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="text-align:center;padding:2rem;color:#64748b;'
            f'background:{_a("bg2")};border-radius:12px;border:1px solid {_a("1")}0f;">'
            f'No active loans — visit Issue / Return to borrow a book.</div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: BOOKS
# ══════════════════════════════════════════════════════════════
def page_books():
    auth.require_login()
    u = auth.current_user()
    st.markdown(section_title("BOOK CATALOG", "SEARCH & BROWSE LIBRARY INVENTORY"), unsafe_allow_html=True)

    tnames = ["📖 Browse"]
    if u["role"] == "admin":
        tnames += ["➕ Add Book", "🗑 Remove Book"]
    tabs = st.tabs(tnames)

    # ── browse ────────────────────────────────────────────────
    with tabs[0]:
        cs, cf = st.columns([3, 1])
        with cs:
            q = st.text_input("", placeholder="🔍  Search title, author or category…",
                              label_visibility="collapsed")
        with cf:
            sort = st.selectbox("", ["Default","Most Borrowed","A–Z","Available First"],
                                label_visibility="collapsed")

        books = services.search_books(q) if q else services.all_books_as_dicts()
        if sort == "Most Borrowed":    books = sorted(books, key=lambda b: b.get("borrow_count",0), reverse=True)
        elif sort == "A–Z":            books = sorted(books, key=lambda b: b["title"].lower())
        elif sort == "Available First":books = sorted(books, key=lambda b: b["available_copies"], reverse=True)

        mf = "Share Tech Mono" if DARK else "Inter"
        st.markdown(f'<div style="font-family:{mf},monospace;font-size:.72rem;color:#64748b;margin-bottom:.9rem;">'
                    f'{len(books)} books{"  ·  linear search O(n)" if q else ""}</div>',
                    unsafe_allow_html=True)

        for i in range(0, len(books), 3):
            cols_ = st.columns(3)
            for j, bk in enumerate(books[i:i+3]):
                with cols_[j]:
                    av   = bk["available_copies"]; tot = bk["total_copies"]
                    ac_  = _a("3") if av > 0 else "#ff2d55"
                    pct_ = (av / tot * 100) if tot else 0
                    avg_r, _ = db.get_book_avg_rating(bk["book_id"])
                    in_w = db.is_in_wishlist(u["user_id"], bk["book_id"])

                    st.markdown(
                        f'<div class="bcard">'
                        f'<{"div class=\\'dot-g\\'" if av else "div class=\\'dot-r\\'"}></div>'
                        f'<div style="font-weight:700;color:{_a("t")};font-size:.92rem;padding-right:1.4rem;line-height:1.35;margin-bottom:.28rem;">{bk["title"]}</div>'
                        f'<div style="font-size:.7rem;color:{_a("1")};">✍ {bk["author"]}</div>'
                        f'<div style="font-size:.68rem;color:#64748b;margin:.18rem 0 .5rem;">🗂 {bk["category"]}</div>'
                        f'{"<div style=\\'font-size:.72rem;margin-bottom:.3rem;\\'>" + stars(int(avg_r)) + "</div>" if avg_r else ""}'
                        f'<div style="display:flex;justify-content:space-between;font-size:.7rem;">'
                        f'<span style="color:{ac_};">{av}/{tot} avail</span>'
                        f'<span style="color:#3a4a5a;font-size:.63rem;">ID: {bk["book_id"]}</span></div>'
                        f'{pbar(pct_, ac_)}'
                        f'<div style="font-size:.63rem;color:#3a4a5a;margin-top:.35rem;">📊 {bk["borrow_count"]} borrows {"♥" if in_w else ""}</div>'
                        f'</div>',
                        unsafe_allow_html=True)

                    wl = "♥ Wishlisted" if in_w else "♡ Wishlist"
                    if st.button(wl, key=f"wl_{bk['book_id']}_{i}_{j}", use_container_width=True):
                        _, msg = services.toggle_wishlist(u["user_id"], bk["book_id"])
                        st.toast(msg); st.rerun()

    # ── add / remove (admin) ──────────────────────────────────
    if u["role"] == "admin" and len(tabs) > 1:
        with tabs[1]:
            st.markdown(section_title("ADD NEW BOOK","","3"), unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                title    = st.text_input("BOOK TITLE *")
                author   = st.text_input("AUTHOR *")
                category = st.text_input("CATEGORY *")
            with c2:
                copies = st.number_input("TOTAL COPIES *", min_value=1, max_value=200, value=1)
            if st.button("➕ ADD BOOK", use_container_width=True):
                ok, msg = services.add_book(title, author, category, copies, u["user_id"])
                st.success(msg) if ok else st.error(msg)
                if ok: st.rerun()

        with tabs[2]:
            st.markdown(section_title("REMOVE BOOK","","4"), unsafe_allow_html=True)
            st.warning("⚠️ Books with active loans cannot be deleted.")
            all_bks = services.all_books_as_dicts()
            if all_bks:
                opts = {f"{b['title']}  ({b['book_id']})": b["book_id"] for b in all_bks}
                sel = st.selectbox("SELECT BOOK", list(opts.keys()))
                if st.button("🗑 CONFIRM DELETE", use_container_width=True):
                    ok, msg = services.remove_book(opts[sel])
                    st.success(msg) if ok else st.error(msg)
                    if ok: st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE: ISSUE / RETURN
# ══════════════════════════════════════════════════════════════
def page_loans():
    auth.require_login()
    u = auth.current_user()
    st.markdown(section_title("ISSUE / RETURN", "MANAGE BOOK LOANS", "2"), unsafe_allow_html=True)

    t1, t2 = st.tabs(["📤 Issue Book", "📥 Return Book"])

    with t1:
        st.markdown(
            f'<div style="background:{_a("bg2")};border:1px solid {_a("2")}1a;border-radius:8px;'
            f'padding:.75rem 1rem;margin-bottom:1rem;font-size:.72rem;color:#64748b;">'
            f'Due date = today + 7 days &nbsp;·&nbsp; Fine = ₹5/day overdue &nbsp;·&nbsp; 1 copy per user per book</div>',
            unsafe_allow_html=True)
        ci, cb = st.columns([2, 1])
        with ci:
            bid = st.text_input("BOOK ID", placeholder="BK-XXXXXX", key="iss_bid")
            target = u["user_id"]
            if u["role"] == "admin":
                uf = st.text_input("ISSUE FOR USER ID (blank = yourself)", placeholder="USR-XXXXXX", key="iss_uid")
                if uf.strip(): target = uf.strip()
        with cb:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("📤 ISSUE", use_container_width=True):
                if not bid.strip(): st.error("Enter a Book ID.")
                else:
                    ok, msg = services.issue_book(bid.strip().upper(), target)
                    st.success(msg) if ok else st.error(f"⛔ {msg}")
                    if ok: st.rerun()
        st.markdown("---")
        st.markdown(f'<div style="font-size:.7rem;color:#64748b;margin-bottom:.4rem;">AVAILABLE BOOKS (quick ref)</div>', unsafe_allow_html=True)
        for b in [x for x in services.all_books_as_dicts() if x["available_copies"] > 0][:8]:
            st.markdown(row_line(b["title"], b["book_id"], f'<span style="color:{_a("3")};">{b["available_copies"]} avail</span>'), unsafe_allow_html=True)

    with t2:
        cr, cb2 = st.columns([2, 1])
        with cr:
            rbid = st.text_input("BOOK ID", placeholder="BK-XXXXXX", key="ret_bid")
            rtarget = u["user_id"]
            if u["role"] == "admin":
                ruf = st.text_input("RETURN FOR USER ID", placeholder="USR-XXXXXX", key="ret_uid")
                if ruf.strip(): rtarget = ruf.strip()
        with cb2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("📥 RETURN", use_container_width=True):
                if not rbid.strip(): st.error("Enter a Book ID.")
                else:
                    ok, msg, fine = services.return_book(rbid.strip().upper(), rtarget)
                    if ok:
                        st.warning(msg) if fine > 0 else st.success(msg)
                        st.rerun()
                    else:
                        st.error(f"⛔ {msg}")
        st.markdown("---")
        for b in services.student_issued_books(u["user_id"]):
            days = b["days_left"]
            badge = f'<span class="b-ov">OVERDUE</span>' if b["is_overdue"] else f'<span class="b-ok">{days}d</span>'
            st.markdown(row_line(b["title"], b["book_id"], badge), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: BOOK REQUESTS
# ══════════════════════════════════════════════════════════════
def page_requests():
    auth.require_login()
    u = auth.current_user()
    if u["role"] == "admin":
        _admin_reqs(u)
    else:
        _student_reqs(u)


def _student_reqs(u):
    st.markdown(section_title("BOOK REQUESTS", "REQUEST A BOOK FROM ADMIN", "5"), unsafe_allow_html=True)
    t1, t2 = st.tabs(["📬 New Request", "📋 My Requests"])
    with t1:
        st.markdown(
            f'<div style="background:{_a("bg2")};border:1px solid {_a("5")}1a;border-radius:8px;'
            f'padding:.85rem;margin-bottom:1rem;font-size:.82rem;color:#64748b;">'
            f'Can\'t find a book? Request it — admin will review and add it to the catalog.</div>',
            unsafe_allow_html=True)
        bt = st.text_input("BOOK TITLE *", placeholder="e.g. The Pragmatic Programmer")
        ba = st.text_input("AUTHOR (optional)")
        br = st.text_area("WHY DO YOU NEED THIS BOOK?", height=85)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📬 SUBMIT REQUEST", use_container_width=True):
            ok, msg = services.submit_request(u["user_id"], u["name"], bt, ba, br)
            st.success(msg) if ok else st.error(msg)

    with t2:
        reqs = db.get_requests_by_user(u["user_id"])
        if not reqs:
            st.info("No requests submitted yet.")
        for r in reqs:
            r = dict(r)
            note_html = (f'<div style="font-size:.78rem;color:{_a("3")};margin-top:.3rem;">'
                         f'💬 Admin: {r["admin_note"]}</div>') if r["admin_note"] else ""
            st.markdown(
                f'<div class="card" style="padding:.9rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:flex-start;">'
                f'<div>'
                f'<div style="font-weight:700;color:{_a("t")};font-size:.93rem;">{r["book_title"]}</div>'
                f'{"<div style=\\'font-size:.7rem;color:#64748b;\\'>" + r["author"] + "</div>" if r["author"] else ""}'
                f'<div style="font-size:.7rem;color:#64748b;">{fmt_date(r["created_at"])}</div>'
                f'{note_html}</div>'
                f'{status_badge(r["status"])}</div>'
                f'{"<div style=\\'font-size:.78rem;color:#64748b;margin-top:.5rem;font-style:italic;\\'>" + chr(34) + r["reason"] + chr(34) + "</div>" if r["reason"] else ""}'
                f'</div>',
                unsafe_allow_html=True)


def _admin_reqs(u):
    st.markdown(section_title("BOOK REQUESTS", "REVIEW & RESPOND", "5"), unsafe_allow_html=True)
    pend = db.count_pending_requests()
    t1, t2 = st.tabs([f"⏳ Pending ({pend})", "📋 All"])

    for idx, tab in enumerate([t1, t2]):
        with tab:
            all_r = [dict(r) for r in db.get_all_requests()]
            reqs  = [r for r in all_r if r["status"] == "pending"] if idx == 0 else all_r
            if not reqs:
                st.info("Nothing here."); continue
            for r in reqs:
                with st.expander(f"📬  {r['book_title']}  —  {r['user_name']}", expanded=(r["status"]=="pending")):
                    st.markdown(
                        f'<div style="font-size:.82rem;color:#64748b;margin-bottom:.8rem;">'
                        f'<b style="color:{_a("t")};">From:</b> {r["user_name"]} ({r["user_id"]})<br>'
                        f'<b style="color:{_a("t")};">Author:</b> {r["author"] or "—"}<br>'
                        f'<b style="color:{_a("t")};">Reason:</b> {r["reason"] or "None"}<br>'
                        f'<b style="color:{_a("t")};">Date:</b> {fmt_date(r["created_at"])} &nbsp;'
                        f'{status_badge(r["status"])}</div>',
                        unsafe_allow_html=True)
                    if r["status"] == "pending":
                        note = st.text_input("Admin note", key=f"n_{r['request_id']}", placeholder="e.g. Will add next week")
                        ca, cb_ = st.columns(2)
                        with ca:
                            if st.button("✅ Approve", key=f"ap_{r['request_id']}", use_container_width=True):
                                ok, msg = services.respond_to_request(r["request_id"], "approved", note, u["name"])
                                st.success(msg); st.rerun()
                        with cb_:
                            if st.button("❌ Reject", key=f"rj_{r['request_id']}", use_container_width=True):
                                ok, msg = services.respond_to_request(r["request_id"], "rejected", note, u["name"])
                                st.warning(msg); st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE: NOTIFICATIONS
# ══════════════════════════════════════════════════════════════
def page_notifs():
    auth.require_login()
    u = auth.current_user()
    st.markdown(section_title("NOTIFICATIONS", "YOUR ACTIVITY FEED"), unsafe_allow_html=True)
    notifs = db.get_notifications(u["user_id"], 30)
    if notifs:
        if st.button("✓  Mark all as read"):
            db.mark_notifications_read(u["user_id"]); st.rerun()
        tmap = {"success":_a("3"),"warning":_a("5"),"error":"#ff2d55","info":_a("1")}
        imap = {"success":"✅","warning":"⚠️","error":"❌","info":"ℹ️"}
        for n in notifs:
            n = dict(n)
            c = tmap.get(n["type"], _a("1"))
            ico = imap.get(n["type"], "ℹ️")
            op = "1" if not n["is_read"] else ".44"
            dot = '<span class="ndot"></span>' if not n["is_read"] else ""
            st.markdown(
                f'<div style="background:{_a("bg2")};border:1px solid {c}22;border-radius:10px;'
                f'padding:.78rem 1rem;margin:.28rem 0;opacity:{op};transition:opacity .3s;">'
                f'<div style="display:flex;align-items:flex-start;gap:.8rem;">'
                f'<span style="font-size:1.05rem;">{ico}</span>'
                f'<div style="flex:1;">'
                f'<div style="font-size:.88rem;color:{_a("t")};">{n["message"]}{dot}</div>'
                f'<div style="font-size:.67rem;color:#64748b;margin-top:3px;">{fmt_date(n["created_at"])}</div>'
                f'</div></div></div>',
                unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="text-align:center;padding:3rem;color:#64748b;">'
            f'<div style="font-size:2rem;margin-bottom:.5rem;">🔔</div>'
            f'<div>No notifications yet.</div></div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: WISHLIST
# ══════════════════════════════════════════════════════════════
def page_wishlist():
    auth.require_login()
    u = auth.current_user()
    st.markdown(section_title("MY WISHLIST", "BOOKS YOU WANT TO READ", "2"), unsafe_allow_html=True)
    items = list(db.get_wishlist(u["user_id"]))
    if not items:
        st.markdown(
            f'<div style="text-align:center;padding:3rem;color:#64748b;'
            f'background:{_a("bg2")};border-radius:12px;">'
            f'<div style="font-size:2rem;">♡</div>'
            f'<div>Wishlist empty. Browse books and click ♡ Wishlist.</div></div>',
            unsafe_allow_html=True)
        return
    for i in range(0, len(items), 3):
        cols_ = st.columns(3)
        for j, it in enumerate(items[i:i+3]):
            it = dict(it)
            with cols_[j]:
                av_c = _a("3") if it["available_copies"] > 0 else "#ff2d55"
                st.markdown(
                    f'<div class="card card-m">'
                    f'<div style="font-weight:700;color:{_a("t")};font-size:.93rem;">{it["title"]}</div>'
                    f'<div style="font-size:.7rem;color:{_a("1")};margin-top:3px;">✍ {it["author"]}</div>'
                    f'<div style="font-size:.7rem;color:#64748b;">🗂 {it["category"]}</div>'
                    f'<div style="margin-top:.55rem;font-size:.72rem;color:{av_c};">'
                    f'{"✅ Available now!" if it["available_copies"] > 0 else "❌ Currently out"}</div>'
                    f'<div style="font-size:.63rem;color:#64748b;margin-top:3px;">ID: {it["book_id"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True)
                if st.button("♥ Remove", key=f"rw_{it['book_id']}_{i}_{j}", use_container_width=True):
                    db.remove_from_wishlist(u["user_id"], it["book_id"]); st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE: READING HISTORY + RATINGS
# ══════════════════════════════════════════════════════════════
def page_history():
    auth.require_login()
    u = auth.current_user()
    st.markdown(section_title("READING HISTORY", "BOOKS YOU'VE READ — RATE & REVIEW", "5"), unsafe_allow_html=True)
    hist = db.get_reading_history(u["user_id"])
    if not hist:
        st.info("No history yet. Return a book to start tracking!"); return

    total_days = sum(h["days_kept"] for h in hist)
    rated = [h for h in hist if h["rating"] > 0]
    avg_pr = round(sum(h["rating"] for h in rated) / len(rated), 1) if rated else 0
    fav_cat: dict = {}
    for h in hist: fav_cat[h["category"]] = fav_cat.get(h["category"], 0) + 1
    fav = max(fav_cat, key=fav_cat.get) if fav_cat else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card(len(hist),      "BOOKS READ",  "1","📚"), unsafe_allow_html=True)
    c2.markdown(metric_card(total_days,     "TOTAL DAYS",  "3","📅"), unsafe_allow_html=True)
    c3.markdown(metric_card(f"{avg_pr}★",   "AVG RATING",  "5",""), unsafe_allow_html=True)
    c4.markdown(metric_card(fav,            "FAV GENRE",   "2","🎯"), unsafe_allow_html=True)

    st.markdown("---")
    for h in hist:
        h = dict(h)
        avg_r, rev_n = db.get_book_avg_rating(h["book_id"])
        with st.expander(f"📖  {h['book_title']}  —  {h['author']}  —  {fmt_date(h['returned_at'])}"):
            cl1, cl2 = st.columns([2, 1])
            with cl1:
                st.markdown(
                    f'<div style="font-size:.82rem;color:#64748b;margin-bottom:.8rem;">'
                    f'<span style="color:{_a("1")};">Category:</span> {h["category"]} &nbsp;·&nbsp;'
                    f'<span style="color:{_a("1")};">Kept:</span> {h["days_kept"]} days</div>',
                    unsafe_allow_html=True)
                if avg_r:
                    st.markdown(f'<div style="font-size:.8rem;color:#64748b;">Community: {stars(int(avg_r))} {avg_r}/5 ({rev_n} reviews)</div>', unsafe_allow_html=True)
                if h["review"]:
                    st.markdown(
                        f'<div style="font-size:.84rem;color:{_a("t")};margin-top:.5rem;padding:.65rem;'
                        f'background:{_a("bg2")};border-radius:6px;font-style:italic;">"{h["review"]}"</div>',
                        unsafe_allow_html=True)
            with cl2:
                st.markdown(f'<div style="font-size:.72rem;color:#64748b;margin-bottom:.28rem;">YOUR RATING</div>', unsafe_allow_html=True)
                nr   = st.selectbox("R", [0,1,2,3,4,5], index=h["rating"],
                                    format_func=lambda x: "Not rated" if x==0 else "⭐"*x,
                                    key=f"rt_{h['history_id']}", label_visibility="collapsed")
                nrev = st.text_area("Rev", value=h["review"] or "", key=f"rv_{h['history_id']}",
                                    height=62, label_visibility="collapsed", placeholder="Write a short review…")
                if st.button("Save ★", key=f"sv_{h['history_id']}", use_container_width=True):
                    ok, msg = services.rate_book(h["history_id"], nr, nrev)
                    st.success(msg) if ok else st.error(msg); st.rerun()


# ══════════════════════════════════════════════════════════════
# PAGE: MY PROFILE
# ══════════════════════════════════════════════════════════════
def page_profile():
    auth.require_login()
    u = auth.current_user()
    st.markdown(section_title("MY PROFILE", "ACCOUNT & ACTIVITY", "6"), unsafe_allow_html=True)

    cl, cr = st.columns([1, 2])
    with cl:
        color = u.get("avatar_color", _a("1"))
        st.markdown(
            f'<div class="card" style="text-align:center;border-color:{_a("6")}2e;">'
            f'<div style="width:80px;height:80px;border-radius:50%;background:{color};'
            f'margin:0 auto 1rem;display:flex;align-items:center;justify-content:center;'
            f'font-weight:900;font-size:2rem;color:#000;{_sh(color,22)}animation:floatY 4s ease-in-out infinite;">'
            f'{u["name"][0].upper()}</div>'
            f'<div style="font-weight:700;font-size:1rem;color:{_a("t")};">{u["name"]}</div>'
            f'<div style="font-size:.7rem;color:#64748b;">{u["email"]}</div>'
            f'<br>{status_badge(u["role"])}<br><br>'
            f'<div style="font-size:.63rem;color:#3a4a5a;">ID: {u["user_id"]}<br>SINCE: {fmt_date(u["created_at"])}</div>'
            f'</div>',
            unsafe_allow_html=True)

    with cr:
        issued   = services.student_issued_books(u["user_id"])
        fines, total_fine = services.student_fines(u["user_id"])
        history  = db.get_reading_history(u["user_id"])
        wishlist = list(db.get_wishlist(u["user_id"]))

        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(metric_card(len(issued),          "ACTIVE LOANS","1","📖"), unsafe_allow_html=True)
        c2.markdown(metric_card(f"₹{total_fine:.0f}", "FINE",        "4" if total_fine else "3","💸"), unsafe_allow_html=True)
        c3.markdown(metric_card(len(history),         "READ",        "5","📚"), unsafe_allow_html=True)
        c4.markdown(metric_card(len(wishlist),        "WISHLIST",    "2","♥"), unsafe_allow_html=True)

        if fines:
            st.markdown(section_title("FINE HISTORY","","4"), unsafe_allow_html=True)
            for f in fines[:6]:
                sc = "#ff2d55" if not f["paid"] else _a("3")
                st.markdown(
                    f'<div style="background:{_a("bg2")};border:1px solid {_a("4")}1f;border-radius:8px;'
                    f'padding:.55rem 1rem;margin:.28rem 0;">'
                    f'<span style="font-weight:600;color:{_a("t")};">{f["title"]}</span>'
                    f'<span style="float:right;font-weight:700;color:{sc};">₹{f["amount"]:.0f}</span><br>'
                    f'<span style="font-size:.67rem;color:#64748b;">{f["days_late"]}d late · {fmt_date(f["created_at"])}</span>'
                    f'<span style="float:right;font-size:.67rem;color:{sc};">{"UNPAID" if not f["paid"] else "PAID"}</span>'
                    f'</div>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PAGE: ALL USERS  (admin only)
# ══════════════════════════════════════════════════════════════
def page_users():
    auth.require_login()
    auth.require_admin()
    st.markdown(section_title("USER REGISTRY", "ALL REGISTERED ACCOUNTS", "2"), unsafe_allow_html=True)

    q = st.text_input("", placeholder="🔍  Search by name or email…", label_visibility="collapsed")
    users = services.search_users(q) if q else services.all_users_as_dicts()
    mf = "Share Tech Mono" if DARK else "Inter"
    st.markdown(f'<div style="font-family:{mf},monospace;font-size:.72rem;color:#64748b;margin-bottom:.8rem;">{len(users)} users</div>', unsafe_allow_html=True)

    for u in users:
        u = dict(u) if not isinstance(u, dict) else u
        color  = u.get("avatar_color", _a("1"))
        issued = db.get_issued_books_by_user(u["user_id"])
        fine   = db.get_total_fine_by_user(u["user_id"])
        hist   = db.get_reading_history(u["user_id"])
        st.markdown(
            f'<div class="card {"card-m" if u["role"]=="admin" else ""}">'
            f'<div style="display:flex;align-items:center;gap:.9rem;">'
            f'<div style="width:42px;height:42px;border-radius:50%;background:{color};flex-shrink:0;'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-weight:900;font-size:1.1rem;color:#000;{_sh(color,11)}">'
            f'{u["name"][0].upper()}</div>'
            f'<div style="flex:1;">'
            f'<div style="font-weight:700;color:{_a("t")};font-size:.93rem;">{u["name"]}</div>'
            f'<div style="font-size:.67rem;color:#64748b;">{u["email"]} · {u["user_id"]}</div>'
            f'</div>'
            f'<div style="display:flex;gap:.55rem;align-items:center;flex-shrink:0;">'
            f'{status_badge(u["role"])}'
            f'<span style="font-size:.67rem;color:{_a("1")};">{len(issued)} loans</span>'
            f'<span style="font-size:.67rem;color:{_a("5")};">{len(hist)} read</span>'
            f'{"<span style=\\'font-size:.67rem;color:" + _a("4") + ";\\'>" + f"₹{fine:.0f}" + "</span>" if fine > 0 else ""}'
            f'</div></div></div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════
def main():
    page = sidebar()

    if not auth.is_logged_in():
        if page == "REGISTER": page_register()
        else:                  page_login()
        return

    dispatch = {
        "DASH":   page_dash,
        "BOOKS":  page_books,
        "LOANS":  page_loans,
        "REQS":   page_requests,
        "NOTIFS": page_notifs,
        "WISH":   page_wishlist,
        "HIST":   page_history,
        "PROF":   page_profile,
        "USERS":  page_users,
    }
    dispatch.get(page, page_dash)()


if __name__ == "__main__":
    main()
