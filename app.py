import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    layout="wide",
    page_title="Cost Management System",
    page_icon="📊",
)

# ─── Constants ───
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

CREDIT_CATEGORIES = [
    "Sales Revenue", "Service Income", "Investment Returns",
    "Rental Income", "Grants & Subsidies", "Other Income",
]

DEBIT_CATEGORIES = [
    "Rent & Utilities", "Salaries & Wages", "Raw Materials",
    "Marketing & Ads", "Transport & Logistics", "Equipment & Maintenance",
    "Insurance", "Professional Fees", "Office Supplies",
    "Tax & Compliance", "Loan Repayment", "Other Expense",
]

STATUS_OPTIONS = ["Confirmed", "Pending", "Projected"]

DATA_FILE = "cms_data.json"

# ─── Persistence helpers ───
def empty_month():
    return {
        "credits": [],
        "debits": [],
    }

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {m: empty_month() for m in MONTHS}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def rows_to_df(rows, kind="credit"):
    if not rows:
        cats = CREDIT_CATEGORIES if kind == "credit" else DEBIT_CATEGORIES
        return pd.DataFrame({
            "Category": pd.Categorical([], categories=cats),
            "Description": pd.Series([], dtype="str"),
            "Amount (RM)": pd.Series([], dtype="float"),
            "Date": pd.Series([], dtype="str"),
            "Status": pd.Categorical([], categories=STATUS_OPTIONS),
        })
    df = pd.DataFrame(rows)
    cats = CREDIT_CATEGORIES if kind == "credit" else DEBIT_CATEGORIES
    df["Category"] = pd.Categorical(df["Category"], categories=cats)
    df["Status"] = pd.Categorical(df["Status"], categories=STATUS_OPTIONS)
    return df

def df_to_rows(df):
    return df.where(df.notna(), "").to_dict(orient="records")

# ─── Load data into session state ───
if "data" not in st.session_state:
    st.session_state.data = load_data()

# ─── Sidebar ───
with st.sidebar:
    st.markdown("## 📊 Cost Management System")
    st.caption("Fiscal Year 2026 · MYR")
    st.divider()

    page = st.radio("Navigate", ["Monthly Ledger", "Annual Dashboard"], label_visibility="collapsed")

    st.divider()
    selected_month = st.selectbox("Active Month", MONTHS, index=datetime.now().month - 1)

    st.divider()
    if st.button("💾  Save All Data", use_container_width=True):
        save_data(st.session_state.data)
        st.success("Data saved to disk.")

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
            st.success("Data imported successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"Invalid file: {e}")

# ═══════════════════════════════════════════
#  MONTHLY LEDGER
# ═══════════════════════════════════════════
if page == "Monthly Ledger":
    st.markdown(f"## {selected_month} 2026")

    month_data = st.session_state.data[selected_month]

    col_c, col_d = st.columns(2, gap="large")

    # ── Credits ──
    with col_c:
        st.markdown("#### ✅ Credits (Inflows)")
        credit_df = rows_to_df(month_data["credits"], "credit")
        edited_credits = st.data_editor(
            credit_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Category": st.column_config.SelectboxColumn(options=CREDIT_CATEGORIES, required=True),
                "Amount (RM)": st.column_config.NumberColumn(min_value=0, format="%.2f"),
                "Date": st.column_config.TextColumn(),
                "Status": st.column_config.SelectboxColumn(options=STATUS_OPTIONS, required=True),
            },
            key=f"cred_{selected_month}",
        )
        st.session_state.data[selected_month]["credits"] = df_to_rows(edited_credits)
        total_credit = edited_credits["Amount (RM)"].sum()

    # ── Debits ──
    with col_d:
        st.markdown("#### 🔻 Debits (Outflows)")
        debit_df = rows_to_df(month_data["debits"], "debit")
        edited_debits = st.data_editor(
            debit_df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Category": st.column_config.SelectboxColumn(options=DEBIT_CATEGORIES, required=True),
                "Amount (RM)": st.column_config.NumberColumn(min_value=0, format="%.2f"),
                "Date": st.column_config.TextColumn(),
                "Status": st.column_config.SelectboxColumn(options=STATUS_OPTIONS, required=True),
            },
            key=f"deb_{selected_month}",
        )
        st.session_state.data[selected_month]["debits"] = df_to_rows(edited_debits)
        total_debit = edited_debits["Amount (RM)"].sum()

    # ── Monthly summary strip ──
    st.divider()
    s1, s2, s3, s4 = st.columns(4)
    net = total_credit - total_debit
    margin = (net / total_credit * 100) if total_credit else 0

    s1.metric("Total Credits", f"RM {total_credit:,.2f}")
    s2.metric("Total Debits", f"RM {total_debit:,.2f}")
    s3.metric("Net Profit / Loss", f"RM {net:,.2f}", delta=f"{margin:+.1f}%")
    s4.metric("Entries", f"{len(edited_credits) + len(edited_debits)}")

    # ── Category breakdown charts ──
    if total_debit > 0 or total_credit > 0:
        st.divider()
        st.markdown("#### Category Breakdown")
        ch1, ch2 = st.columns(2)
        with ch1:
            if total_credit > 0:
                credit_grp = edited_credits.groupby("Category", observed=True)["Amount (RM)"].sum().reset_index()
                credit_grp.columns = ["Category", "Amount"]
                st.bar_chart(credit_grp, x="Category", y="Amount", color="#22c55e", horizontal=True)
        with ch2:
            if total_debit > 0:
                debit_grp = edited_debits.groupby("Category", observed=True)["Amount (RM)"].sum().reset_index()
                debit_grp.columns = ["Category", "Amount"]
                st.bar_chart(debit_grp, x="Category", y="Amount", color="#ef4444", horizontal=True)

