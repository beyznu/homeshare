# 🏠 HomeShare — Shared Expense Tracker for Roommates

A desktop application built with Python and tkinter that helps roommates track shared expenses, record payments, and visualize spending data.


---

## Features

- **User authentication** — register and log in with a personal account; each user's data is fully isolated
- **Roommate management** — add, edit, and deactivate roommates (soft delete preserves expense history)
- **Expense tracking** — log shared expenses with category, date, and payer; costs are split equally among selected roommates
- **Balance summary** — real-time dashboard showing who owes what, including settled payments
- **Payment recording** — log cash settlements between roommates to keep balances up to date
- **Category management** — organize expenses with default and custom categories
- **Charts** — visualize spending by category (pie chart) and by month (bar chart) via matplotlib
- **Excel export** — export expenses, balance summary, and payment history to a formatted `.xlsx` file with formula-based totals

---

## Tech Stack

| | |
|---|---|
| Language | Python 3 |
| GUI | tkinter + [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) (Minty theme) |
| Database | SQLite3 |
| Charts | matplotlib (`FigureCanvasTkAgg`) |
| Spreadsheet | openpyxl |

---

## Project Structure
├── main.py           # Entry point — login & register window

├── db_manager.py     # Database layer (ValidationError, Validator, Database classes)

├── dashboard.py      # Main hub window with balance overview and navigation

├── expenses.py       # Expense list, add, and edit windows

├── roommates.py      # Roommate management window

├── payments.py       # Payment recording window

├── categories.py     # Category management window

├── charts.py         # Matplotlib chart window (pie + bar)

└── reports.py        # Excel export window

## How to Run

**Requirements**
```bash
pip install ttkbootstrap matplotlib openpyxl
```

> On macOS with Python 3.13+, tkinter may need to be installed separately:
> ```bash
> brew install python-tk@3.13
> ```

**Run**
```bash
python main.py
```
