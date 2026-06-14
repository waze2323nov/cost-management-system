import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ─── Page Config ───
st.set_page_config(layout="wide", page_title="Cost Management System 2026", page_icon="📊")

# ─── Custom CSS: Yellow header + styling ───
st.markdown("""
<style>
    /* Yellow header banner */
    .cms-header {
        background: #facc15;
        padding: 18px 28px;
        border-radius: 10px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
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
    /* Hide default Streamlit header */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    /* KPI cards */
    .kpi-card {
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid #e2e8f0;
    }
    .kpi-label {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
    }
    .kpi-sub {
        font-size: 11px;
        font-weight: 500;
        margin-top: 2px;
    }
    /* Tighten data editor */
    [data-testid="stDataEditor"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    /* Section dividers */
    .section-header {
        font-weight: 700;
        font-size: 15px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

CREDIT_CATS = [
    "Business Revenue", "Ad Revenue", "Salary / Wages", "Refund / Return",
    "Loan Repayment Received", "Rental Income", "EPF / SOCSO", "Other Income",
]

DEBIT_CATS = [
    "Rent & Utilities", "Salaries & Wages", "Advertising", "Car / Transport",
    "Insurance", "Loan / Instalment", "Family Support", "EPF / SOCSO",
    "Ad Management Fee", "Office / Supplies", "Tax & Compliance", "Other Expense",
]

STATUS_OPTIONS = ["Confirmed", "Pending", "Projected"]
DATA_FILE = "cms_data.json"

# ─── Data helpers ───
def get_june_seed():
    return {
        "credits": [
            {"Category": "Business Revenue", "Description": "BUSINESS", "Amount": 8100.0, "Date": "2026-06-19", "Status": "Pending", "Notes": ""},
            {"Category": "Other Income", "Description": "BUSINESS", "Amount": 1000.0, "Date": "2026-06-19", "Status": "Confirmed", "Notes": ""},
            {"Category": "EPF / SOCSO", "Description": "3089", "Amount": 0.0, "Date": "2026-06-10", "Status": "Confirmed", "Notes": ""},
            {"Category": "Ad Revenue", "Description": "G AD CHARGES", "Amount": 3000.0, "Date": "2026-06-10", "Status": "Confirmed", "Notes": ""},
            {"Category": "Ad Revenue", "Description": "CL AD CHARGES", "Amount": 3300.0, "Date": "2026-06-07", "Status": "Confirmed", "Notes": ""},
        ],
        "debits": [
            {"Category": "Insurance", "Description": "Great Eastern", "Amount": 250.0, "Date": "2026-06-07", "Status": "Pending", "Notes": "Pay at 7th"},
            {"Category": "Car / Transport", "Description": "Car hire purchase", "Amount": 430.0, "Date": "2026-06-07", "Status": "Pending", "Notes": "Pay at 7th"},
            {"Category": "Family Support", "Description": "Baba", "Amount": 600.0, "Date": "", "Status": "Pending", "Notes": ""},
            {"Category": "Family Support", "Description": "Erjie", "Amount": 200.0, "Date": "", "Status": "Pending", "Notes": ""},
            {"Category": "Loan / Instalment", "Description": "Shopee", "Amount": 727.61, "Date": "", "Status": "Pending", "Notes": ""},
            {"Category": "Loan / Instalment", "Description": "Maxis", "Amount": 237.20, "Date": "", "Status": "Pending", "Notes": "Before 15/6"},
            {"Category": "Family Support", "Description": "2 Jie", "Amount": 1200.0, "Date": "", "Status": "Pending", "Notes": "Return 1.0k"},
            {"Category": "Family Support", "Description": "Mum", "Amount": 2500.0, "Date": "", "Status": "Pending", "Notes": "Return 1.0k"},
            {"Category": "Family Support", "Description": "Da Jie", "Amount": 1000.0, "Date": "", "Status": "Pending", "Notes": "Cash, no return yet"},
            {"Category": "Family Support", "Description": "Baba (loan)", "Amount": 1200.0, "Date": "", "Status": "Pending", "Notes": "Return 600 next month"},
            {"Category": "Rent & Utilities", "Description": "Electric", "Amount": 0.0, "Date": "", "Status": "Pending", "Notes": "Amount TBC"},
            {"Category": "Rent & Utilities", "Description": "Water", "Amount": 0.0, "Date": "", "Status": "Pending", "Notes": "Amount TBC"},
            {"Category": "Insurance", "Description": "Insurance", "Amount": 200.0, "Date": "", "Status": "Pending", "Notes": ""},
            {"Category": "Loan / Instalment", "Description": "OCBC", "Amount": 0.0, "Date": "", "Status": "Pending", "Notes": "Amount TBC"},
            {"Category": "Advertising", "Description": "FB Ads", "Amount": 0.0, "Date": "", "Status": "Pending", "Notes": "Amount TBC"},
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


def rows_to_df(rows, kind="credit"):
    cats = CREDIT_CATS if kind == "credit" else DEBIT_CATS
    if not rows:
        return pd.DataFrame({
            "Category": pd.Categorical([], categories=cats),
            "Description": pd.Series([], dtype="str"),
            "Amount": pd.Series([], dtype="float"),
            "Date": pd.Series([], dtype="str"),
            "Status": pd.Categorical([], categories=STATUS_OPTIONS),
            "Notes": pd.Series([], dtype="str"),
        })
    df = pd.DataFrame(rows)
    for col in ["Category", "Description", "Amount", "Date", "Status", "Notes"]:
        if col not in df.columns:
            df[col] = "" if col != "Amount" else 0.0
    df["Category"] = pd.Categorical(df["Category"], categories=cats)
    df["Status"] = pd.Categorical(df["Status"], categories=STATUS_OPTIONS)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = df["Date"].fillna("").astype(str)
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    return df[["Category", "Description", "Amount", "Date", "Status", "Notes"]]


def df_to_rows(df):
    df = df.copy()
    df = df.where(df.notna(), "")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    return df.to_dict(orient="records")


# ─── Load data ───
if "data" not in st.session_state:
    st.session_state.data = load_data()

# ─── Yellow Header ───
st.markdown("""
<div class="cms-header">
    <div>
        <h1>COST MANAGEMENT SYSTEM</h1>
        <p>Fiscal Year 2026 · MYR</p>
    </div>
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
    st.download_button(
        "⬇  Export JSON Backup",
        data=dl_bytes,
        file_name="cms_backup_2026.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded = st.file_uploader("⬆  Import JSON Backup", type=["json"])
    if uploaded:
        try:
            st.session_state.data = json.load(uploaded)
            save_data(st.session_state.data)
            st.success("Imported!")
            st.rerun()
        except Exception as e:
            st.error(f"Invalid file: {e}")


# ═════════════════════════════════════
#  MONTHLY LEDGER
# ═════════════════════════════════════
if page == "Monthly Ledger":
    # Month pill bar
    cols = st.columns(12)
    for i, m in enumerate(MONTHS):
        if cols[i].button(
            m[:3],
            key=f"month_{m}",
            use_container_width=True,
            type="primary" if m == selected_month else "secondary",
        ):
            selected_month = m

    month_data = st.session_state.data.get(selected_month, {"credits": [], "debits": []})

    # ── Credits ──
    credit_df = rows_to_df(month_data.get("credits", []), "credit")
    edited_credits = st.data_editor(
        credit_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Category": st.column_config.SelectboxColumn("Category", options=CREDIT_CATS, required=True),
            "Description": st.column_config.TextColumn("Description"),
            "Amount": st.column_config.NumberColumn("Amount (RM)", min_value=0, format="%.2f"),
            "Date": st.column_config.TextColumn("Date"),
            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True),
            "Notes": st.column_config.TextColumn("Notes"),
        },
        key=f"credits_{selected_month}",
    )
    st.session_state.data[selected_month]["credits"] = df_to_rows(edited_credits)
    total_credit = edited_credits["Amount"].sum()

    st.markdown("---")

    # ── Debits ──
    debit_df = rows_to_df(month_data.get("debits", []), "debit")
    edited_debits = st.data_editor(
        debit_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Category": st.column_config.SelectboxColumn("Category", options=DEBIT_CATS, required=True),
            "Description": st.column_config.TextColumn("Description"),
            "Amount": st.column_config.NumberColumn("Amount (RM)", min_value=0, format="%.2f"),
            "Date": st.column_config.TextColumn("Date"),
            "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True),
            "Notes": st.column_config.TextColumn("Notes"),
        },
        key=f"debits_{selected_month}",
    )
    st.session_state.data[selected_month]["debits"] = df_to_rows(edited_debits)
    total_debit = edited_debits["Amount"].sum()

    # ── KPI strip ──
    st.markdown("---")
    net = total_credit - total_debit
    margin = (net / total_credit * 100) if total_credit else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Credits", f"RM {total_credit:,.2f}")
    k2.metric("Total Debits", f"RM {total_debit:,.2f}")
    k3.metric("Net P&L", f"RM {net:,.2f}", delta=f"{margin:+.1f}%")
    k4.metric("Entries", f"{len(edited_credits) + len(edited_debits)}")

    # ── Category breakdown ──
    if total_debit > 0 or total_credit > 0:
        st.markdown("---")
        st.markdown("#### Category Breakdown")
        ch1, ch2 = st.columns(2)
        with ch1:
            if total_credit > 0:
                grp = edited_credits.groupby("Category", observed=True)["Amount"].sum().reset_index()
                grp.columns = ["Category", "Amount"]
                grp = grp[grp["Amount"] > 0].sort_values("Amount", ascending=True)
                if len(grp) > 0:
                    st.markdown("**Credits**")
                    st.bar_chart(grp, x="Category", y="Amount", color="#22c55e", horizontal=True)
        with ch2:
            if total_debit > 0:
                grp = edited_debits.groupby("Category", observed=True)["Amount"].sum().reset_index()
                grp.columns = ["Category", "Amount"]
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

    # YTD KPIs
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

    # Monthly trend chart
    st.markdown("#### Monthly Trend")
    trend = sdf[["Month", "Credits", "Debits"]].set_index("Month")
    st.bar_chart(trend, color=["#22c55e", "#ef4444"])

    # Net P&L line chart
    st.markdown("#### Net Profit / Loss")
    net_line = sdf[["Month", "Net"]].set_index("Month")
    st.line_chart(net_line, color="#3b82f6")

    st.divider()

    # Summary table
    st.markdown("#### Monthly Summary Table")
    display_df = sdf[["Full", "Credits", "Debits", "Net"]].copy()
    display_df.columns = ["Month", "Credits (RM)", "Debits (RM)", "Net (RM)"]
    st.dataframe(
        display_df.style.format({
            "Credits (RM)": "{:,.2f}",
            "Debits (RM)": "{:,.2f}",
            "Net (RM)": "{:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # Annual expense by category
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
