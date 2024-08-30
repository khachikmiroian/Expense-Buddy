import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from telebot import types, TeleBot
from csv_handler import initialize_csv, add_expense_to_csv, load_expenses, delete_last_expense, delete_all_expenses
from TOKEN import my_token

matplotlib.use('Agg')
г
bot = TeleBot(my_token)

user_data = {}


@bot.message_handler(commands=['start'])
def start_bot(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('AMD')
    btn2 = types.KeyboardButton('USD')
    btn3 = types.KeyboardButton('RUB')
    btn4 = types.KeyboardButton('EUR')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, 'Welcome to your wallet! Select a currency for further interaction with the bot.',
                     reply_markup=markup)
    bot.register_next_step_handler(message, set_currency)


def set_currency(message):
    currency = message.text
    user_data[message.chat.id] = {'currency': currency, 'expenses': []}
    bot.send_message(message.chat.id, f'You have successfully selected your currency: {currency}!')
    show_main_menu(message)


def show_main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Add by category!')
    btn2 = types.KeyboardButton('Show your statistics!')
    btn3 = types.KeyboardButton('Delete last expense!')
    btn4 = types.KeyboardButton('Delete all your expenses!')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, 'What would you like to do?', reply_markup=markup)
    bot.register_next_step_handler(message, menu_handler)


@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    if message.text == 'Add by category!':
        select_category_to_add_expense(message)
    elif message.text == 'Show your statistics!':
        show_statistics(message)
    elif message.text == 'Delete last expense!':
        currency = user_data[message.chat.id]['currency']
        if delete_last_expense(currency):
            bot.send_message(message.chat.id, 'You have deleted your last expense. What would you like to do next?')
        else:
            bot.send_message(message.chat.id, 'No expenses found to delete.')
        show_main_menu(message)
    elif message.text == 'Delete all your expenses!':
        currency = user_data[message.chat.id]['currency']
        delete_all_expenses(currency)
        bot.send_message(message.chat.id, 'You have deleted all your expenses!')
        show_main_menu(message)


def select_category_to_add_expense(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Food')
    btn2 = types.KeyboardButton('Transport')
    btn3 = types.KeyboardButton('Entertainment')
    btn4 = types.KeyboardButton('Other')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, 'Choose a category to add an expense!', reply_markup=markup)
    bot.register_next_step_handler(message, add_expense)


def add_expense(message):
    category = message.text
    bot.send_message(message.chat.id, 'Enter the amount of the expense:')
    bot.register_next_step_handler(message, lambda msg: validate_and_save_expense(msg, category))


def validate_and_save_expense(message, category):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError('The amount must be positive.')

        currency = user_data[message.chat.id]['currency']
        date = pd.Timestamp.now().strftime('%Y-%m-%d')

        add_expense_to_csv(date, category, amount, currency)
        bot.send_message(message.chat.id,
                         f'You have successfully added an expense in the category: {category} for the amount of: {amount} {currency}.')
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid amount.")
        bot.register_next_step_handler(message, lambda msg: validate_and_save_expense(msg, category))

    show_main_menu(message)


def show_statistics(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Per day')
    btn2 = types.KeyboardButton('Per week')
    btn3 = types.KeyboardButton('Per month')
    btn4 = types.KeyboardButton('Per year')
    btn5 = types.KeyboardButton('Average per month')
    btn6 = types.KeyboardButton('Average per year')
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, 'Choose a period for statistics:', reply_markup=markup)
    bot.register_next_step_handler(message, process_statistics)


def process_statistics(message):
    period = message.text
    df = load_expenses()
    currency = user_data[message.chat.id]['currency']

    if period == "Per day":
        df = df[(df['date'] == pd.Timestamp.now().strftime('%Y-%m-%d')) & (df['currency'] == currency)]
    elif period == "Per week":
        df = df[(df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d')) & (
                df['currency'] == currency)]
    elif period == "Per month":
        df = df[(df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime('%Y-%m-%d')) & (
                df['currency'] == currency)]
    elif period == "Per year":
        df = df[(df['date'] >= (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime('%Y-%m-%d')) & (
                df['currency'] == currency)]
    elif period == "Average per month":
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            df = df[df['currency'] == currency].groupby('month')['amount'].mean().reset_index()
            df['month'] = df['month'].astype(str)  # Convert periods to string for plotting
    elif period == "Average per year":
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            df = df[df['currency'] == currency].groupby('year')['amount'].mean().reset_index()

    if not df.empty:

        formatted_data = '\n'.join(
            [f"Date: {row['date']}\nCategory: {row['category']}\nAmount: {row['amount']} {row['currency']}\n" for _, row
             in df.iterrows()]) if 'date' in df.columns else ''
        bot.send_message(message.chat.id, f"Statistics for {period}:\n\n{formatted_data}")

        df['amount'] = df['amount'].astype(float)
        fig, ax = plt.subplots()
        if period in ["Average per month", "Average per year"]:
            df.plot(kind='bar', x=df.columns[0], y='amount', ax=ax)
        else:
            df.groupby('category')['amount'].sum().plot(kind='bar', ax=ax)
        ax.set_title(f'Expenses for {period}')
        ax.set_ylabel('Amount')
        ax.set_xlabel('Categories')
        plt.savefig('expense_chart.png')

        with open('expense_chart.png', 'rb') as chart:
            bot.send_photo(message.chat.id, chart)
    else:
        bot.send_message(message.chat.id, f"No data for the period: {period}.")

    show_main_menu(message)


initialize_csv()
bot.polling()
