import pandas as pd
import os

CSV_FILE = 'expenses.csv'


def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "category", "amount", "currency"])
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)


def add_expense_to_csv(date, category, amount, currency):
    expense = [[date, category, amount, currency]]
    df = pd.DataFrame(expense, columns=["date", "category", "amount", "currency"])
    df.to_csv(CSV_FILE, mode='a', header=False, index=False)


def load_expenses():
    if not os.path.exists(CSV_FILE):
        initialize_csv()
    df = pd.read_csv(CSV_FILE)
    expected_columns = {"date", "category", "amount", "currency"}
    if not expected_columns.issubset(df.columns):
        raise KeyError(f"The CSV file is missing required columns: {expected_columns - set(df.columns)}")
    return df


def delete_last_expense(currency):
    df = load_expenses()
    filtered_df = df[df['currency'] == currency]
    if not filtered_df.empty:
        df = df.drop(filtered_df.tail(1).index)
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)
        return True
    return False


def delete_all_expenses(currency):
    df = load_expenses()

    filtered_df = df[df['currency'] != currency]
    if len(filtered_df) < len(df):
        filtered_df.to_csv(CSV_FILE, mode='w', header=True, index=False)
        return True
    return False
