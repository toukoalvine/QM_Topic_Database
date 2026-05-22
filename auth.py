"""auth.py – lightweight password gate + role system."""
from __future__ import annotations
import streamlit as st

_USERS = {
    "admin": {"password": "ngk2024", "role": "editor"},
    "viewer": {"password": "view2024", "role": "viewer"},
}

def require_auth() -> None:
    if st.session_state.get("_auth_ok"):
        return
    st.markdown("""
    <style>
    .auth-wrap{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;gap:1rem;}
    .auth-title{font-size:1.6rem;font-weight:800;color:#0F2240;letter-spacing:-0.02em;}
    </style>
    <div class="auth-wrap">
      <div class="auth-title">🔵 NGK Europe · QM Dashboard</div>
      <div style="color:#64748B;font-size:.85rem;">Please sign in to continue</div>
    </div>
    """, unsafe_allow_html=True)
    with st.form("login"):
        user = st.text_input("Username", placeholder="admin")
        pwd  = st.text_input("Password", type="password")
        if st.form_submit_button("Sign in", use_container_width=True):
            rec = _USERS.get(user)
            if rec and rec["password"] == pwd:
                st.session_state["_auth_ok"]   = True
                st.session_state["_auth_user"]  = user
                st.session_state["_auth_role"]  = rec["role"]
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

def can_edit() -> bool:
    return st.session_state.get("_auth_role") == "editor"

def render_auth_header() -> None:
    user = st.session_state.get("_auth_user", "")
    role = st.session_state.get("_auth_role", "")
    badge_color = "#059669" if role == "editor" else "#64748B"
    c1, c2 = st.columns([8, 1])
    with c2:
        st.markdown(
            f'<div style="text-align:right;font-size:.7rem;color:{badge_color};padding-top:.3rem;">'
            f'👤 {user} <span style="background:{badge_color};color:#fff;padding:1px 7px;border-radius:4px;margin-left:4px;">{role}</span></div>',
            unsafe_allow_html=True,
        )
        if st.button("↩", help="Sign out", key="_signout"):
            for k in ["_auth_ok", "_auth_user", "_auth_role"]:
                st.session_state.pop(k, None)
            st.rerun()
