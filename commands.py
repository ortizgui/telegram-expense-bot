from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import db

AMOUNT, CATEGORY, DATE, NOTE = range(4)
REPORT_MENU, REPORT_CUSTOM = range(100, 102)

categories = [
    "Groceries", "Household", "Occasional Expenses", "Necessity", "Clothing",
    "Health", "Gifts", "Beauty", "Professional Development", "Leisure",
    "Electronics", "Subscription", "Transport", "Dining Out", "Rent",
    "Mortgage", "Bills", "Investment", "Vacation"
]

async def start_add(update: Update, context: CallbackContext):
    args = context.args
    if args:
        context.user_data['amount'] = args[0]
        return await ask_category(update, context)
    await update.message.reply_text("Please enter the expense amount (e.g. 12.50).")
    return AMOUNT


async def ask_category(update: Update, context: CallbackContext):
    amt = context.user_data.get('amount')
    try:
        if isinstance(amt, str):
            amt = amt.replace(',', '.')
        context.user_data['amount'] = float(amt)
    except (TypeError, ValueError):
        await update.message.reply_text("Invalid amount. Please enter numbers only, e.g. 12.50.")
        return AMOUNT

    keyboard = [
        [InlineKeyboardButton(cat, callback_data=cat)] for cat in categories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a category:", reply_markup=reply_markup)
    return CATEGORY


async def category_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data['category'] = query.data

    keyboard = [
        [InlineKeyboardButton("Today", callback_data="date_today")],
        [InlineKeyboardButton("Custom Date", callback_data="date_custom")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select a date:", reply_markup=reply_markup)
    return DATE


async def date_selection_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    choice = query.data

    if choice == "date_today":
        context.user_data['date'] = datetime.today().strftime('%Y-%m-%d')
        await query.edit_message_text("Please enter a brief note about the expense or use /skip for none.")
        return NOTE
    else:
        await query.edit_message_text("Please enter the date in YYYY-MM-DD format:")
        return DATE + 1

async def date_handler(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        datetime.strptime(text, '%Y-%m-%d')
        context.user_data['date'] = text
        await update.message.reply_text("Please enter a brief note about the expense or use /skip for none.")
        return NOTE
    except ValueError:
        await update.message.reply_text("Invalid format. Please use YYYY-MM-DD.")
        return DATE + 1

async def note_handler(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    note = "" if text == '/skip' or not text else text
    data = context.user_data
    db.add_expense(
        user_id=update.effective_user.id,
        amount=data['amount'],
        category=data['category'],
        date=data['date'],
        note=note
    )
    await update.message.reply_text(
        f"✅ Recorded: ${data['amount']} in {data['category']} on {data['date']}. Note: {note or '–'}"
    )
    return ConversationHandler.END


async def report(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        keyboard = [
            [InlineKeyboardButton("Current Month", callback_data="report_current")],
            [InlineKeyboardButton("Last Month", callback_data="report_last")],
            [InlineKeyboardButton("Custom Month", callback_data="report_custom")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Select the report period:", reply_markup=reply_markup)
        return REPORT_MENU

    month = args[0]
    try:
        datetime.strptime(month, '%Y-%m')
    except ValueError:
        await update.message.reply_text("Invalid format. Please use YYYY-MM.")
        return

    await generate_report(update, context, month)


async def report_menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    choice = query.data

    today = date.today()

    if choice == "report_current":
        month = today.strftime('%Y-%m')
        await generate_report(update, context, month, is_callback=True)
        return ConversationHandler.END

    elif choice == "report_last":
        last_month = today - relativedelta(months=1)
        month = last_month.strftime('%Y-%m')
        await generate_report(update, context, month, is_callback=True)
        return ConversationHandler.END

    elif choice == "report_custom":
        await query.edit_message_text("Please enter the month in YYYY-MM format:")
        return REPORT_CUSTOM


async def report_custom_handler(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        datetime.strptime(text, '%Y-%m')
        await generate_report(update, context, text)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid format. Please use YYYY-MM.")
        return REPORT_CUSTOM


async def generate_report(update: Update, context: CallbackContext, month, is_callback=False):
    totals = db.get_monthly_report(update.effective_user.id, month)
    if not totals:
        message = f"No expenses in {month}."
    else:
        lines = [f"*{cat}*: R${tot:.2f}" for cat, tot in totals.items()]
        message = f"Report for {month}:\n" + "\n".join(lines)

    if is_callback:
        await update.callback_query.edit_message_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, parse_mode='Markdown')

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


def get_handlers():
    add_conv = ConversationHandler(
        entry_points=[CommandHandler('add', start_add)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],
            CATEGORY: [CallbackQueryHandler(category_handler)],
            DATE: [CallbackQueryHandler(date_selection_handler)],
            DATE + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_handler)],
            NOTE: [
                CommandHandler('skip', skip_note_handler),
                MessageHandler(filters.TEXT & ~filters.COMMAND, note_handler)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    return add_conv

def get_report_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('report', report)],
        states={
            REPORT_MENU: [CallbackQueryHandler(report_menu_handler)],
            REPORT_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_custom_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

async def skip_note_handler(update: Update, context: CallbackContext):
    data = context.user_data
    db.add_expense(
        user_id=update.effective_user.id,
        amount=data['amount'],
        category=data['category'],
        date=data['date'],
        note=""
    )
    await update.message.reply_text(
        f"✅ Recorded: ${data['amount']} in {data['category']} on {data['date']}. Note: '–'"
    )
    return ConversationHandler.END

async def amount_handler(update: Update, context: CallbackContext):
    context.user_data['amount'] = update.message.text
    return await ask_category(update, context)


async def undo(update: Update, context: CallbackContext):
    """Handler for /undo command to delete the user's most recent expense."""
    user_id = update.effective_user.id
    deleted_expense = db.remove_last_expense(user_id)

    if deleted_expense:
        await update.message.reply_text(
            f"✅ Last expense removed:\n"
            f"Amount: R${deleted_expense['amount']:.2f}\n"
            f"Category: {deleted_expense['category']}\n"
            f"Date: {deleted_expense['date']}\n"
            f"Note: {deleted_expense['note'] or '–'}"
        )
    else:
        await update.message.reply_text("No recent expenses found to remove.")