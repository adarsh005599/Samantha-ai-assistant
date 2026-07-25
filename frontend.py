import datetime as dt
import time

import requests
import streamlit as st

st.set_page_config(
    page_title="Fortis Hospital · Appointments",
    page_icon="🩺",
    layout="centered",
)

# ----------------------------------------------------------------------------
# Design tokens & global styling
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root{
        --ink:        #10242B;
        --deep-teal:  #0E5E59;
        --teal:       #1C8C82;
        --mint:       #E7F4F1;
        --paper:      #F6F8F7;
        --line:       #DCE7E4;
        --coral:      #D6553F;
        --amber:      #C98A2C;
        --good:       #1E8A5F;
    }

    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; color: var(--ink) !important; }
    .stApp { background: var(--paper) !important; }

    /* Hide default streamlit chrome for a cleaner shell */
    #MainMenu, footer { visibility: hidden; }

    /* Force readable light-mode text regardless of the browser/OS theme,
       in case the .streamlit/config.toml isn't picked up */
    label, .stMarkdown, p, span, div { color: var(--ink); }
    [data-testid="stWidgetLabel"] p{ color: var(--ink) !important; font-weight:500; }
    [data-testid="stSidebar"] * { color: var(--ink) !important; }
    [data-testid="stSidebar"] { background: #FFFFFF !important; border-right:1px solid var(--line); }

    /* Tabs */
    button[data-baseweb="tab"] p{ color: #5B6F6B !important; font-weight:500; }
    button[data-baseweb="tab"][aria-selected="true"] p{ color: var(--deep-teal) !important; font-weight:600; }
    div[data-baseweb="tab-highlight"]{ background-color: var(--deep-teal) !important; }
    div[data-baseweb="tab-border"]{ background-color: var(--line) !important; }

    /* ---------- Header ---------- */
    .brand-wrap{
        display:flex; flex-direction:column; align-items:flex-start;
        margin-bottom: 0.25rem;
        animation: fadeUp 0.6s ease-out;
    }
    .brand-eyebrow{
        font-family:'JetBrains Mono', monospace;
        font-size: 0.72rem; letter-spacing: 0.14em; text-transform: uppercase;
        color: var(--teal); margin-bottom: 0.35rem;
    }
    .brand-title{
        font-family:'Fraunces', serif; font-weight:600; font-optical-sizing:auto;
        font-size: 2.35rem; line-height:1.1; color: var(--ink); margin:0;
    }
    .brand-sub{
        color:#5B6F6B; font-size:0.95rem; margin-top:0.4rem;
    }

    /* animated ECG divider — the page's signature element */
    .ecg-wrap{ width:100%; margin: 1.1rem 0 1.6rem 0; }
    .ecg-line{
        stroke: var(--teal); stroke-width:2; fill:none;
        stroke-dasharray: 320; stroke-dashoffset: 320;
        animation: draw 2.2s ease-out forwards, pulseColor 3.4s ease-in-out 2.2s infinite;
    }
    @keyframes draw{ to { stroke-dashoffset: 0; } }
    @keyframes pulseColor{
        0%, 100% { stroke: var(--teal); }
        50% { stroke: var(--deep-teal); }
    }

    /* ---------- Cards ---------- */
    .card{
        background:#FFFFFF; border:1px solid var(--line); border-radius:14px;
        padding:1.5rem 1.5rem 0.9rem 1.5rem; margin-bottom:1.1rem;
        box-shadow: 0 1px 2px rgba(16,36,43,0.03);
        animation: fadeUp 0.5s ease-out both;
    }
    .card:hover{ border-color:#C4D8D3; transition: border-color 0.25s ease; }

    .card-eyebrow{
        font-family:'JetBrains Mono', monospace; font-size:0.7rem;
        letter-spacing:0.1em; text-transform:uppercase; color:var(--teal);
        margin-bottom:0.15rem;
    }
    .card-title{
        font-family:'Fraunces', serif; font-weight:600; font-size:1.28rem;
        margin: 0 0 0.9rem 0; color: var(--ink);
    }
    .card-title.cancel{ color: var(--coral); }

    @keyframes fadeUp{
        from{ opacity:0; transform: translateY(8px); }
        to{ opacity:1; transform: translateY(0); }
    }

    /* ---------- Inputs ---------- */
    .stTextInput input, .stDateInput input, .stTimeInput input,
    .stTextInput input::placeholder{
        border-radius:9px !important; border:1px solid var(--line) !important;
        background:#FFFFFF !important; color: var(--ink) !important;
        font-family:'Inter', sans-serif;
    }
    .stTextInput input:focus, .stDateInput input:focus, .stTimeInput input:focus{
        border-color: var(--teal) !important; box-shadow: 0 0 0 1px var(--teal) !important;
    }
    /* Date/time picker popovers and the little step buttons */
    [data-baseweb="popover"] *, [data-baseweb="calendar"] *{ color: var(--ink) !important; }
    [data-testid="stDateInput"] svg, [data-testid="stTimeInput"] svg{ fill: var(--ink) !important; }

    /* ---------- Buttons ---------- */
    .stButton>button{
        border-radius:9px; border:1px solid var(--deep-teal);
        background: var(--deep-teal); color:#fff; font-weight:600;
        padding:0.5rem 1.1rem; transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton>button:hover{
        transform: translateY(-1px); box-shadow: 0 4px 10px rgba(14,94,89,0.22);
        background: var(--teal); border-color: var(--teal);
    }
    .stButton>button:active{ transform: translateY(0); }

    /* Cancel tab gets a coral action button */
    div[data-testid="stVerticalBlock"] div:has(> div > .cancel-marker) + div .stButton>button{
        background: var(--coral); border-color: var(--coral);
    }

    /* ---------- Status pill ---------- */
    .pill{
        display:inline-flex; align-items:center; gap:0.4rem;
        font-family:'JetBrains Mono', monospace; font-size:0.75rem;
        padding:0.28rem 0.6rem; border-radius:99px; background:var(--mint); color:var(--deep-teal);
        border:1px solid #CFE7E1; margin-bottom:0.6rem;
    }
    .dot{ width:7px; height:7px; border-radius:50%; background:var(--good); }
    .dot.off{ background:#B8433A; }

    hr{ border-color: var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="brand-wrap">
        <div class="brand-eyebrow">Fortis Hospital · Front Desk</div>
        <p class="brand-title">Appointment Booking Portal</p>
        <div class="brand-sub">Schedule, cancel, and review patient appointments in one place.</div>
    </div>
    <div class="ecg-wrap">
        <svg viewBox="0 0 600 40" width="100%" height="40" preserveAspectRatio="none">
            <path class="ecg-line" d="M0,20 L140,20 L160,20 L172,4 L184,36 L196,20 L230,20
                     L242,20 L254,4 L266,36 L278,20 L600,20" />
        </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Backend connection (tucked in the sidebar, out of the main flow)
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("**Backend connection**")
    base_url = st.text_input("Backend URL", "http://localhost:4444").rstrip("/")
    ping_ok = None
    if st.button("Test connection", use_container_width=True):
        try:
            requests.get(f"{base_url}/", timeout=3)
            ping_ok = True
        except requests.RequestException:
            ping_ok = False
    if ping_ok is True:
        st.markdown('<span class="pill"><span class="dot"></span> Reachable</span>', unsafe_allow_html=True)
    elif ping_ok is False:
        st.markdown('<span class="pill"><span class="dot off"></span> Unreachable</span>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Tabs: Schedule / Cancel / Check
# ----------------------------------------------------------------------------
tab_schedule, tab_cancel, tab_check = st.tabs(["📅  Schedule", "✕  Cancel", "🔍  Check appointments"])

# ---- Schedule -----------------------------------------------------------
with tab_schedule:
    st.markdown(
        """
        <div class="card">
            <div class="card-eyebrow">New booking</div>
            <p class="card-title">Schedule an appointment</p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient name", key="sched_name")
        start_date = st.date_input("Date", value=dt.date.today() + dt.timedelta(days=1), key="sched_date")
    with col2:
        reason = st.text_input("Reason (optional)", key="sched_reason")
        start_time = st.time_input("Time", value=dt.time(9, 0), key="sched_time")

    schedule_clicked = st.button("Schedule appointment", key="btn_schedule")
    st.markdown("</div>", unsafe_allow_html=True)

    if schedule_clicked:
        if not patient_name.strip():
            st.warning("Please enter a patient name.")
        else:
            start_dt = dt.datetime.combine(start_date, start_time)
            payload = {
                "patient_name": patient_name.strip(),
                "reason": reason.strip() or None,
                "start_time": start_dt.isoformat(),
            }
            with st.spinner("Booking appointment…"):
                try:
                    resp = requests.post(f"{base_url}/schedule_appointment/", json=payload, timeout=10)
                    resp.raise_for_status()
                    time.sleep(0.2)
                    st.success(f"Scheduled for {patient_name.strip()} on {start_dt:%b %d, %Y at %I:%M %p}.")
                except requests.RequestException as exc:
                    st.error(f"Schedule failed: {exc}")

# ---- Cancel --------------------------------------------------------------
with tab_cancel:
    st.markdown('<span class="cancel-marker"></span>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="card">
            <div class="card-eyebrow">Remove booking</div>
            <p class="card-title cancel">Cancel appointments</p>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        cancel_name = st.text_input("Patient name to cancel", key="cancel_name")
    with col2:
        cancel_date = st.date_input("Date to cancel", value=dt.date.today(), key="cancel_date")

    cancel_clicked = st.button("Cancel appointments", key="btn_cancel")
    st.markdown("</div>", unsafe_allow_html=True)

    if cancel_clicked:
        if not cancel_name.strip():
            st.warning("Please enter a patient name to cancel.")
        else:
            payload = {"patient_name": cancel_name.strip(), "date": cancel_date.isoformat()}
            with st.spinner("Cancelling…"):
                try:
                    resp = requests.post(f"{base_url}/cancel_appointment/", json=payload, timeout=10)
                    resp.raise_for_status()
                    data = resp.json() if resp.content else {}
                    count = data.get("canceled_count", 0)
                    if count:
                        st.success(f"Canceled {count} appointment(s) for {cancel_name.strip()}.")
                    else:
                        st.info("No matching appointments were found to cancel.")
                except requests.RequestException as exc:
                    err_msg = exc.response.text if exc.response is not None else str(exc)
                    st.error(f"Cancel failed: {err_msg}")

# ---- Check -----------------------------------------------------------
with tab_check:
    st.markdown(
        """
        <div class="card">
            <div class="card-eyebrow">Daily view</div>
            <p class="card-title">Check appointments</p>
        """,
        unsafe_allow_html=True,
    )

    appointments_date = st.date_input("Date to check", value=dt.date.today(), key="check_appointment_date")
    check_clicked = st.button("Check appointments", key="btn_check")
    st.markdown("</div>", unsafe_allow_html=True)

    if check_clicked:
        with st.spinner("Loading appointments…"):
            try:
                params = {"date": appointments_date.isoformat()}
                resp = requests.get(f"{base_url}/list_appointments/", params=params, timeout=10)
                resp.raise_for_status()
                rows = resp.json()
                if rows:
                    st.dataframe(rows, use_container_width=True, hide_index=True)
                else:
                    st.info(f"No appointments found for {appointments_date:%b %d, %Y}.")
            except requests.RequestException as exc:
                st.warning(f"Could not load appointments: {exc}")