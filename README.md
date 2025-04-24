# Telegram Expense Bot

A simple Telegram bot for tracking expenses and generating monthly reports.

## Project Overview

This bot allows users to:
- Track daily expenses with categories and notes
- View monthly expense reports by category
- Undo recent expense entries

## 1. Creating a Telegram Bot with BotFather

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot` command
3. Follow the prompts to set your bot's display name
4. Choose a username ending with "bot" (e.g., `my_expense_tracker_bot`)
5. BotFather will respond with a token like `123456789:ABCdefGhIjKlmNOpQrsTUVwxyz`
6. Save this token - it's required to authenticate your bot

## 2. Project Components

- **bot.py**: Main entry point that initializes the bot and adds command handlers
- **commands.py**: Implements conversation handlers for all bot interactions
- **db.py**: Database interface for storing and retrieving expense data
- **Dockerfile/docker-compose.yml**: Containerization configuration

## 3. Features

### `/add [amount]`
Starts the expense recording flow:
1. Amount (e.g., 12.50)
2. Category (via inline keyboard)
3. Date (today or custom date)
4. Optional note

### `/report`
Shows total expenses by category

### `/undo`
Deletes the most recent expense entry

### `/cancel`
Cancels the current conversation

## 4. Installation

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Telegram bot token

### Option 1: Local Installation

1. Clone the repository and navigate to the project folder
```cli
git clone https://github.com/username/expense-bot.git cd expense-bot
```

2. Create a virtual environment
```cli
python -m venv venv source venv/bin/activate # Linux/macOS 
venv\Scripts\activate # Windows
```

3. Install dependencies
```cli
pip install -r requirements.txt
```

4. Set environment variables
```cli
export TELEGRAM_TOKEN="your_bot_token" 
export DATABASE_URL="postgresql://user:password@localhost:5432/expenses"
```

5. Run the bot
```cli
python bot.py
```

### Option 2: Using Docker
1. Edit `docker-compose.yml` to set your Telegram token

2. Start the services
```cli
docker-compose up -d
```

## 5. Database Structure

The application uses PostgreSQL to store expense data with a simple schema:
- `expenses` table: Stores all expense records with user ID, amount, category, date, and optional note

## 6. Technical Implementation

- **Conversation Handlers**: Uses python-telegram-bot's ConversationHandler to manage multi-step interactions
- **Connection Pooling**: Implements database connection pooling for efficient resource usage
- **Docker Compose**: Includes PostgreSQL and pgweb (database admin tool) containers

The pgweb interface is accessible at http://localhost:8081 when running with Docker.