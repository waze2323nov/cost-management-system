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

    /* (A) Month-at-a-glance strip */
    .glance { background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #facc15;
              border-radius:8px; padding:10px clamp(10px,1.6vw,16px); margin:4px 0 14px 0;
              font-size:clamp(11px,1.45vw,14px); color:#334155;
              display:flex; flex-wrap:wrap; align-items:center; gap:4px 10px; }
    .glance b { color:#0f172a; }
    .g-sep { color:#cbd5e1; }

    /* Command box */
    .cmd-label { font-weight:700; font-size:clamp(12px,1.7vw,15px); color:#0f172a;
                 margin:2px 0 2px 0; }
    .preview-head { font-weight:700; font-size:clamp(12px,1.6vw,14px); color:#92400e;
                    background:#fffbeb; border:1px solid #fde68a; border-radius:6px;
                    padding:6px 10px; margin:8px 0 6px 0; }

    /* Totals bar pinned under each table */
    .totalbar { display:flex; justify-content:space-between; align-items:center;
                background:#f1f5f9; border:1px solid #cbd5e1; border-top:none;
                border-radius:0 0 8px 8px; padding:7px clamp(8px,1.4vw,14px);
                margin:-6px 0 10px 0; }
    .totalbar .t-lab { font-size:clamp(10px,1.3vw,12px); font-weight:700;
                       color:#64748b; letter-spacing:.04em; }
    .totalbar .t-val { font-size:clamp(13px,1.9vw,17px); font-weight:800;
                       font-variant-numeric:tabular-nums; }

    /* Monthly reminder boxes */
    .alertbox { border-radius:8px; padding:10px 14px; margin:4px 0 10px 0;
                font-size:clamp(11px,1.45vw,14px); }
    .alertbox .a-title { font-weight:800; margin-bottom:4px; letter-spacing:.01em; }
    .alertbox ul { margin:0; padding-left:18px; }
    .alertbox li { margin:2px 0; }
    .alertbox .a-sub { color:#64748b; font-size:.88em; }
    .alert-miss { background:#fef2f2; border:1px solid #fecaca; border-left:4px solid #dc2626;
                  color:#7f1d1d; }
    .alert-miss .a-title { color:#dc2626; }
    .alert-tbc { background:#fffbeb; border:1px solid #fde68a; border-left:4px solid #f59e0b;
                 color:#78350f; }
    .alert-tbc .a-title { color:#b45309; }

    /* Side-by-side: stack on narrow screens, debits first */
    @media (max-width: 820px) {
        div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
        }
        .glance { flex-direction: column; align-items: flex-start; }
        .g-sep { display: none; }
    }
</style>
""", unsafe_allow_html=True)

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]
CREDIT_CATS = ["Business Revenue","Ad Revenue","Salary / Wages","Refund / Return",
               "Loan Repayment Received","Rental Income","EPF / SOCSO","Other Income"]
DEBIT_CATS = ["Rent & Utilities","Salaries & Wages","Advertising","Car / Transport",
              "Insurance","Loan / Instalment","Family Support","EPF / SOCSO",
              "Ad Management Fee","Office / Supplies","Tax & Compliance","Other Expense"]
STATUS_OPTIONS = ["Confirmed","Pending","Projected","TBC"]
YEAR = 2026
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
            {"Category":"Family Support","Description":"Mum","Amount":-1000.0,"Date":"2026-06-19","Status":"Confirmed","Notes":"Return 1.0k","Lent":True},
            {"Category":"Family Support","Description":"2 Jie","Amount":-1000.0,"Date":"","Status":"Pending","Notes":"Return 1.0k","Lent":True},
            {"Category":"Family Support","Description":"Da Jie","Amount":0.0,"Date":"","Status":"TBC","Notes":"Cash, no return yet","Lent":True},
            {"Category":"Family Support","Description":"Baba","Amount":0.0,"Date":"","Status":"TBC","Notes":"Return 600 next month","Lent":True},
            {"Category":"Rent & Utilities","Description":"Electric","Amount":0.0,"Date":"","Status":"TBC","Notes":"Amount TBC"},
            {"Category":"Rent & Utilities","Description":"Water","Amount":0.0,"Date":"","Status":"TBC","Notes":"Amount TBC"},
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


# ══════════════════════════════════════════════════════════
#  STORAGE LAYER — Google Sheets (persistent) with local fallback
# ══════════════════════════════════════════════════════════
COLUMNS = ["Year", "Month", "Type", "Category", "Description",
           "Amount", "Date", "Status", "Notes", "Lent"]


@st.cache_resource(show_spinner=False)
def get_worksheet():
    """Connect to Google Sheets. Returns (worksheet, error_message)."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        return None, "gspread not installed. Add gspread and google-auth to requirements.txt."

    if "gcp_service_account" not in st.secrets:
        return None, "No credentials found. Add [gcp_service_account] to Streamlit secrets."

    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets",
                  "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=scopes)
        client = gspread.authorize(creds)

        sheet_name = st.secrets.get("sheet_name", "CMS_Data_2026")
        try:
            sh = client.open(sheet_name)
        except Exception:
            sh = client.create(sheet_name)

        try:
            ws = sh.worksheet("ledger")
        except Exception:
            ws = sh.add_worksheet(title="ledger", rows=2000, cols=len(COLUMNS))
            ws.append_row(COLUMNS)

        if not ws.get_all_values():
            ws.append_row(COLUMNS)

        return ws, None
    except Exception as e:
        return None, "Google Sheets connection failed: " + str(e)


def sheet_rows_to_data(records):
    """Flat sheet rows -> nested {month: {credits: [], debits: []}} structure."""
    data = {m: {"credits": [], "debits": []} for m in MONTHS}
    for r in records:
        month = str(r.get("Month", "")).strip()
        if month not in data:
            continue
        # Rows written before the Year column existed belong to YEAR.
        yr_raw = str(r.get("Year", "") or "").strip()
        if yr_raw:
            try:
                if int(float(yr_raw)) != YEAR:
                    continue
            except (TypeError, ValueError):
                pass
        kind = "credits" if str(r.get("Type", "")).strip().lower() == "credit" else "debits"
        try:
            amt = float(r.get("Amount", 0) or 0)
        except (TypeError, ValueError):
            amt = 0.0
        amt = abs(amt) if kind == "credits" else -abs(amt)
        if amt == 0:
            amt = 0.0
        lent_raw = str(r.get("Lent", "") or "").strip().lower()
        data[month][kind].append({
            "Category": str(r.get("Category", "") or ""),
            "Description": str(r.get("Description", "") or ""),
            "Amount": amt,
            "Date": str(r.get("Date", "") or ""),
            "Status": str(r.get("Status", "") or "Pending"),
            "Notes": str(r.get("Notes", "") or ""),
            "Lent": lent_raw in ("true", "yes", "1", "y"),
        })
    return data


def data_to_sheet_rows(data):
    """Nested structure -> flat rows ready for the sheet."""
    rows = []
    for m in MONTHS:
        md = data.get(m, {})
        for kind, label in (("credits", "Credit"), ("debits", "Debit")):
            for r in md.get(kind, []):
                desc = str(r.get("Description", "") or "").strip()
                cat = str(r.get("Category", "") or "").strip()
                try:
                    amt = float(r.get("Amount", 0) or 0)
                except (TypeError, ValueError):
                    amt = 0.0
                if not desc and not cat and amt == 0:
                    continue
                rows.append([YEAR, m, label, cat, desc, abs(amt),
                             str(r.get("Date", "") or ""),
                             str(r.get("Status", "") or "Pending"),
                             str(r.get("Notes", "") or ""),
                             "TRUE" if r.get("Lent") else ""])
    return rows


def load_data():
    ws, err = get_worksheet()
    if ws is not None:
        try:
            records = ws.get_all_records()
            st.session_state["storage_mode"] = "sheets"
            if not records:
                seed = init_data()
                save_data(seed)
                return seed
            return sheet_rows_to_data(records)
        except Exception as e:
            st.session_state["storage_error"] = "Read failed: " + str(e)
    else:
        st.session_state["storage_error"] = err

    st.session_state["storage_mode"] = "local"
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return init_data()


def save_data(d):
    ws, err = get_worksheet()
    if ws is not None:
        try:
            rows = data_to_sheet_rows(d)
            ws.clear()
            ws.update([COLUMNS] + rows, value_input_option="USER_ENTERED")
            st.session_state["storage_mode"] = "sheets"
            st.session_state.pop("storage_error", None)
            return True
        except Exception as e:
            st.session_state["storage_error"] = "Write failed: " + str(e)

    st.session_state["storage_mode"] = "local"
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass
    return False


def parse_date(s):
    if not s or s in ("None", "NaT", ""):
        return None
    try:
        return date.fromisoformat(str(s)[:10])
    except Exception:
        return None


def rows_to_df(rows, kind="credit"):
    """Build the editable frame. Category stays in the data but is hidden from
    the table via column_order, so the user never has to touch it."""
    cats = CREDIT_CATS if kind == "credit" else DEBIT_CATS
    cols = ["Sel","Description","Amount","Date","Status","Lent","Notes","Category"]
    if not rows:
        return pd.DataFrame({
            "Sel": pd.Series([], dtype="bool"),
            "Description": pd.Series([], dtype="str"),
            "Amount": pd.Series([], dtype="float"),
            "Date": pd.Series([], dtype="object"),
            "Status": pd.Categorical([], categories=STATUS_OPTIONS),
            "Lent": pd.Series([], dtype="bool"),
            "Notes": pd.Series([], dtype="str"),
            "Category": pd.Series([], dtype="str"),
        })[cols]
    df = pd.DataFrame(rows)
    for col in ["Category","Description","Amount","Date","Status","Notes","Lent"]:
        if col not in df.columns:
            df[col] = 0.0 if col == "Amount" else (False if col == "Lent" else "")
    df["Sel"] = False
    df["Status"] = pd.Categorical(
        df["Status"].fillna("Pending").replace("", "Pending"), categories=STATUS_OPTIONS)
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Date"] = df["Date"].apply(parse_date)
    df["Lent"] = df["Lent"].fillna(False).astype(bool)
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    df["Category"] = df["Category"].fillna("").astype(str)
    return df[cols]


def df_to_rows(df, kind="credit"):
    df = df.copy()
    if "Sel" in df.columns:
        df = df.drop(columns=["Sel"])
    amt = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    df["Amount"] = amt.abs() if kind == "credit" else -amt.abs()
    df["Date"] = df["Date"].apply(lambda x: x.isoformat() if (x is not None and pd.notna(x)) else "")
    df["Notes"] = df["Notes"].fillna("").astype(str)
    df["Description"] = df["Description"].fillna("").astype(str)
    df["Category"] = df["Category"].fillna("").astype(str)
    df["Status"] = df["Status"].astype(str)
    if "Lent" not in df.columns:
        df["Lent"] = False
    df["Lent"] = df["Lent"].fillna(False).astype(bool)
    # Fill in Category silently from what this item was filed under before.
    hist = st.session_state.get("cat_memory", {})
    prefix = "C|" if kind == "credit" else "D|"
    fallback = CREDIT_CATS[0] if kind == "credit" else DEBIT_CATS[0]
    def fill_cat(row):
        cat = str(row.get("Category", "") or "").strip()
        if cat and cat.lower() != "nan":
            return cat
        desc = str(row.get("Description", "") or "").strip()
        if not desc:
            return ""
        return hist.get(prefix + desc.lower(), fallback)
    recs = df.to_dict(orient="records")
    for r in recs:
        r["Category"] = fill_cat(r)
    return recs


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
    mode = st.session_state.get("storage_mode", "local")
    if mode == "sheets":
        st.success("Storage: Google Sheets (data is safe)")
    else:
        st.error("Storage: TEMPORARY - data will be lost on restart")
        if st.session_state.get("storage_error"):
            with st.expander("Why?"):
                st.caption(st.session_state["storage_error"])

    if st.button("Save Data", use_container_width=True):
        ok = save_data(st.session_state.data)
        if ok:
            st.success("Saved to Google Sheets.")
        else:
            st.warning("Saved locally only - not permanent.")
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


def col_config(cats, label, lent_help="Money lent out - not a real expense"):
    return {
        "Sel": st.column_config.CheckboxColumn("Sel", help="Select for sum / copy", width="small", default=False),
        "Category": st.column_config.TextColumn("Category", width="medium"),
        "Description": st.column_config.TextColumn("Item", width="medium"),
        "Amount": st.column_config.NumberColumn(label, format="%.2f", width="medium", step=0.01),
        "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", width="small"),
        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS,
                                                   required=True, width="small",
                                                   help="TBC = amount not known yet"),
        "Lent": st.column_config.CheckboxColumn("Lent", help=lent_help, width="small", default=False),
        "Notes": st.column_config.TextColumn("Notes", width="medium"),
    }

# ══════════════════════════════════════════════════════════
#  COMMAND PARSER  —  "baba rm200 paid."  /  "Business received 8100."
# ══════════════════════════════════════════════════════════
DEBIT_WORDS  = ["paid", "pay", "payed", "spent", "bought", "gave", "give",
                "给", "付", "支付", "买", "花"]
CREDIT_WORDS = ["received", "receive", "recieved", "got", "earned", "income",
                "收", "收到", "入账", "进账"]


def parse_command(text, prev_debit, prev_credit, active_month):
    """Rule-based one-line parser. Returns (entry_dict, warnings) or (None, errors).

    Strategy: subtract the known pieces (amount, direction word, date), and
    whatever text remains is the item name. Word order does not matter.
    """
    import re, difflib
    warn = []
    raw = (text or "").strip()
    if not raw:
        return None, ["Type something first."]

    work = raw.rstrip(". ").strip()
    low = work.lower()

    # ---- direction ----
    def word_re(w):
        # Chinese keywords need no word boundaries; they glue to Latin text.
        if any(ord(ch) > 127 for ch in w):
            return re.escape(w)
        return r"(?<![a-z])" + re.escape(w) + r"(?![a-z])"

    kind = None
    hit_word = None
    for w in DEBIT_WORDS:
        if re.search(word_re(w), low):
            kind, hit_word = "debit", w
            break
    if kind is None:
        for w in CREDIT_WORDS:
            if re.search(word_re(w), low):
                kind, hit_word = "credit", w
                break
    if kind is None:
        kind = "debit"
        warn.append("No paid/received word found - assumed this is money OUT. Switch it below if wrong.")

    # ---- amount (strip an explicit date first so 15/6 is not read as money) ----
    tmp = work
    dmatch = re.search(r"\b(\d{1,2})\s*[/-]\s*(\d{1,2})\b", tmp)
    entry_date = ""
    target_month = active_month
    if dmatch:
        try:
            dd, mm = int(dmatch.group(1)), int(dmatch.group(2))
            if 1 <= mm <= 12 and 1 <= dd <= 31:
                entry_date = date(YEAR, mm, dd).isoformat()
                target_month = MONTHS[mm - 1]
        except Exception:
            pass
        tmp = tmp[:dmatch.start()] + " " + tmp[dmatch.end():]

    amts = re.findall(r"(?:rm\s*)?(\d[\d,]*(?:\.\d+)?)", tmp, flags=re.I)
    if not amts:
        return None, ["No amount found. Example:  baba rm200 paid"]
    if len(amts) > 1:
        warn.append("Found more than one number - used the largest. Check it below.")
    try:
        amount = max(float(a.replace(",", "")) for a in amts)
    except ValueError:
        return None, ["Could not read the amount."]

    # ---- item name = what is left over ----
    leftover = tmp
    leftover = re.sub(r"(?:rm\s*)?\d[\d,]*(?:\.\d+)?", " ", leftover, flags=re.I)
    leftover = re.sub(r"(?<![a-z])rm(?![a-z])", " ", leftover, flags=re.I)
    if hit_word:
        leftover = re.sub(word_re(hit_word), " ", leftover, flags=re.I)
    for filler in ["today", "yesterday", "on", "for", "to", "今天", "昨天"]:
        leftover = re.sub(word_re(filler), " ", leftover, flags=re.I)
    name = re.sub(r"\s+", " ", leftover).strip(" -,.")

    if not name:
        return None, ["Could not tell what the item is. Try:  baba rm200 paid"]

    # ---- snap to an item used before, so spelling stays consistent ----
    pool = prev_debit if kind == "debit" else prev_credit
    matched = None
    if pool:
        lower_map = {k.lower(): k for k in pool}
        if name.lower() in lower_map:
            matched = lower_map[name.lower()]
        else:
            close = difflib.get_close_matches(name.lower(), list(lower_map), n=1, cutoff=0.82)
            if close:
                matched = lower_map[close[0]]
    if matched:
        if matched.lower() != name.lower():
            warn.append('Matched to your existing item "' + matched + '".')
        name = matched
        category = pool.get(matched, "")
    else:
        category = ""
        # The typed name may be a category ("ad revenue") rather than an item.
        cat_list = DEBIT_CATS if kind == "debit" else CREDIT_CATS
        cat_map = {c.lower(): c for c in cat_list}
        cat_hit = cat_map.get(name.lower())
        if cat_hit is None:
            cclose = difflib.get_close_matches(name.lower(), list(cat_map), n=1, cutoff=0.82)
            if cclose:
                cat_hit = cat_map[cclose[0]]
        if cat_hit:
            category = cat_hit
            name = cat_hit
            warn.append('Read "' + cat_hit + '" as a category. Rename the item below if you meant something more specific.')
        else:
            warn.append('"' + name + '" is new - it will be added as a new item.')

    if not category:
        category = DEBIT_CATS[0] if kind == "debit" else CREDIT_CATS[0]

    if target_month != active_month:
        warn.append("Date points at " + target_month + " - this will be saved there, not "
                    + active_month + ".")

    return {
        "kind": kind,
        "month": target_month,
        "Description": name,
        "Amount": amount,
        "Date": entry_date,
        "Status": "Confirmed",
        "Category": category,
        "Notes": "",
        "Lent": False,
    }, warn


def recurring_expectations(data, exclude_month=None):
    """Work out which items should show up every month, and how many times.

    Car hire purchase appears twice a month (430 and 1123), so we track the
    usual COUNT per month, not just the name.
    """
    from collections import defaultdict
    counts = defaultdict(list)
    months_seen = 0
    for m in MONTHS:
        if m == exclude_month:
            continue
        md = data.get(m, {})
        rows = md.get("debits", []) + md.get("credits", [])
        names = [str(r.get("Description", "")).strip() for r in rows]
        names = [n for n in names if n]
        if not names:
            continue
        months_seen += 1
        per = defaultdict(int)
        for n in names:
            per[n.lower()] += 1
        for n in set(names):
            counts[n.lower()].append((n, per[n.lower()]))

    expect = {}
    if months_seen == 0:
        return expect
    for key, hits in counts.items():
        # Needs to have appeared in at least 2 months, or in the only month we have.
        if len(hits) < min(2, months_seen):
            continue
        display = hits[0][0]
        usual = max(c for _, c in hits)
        expect[key] = {"name": display, "count": usual, "months": len(hits)}
    return expect


def missing_this_month(data, month):
    """Recurring items that have not been entered in `month` yet."""
    expect = recurring_expectations(data, exclude_month=month)
    md = data.get(month, {})
    rows = md.get("debits", []) + md.get("credits", [])
    have = {}
    for r in rows:
        n = str(r.get("Description", "")).strip().lower()
        if n:
            have[n] = have.get(n, 0) + 1
    missing = []
    for key, info in expect.items():
        got = have.get(key, 0)
        if got < info["count"]:
            missing.append({"name": info["name"], "expected": info["count"],
                            "got": got, "months": info["months"]})
    missing.sort(key=lambda x: (-x["months"], x["name"].lower()))
    return missing


def tbc_items(data, month):
    """Entries whose amount is still unknown - must be chased every month."""
    out = []
    md = data.get(month, {})
    for kind in ("debits", "credits"):
        for r in md.get(kind, []):
            status = str(r.get("Status", "")).strip().lower()
            try:
                amt = abs(float(r.get("Amount", 0) or 0))
            except (TypeError, ValueError):
                amt = 0.0
            desc = str(r.get("Description", "")).strip()
            if not desc:
                continue
            if status == "tbc" or (amt == 0 and status != "confirmed"):
                out.append({"name": desc, "kind": kind,
                            "note": str(r.get("Notes", "") or "")})
    return out


def lent_balances(data):
    """Per-person balance: money lent out minus repayments received."""
    from collections import defaultdict
    bal = defaultdict(lambda: {"lent": 0.0, "back": 0.0})
    for m in MONTHS:
        md = data.get(m, {})
        for r in md.get("debits", []):
            if not r.get("Lent"):
                continue
            n = str(r.get("Description", "")).strip()
            if n:
                try:
                    bal[n]["lent"] += abs(float(r.get("Amount", 0) or 0))
                except (TypeError, ValueError):
                    pass
        for r in md.get("credits", []):
            if not r.get("Lent"):
                continue
            n = str(r.get("Description", "")).strip()
            if n:
                try:
                    bal[n]["back"] += abs(float(r.get("Amount", 0) or 0))
                except (TypeError, ValueError):
                    pass
    out = []
    for n, v in bal.items():
        out.append({"Person / Item": n, "Lent out": v["lent"],
                    "Returned": v["back"], "Still owed": v["lent"] - v["back"]})
    out.sort(key=lambda x: -x["Still owed"])
    return out


def find_duplicate(entry, data):
    """Same item, same amount, already in that month -> likely a double entry."""
    md = data.get(entry["month"], {})
    rows = md.get("credits" if entry["kind"] == "credit" else "debits", [])
    for r in rows:
        if str(r.get("Description", "")).strip().lower() == entry["Description"].strip().lower():
            try:
                if abs(abs(float(r.get("Amount", 0) or 0)) - entry["Amount"]) < 0.01:
                    return True
            except (TypeError, ValueError):
                continue
    return False


SIDE_VISIBLE_ROWS = 10


def merge_edits(base_df, editor_states):
    """Apply st.data_editor edit-states onto the base frame.

    The same month is rendered in two places (single tab + side-by-side), so we
    replay whichever editor the user touched onto one shared frame.
    """
    df = base_df.copy().reset_index(drop=True)
    for state in editor_states:
        if not isinstance(state, dict):
            continue
        for idx, changes in (state.get("edited_rows") or {}).items():
            i = int(idx)
            if i < 0 or i >= len(df):
                continue
            for col, val in changes.items():
                if col not in df.columns:
                    continue
                if col == "Date" and isinstance(val, str):
                    val = parse_date(val)
                if col == "Status":
                    if val is not None and val not in df[col].cat.categories:
                        df[col] = df[col].cat.add_categories([val])
                df.at[i, col] = val
        added = state.get("added_rows") or []
        if added:
            new_rows = []
            for row in added:
                if not isinstance(row, dict):
                    continue
                rec = {c: (False if c in ("Sel", "Lent")
                           else (0.0 if c == "Amount" else None))
                       for c in df.columns}
                for col, val in row.items():
                    if col not in df.columns:
                        continue
                    if col == "Date" and isinstance(val, str):
                        val = parse_date(val)
                    rec[col] = val
                new_rows.append(rec)
            if new_rows:
                add_df = pd.DataFrame(new_rows)
                for col in ("Status",):
                    if col in df.columns and col in add_df.columns:
                        vals = [v for v in add_df[col].dropna().unique()
                                if v not in df[col].cat.categories]
                        if vals:
                            df[col] = df[col].cat.add_categories(vals)
                df = pd.concat([df, add_df], ignore_index=True)
        deleted = state.get("deleted_rows") or []
        if deleted:
            keep = [i for i in range(len(df)) if i not in set(int(x) for x in deleted)]
            df = df.iloc[keep].reset_index(drop=True)
    for bcol in ("Sel", "Lent"):
        if bcol in df.columns:
            df[bcol] = df[bcol].fillna(False).astype(bool)
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    for col in ("Description", "Notes", "Category"):
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
    if "Status" in df.columns:
        df["Status"] = df["Status"].fillna("Pending")
    return df

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

    glance_slot = st.container()
    kpi_slot = st.container()
    alert_slot = st.container()

    # Item history -> used by the command box, quick add, and category auto-fill
    prev_credit, prev_debit, prev_notes = {}, {}, {}
    for m in MONTHS:
        md = st.session_state.data.get(m, {})
        for r in md.get("credits", []):
            dsc = str(r.get("Description", "")).strip()
            if dsc:
                prev_credit.setdefault(dsc, r.get("Category", ""))
                prev_notes.setdefault("C|" + dsc, r.get("Notes", ""))
        for r in md.get("debits", []):
            dsc = str(r.get("Description", "")).strip()
            if dsc:
                prev_debit.setdefault(dsc, r.get("Category", ""))
                prev_notes.setdefault("D|" + dsc, r.get("Notes", ""))

    st.session_state["cat_memory"] = dict(
        [("C|" + k.lower(), v) for k, v in prev_credit.items() if v] +
        [("D|" + k.lower(), v) for k, v in prev_debit.items() if v])

    # ══════════════════════════════════════════════════
    #  COMMAND BOX  —  type one line, confirm, saved
    # ══════════════════════════════════════════════════
    st.markdown('<p class="cmd-label">Quick Entry</p>', unsafe_allow_html=True)
    cbox1, cbox2 = st.columns([5, 1])
    with cbox1:
        cmd_text = st.text_input(
            "cmd", key="cmd_input_" + active, label_visibility="collapsed",
            placeholder="baba rm200 paid     ·     business received 8100     ·     maxis 237.20 paid")
    with cbox2:
        cmd_go = st.button("Enter", use_container_width=True, type="primary",
                           key="cmd_go_" + active)

    if cmd_go and cmd_text.strip():
        entry, msgs = parse_command(cmd_text, prev_debit, prev_credit, active)
        if entry is None:
            st.session_state["cmd_pending"] = None
            st.session_state["cmd_error"] = msgs
        else:
            entry["_dup"] = find_duplicate(entry, st.session_state.data)
            st.session_state["cmd_pending"] = entry
            st.session_state["cmd_warn"] = msgs
            st.session_state.pop("cmd_error", None)

    for e in st.session_state.get("cmd_error", []) or []:
        st.error(e)

    pending = st.session_state.get("cmd_pending")
    if pending:
        st.markdown('<div class="preview-head">Check this, then confirm</div>',
                    unsafe_allow_html=True)
        for w in st.session_state.get("cmd_warn", []) or []:
            st.warning(w)
        if pending.get("_dup"):
            st.error("You already have this exact item and amount in " + pending["month"]
                     + ". Confirming will add a second one.")

        p1, p2, p3, p4 = st.columns([1, 2.2, 1.4, 1.4])
        with p1:
            pv_kind = st.selectbox("Direction", ["Money OUT", "Money IN"],
                                   index=0 if pending["kind"] == "debit" else 1,
                                   key="pv_kind")
        with p2:
            pv_name = st.text_input("Item", value=pending["Description"], key="pv_name")
        with p3:
            pv_amt = st.number_input("Amount (RM)", value=float(pending["Amount"]),
                                     min_value=0.0, step=10.0, format="%.2f", key="pv_amt")
        with p4:
            pv_month = st.selectbox("Save to", MONTHS, index=MONTHS.index(pending["month"]),
                                    key="pv_month")

        p5, p6, p7 = st.columns([1.4, 1.4, 3])
        with p5:
            pv_status = st.selectbox("Status", STATUS_OPTIONS,
                                     index=STATUS_OPTIONS.index(pending.get("Status", "Confirmed")),
                                     key="pv_status")
        with p6:
            pv_lent = st.checkbox("This is money lent out", key="pv_lent",
                                  value=bool(pending.get("Lent")))
        with p7:
            pv_notes = st.text_input("Notes", value=pending.get("Notes", ""), key="pv_notes")

        a1, a2, _ = st.columns([1, 1, 4])
        with a1:
            confirm = st.button("Confirm & Save", type="primary",
                                use_container_width=True, key="pv_ok")
        with a2:
            cancel = st.button("Cancel", use_container_width=True, key="pv_no")

        if cancel:
            st.session_state["cmd_pending"] = None
            st.session_state.pop("cmd_warn", None)
            st.rerun()

        if confirm:
            kind_key = "credits" if pv_kind == "Money IN" else "debits"
            cats = CREDIT_CATS if kind_key == "credits" else DEBIT_CATS
            pfx = "C|" if kind_key == "credits" else "D|"
            cat = st.session_state["cat_memory"].get(pfx + pv_name.strip().lower(), "")
            if not cat:
                cat = pending.get("Category") or cats[0]
            amt = abs(float(pv_amt))
            if kind_key == "debits":
                amt = -amt
            st.session_state.data.setdefault(pv_month, {"credits": [], "debits": []})
            st.session_state.data[pv_month][kind_key].append({
                "Category": cat,
                "Description": pv_name.strip(),
                "Amount": amt,
                "Date": pending.get("Date", ""),
                "Status": pv_status,
                "Notes": pv_notes,
                "Lent": bool(pv_lent),
            })
            for k in ("credits_", "debits_"):
                st.session_state.pop(k + pv_month, None)
            save_data(st.session_state.data)
            st.session_state["cmd_pending"] = None
            st.session_state.pop("cmd_warn", None)
            st.session_state["cmd_done"] = "Saved: {} RM {:,.2f} to {}".format(
                pv_name.strip(), abs(float(pv_amt)), pv_month)
            st.rerun()

    if st.session_state.get("cmd_done"):
        st.success(st.session_state.pop("cmd_done"))

    # ── Bring recurring items into an empty month ──
    if not credit_rows and not debit_rows:
        miss = missing_this_month(st.session_state.data, active)
        if miss:
            st.info("{} is empty. You normally have {} recurring item(s) each month.".format(
                active, len(miss)))
            bb1, bb2, _ = st.columns([1.6, 1.6, 3])
            with bb1:
                bring_zero = st.button("Bring items in (amounts blank)",
                                       use_container_width=True, key="bring0_" + active)
            with bb2:
                bring_amt = st.button("Bring items in (keep amounts)",
                                      use_container_width=True, key="bring1_" + active)
            if bring_zero or bring_amt:
                last = {}
                for m in MONTHS:
                    for kind in ("debits", "credits"):
                        for r in st.session_state.data.get(m, {}).get(kind, []):
                            n = str(r.get("Description", "")).strip()
                            if n:
                                last[(kind, n.lower())] = r
                added = 0
                for item in miss:
                    for kind in ("debits", "credits"):
                        srcrow = last.get((kind, item["name"].lower()))
                        if not srcrow:
                            continue
                        for _ in range(item["expected"] - item["got"]):
                            amt = abs(float(srcrow.get("Amount", 0) or 0)) if bring_amt else 0.0
                            if kind == "debits":
                                amt = -amt
                            st.session_state.data[active][kind].append({
                                "Category": srcrow.get("Category", ""),
                                "Description": item["name"],
                                "Amount": amt,
                                "Date": "",
                                "Status": "Pending" if bring_amt else "TBC",
                                "Notes": srcrow.get("Notes", ""),
                                "Lent": bool(srcrow.get("Lent")),
                            })
                            added += 1
                        break
                for k in ("credits_", "debits_"):
                    st.session_state.pop(k + active, None)
                save_data(st.session_state.data)
                st.success("Added {} item(s) to {}.".format(added, active))
                st.rerun()

    with st.expander("All items you have used before  -  {} in, {} out".format(
            len(prev_credit), len(prev_debit))):
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("**Money in**")
            if prev_credit:
                st.dataframe(pd.DataFrame({"Item": sorted(prev_credit.keys())}),
                             use_container_width=True, hide_index=True,
                             height=min(300, 38 + len(prev_credit) * 35))
            else:
                st.caption("None yet.")
        with pc2:
            st.markdown("**Money out**")
            if prev_debit:
                st.dataframe(pd.DataFrame({"Item": sorted(prev_debit.keys())}),
                             use_container_width=True, hide_index=True,
                             height=min(300, 38 + len(prev_debit) * 35))
            else:
                st.caption("None yet.")

    st.markdown("---")

    credit_df = rows_to_df(credit_rows, "credit")
    debit_df = rows_to_df(debit_rows, "debit")

    def table_height(df):
        return 35 + min(max(len(df) + 1, 4), VISIBLE_ROWS) * 35 + 3

    def total_bar(df, kind):
        """Totals live just under the table - they cannot be edited or deleted."""
        n = len(df)
        tot = float(df["Amount"].abs().sum()) if n else 0.0
        colr = "#dc2626" if kind == "debit" else "#16a34a"
        sign = "-" if (kind == "debit" and tot) else ""
        st.markdown(
            '<div class="totalbar"><span class="t-lab">TOTAL &nbsp;({} item{})</span>'
            '<span class="t-val" style="color:{}">{} RM {:,.2f}</span></div>'.format(
                n, "" if n == 1 else "s", colr, sign, tot), unsafe_allow_html=True)

    # Single side-by-side view: money out on the left, money in on the right.
    st.caption("Money out on the left, money in on the right. "
               "On a narrow screen they stack: money out first, then money in.")
    sb1, sb2 = st.columns(2)
    with sb1:
        st.markdown('<p class="section-debit">Money OUT - counted as negative</p>',
                    unsafe_allow_html=True)
        st.data_editor(debit_df, num_rows="dynamic", use_container_width=True,
                       height=table_height(debit_df),
                       column_config=col_config(DEBIT_CATS, "RM (-)"),
                       column_order=SIDE_ORDER, key="debits_" + active)
        total_bar(debit_df, "debit")
    with sb2:
        st.markdown('<p class="section-credit">Money IN - counted as positive</p>',
                    unsafe_allow_html=True)
        st.data_editor(credit_df, num_rows="dynamic", use_container_width=True,
                       height=table_height(credit_df),
                       column_config=col_config(CREDIT_CATS, "RM (+)",
                                                lent_help="Repayment of money you lent out"),
                       column_order=SIDE_ORDER, key="credits_" + active)
        total_bar(credit_df, "credit")

    ec = merge_edits(credit_df, [st.session_state.get("credits_" + active)])
    ed = merge_edits(debit_df, [st.session_state.get("debits_" + active)])

    st.session_state.data[active]["credits"] = df_to_rows(ec, "credit")
    st.session_state.data[active]["debits"] = df_to_rows(ed, "debit")

    fingerprint = json.dumps(st.session_state.data, sort_keys=True, default=str)
    if st.session_state.get("last_saved_fingerprint") != fingerprint:
        if st.session_state.get("last_saved_fingerprint") is not None:
            save_data(st.session_state.data)
        st.session_state["last_saved_fingerprint"] = fingerprint

    lent_out = float(ed.loc[ed["Lent"] == True, "Amount"].abs().sum()) if len(ed) else 0.0
    total_credit = float(ec["Amount"].abs().sum()) if len(ec) else 0.0
    debit_mag = float(ed["Amount"].abs().sum()) if len(ed) else 0.0
    total_debit = -debit_mag if debit_mag else 0.0
    net = total_credit + total_debit
    net_real = net + lent_out
    margin = (net / total_credit * 100) if total_credit else 0.0

    with kpi_slot:
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Money In", "RM {:,.2f}".format(total_credit))
        k2.metric("Money Out", "RM {:,.2f}".format(total_debit))
        k3.metric("Net", "RM {:,.2f}".format(net), delta="{:+.1f}%".format(margin))
        if lent_out:
            k4.metric("Net excl. lent", "RM {:,.2f}".format(net_real),
                      help="Money you lent out is not a real expense")
        else:
            k4.metric("Entries", str(len(ec) + len(ed)))

    # ── Glance strip ──
    pend_d = ed[ed["Status"].astype(str).isin(["Pending", "TBC"])] if len(ed) else ed
    pend_amt = float(pend_d["Amount"].abs().sum()) if len(pend_d) else 0.0
    pend_n = len(pend_d)
    today = date.today()
    upcoming = [r["Date"] for _, r in pend_d.iterrows()
                if r["Date"] is not None and pd.notna(r["Date"])] if len(pend_d) else []
    next_due = min([d for d in upcoming if d >= today], default=None)
    overdue_n = len([d for d in upcoming if d < today])

    with glance_slot:
        net_col = "#16a34a" if net >= 0 else "#dc2626"
        due_txt = next_due.strftime("%d %b") if next_due else "none dated"
        od_txt = ("  ·  <b style='color:#dc2626'>{} overdue</b>".format(overdue_n)) if overdue_n else ""
        lent_txt = ('<span class="g-sep">|</span><span class="g-item">Lent out '
                    '<b style="color:#7c3aed">RM {:,.2f}</b></span>'.format(lent_out)) if lent_out else ""
        st.markdown(
            '<div class="glance">'
            '<span class="g-item">Net <b style="color:{}">RM {:,.2f}</b></span>'
            '<span class="g-sep">|</span>'
            '<span class="g-item">Unpaid <b>{}</b> · <b>RM {:,.2f}</b></span>'
            '<span class="g-sep">|</span>'
            '<span class="g-item">Next due <b>{}</b>{}</span>{}'
            '</div>'.format(net_col, net, pend_n, pend_amt, due_txt, od_txt, lent_txt),
            unsafe_allow_html=True)

    # ══════════════════════════════════════════════════
    #  MONTHLY REMINDERS  —  always visible, never hidden
    # ══════════════════════════════════════════════════
    with alert_slot:
        miss = missing_this_month(st.session_state.data, active)
        tbcs = tbc_items(st.session_state.data, active)

        if miss:
            lines = []
            for item in miss:
                if item["expected"] > 1:
                    lines.append("<li><b>{}</b> &nbsp;<span class='a-sub'>usually {}x a month, "
                                 "you have {}</span></li>".format(
                                     item["name"], item["expected"], item["got"]))
                else:
                    lines.append("<li><b>{}</b></li>".format(item["name"]))
            st.markdown(
                '<div class="alertbox alert-miss"><div class="a-title">'
                'Not entered yet this month ({})</div><ul>{}</ul></div>'.format(
                    len(miss), "".join(lines)), unsafe_allow_html=True)

        if tbcs:
            lines = []
            for t in tbcs:
                note = (" &nbsp;<span class='a-sub'>" + t["note"] + "</span>") if t["note"] else ""
                lines.append("<li><b>{}</b>{}</li>".format(t["name"], note))
            st.markdown(
                '<div class="alertbox alert-tbc"><div class="a-title">'
                'Amount still unknown ({})</div><ul>{}</ul></div>'.format(
                    len(tbcs), "".join(lines)), unsafe_allow_html=True)

    sel_c = float(ec.loc[ec["Sel"] == True, "Amount"].abs().sum()) if len(ec) else 0.0
    sel_d_mag = float(ed.loc[ed["Sel"] == True, "Amount"].abs().sum()) if len(ed) else 0.0
    sel_d = -sel_d_mag if sel_d_mag else 0.0
    sel_cc = int(ec["Sel"].sum()) if len(ec) else 0
    sel_dc = int(ed["Sel"].sum()) if len(ed) else 0
    sel_net = sel_c + sel_d
    sel_count = sel_cc + sel_dc

    if pend_n:
        with st.expander("Unpaid this month  -  {} item(s), RM {:,.2f}".format(pend_n, pend_amt),
                         expanded=bool(overdue_n)):
            w = pend_d[["Description", "Amount", "Date", "Status", "Notes"]].copy()
            w["Amount"] = w["Amount"].abs()
            w["Due"] = w["Date"].apply(
                lambda d: "OVERDUE" if (d is not None and pd.notna(d) and d < today)
                else (d.strftime("%d %b") if (d is not None and pd.notna(d)) else "-"))
            w = w.drop(columns=["Date"]).sort_values("Due")
            st.dataframe(w, use_container_width=True, hide_index=True,
                         height=min(320, 38 + len(w) * 35))
            if overdue_n:
                st.warning("{} item(s) are past their date and still unpaid.".format(overdue_n))

    st.markdown("---")
    st.markdown("#### Selection Sum")
    if sel_count == 0:
        st.caption("Tick Sel on any row to start summing - works across both tables.")
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown('<div class="sum-box"><div class="label">Selected IN (+)</div>'
                    '<div class="value" style="color:#4ade80">+ RM {:,.2f}</div>'
                    '<div class="detail">{} item(s)</div></div>'.format(sel_c, sel_cc),
                    unsafe_allow_html=True)
    with s2:
        st.markdown('<div class="sum-box"><div class="label">Selected OUT (-)</div>'
                    '<div class="value" style="color:#f87171">RM {:,.2f}</div>'
                    '<div class="detail">{} item(s)</div></div>'.format(sel_d, sel_dc),
                    unsafe_allow_html=True)
    with s3:
        col = "#4ade80" if sel_net >= 0 else "#f87171"
        sign = "+" if sel_net >= 0 else ""
        st.markdown('<div class="sum-box"><div class="label">Net Total</div>'
                    '<div class="value" style="color:{}">{} RM {:,.2f}</div>'
                    '<div class="detail">{} item(s) selected</div></div>'.format(
                        col, sign, sel_net, sel_count), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Copy Selected Items To...")
    if sel_count == 0:
        st.caption("Tick Sel on the rows you want to copy, then choose the target months.")
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
                        "Category": str(r.get("Category", "") or ""),
                        "Description": str(r["Description"] or ""),
                        "Amount": a,
                        "Date": dv.isoformat() if (dv is not None and pd.notna(dv)) else "",
                        "Status": str(r["Status"]),
                        "Notes": str(r["Notes"] or ""),
                        "Lent": bool(r.get("Lent", False)),
                    })
                return out

            pc = payload(ec[ec["Sel"] == True], "credits")
            pdd = payload(ed[ed["Sel"] == True], "debits")
            for tm in copy_targets:
                st.session_state.data.setdefault(tm, {"credits": [], "debits": []})
                st.session_state.data[tm]["credits"] = st.session_state.data[tm].get("credits", []) + pc
                st.session_state.data[tm]["debits"] = st.session_state.data[tm].get("debits", []) + pdd
                for k in ("credits_", "debits_"):
                    st.session_state.pop(k + tm, None)
            save_data(st.session_state.data)
            st.success("Copied {} item(s) into {} month(s): {}".format(
                sel_count, len(copy_targets), ", ".join(copy_targets)))

    # ── Charts last, so the top of the page stays for entry ──
    cred_tot = ec["Amount"].abs().sum() if len(ec) else 0
    deb_tot = ed["Amount"].abs().sum() if len(ed) else 0
    if cred_tot > 0 or deb_tot > 0:
        with st.expander("Breakdown charts", expanded=False):
            ch1, ch2 = st.columns(2)
            with ch1:
                if deb_tot > 0:
                    g = ed.copy()
                    g["Amount"] = g["Amount"].abs()
                    g = g.groupby("Description", observed=True)["Amount"].sum().reset_index()
                    g = g[g["Amount"] > 0].sort_values("Amount")
                    if len(g):
                        st.markdown("**Money out by item**")
                        st.bar_chart(g, x="Description", y="Amount", color="#ef4444",
                                     horizontal=True)
            with ch2:
                if cred_tot > 0:
                    g = ec.copy()
                    g["Amount"] = g["Amount"].abs()
                    g = g.groupby("Description", observed=True)["Amount"].sum().reset_index()
                    g = g[g["Amount"] > 0].sort_values("Amount")
                    if len(g):
                        st.markdown("**Money in by item**")
                        st.bar_chart(g, x="Description", y="Amount", color="#22c55e",
                                     horizontal=True)

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

    # ── Money lent out / still owed ──
    bals = lent_balances(st.session_state.data)
    if bals:
        st.divider()
        st.markdown("#### Money Lent Out")
        owed = sum(b["Still owed"] for b in bals)
        st.caption("These are marked Lent, so they are not counted as real expenses.")
        lb = pd.DataFrame(bals)
        st.dataframe(lb.style.format({"Lent out": "RM {:,.2f}", "Returned": "RM {:,.2f}",
                                      "Still owed": "RM {:,.2f}"}),
                     use_container_width=True, hide_index=True,
                     height=min(360, 38 + len(lb) * 35))
        st.metric("Total still owed to you", "RM {:,.2f}".format(owed))

    # ── Items with no category yet ──
    uncat = set()
    for m in MONTHS:
        md = st.session_state.data.get(m, {})
        for kind in ("credits", "debits"):
            for r in md.get(kind, []):
                d = str(r.get("Description", "")).strip()
                c = str(r.get("Category", "") or "").strip()
                if d and (not c or c.lower() == "nan"):
                    uncat.add(d)
    if uncat:
        with st.expander("Items with no category ({})".format(len(uncat))):
            st.caption("Grouping still works without a category. Set one in the sheet if you want "
                       "these rolled into a group.")
            st.dataframe(pd.DataFrame({"Item": sorted(uncat)}),
                         use_container_width=True, hide_index=True,
                         height=min(300, 38 + len(uncat) * 35))

    # ── (F) Month vs month comparison ──
    st.divider()
    st.markdown("#### Compare Two Months")
    active_idx = MONTHS.index(st.session_state.get("active_month", "June"))
    cmp1, cmp2 = st.columns(2)
    with cmp1:
        m_base = st.selectbox("Earlier month", MONTHS,
                              index=max(active_idx - 1, 0), key="cmp_base")
    with cmp2:
        m_curr = st.selectbox("Later month", MONTHS, index=active_idx, key="cmp_curr")

    def month_totals(m):
        md = st.session_state.data.get(m, {"credits": [], "debits": []})
        c = signed(md.get("credits", []), "credit")
        d = abs(signed(md.get("debits", []), "debit"))
        return c, d, c - d

    b_c, b_d, b_n = month_totals(m_base)
    c_c, c_d, c_n = month_totals(m_curr)

    def delta_str(new, old):
        diff = new - old
        if old == 0:
            return "RM {:+,.2f}".format(diff)
        return "RM {:+,.2f}  ({:+.1f}%)".format(diff, diff / abs(old) * 100)

    d1, d2, d3 = st.columns(3)
    d1.metric("Revenue - " + m_curr[:3], "RM {:,.2f}".format(c_c), delta=delta_str(c_c, b_c))
    d2.metric("Expenses - " + m_curr[:3], "RM {:,.2f}".format(c_d),
              delta=delta_str(c_d, b_d), delta_color="inverse")
    d3.metric("Net - " + m_curr[:3], "RM {:,.2f}".format(c_n), delta=delta_str(c_n, b_n))
    st.caption("Compared against {}: revenue RM {:,.2f} · expenses RM {:,.2f} · net RM {:,.2f}".format(
        m_base, b_c, b_d, b_n))

    # Category-level movement between the two months
    def cat_totals(m, kind):
        md = st.session_state.data.get(m, {"credits": [], "debits": []})
        out = {}
        for r in md.get(kind, []):
            try:
                amt = abs(float(r.get("Amount", 0) or 0))
            except (TypeError, ValueError):
                amt = 0.0
            if amt:
                key = str(r.get("Description", "") or "-").strip() or "-"
                out[key] = out.get(key, 0) + amt
        return out

    base_cats = cat_totals(m_base, "debits")
    curr_cats = cat_totals(m_curr, "debits")
    all_cats = sorted(set(base_cats) | set(curr_cats))
    if all_cats:
        move = pd.DataFrame([{
            "Category": c,
            m_base[:3]: base_cats.get(c, 0.0),
            m_curr[:3]: curr_cats.get(c, 0.0),
            "Change": curr_cats.get(c, 0.0) - base_cats.get(c, 0.0),
        } for c in all_cats]).sort_values("Change", ascending=False)
        st.markdown("**Money out: what changed**")
        st.dataframe(move.style.format({m_base[:3]: "{:,.2f}", m_curr[:3]: "{:,.2f}",
                                        "Change": "{:+,.2f}"}),
                     use_container_width=True, hide_index=True,
                     height=min(400, 38 + len(move) * 35))

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
