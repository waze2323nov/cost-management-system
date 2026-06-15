import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# ─── Page Config ───
st.set_page_config(layout="wide", page_title="Cost Management System 2026", page_icon="📊")

# ─── Custom CSS ───
st.markdown("""
<style>
    .cms-header {
        background: #facc15;
        padding: 18px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .cms-header h1 {
        color: #1e293b !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em;
        margin: 0 !important;
        padding: 0 !important;
    }
    .cms-header p {
        color: #713f12;
        font-size: 13px;
        margin: 2px 0 0 0;
    }
    header[data-testid="stHeader"] { background: transparent; }
    .section-credit { color: #16a34a; font-weight: 700; font-size: 16px; }
    .section-debit { color: #dc2626; font-weight: 700; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───
MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

CREDIT_CATS = ["Business Revenue","Ad Revenue","Salary / Wages","Refund / Return",
               "Loan Repayment Received","Rental Income","EPF / SOCSO","Other Income"]

DEBIT_CATS = ["Rent & Utilities","Salaries & Wages","Advertising","Car / Transport",
              "Insurance","Loan / Instalment","Family Support","EPF / SOCSO",
              "Ad Management Fee","Office / Supplies","Tax & Compliance","Other Expense"]

STATUS_OPTIONS = ["Confirmed","Pending","Projected"]
DATA_FILE = "cms_data.json"

# ─── Data helpers ───
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
    df["Category"] = pd.Categorical(df["Category"], categories=cats)
    df["Status"] = pd.Categorical(df["Status"], categories=STATUS_OPTIONS)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = df["Date"].apply(parse_date)
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    return df[["Category","Description","Amount","Date","Status","Notes"]]

def df_to_rows(df):
    df = df.copy()
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = df["Date"].apply(lambda x: x.isoformat() if pd.notna(x) and x is not None else "")
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    return df.to_dict(orient="records")

# ─── Load data ───
if "data" not in st.session_state:
    st.session_state.data = load_data()

# ─── Yellow Header ───
st.markdown("""
<div class="cms-header">
    <h1>COST MANAGEMENT SYSTEM</h1>
    <p>Fiscal Year 2026 · MYR</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ───
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

# ─── Column config shared ───
def get_col_config(cats):
    return {
        "Category": st.column_config.SelectboxColumn("Category", options=cats, required=True),
        "Description": st.column_config.TextColumn("Description"),
        "Amount": st.column_config.NumberColumn("Amount (RM)", min_value=0, format="%.2f"),
        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True),
        "Notes": st.column_config.TextColumn("Notes"),
    }

