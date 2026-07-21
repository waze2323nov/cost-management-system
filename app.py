import streamlit as st
import pandas as pd
import json
import os
from datetime import date

st.set_page_config(layout="wide", page_title="Cost Management System 2026", page_icon="CMS")

st.markdown("""
<style>
    .cms-header { background:#facc15; padding:clamp(12px,2vw,18px) clamp(14px,2.5vw,28px);
                  border-radius:10px; margin-bottom:20px; }
    .cms-header h1 { color:#1e293b !important; font-size:clamp(15px,3vw,22px) !important;
                     font-weight:700 !important; letter-spacing:-0.03em; margin:0 !important;
                     padding:0 !important; line-height:1.25 !important; white-space:nowrap;
                     overflow:hidden; text-overflow:ellipsis; }
    .cms-header p { color:#713f12; font-size:clamp(10px,1.5vw,13px); margin:2px 0 0 0; }
    header[data-testid="stHeader"] { background: transparent; }

    .section-credit { color:#16a34a; font-weight:700; font-size:clamp(13px,1.9vw,16px); }
    .section-debit  { color:#dc2626; font-weight:700; font-size:clamp(13px,1.9vw,16px); }

    /* Month pills: never wrap "Jan" into "Ja / n" */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        white-space: nowrap; min-width: 0; padding: 0.35rem 0.2rem;
        font-size: clamp(10px, 1.35vw, 14px); overflow: hidden;
    }
    /* Sidebar buttons keep normal wrapping and padding */
    section[data-testid="stSidebar"] .stButton > button {
        white-space: normal; padding: 0.4rem 0.75rem; font-size: 14px;
    }

    [data-testid="stMetricValue"] { font-size: clamp(17px, 2.5vw, 30px) !important; }
    [data-testid="stMetricLabel"] { font-size: clamp(10px, 1.4vw, 14px) !important; }
    [data-testid="stMetricLabel"] p { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    [data-testid="stDataEditor"] div[role="gridcell"] { font-size: clamp(12px,1.4vw,15px) !important; }

    .sum-box { background:#1e293b; color:#fff; padding:clamp(10px,1.5vw,14px) clamp(12px,2vw,20px);
               border-radius:10px; border:2px solid #a855f7; text-align:center; margin:10px 0; }
    .sum-box .label { font-size:clamp(10px,1.3vw,12px); color:#94a3b8;
                      text-transform:uppercase; letter-spacing:0.05em; }
    .sum-box .value { font-size:clamp(15px,2.4vw,22px); font-weight:700; color:#facc15;
                      margin-top:4px; white-space:nowrap; }
    .sum-box .detail { font-size:clamp(10px,1.3vw,12px); color:#94a3b8; margin-top:4px; }
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
            {"Category":"Business Revenue","Description":"BUSINESS","Amount":8100.0,"Date":"2026-06-19","Status":"Pending","Notes":""},
            {"Category":"Other Income","Description":"BUSINESS","Amount":1000.0,"Date":"2026-06-19","Status":"Confirmed","Notes":""},
            {"Category":"EPF / SOCSO","Description":"TOTAL EPFSOCSO","Amount":3089.0,"Date":"2026-06-10","Status":"Confirmed","Notes":""},
            {"Category":"Ad Revenue","Description":"G AD CHARGES","Amount":3000.0,"Date":"2026-06-10","Status":"Confirmed","Notes":""},
            {"Category":"Ad Revenue","Description":"CL AD CHARGES","Amount":3300.0,"Date":"2026-06-07","Status":"Confirmed","Notes":""},
        ],
        "debits": [
            {"Category":"Insurance","Description":"Great Eastern","Amount":-250.0,"Date":"2026-06-07","Status":"Confirmed","Notes":"Pay at 7th"},
            {"Category":"Car / Transport","Description":"Car hire purchase","Amount":-430.0,"Date":"2026-06-07","Status":"Confirmed","Notes":"Pay at 7th"},
            {"Category":"Family Support","Description":"Baba","Amount":-300.0,"Date":"2026-06-07","Status":"Confirmed","Notes":"Pay at 7th"},
            {"Category":"Family Support","Description":"Erjie","Amount":-450.0,"Date":"2026-06-07","Status":"Confirmed","Notes":"Pay at 7th"},
            {"Category":"Loan / Instalment","Description":"Shopee","Amount":-744.03,"Date":"2026-06-07","Status":"Confirmed","Notes":"Pay at 7th"},
            {"Category":"Rent & Utilities","Description":"Maxis","Amount":-237.20,"Date":"2026-06-19","Status":"Confirmed","Notes":"Before 15/6"},
            {"Category":"Family Support","Description":"Mum","Amount":-1000.0,"Date":"2026-06-19","Status":"Confirmed","Notes":"Return 1.0k"},
            {"Category":"Family Support","Description":"2 Jie","Amount":-1000.0,"Date":"","Status":"Pending","Notes":"Return 1.0k"},
            {"Category":"Family Support","Description":"Da Jie","Amount":0.0,"Date":"","Status":"Pending","Notes":"Cash, no return yet"},
            {"Category":"Family Support","Description":"Baba","Amount":0.0,"Date":"","Status":"Pending","Notes":"Return 600 next month"},
            {"Category":"Rent & Utilities","Description":"Electric","Amount":0.0,"Date":"","Status":"Pending","Notes":"Amount TBC"},
            {"Category":"Rent & Utilities","Description":"Water","Amount":0.0,"Date":"","Status":"Pending","Notes":"Amount TBC"},
            {"Category":"Insurance","Description":"Insurance BABA","Amount":-200.0,"Date":"2026-06-26","Status":"Pending","Notes":""},
            {"Category":"Loan / Instalment","Description":"OCBC","Amount":-266.66,"Date":"2026-06-07","Status":"Confirmed","Notes":""},
            {"Category":"Advertising","Description":"FB Ads","Amount":-31.6,"Date":"2026-06-08","Status":"Confirmed","Notes":""},
            {"Category":"Advertising","Description":"FB Ads","Amount":-3000.0,"Date":"2026-06-19","Status":"Pending","Notes":""},
            {"Category":"Advertising","Description":"FB Ads","Amount":-1488.55,"Date":"2026-06-07","Status":"Confirmed","Notes":""},
            {"Category":"Family Support","Description":"Baba","Amount":-200.0,"Date":"2026-06-19","Status":"Pending","Notes":""},
            {"Category":"Salaries & Wages","Description":"Salary","Amount":-3300.0,"Date":"","Status":"Pending","Notes":""},
        ],
    }


def init_data():
    return {m: (get_june_seed() if m == "June" else {"credits": [], "debits": []}) for m in MONTHS}


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
    if not s or s in ("None", "NaT", ""):
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def rows_to_df(rows, kind="credit"):
    cats = CREDIT_CATS if kind == "credit" else DEBIT_CATS
    if not rows:
        return pd.DataFrame({
            "Sel": pd.Series([], dtype="bool"),
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
            df[col] = 0.0 if col == "Amount" else ""
    df["Sel"] = False
    df["Category"] = pd.Categorical(df["Category"], categories=cats)
    df["Status"] = pd.Categorical(df["Status"], categories=STATUS_OPTIONS)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = df["Date"].apply(parse_date)
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    return df[["Sel","Category","Description","Amount","Date","Status","Notes"]]


def df_to_rows(df, kind="credit"):
    df = df.copy()
    if "Sel" in df.columns:
        df = df.drop(columns=["Sel"])
    amt = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Amount"] = amt.abs() if kind == "credit" else -amt.abs()
    df["Date"] = df["Date"].apply(lambda x: x.isoformat() if (x is not None and pd.notna(x)) else "")
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    df["Category"] = df["Category"].astype(str)
    df["Status"] = df["Status"].astype(str)
    return df.to_dict(orient="records")


def signed(rows, kind):
    total = 0.0
    for r in rows:
        v = r.get("Amount", 0) or 0
        try:
            v = float(v)
        except Exception:
            v = 0.0
        total += abs(v) if kind == "credit" else -abs(v)
    return total


if "data" not in st.session_state:
    st.session_state.data = load_data()
if "active_month" not in st.session_state:
    st.session_state.active_month = "June"

st.markdown("""
<div class="cms-header">
    <h1>COST MANAGEMENT SYSTEM</h1>
    <p>Fiscal Year 2026 - MYR</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("nav", ["Monthly Ledger", "Annual Dashboard"], label_visibility="collapsed")
    st.divider()
    picked = st.selectbox("Active Month", MONTHS,
                          index=MONTHS.index(st.session_state.active_month),
                          key="msel_" + st.session_state.active_month)
    if picked != st.session_state.active_month:
        st.session_state.active_month = picked
        st.rerun()

    st.divider()
    with st.expander("Copy Template to Months", expanded=False):
        st.caption("Copy item names from a source month into other months, with all amounts set to 0.")
        src_month = st.selectbox("Copy items from", MONTHS, index=MONTHS.index("June"), key="tpl_src")
        tgt_months = st.multiselect("Paste into these months",
                                    [m for m in MONTHS if m != src_month], key="tpl_tgt")
        tpl_mode = st.radio("If target month already has rows",
                            ["Append (keep existing)", "Replace (clear first)"], key="tpl_mode")
        if st.button("Copy Template", use_container_width=True, key="tpl_go"):
            if not tgt_months:
                st.warning("Pick at least one target month.")
            else:
                src = st.session_state.data.get(src_month, {"credits": [], "debits": []})
                for tm in tgt_months:
                    st.session_state.data.setdefault(tm, {"credits": [], "debits": []})
                    for kind in ("credits", "debits"):
                        blanks = [{
                            "Category": r.get("Category",""),
                            "Description": r.get("Description",""),
                            "Amount": 0.0, "Date": "", "Status": "Pending",
                            "Notes": r.get("Notes",""),
                        } for r in src.get(kind, []) if str(r.get("Description","")).strip()]
                        if tpl_mode.startswith("Replace"):
                            st.session_state.data[tm][kind] = blanks
                        else:
                            st.session_state.data[tm][kind] = st.session_state.data[tm].get(kind, []) + blanks
                        st.session_state.pop("credits_" + tm, None)
                        st.session_state.pop("debits_" + tm, None)
                save_data(st.session_state.data)
                st.success("Copied " + src_month + " template into " + str(len(tgt_months)) + " month(s).")
                st.rerun()

    st.divider()
    if st.button("Save Data", use_container_width=True):
        save_data(st.session_state.data)
        st.success("Saved!")
    st.download_button("Export JSON Backup",
                       data=json.dumps(st.session_state.data, indent=2).encode(),
                       file_name="cms_backup_2026.json", mime="application/json",
                       use_container_width=True)
    uploaded = st.file_uploader("Import JSON Backup", type=["json"])
    if uploaded:
        try:
            st.session_state.data = json.load(uploaded)
            save_data(st.session_state.data)
            for m in MONTHS:
                st.session_state.pop("credits_" + m, None)
                st.session_state.pop("debits_" + m, None)
            st.success("Imported!")
            st.rerun()
        except Exception as e:
            st.error("Invalid file: " + str(e))


def col_config(cats, label):
    return {
        "Sel": st.column_config.CheckboxColumn("Sel", help="Select for sum / copy", width="small", default=False),
        "Category": st.column_config.SelectboxColumn("Category", options=cats, required=True, width="medium"),
        "Description": st.column_config.TextColumn("Description", width="medium"),
        "Amount": st.column_config.NumberColumn(label, format="%.2f", width="medium", step=0.01),
        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", width="small"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS, required=True, width="small"),
        "Notes": st.column_config.TextColumn("Notes", width="medium"),
    }

ORDER = ["Sel","Category","Description","Amount","Date","Status","Notes"]

if page == "Monthly Ledger":
    active = st.session_state.active_month
    cols = st.columns(12)
    for i, m in enumerate(MONTHS):
        if cols[i].button(m[:3], key="mbtn_" + m, use_container_width=True,
                          type="primary" if m == active else "secondary"):
            st.session_state.active_month = m
            st.rerun()

    month_data = st.session_state.data.setdefault(active, {"credits": [], "debits": []})
    credit_rows = month_data.get("credits", [])
    debit_rows = month_data.get("debits", [])

    kpi_slot = st.container()

    prev_credit, prev_debit = {}, {}
    for m in MONTHS:
        md = st.session_state.data.get(m, {})
        for r in md.get("credits", []):
            dsc = str(r.get("Description","")).strip()
            if dsc:
                prev_credit.setdefault(dsc, r.get("Category",""))
        for r in md.get("debits", []):
            dsc = str(r.get("Description","")).strip()
            if dsc:
                prev_debit.setdefault(dsc, r.get("Category",""))

    with st.expander("Previous Items Reference  -  {} credits, {} debits".format(len(prev_credit), len(prev_debit))):
        st.caption("Items you have used before across all months. Free text is still allowed in the tables.")
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("**Credits**")
            if prev_credit:
                st.dataframe(pd.DataFrame([{"Description":k,"Category":v} for k,v in sorted(prev_credit.items())]),
                             use_container_width=True, hide_index=True,
                             height=min(320, 38 + len(prev_credit) * 35))
            else:
                st.caption("None yet.")
        with pc2:
            st.markdown("**Debits**")
            if prev_debit:
                st.dataframe(pd.DataFrame([{"Description":k,"Category":v} for k,v in sorted(prev_debit.items())]),
                             use_container_width=True, hide_index=True,
                             height=min(320, 38 + len(prev_debit) * 35))
            else:
                st.caption("None yet.")

    st.markdown("---")

    st.markdown('<p class="section-credit">Credits (Inflows) - Positive (+)</p>', unsafe_allow_html=True)
    st.caption("Tick Sel to include in Selection Sum or to copy.")
    credit_df = rows_to_df(credit_rows, "credit")
    edited_credits = st.data_editor(
        credit_df, num_rows="dynamic", use_container_width=True,
        height=max(35 + (len(credit_df) + 2) * 35 + 3, 120),
        column_config=col_config(CREDIT_CATS, "RM (+)"),
        column_order=ORDER, key="credits_" + active)
    st.session_state.data[active]["credits"] = df_to_rows(edited_credits, "credit")

    st.markdown("---")

    st.markdown('<p class="section-debit">Debits (Outflows) - Negative (-)</p>', unsafe_allow_html=True)
    st.caption("Type any number. It is counted as NEGATIVE in every total, and shows with a minus sign next time the page loads.")
    debit_df = rows_to_df(debit_rows, "debit")
    edited_debits = st.data_editor(
        debit_df, num_rows="dynamic", use_container_width=True,
        height=max(35 + (len(debit_df) + 2) * 35 + 3, 120),
        column_config=col_config(DEBIT_CATS, "RM (-)"),
        column_order=ORDER, key="debits_" + active)
    st.session_state.data[active]["debits"] = df_to_rows(edited_debits, "debit")

    ec = edited_credits
    ed = edited_debits

    total_credit = float(ec["Amount"].abs().sum()) if len(ec) else 0.0
    debit_mag = float(ed["Amount"].abs().sum()) if len(ed) else 0.0
    total_debit = -debit_mag if debit_mag else 0.0
    net = total_credit + total_debit
    margin = (net / total_credit * 100) if total_credit else 0.0

    with kpi_slot:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Credits", "RM {:,.2f}".format(total_credit))
        k2.metric("Total Debits", "RM {:,.2f}".format(total_debit))
        k3.metric("Net P&L", "RM {:,.2f}".format(net), delta="{:+.1f}%".format(margin))
        k4.metric("Entries", str(len(ec) + len(ed)))

    sel_c = float(ec.loc[ec["Sel"] == True, "Amount"].abs().sum()) if len(ec) else 0.0
    sel_d_mag = float(ed.loc[ed["Sel"] == True, "Amount"].abs().sum()) if len(ed) else 0.0
    sel_d = -sel_d_mag if sel_d_mag else 0.0
    sel_cc = int(ec["Sel"].sum()) if len(ec) else 0
    sel_dc = int(ed["Sel"].sum()) if len(ed) else 0
    sel_net = sel_c + sel_d
    sel_count = sel_cc + sel_dc

    st.markdown("---")
    st.markdown("#### Selection Sum")
    if sel_count == 0:
        st.caption("Tick Sel on any row above to start summing - works across both tables.")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown('<div class="sum-box"><div class="label">Selected Credits (+)</div>'
                    '<div class="value" style="color:#4ade80">+ RM {:,.2f}</div>'
                    '<div class="detail">{} item(s)</div></div>'.format(sel_c, sel_cc), unsafe_allow_html=True)
    with s2:
        st.markdown('<div class="sum-box"><div class="label">Selected Debits (-)</div>'
                    '<div class="value" style="color:#f87171">RM {:,.2f}</div>'
                    '<div class="detail">{} item(s)</div></div>'.format(sel_d, sel_dc), unsafe_allow_html=True)
    with s3:
        col = "#4ade80" if sel_net >= 0 else "#f87171"
        sign = "+" if sel_net >= 0 else ""
        st.markdown('<div class="sum-box"><div class="label">Net Total (Credits + Debits)</div>'
                    '<div class="value" style="color:{}">{} RM {:,.2f}</div>'
                    '<div class="detail">{} item(s) selected</div></div>'.format(
                        col, sign, sel_net, sel_count), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Copy Selected Items To...")
    if sel_count == 0:
        st.caption("Tick Sel on the rows you want to copy, then choose the target months below.")
    cp1, cp2, cp3 = st.columns([2, 1.4, 1])
    with cp1:
        copy_targets = st.multiselect("Target months", [m for m in MONTHS if m != active],
                                      key="copy_tgt_" + active, label_visibility="collapsed",
                                      placeholder="Choose target months...")
    with cp2:
        copy_mode = st.selectbox("Mode", ["Copy with amounts", "Copy without amounts"],
                                 key="copy_mode_" + active, label_visibility="collapsed")
    with cp3:
        do_copy = st.button("Copy", use_container_width=True, key="copy_go_" + active,
                            disabled=(sel_count == 0))

    if do_copy:
        if not copy_targets:
            st.warning("Pick at least one target month.")
        else:
            keep = copy_mode.startswith("Copy with")

            def payload(df, kind):
                out = []
                for _, r in df.iterrows():
                    a = abs(float(r["Amount"] or 0)) if keep else 0.0
                    if kind == "debits":
                        a = -a
                    dv = r["Date"]
                    out.append({
                        "Category": str(r["Category"]),
                        "Description": str(r["Description"] or ""),
                        "Amount": a,
                        "Date": dv.isoformat() if (dv is not None and pd.notna(dv)) else "",
                        "Status": str(r["Status"]),
                        "Notes": str(r["Notes"] or ""),
                    })
                return out

            pc = payload(ec[ec["Sel"] == True], "credits")
            pdd = payload(ed[ed["Sel"] == True], "debits")
            for tm in copy_targets:
                st.session_state.data.setdefault(tm, {"credits": [], "debits": []})
                st.session_state.data[tm]["credits"] = st.session_state.data[tm].get("credits", []) + pc
                st.session_state.data[tm]["debits"] = st.session_state.data[tm].get("debits", []) + pdd
                st.session_state.pop("credits_" + tm, None)
                st.session_state.pop("debits_" + tm, None)
            save_data(st.session_state.data)
            st.success("Copied {} item(s) into {} month(s): {}".format(
                sel_count, len(copy_targets), ", ".join(copy_targets)))

    cred_tot = ec["Amount"].abs().sum() if len(ec) else 0
    deb_tot = ed["Amount"].abs().sum() if len(ed) else 0
    if cred_tot > 0 or deb_tot > 0:
        st.markdown("---")
        st.markdown("#### Category Breakdown")
        ch1, ch2 = st.columns(2)
        with ch1:
            if cred_tot > 0:
                g = ec.copy()
                g["Amount"] = g["Amount"].abs()
                g = g.groupby("Category", observed=True)["Amount"].sum().reset_index()
                g = g[g["Amount"] > 0].sort_values("Amount")
                if len(g):
                    st.markdown("**Credits**")
                    st.bar_chart(g, x="Category", y="Amount", color="#22c55e", horizontal=True)
        with ch2:
            if deb_tot > 0:
                g = ed.copy()
                g["Amount"] = g["Amount"].abs()
                g = g.groupby("Category", observed=True)["Amount"].sum().reset_index()
                g = g[g["Amount"] > 0].sort_values("Amount")
                if len(g):
                    st.markdown("**Debits**")
                    st.bar_chart(g, x="Category", y="Amount", color="#ef4444", horizontal=True)

elif page == "Annual Dashboard":
    st.markdown("## Annual Dashboard - 2026")
    rows = []
    for m in MONTHS:
        md = st.session_state.data.get(m, {"credits": [], "debits": []})
        c = signed(md.get("credits", []), "credit")
        d = abs(signed(md.get("debits", []), "debit"))
        rows.append({"Month": m[:3], "Full": m, "Credits": c, "Debits": d, "Net": c - d})
    sdf = pd.DataFrame(rows)
    ytd_c, ytd_d = sdf["Credits"].sum(), sdf["Debits"].sum()
    ytd_n = ytd_c - ytd_d
    ytd_m = (ytd_n / ytd_c * 100) if ytd_c else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("YTD Revenue", "RM {:,.2f}".format(ytd_c))
    k2.metric("YTD Expenses", "RM -{:,.2f}".format(ytd_d))
    k3.metric("YTD Net", "RM {:,.2f}".format(ytd_n), delta="{:+.1f}%".format(ytd_m))
    k4.metric("Best Month", sdf.loc[sdf["Net"].idxmax(), "Month"] if ytd_c > 0 else "-")

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
        all_d.extend(st.session_state.data.get(m, {}).get("debits", []))
    if all_d:
        adf = pd.DataFrame(all_d)
        if "Category" in adf.columns and "Amount" in adf.columns:
            adf["Amount"] = pd.to_numeric(adf["Amount"], errors="coerce").fillna(0).abs()
            cs = adf.groupby("Category")["Amount"].sum().sort_values().reset_index()
            cs.columns = ["Category","Total (RM)"]
            cs = cs[cs["Total (RM)"] > 0]
            if len(cs):
                st.bar_chart(cs, x="Category", y="Total (RM)", color="#f59e0b", horizontal=True)
