# ⚽ Fantacalcio Auction Bot (Telegram)

A robust Telegram bot designed to manage **Fantacalcio (Italian Fantasy Football) auctions** in real-time. It supports both "Live" (fast-paced) and "Delayed" (24-hour) auction modes, manages user budgets, and includes a full GUI via Telegram Reply Keyboards.

## 🚀 Features

* **Dual Auction Modes:** * `Live`: Quick 30-second auctions for real-time gatherings.
    * `Delayed`: 24-hour auctions for remote leagues.
* **Budget Management:** Automatically deducts credits from winners and prevents overspending.
* **Smart "Withdraw" Logic:** Allows users to revert their last bid, automatically rolling back the price and restoring the previous bidder.
* **Admin Tools:** Forced closure of auctions and manual credit overrides.
* **Mobile-Friendly GUI:** Custom keyboards to reduce typing and prevent syntax errors on mobile devices.
* **Persistence:** Uses SQLite to ensure data survives bot restarts.

## 🛠 Tech Stack

* **Language:** Python 3.x
* **Library:** `pyTelegramBotAPI` (telebot)
* **Scheduler:** `APScheduler` (handles auction timers)
* **Database:** `SQLite3`

## 📋 Prerequisites

1.  Python 3.8+ installed.
2.  A Telegram Bot Token from [@BotFather](https://t.me/botfather).

## 🔧 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/fantacalcio-auction-bot.git](https://github.com/yourusername/fantacalcio-auction-bot.git)
    cd fantacalcio-auction-bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install pyTelegramBotAPI apscheduler
    ```

3.  **Configure the Token:**
    Open `bot.py` and replace the `API_TOKEN` value with your actual Bot Token.

4.  **Run the Bot:**
    ```bash
    python3 bot.py
    ```

## 🎮 How to Use

1.  **Join:** Users click `🎮 Registrati` to enter the league with a starting budget (default: 500).
2.  **Start Auction:** Click `🚀 Inizia Asta`, follow the prompts to enter the player name, role, and base price.
3.  **Bid:** Click `⚽ Fai Offerta`, select an active player, and enter your amount.
4.  **Status:** Click `💰 Status / Crediti` to see all active auctions and the ranking of remaining budgets.
5.  **Withdraw:** If a mistake is made, click `⏪ Ritira Offerta` to roll the auction back to the previous state.

## 👮 Admin Commands

| Command | Description |
| :--- | :--- |
| `/chiudi_forzato [nome]` | Instantly ends an auction and assigns the player. |
| `/set_crediti [nome] [quantità]` | Manually updates a user's budget. |

## 📝 License

This project is open-source and available under the MIT License
