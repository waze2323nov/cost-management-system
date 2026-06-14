# 📊 Cost Management System

**Fiscal Year 2026 · MYR**

A Streamlit-based cost management system for tracking monthly credits and debits, with real-time calculations, category breakdowns, and an annual dashboard.

## Features

- **Monthly Ledger** — Credits and debits with categories, descriptions, amounts, dates, status, and notes
- **Annual Dashboard** — YTD KPIs, monthly trend charts, net P&L line chart, and category-level expense analysis
- **Data Persistence** — Save/load data as JSON; export backups anytime
- **12-Month Switcher** — Quick month navigation
- **Custom Categories** — Tailored for business, advertising, family support, loans, and more

## Deploy to Streamlit Cloud

1. Push all files to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click **New App** → select your repository → set main file to `app.py` → **Deploy**

## File Structure

```
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .streamlit/
    └── config.toml     # Theme configuration
```
