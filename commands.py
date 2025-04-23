from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler
from datetime import datetime
import db

# Estados da conversa
AMOUNT, CATEGORY, DATE, NOTE = range(4)

categories = [
    "Market", "Occasional Expenses", "Necessity", "Clothing", "Health",
    "Gifts", "Beauty", "Development", "Leisure", "Electronics",
    "Subscription", "Uber/Transport", "iFood/Restaurant", "Rent",
    "Bills", "Investment", "Vacation"
]

async def start_add(update: Update, context: CallbackContext):
    args = context.args
    if args:
        context.user_data['amount'] = args[0]
        return await ask_category(update, context)
    await update.message.reply_text("Por favor, envie o valor da despesa (ex: 12.50).")
    return AMOUNT


async def ask_category(update: Update, context: CallbackContext):
    amt = context.user_data.get('amount')
    try:
        if isinstance(amt, str):
            amt = amt.replace(',', '.')
        context.user_data['amount'] = float(amt)
    except (TypeError, ValueError):
        await update.message.reply_text("Valor inválido. Envie apenas números, ex: 12.50.")
        return AMOUNT

    # Rest of your function remains the same
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=cat)] for cat in categories
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Escolha a categoria:", reply_markup=reply_markup)
    return CATEGORY

async def category_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data['category'] = query.data
    await query.edit_message_text("Por favor, envie a data em YYYY-MM-DD ou /skip para hoje.")
    return DATE

async def date_handler(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if text == '/skip' or not text:
        date = datetime.today().strftime('%Y-%m-%d')
    else:
        try:
            datetime.strptime(text, '%Y-%m-%d')
            date = text
        except ValueError:
            await update.message.reply_text("Formato inválido. Use YYYY-MM-DD ou /skip.")
            return DATE
    context.user_data['date'] = date
    await update.message.reply_text("Por favor, envie uma nota breve sobre a despesa ou /skip para nenhuma.")
    return NOTE

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
        f"✅ Registrado: R${data['amount']} em {data['category']} em {data['date']}. "
        f"Nota: {note or '–'}"
    )
    return ConversationHandler.END

async def report(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        await update.message.reply_text("Use /report YYYY-MM")
        return
    month = args[0]
    try:
        datetime.strptime(month, '%Y-%m')
    except ValueError:
        await update.message.reply_text("Formato inválido. Use YYYY-MM.")
        return
    totals = db.get_monthly_report(update.effective_user.id, month)
    if not totals:
        await update.message.reply_text("Sem despesas neste mês.")
        return
    lines = [f"*{cat}*: R${tot:.2f}" for cat, tot in totals.items()]
    text = f"Relatório {month}:\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode='Markdown')

# Handler de /cancel opcional
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Operação cancelada.")
    return ConversationHandler.END


def get_handlers():
    conv = ConversationHandler(
        entry_points=[CommandHandler('add', start_add)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],  # Call a new handler
            CATEGORY: [CallbackQueryHandler(category_handler)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_handler)],
            NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, note_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    return conv

# Add this new handler
async def amount_handler(update: Update, context: CallbackContext):
    context.user_data['amount'] = update.message.text
    return await ask_category(update, context)