# ═════════════════════════════════════
#  MONTHLY LEDGER
# ═════════════════════════════════════
if page == "Monthly Ledger":
    # Month pill bar
    cols = st.columns(12)
    for i, m in enumerate(MONTHS):
        if cols[i].button(m[:3], key=f"month_{m}", use_container_width=True,
                          type="primary" if m == selected_month else "secondary"):
            selected_month = m

    month_data = st.session_state.data.get(selected_month, {"credits": [], "debits": []})

    # ── Pre-calculate totals for KPI ──
    credit_rows = month_data.get("credits", [])
    debit_rows = month_data.get("debits", [])
    total_credit = sum(r.get("Amount", 0) for r in credit_rows if r.get("Amount"))
    total_debit = sum(r.get("Amount", 0) for r in debit_rows if r.get("Amount"))
    net = total_credit - total_debit
    margin = (net / total_credit * 100) if total_credit else 0
    entry_count = len(credit_rows) + len(debit_rows)

    # ── KPI strip AT THE TOP ──
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Credits", f"RM {total_credit:,.2f}")
    k2.metric("Total Debits", f"RM {total_debit:,.2f}")
    k3.metric("Net P&L", f"RM {net:,.2f}", delta=f"{margin:+.1f}%")
    k4.metric("Entries", f"{entry_count}")

    st.markdown("---")

    # ── Credits table ──
    st.markdown('<p class="section-credit">✅ Credits (Inflows)</p>', unsafe_allow_html=True)
    st.caption("To delete: select row checkbox on the left → press Delete key")
    credit_df = rows_to_df(credit_rows, "credit")
    edited_credits = st.data_editor(
        credit_df, num_rows="dynamic", use_container_width=True,
        column_config=get_col_config(CREDIT_CATS),
        key=f"credits_{selected_month}",
    )
    st.session_state.data[selected_month]["credits"] = df_to_rows(edited_credits)

    st.markdown("---")

    # ── Debits table ──
    st.markdown('<p class="section-debit">🔻 Debits (Outflows)</p>', unsafe_allow_html=True)
    st.caption("To delete: select row checkbox on the left → press Delete key")
    debit_df = rows_to_df(debit_rows, "debit")
    edited_debits = st.data_editor(
        debit_df, num_rows="dynamic", use_container_width=True,
        column_config=get_col_config(DEBIT_CATS),
        key=f"debits_{selected_month}",
    )
    st.session_state.data[selected_month]["debits"] = df_to_rows(edited_debits)

    # ── Category breakdown ──
    new_total_c = edited_credits["Amount"].sum() if not edited_credits.empty else 0
    new_total_d = edited_debits["Amount"].sum() if not edited_debits.empty else 0
    if new_total_c > 0 or new_total_d > 0:
        st.markdown("---")
        st.markdown("#### Category Breakdown")
        ch1, ch2 = st.columns(2)
        with ch1:
            if new_total_c > 0:
                grp = edited_credits.groupby("Category", observed=True)["Amount"].sum().reset_index()
                grp = grp[grp["Amount"] > 0].sort_values("Amount", ascending=True)
                if len(grp) > 0:
                    st.markdown("**Credits**")
                    st.bar_chart(grp, x="Category", y="Amount", color="#22c55e", horizontal=True)
        with ch2:
            if new_total_d > 0:
                grp = edited_debits.groupby("Category", observed=True)["Amount"].sum().reset_index()
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
    ytd_c = sdf["Credits"].sum()
    ytd_d = sdf["Debits"].sum()
    ytd_n = ytd_c - ytd_d
    ytd_m = (ytd_n / ytd_c * 100) if ytd_c else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("YTD Revenue", f"RM {ytd_c:,.2f}")
    k2.metric("YTD Expenses", f"RM {ytd_d:,.2f}")
    k3.metric("YTD Net", f"RM {ytd_n:,.2f}", delta=f"{ytd_m:+.1f}%")
    best = sdf.loc[sdf["Net"].idxmax(), "Month"] if ytd_c > 0 else "—"
    k4.metric("Best Month", best)

    st.divider()
    st.markdown("#### Monthly Trend")
    trend = sdf[["Month", "Credits", "Debits"]].set_index("Month")
    st.bar_chart(trend, color=["#22c55e", "#ef4444"])

    st.markdown("#### Net Profit / Loss")
    net_line = sdf[["Month", "Net"]].set_index("Month")
    st.line_chart(net_line, color="#3b82f6")

    st.divider()
    st.markdown("#### Monthly Summary Table")
    display_df = sdf[["Full", "Credits", "Debits", "Net"]].copy()
    display_df.columns = ["Month", "Credits (RM)", "Debits (RM)", "Net (RM)"]
    st.dataframe(
        display_df.style.format({"Credits (RM)": "{:,.2f}", "Debits (RM)": "{:,.2f}", "Net (RM)": "{:,.2f}"}),
        use_container_width=True, hide_index=True,
    )

    st.divider()
    st.markdown("#### Annual Expense by Category")
    all_debits = []
    for m in MONTHS:
        all_debits.extend(st.session_state.data.get(m, {}).get("debits", []))
    if all_debits:
        adf = pd.DataFrame(all_debits)
        if "Category" in adf.columns and "Amount" in adf.columns:
            adf["Amount"] = pd.to_numeric(adf["Amount"], errors="coerce").fillna(0)
            cat_sum = adf.groupby("Category")["Amount"].sum().sort_values(ascending=True).reset_index()
            cat_sum.columns = ["Category", "Total (RM)"]
            cat_sum = cat_sum[cat_sum["Total (RM)"] > 0]
            if len(cat_sum) > 0:
                st.bar_chart(cat_sum, x="Category", y="Total (RM)", color="#f59e0b", horizontal=True)
