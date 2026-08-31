import os

import httpx
import pandas as pd
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(page_title="GTM Signal Hub", page_icon="🎯", layout="wide")
st.title("GTM Signal Hub")
st.caption("Evidence-driven account prioritization: signals → score → why now → next action")


def get_json(path: str):
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{API_URL}{path}")
        response.raise_for_status()
        return response.json()


try:
    summary = get_json("/dashboard")
    accounts = get_json("/accounts/ranked")
except Exception as exc:
    st.error(f"Backend unavailable at {API_URL}: {exc}")
    st.stop()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Accounts", summary["total_accounts"])
c2.metric("Hot", summary["hot_accounts"])
c3.metric("Warm", summary["warm_accounts"])
c4.metric("Watch", summary["watch_accounts"])
c5.metric("Signals", summary["total_signals"])

st.subheader("Prioritized accounts")
rows = [
    {
        "Account": item["account_name"],
        "Score": item["score"],
        "Tier": item["tier"].upper(),
        "Why now": item["why_now"],
        "Account ID": item["account_id"],
    }
    for item in accounts
]
df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

if accounts:
    st.subheader("Opportunity brief")
    labels = {f'{item["account_name"]} — {item["score"]}/100': item["account_id"] for item in accounts}
    selected = st.selectbox("Account", labels.keys())
    brief = get_json(f'/accounts/{labels[selected]}/brief')

    left, right = st.columns([1, 2])
    with left:
        st.metric("Opportunity score", f'{brief["score"]["score"]}/100')
        st.metric("Tier", brief["score"]["tier"].upper())
        st.caption(f'Reasoning mode: {brief["reasoning_mode"]}')
    with right:
        st.markdown("**Why now**")
        st.write(brief["why_now"])
        st.markdown("**Recommended outreach angle**")
        st.write(brief["outreach_angle"])

    st.markdown("**Evidence**")
    evidence = brief.get("evidence_summary", [])
    if evidence:
        for item in evidence:
            st.write(f"• {item}")
    else:
        st.info("No evidence yet.")

st.divider()
st.caption("Scores are deterministic and auditable. AI reasoning is optional and evidence-grounded.")
