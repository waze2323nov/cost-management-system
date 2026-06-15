import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

st.set_page_config(layout="wide", page_title="Cost Management System 2026", page_icon="📊")

st.markdown("""
<style>
    .cms-header {
        background: #facc15; padding: 18px 28px; border-radius: 10px; margin-bottom: 20px;
    }
    .cms-header h1 {
        color: #1e293b !important; font-size: 22px !important;
        font-weight: 700 !important; letter-spacing: -0.03em;
        margin: 0 !important; padding: 0 !important;
    }
    .cms-header p { color: #713f12; font-size: 13px; margin: 2px 0 0 0; }
    header[data-testid="stHeader"] { background: transparent; }
    .section-credit { color: #16a34a; font-weight: 700; font-size: 16px; }
    .section-debit { color: #dc2626; font-weight: 700; font-size: 16px; }
    [data-testid="stDataEditor"] { overflow-x: hidden !important; }
    [data-testid="stDataEditor"] > div > div { overflow-x: hidden !important; }
    .sum-box {
        background: #1e293b; color: #fff; padding: 14px 20px;
        border-radius: 10px; border: 2px solid #a855f7; text-align: center; margin: 10px 0;
    }
    .sum-box .label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .sum-box .value { font-size: 22px; font-weight: 700; color: #facc15; margin-top: 4px; }
    .sum-box .detail { font-size: 12px; color: #94a3b8; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
CREDIT_CATS = ["Business Revenue","Ad Revenue","Salary / Wages","Refund / Return",
               "Loan Repayment Received","Rental Income","EPF / SOCSO","Other Income"]
DEBIT_CATS = ["Rent & Utilities","Salaries & Wages","Advertising","Car / Transport",
              "Insurance","Loan / Instalment","Family Support","EPF / SOCSO",
              "Ad Management Fee","Office / Supplies","Tax & Compliance","Other Expense"]
STATUS_OPTIONS = ["Confirmed","Pending","Projected"]
DATA_FILE = "cms_data.json"

def get_june_seed():
    return {
        "credits": [
            {"Category": "Business Revenue", "Description": "BUSINESS", "Amount": 8100.0, "Date": "2026-06-19", "Status": "Pending", "Notes": ""},
            {"Category": "Other Income", "Description": "BUSINESS", "Amount": 1000.0, "Date": "2026-06-19", "Status": "Confirmed", "Notes": ""},
            {"Category": "EPF / SOCSO", "Description": "3089", "Amount": 3089.0, "Date": "2026-06-10", "Status": "Confirmed", "Notes": ""},
            {"Category": "Ad Revenue", "Description": "G AD CHARGES", "Amount": 3000.0, "Date": "2026-06-10", "Status": "Confirmed", "Notes": ""},
            {"Category": "Ad Revenue", "Description": "CL AD CHARGES", "Amount": 3300.0, "Date": "2026-06-07", "Status": "Confirmed", "Notes": ""},
        ],
        "debits": [
            {"Category": "Insurance", "Description": "Great Eastern", "Amount": 250.0, "Date": "2026-06-07", "Status": "Confirmed", "Notes": "Pay at 7th"},
            {"Category": "Car / Transport", "Description": "Car hire purchase", "Amount": 430.0, "Date": "2026-06-07", "Status": "Confirmed", "Notes": "Pay at 7th"},
            {"Category": "Family Support", "Description": "Baba", "Amount": 300.0, "Date": "2026-06-07", "Status": "Confirmed", "Notes": "Pay at 7th"},
            {"Category": "Family Support", "Description": "Erjie", "Amount": 450.0, "Date": "2026-06-07", "Status": "Confirmed", "Notes": "Pay at 7th"},
            {"Category": "Loan / Instalment", "Description": "Shopee", "Amount": 744.03, "Date": "2026-06-07", "Status": "Confirmed", "Notes": "Pay at 7th"},
            {"Category": "Rent & Utilities", "Description": "Maxis", "Amount": 237.20, "Date": "2026-06-19", "Status": "Confirmed", "Notes": "Before 15/6"},
            {"Category": "Family Support", "Description": "Mum", "Amount": 1000.0, "Date": "2026-06-19", "Status": "Confirmed", "Notes": "Return 1.0k"},
            {"Category": "Family Support", "Description": "2 Jie", "Amount": 1200.0, "Date": "", "Status": "Pending", "Notes": "Return 1.0k"},
            {"Category": "Family Support", "Description": "Da Jie", "Amount": 1000.0, "Date": "", "Status": "Pending", "Notes": "Cash, no return yet"},
            {"Category": "Family Support", "Description": "Baba (loan)", "Amount": 1200.0, "Date": "", "Status": "Pending", "Notes": "Return 600 next month"},
            {"Category": "Rent & Utilities", "Description": "Electric", "Amount": 0.0, "Date": "", "Status": "Pending", "Notes": "Amount TBC"},
            {"Category": "Rent & Utilities", "Description": "Water", "Amount": 0.01, "Date": "", "Status": "Pending", "Notes": "Amount TBC"},
            {"Category": "Insurance", "Description": "Insurance BABA", "Amount": 200.0, "Date": "2026-06-26", "Status": "Pending", "Notes": ""},
            {"Category": "Loan / Instalment", "Description": "OCBC", "Amount": 266.66, "Date": "", "Status": "Confirmed", "Notes": "Amount TBC"},
            {"Category": "Advertising", "Description": "FB Ads", "Amount": 31.6, "Date": "2026-06-08", "Status": "Confirmed", "Notes": ""},
            {"Category": "Advertising", "Description": "FB Ads", "Amount": 3000.0, "Date": "2026-06-19", "Status": "Pending", "Notes": ""},
            {"Category": "Advertising", "Description": "FB Ads", "Amount": 1488.55, "Date": "2026-06-07", "Status": "Confirmed", "Notes": ""},
            {"Category": "Family Support", "Description": "Baba", "Amount": 200.0, "Date": "2026-06-19", "Status": "Pending", "Notes": ""},
            {"Category": "Salaries & Wages", "Description": "Salary", "Amount": 3300.0, "Date": "", "Status": "Pending", "Notes": ""},
        ],
    }

def init_data():
    d = {}
    for m in MONTHS:
        d[m] = get_june_seed() if m == "June" else {"credits": [], "debits": []}
    return d

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return init_data()

def save_data(d):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass

def parse_date(s):
    if not s or s == "" or s == "None" or s == "NaT":
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except Exception:
        return None

def rows_to_df(rows, kind="credit"):
    cats = CREDIT_CATS if kind == "credit" else DEBIT_CATS
    if not rows:
        return pd.DataFrame({
            "✓": pd.Series([], dtype="bool"),
            "Category": pd.Categorical([], categories=cats),
            "Description": pd.Series([], dtype="str"),
            "Amount": pd.Series([], dtype="float"),
            "Date": pd.Series([], dtype="object"),
            "Status": pd.Categorical([], categories=STATUS_OPTIONS),
            "Notes": pd.Series([], dtype="str"),
        })
    df = pd.DataFrame(rows)
    for col in ["Category","Description","Amount","Date","Status","Notes"]:
        if col not in df.columns:
            df[col] = "" if col != "Amount" else 0.0
    df["✓"] = False
    df["Category"] = pd.Categorical(df["Category"], categories=cats)
    df["Status"] = pd.Categorical(df["Status"], categories=STATUS_OPTIONS)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    # Debits displayed as NEGATIVE
    if kind == "debit":
        df["Amount"] = -df["Amount"].abs()
        df.loc[df["Amount"] == 0, "Amount"] = 0.0
    df["Date"] = df["Date"].apply(parse_date)
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    return df[["✓","Category","Description","Amount","Date","Status","Notes"]]

def df_to_rows(df, kind="credit"):
    df = df.copy()
    if "✓" in df.columns:
        df = df.drop(columns=["✓"])
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    # Convert debit negatives back to positive for storage
    if kind == "debit":
        df["Amount"] = df["Amount"].abs()
    df["Date"] = df["Date"].apply(lambda x: x.isoformat() if pd.notna(x) and x is not None else "")
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    return df.to_dict(orient="records")

if "data" not in st.session_state:
    st.session_state.data = load_data()

st.markdown("""
<div class="cms-header">
    <h1>COST MANAGEMENT SYSTEM</h1>
    <p>Fiscal Year 2026 · MYR</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 Navigation")
    page = st.radio("", ["Monthly Ledger", "Annual Dashboard"], label_visibility="collapsed")
    st.divider()
    selected_month = st.selectbox("Active Month", MONTHS, index=MONTHS.index("June"))
    st.divider()
    if st.button("💾  Save Data", use_container_width=True):
        save_data(st.session_state.data)
        st.success("Saved!")
    dl_bytes = json.dumps(st.session_state.data, indent=2).encode()
    st.download_button("⬇  Export JSON Backup", data=dl_bytes,
                       file_name="cms_backup_2026.json", mime="application/json",
                       use_container_width=True)
    uploaded = st.file_uploader("⬆  Import JSON Backup", type=["json"])
    if uploaded:
        try:
            st.session_state.data = json.load(uploaded)
            save_data(st.session_state.data)
            st.success("Imported!")
            st.rerun()
        except Exception as e:
            st.error(f"Invalid file: {e}")

def credit_col_config():
    return {
        "✓": st.column_config.CheckboxColumn("✓", help="Select for sum", width="small", default=False),
        "Category": st.column_config.SelectboxColumn("Category", options=CREDIT_CATS, required=True, width="medium"),
        "Description": st.column_config.TextColumn("Description", width="medium"),
        "Amount": st.column_config.NumberColumn("RM (+)", min_value=0, format="%.2f", width="small"),
        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", width="small"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True, width="small"),
        "Notes": st.column_config.TextColumn("Notes", width="medium"),
    }

def debit_col_config():
    return {
        "✓": st.column_config.CheckboxColumn("✓", help="Select for sum", width="small", default=False),
        "Category": st.column_config.SelectboxColumn("Category", options=DEBIT_CATS, required=True, width="medium"),
        "Description": st.column_config.TextColumn("Description", width="medium"),
        "Amount": st.column_config.NumberColumn("RM (-)", max_value=0, format="%.2f", width="small"),
        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", width="small"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True, width="small"),
        "Notes": st.column_config.TextColumn("Notes", width="medium"),
    }

# ═════════════════════════════════════
#  MONTHLY LEDGER
# ═════════════════════════════════════
if page == "Monthly Ledger":
    cols = st.columns(12)
    for i, m in enumerate(MONTHS):
        if cols[i].button(m[:3], key=f"month_{m}", use_container_width=True,
                          type="primary" if m == selected_month else "secondary"):
            selected_month = m

    month_data = st.session_state.data.get(selected_month, {"credits": [], "debits": []})
    credit_rows = month_data.get("credits", [])
    debit_rows = month_data.get("debits", [])
    total_credit = sum(r.get("Amount", 0) for r in credit_rows if r.get("Amount"))
    total_debit = sum(r.get("Amount", 0) for r in debit_rows if r.get("Amount"))
    net = total_credit - total_debit
    margin = (net / total_credit * 100) if total_credit else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Credits", f"RM {total_credit:,.2f}")
    k2.metric("Total Debits", f"RM -{total_debit:,.2f}")
    k3.metric("Net P&L", f"RM {net:,.2f}", delta=f"{margin:+.1f}%")
    k4.metric("Entries", f"{len(credit_rows) + len(debit_rows)}")

    st.markdown("---")

    # Credits (+)
    st.markdown('<p class="section-credit">✅ Credits (Inflows) — Positive (+)</p>', unsafe_allow_html=True)
    st.caption("Tick ✓ to include in Selection Sum · Amounts are POSITIVE")
    credit_df = rows_to_df(credit_rows, "credit")
    credit_height = max(35 + (len(credit_df) + 2) * 35 + 3, 120)
    edited_credits = st.data_editor(
        credit_df, num_rows="dynamic", use_container_width=True,
        height=credit_height,
        column_config=credit_col_config(),
        column_order=["✓","Category","Description","Amount","Date","Status","Notes"],
        key=f"credits_{selected_month}",
    )
    st.session_state.data[selected_month]["credits"] = df_to_rows(edited_credits, "credit")

    st.markdown("---")

    # Debits (-)
    st.markdown('<p class="section-debit">🔻 Debits (Outflows) — Negative (-)</p>', unsafe_allow_html=True)
    st.caption("Tick ✓ to include in Selection Sum · Amounts are auto NEGATIVE")
    debit_df = rows_to_df(debit_rows, "debit")
    debit_height = max(35 + (len(debit_df) + 2) * 35 + 3, 120)
    edited_debits = st.data_editor(
        debit_df, num_rows="dynamic", use_container_width=True,
        height=debit_height,
        column_config=debit_col_config(),
        column_order=["✓","Category","Description","Amount","Date","Status","Notes"],
        key=f"debits_{selected_month}",
    )
    # Force any positive input to negative before saving
    edited_debits_save = edited_debits.copy()
    edited_debits_save["Amount"] = -edited_debits_save["Amount"].abs()
    edited_debits_save.loc[edited_debits_save["Amount"] == 0, "Amount"] = 0.0
    st.session_state.data[selected_month]["debits"] = df_to_rows(edited_debits_save, "debit")

    # ── SELECTION SUM — always visible ──
    sel_c = edited_credits[edited_credits["✓"] == True]["Amount"].sum() if "✓" in edited_credits.columns else 0
    sel_d = edited_debits[edited_debits["✓"] == True]["Amount"].sum() if "✓" in edited_debits.columns else 0
    sel_cc = int(edited_credits["✓"].sum()) if "✓" in edited_credits.columns else 0
    sel_dc = int(edited_debits["✓"].sum()) if "✓" in edited_debits.columns else 0
    sel_net = sel_c + sel_d
    sel_total_count = sel_cc + sel_dc

    st.markdown("---")
    st.markdown("#### 📊 Selection Sum")
    if sel_total_count == 0:
        st.caption("Tick ✓ on any row above to start summing — works across both tables")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""<div class="sum-box">
            <div class="label">Selected Credits (+)</div>
            <div class="value" style="color:#4ade80">+ RM {sel_c:,.2f}</div>
            <div class="detail">{sel_cc} item(s)</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="sum-box">
            <div class="label">Selected Debits (-)</div>
            <div class="value" style="color:#f87171">RM {sel_d:,.2f}</div>
            <div class="detail">{sel_dc} item(s)</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        net_color = "#4ade80" if sel_net >= 0 else "#f87171"
        net_sign = "+" if sel_net >= 0 else ""
        st.markdown(f"""<div class="sum-box">
            <div class="label">Net Total (Credits + Debits)</div>
            <div class="value" style="color:{net_color}">{net_sign} RM {sel_net:,.2f}</div>
            <div class="detail">{sel_total_count} item(s) selected</div>
        </div>""", unsafe_allow_html=True)

    # Category breakdown
    new_c = edited_credits["Amount"].sum() if not edited_credits.empty else 0
    new_d = edited_debits["Amount"].abs().sum() if not edited_debits.empty else 0
    if new_c > 0 or new_d > 0:
        st.markdown("---")
        st.markdown("#### Category Breakdown")
        ch1, ch2 = st.columns(2)
        with ch1:
            if new_c > 0:
                grp = edited_credits.groupby("Category", observed=True)["Amount"].sum().reset_index()
                grp = grp[grp["Amount"] > 0].sort_values("Amount", ascending=True)
                if len(grp) > 0:
                    st.markdown("**Credits**")
                    st.bar_chart(grp, x="Category", y="Amount", color="#22c55e", horizontal=True)
        with ch2:
            if new_d > 0:
                dgrp = edited_debits.copy()
                dgrp["Amount"] = dgrp["Amount"].abs()
                grp = dgrp.groupby("Category", observed=True)["Amount"].sum().reset_index()
                grp = grp[grp["Amount"] > 0].sort_values("Amount", ascending=True)
                if len(grp) > 0:
                    st.markdown("**Debits**")
                    st.bar_chart(grp, x="Category", y="Amount", color="#ef4444", horizontal=True)

# ═════════════════════════════════════
#  ANNUAL DASHBOARD
# ═════════════════════════════════════
elif page == "Annual Dashboard":
    st.markdown("## Annual Dashboard · 2026")
    summary = []
    for m in MONTHS:
        md = st.session_state.data.get(m, {"credits": [], "debits": []})
        c = sum(r.get("Amount", 0) for r in md.get("credits", []) if r.get("Amount"))
        d = sum(r.get("Amount", 0) for r in md.get("debits", []) if r.get("Amount"))
        summary.append({"Month": m[:3], "Full": m, "Credits": c, "Debits": d, "Net": c - d})
    sdf = pd.DataFrame(summary)
    ytd_c, ytd_d = sdf["Credits"].sum(), sdf["Debits"].sum()
    ytd_n = ytd_c - ytd_d
    ytd_m = (ytd_n / ytd_c * 100) if ytd_c else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("YTD Revenue", f"RM {ytd_c:,.2f}")
    k2.metric("YTD Expenses", f"RM -{ytd_d:,.2f}")
    k3.metric("YTD Net", f"RM {ytd_n:,.2f}", delta=f"{ytd_m:+.1f}%")
    best = sdf.loc[sdf["Net"].idxmax(), "Month"] if ytd_c > 0 else "—"
    k4.metric("Best Month", best)
    st.divider()
    st.markdown("#### Monthly Trend")
    st.bar_chart(sdf[["Month","Credits","Debits"]].set_index("Month"), color=["#22c55e","#ef4444"])
    st.markdown("#### Net Profit / Loss")
    st.line_chart(sdf[["Month","Net"]].set_index("Month"), color="#3b82f6")
    st.divider()
    st.markdown("#### Monthly Summary Table")
    disp = sdf[["Full","Credits","Debits","Net"]].copy()
    disp.columns = ["Month","Credits (RM)","Debits (RM)","Net (RM)"]
    st.dataframe(disp.style.format({"Credits (RM)":"{:,.2f}","Debits (RM)":"{:,.2f}","Net (RM)":"{:,.2f}"}),
                 use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### Annual Expense by Category")
    all_d = []
    for m in MONTHS:
        all_d.extend(st.session_state.data.get(m,{}).get("debits",[]))
    if all_d:
        adf = pd.DataFrame(all_d)
        if "Category" in adf.columns and "Amount" in adf.columns:
            adf["Amount"] = pd.to_numeric(adf["Amount"], errors="coerce").fillna(0)
            cs = adf.groupby("Category")["Amount"].sum().sort_values(ascending=True).reset_index()
            cs.columns = ["Category","Total (RM)"]
            cs = cs[cs["Total (RM)"] > 0]
            if len(cs) > 0:
                st.bar_chart(cs, x="Category", y="Total (RM)", color="#f59e0b", horizontal=True)
