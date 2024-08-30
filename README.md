# Expense Tracker Bot

This is a Telegram bot designed to help you track your daily expenses by category, display statistics over different periods, and manage your expense records. The bot uses a simple CSV file to store expense data and offers a user-friendly interface for adding, viewing, and deleting expenses.

## Features

- **Currency Selection**: Choose your preferred currency for tracking expenses.
- **Expense Tracking**: Add expenses by category, including Food, Transport, Entertainment, and Other.
- **Statistics**: View your expenses for different periods (day, week, month, year) and see average expenses per month or year.
- **Data Management**: Delete the last added expense or clear all expenses for the selected currency.
- **Chart Generation**: The bot generates bar charts displaying expenses by category or averages over time.

## Requirements

- Python 3.x
- `pandas`
- `matplotlib`
- `telebot`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/expense-tracker-bot.git
   cd expense-tracker-bot
