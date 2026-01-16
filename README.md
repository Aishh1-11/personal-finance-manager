Personal Finance Manager (PFM)

A Personal Finance Manager web application built using Python & Django to help users track income, expenses, and financial commitments in a structured and meaningful way. The goal of this project is to promote better money awareness, disciplined spending, and informed financial decisions.

This project is actively under development and is designed as a real-world portfolio project for backend / full‑stack roles.

🚀 Features
✅ Income Management

Add multiple income sources (salary, freelance, borrowed, etc.)

Monthly income tracking

Flexible source names (user-defined)

✅ Expense Management

Categorized expenses:

Consumption

Safety

Growth

Freedom

Commitment (auto-generated)

CRUD operations for expenses

Monthly expense summaries

✅ Commitment System (Core Feature)

Commitments are fixed financial obligations (rent, EMI, subscriptions, etc.)

Stored separately from expenses

Commitments reduce spendable balance even if unpaid

Monthly commitment logic without duplicating records

Commitment workflow:

Add commitment with due day & amount

Commitment appears as unpaid / overdue

Mark as paid →

Automatically creates an expense

Updates last_paid_date

Changes status to paid

✅ Dashboard

Total Income

Total Expenses

Total Commitments (monthly)

Balance

Spendable Amount

Remaining Commitments

✅ Smart Calculations

Balance = Income − Expenses

Spendable = Income − Expenses − Unpaid Commitments



🛠️ Tech Stack

Backend: Python, Django

Frontend: HTML, CSS, Bootstrap

Database: SQLite

Version Control: Git & GitHub