# ═══════════════════════════════════════════
#  ANNUAL DASHBOARD
# ═══════════════════════════════════════════
elif page == "Annual Dashboard":
    st.markdown("## Annual Dashboard · 2026")

    summary_rows = []
    for m in MONTHS:
        md = st.session_state.data[m]
        c = sum(r.get("Amount (RM)", 0) for r in md["credits"] if r.get("Amount (RM)"))
        d = sum(r.get("Amount (RM)", 0) for r in md["debits"] if r.get("Amount (RM)"))
        summary_rows.append({"Month": m[:3], "Credits": c, "Debits": d, "Net": c - d})

    summary_df = pd.DataFrame(summary_rows)

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    ytd_c = summary_df["Credits"].sum()
    ytd_d = summary_df["Debits"].sum()
    ytd_n = ytd_c - ytd_d
    ytd_margin = (ytd_n / ytd_c * 100) if ytd_c else 0

    k1.metric("YTD Revenue", f"RM {ytd_c:,.2f}")
    k2.metric("YTD Expenses", f"RM {ytd_d:,.2f}")
    k3.metric("YTD Net", f"RM {ytd_n:,.2f}", delta=f"{ytd_margin:+.1f}%")
    best = summary_df.loc[summary_df["Net"].idxmax(), "Month"] if ytd_c else "—"
    k4.metric("Best Month", best)

    st.divider()

    # Trend chart
    st.markdown("#### Monthly Trend")
    trend = summary_df[["Month", "Credits", "Debits"]].set_index("Month")
    st.bar_chart(trend, color=["#22c55e", "#ef4444"])

    # Net profit line
    st.markdown("#### Net Profit / Loss Trend")
    net_line = summary_df[["Month", "Net"]].set_index("Month")
    st.line_chart(net_line, color="#3b82f6")

    # Monthly table
    st.divider()
    st.markdown("#### Monthly Summary Table")
    display_df = summary_df.copy()
    display_df.columns = ["Month", "Credits (RM)", "Debits (RM)", "Net (RM)"]
    st.dataframe(
        display_df.style.format({"Credits (RM)": "{:,.2f}", "Debits (RM)": "{:,.2f}", "Net (RM)": "{:,.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

    # Annual category aggregation
    st.divider()
    st.markdown("#### Annual Expense by Category")
    all_debits = []
    for m in MONTHS:
        all_debits.extend(st.session_state.data[m]["debits"])
    if all_debits:
        adf = pd.DataFrame(all_debits)
        if "Category" in adf.columns and "Amount (RM)" in adf.columns:
            cat_sum = adf.groupby("Category")["Amount (RM)"].sum().sort_values(ascending=False).reset_index()
            cat_sum.columns = ["Category", "Total (RM)"]
            st.bar_chart(cat_sum, x="Category", y="Total (RM)", color="#f59e0b", horizontal=True)
