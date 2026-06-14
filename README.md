# 📊 Cost Management System

**Fiscal Year 2026 · MYR**

A Streamlit-based cost management application for tracking monthly credits (inflows) and debits (outflows), with real-time calculations, category breakdowns, and an annual dashboard.

## Features

- **Monthly Ledger** — Enter credits and debits with categories, descriptions, amounts, dates, and status tracking
- **Annual Dashboard** — YTD KPIs, monthly trend charts, net profit/loss line chart, and category-level expense analysis
- **Data Persistence** — Save/load data as JSON; export backups anytime
- **12-Month Switcher** — Sidebar selector for quick month navigation
- **Category Management** — Pre-defined categories for both income and expense entries

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push `app.py` and `requirements.txt` to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click **New App** → select your repository → set main file to `app.py` → **Deploy**

## File Structure

```
├── app.py              # Main application
├── requirements.txt    # Python dependencies
└── README.md           # This file
```
