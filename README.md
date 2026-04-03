{\rtf1\ansi\ansicpg1252\cocoartf2867
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww29200\viewh17740\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # \uc0\u9917  Fantacalcio Auction Bot (Telegram)\
\
A robust Telegram bot designed to manage **Fantacalcio (Italian Fantasy Football) auctions** in real-time. It supports both "Live" (fast-paced) and "Delayed" (24-hour) auction modes, manages user budgets, and includes a full GUI via Telegram Reply Keyboards.\
\
## \uc0\u55357 \u56960  Features\
\
* **Dual Auction Modes:** * `Live`: Quick 30-second auctions for real-time gatherings.\
    * `Delayed`: 24-hour auctions for remote leagues.\
* **Budget Management:** Automatically deducts credits from winners and prevents overspending.\
* **Smart "Withdraw" Logic:** Allows users to revert their last bid, automatically rolling back the price and restoring the previous bidder.\
* **Admin Tools:** Forced closure of auctions and manual credit overrides.\
* **Mobile-Friendly GUI:** Custom keyboards to reduce typing and prevent syntax errors on mobile devices.\
* **Persistence:** Uses SQLite to ensure data survives bot restarts.\
\
## \uc0\u55357 \u57056  Tech Stack\
\
* **Language:** Python 3.x\
* **Library:** `pyTelegramBotAPI` (telebot)\
* **Scheduler:** `APScheduler` (handles auction timers)\
* **Database:** `SQLite3`\
\
## \uc0\u55357 \u56523  Prerequisites\
\
1.  Python 3.8+ installed.\
2.  A Telegram Bot Token from [@BotFather](https://t.me/botfather).\
\
## \uc0\u55357 \u56615  Installation & Setup\
\
1.  **Clone the repository:**\
    ```bash\
    git clone [https://github.com/yourusername/fantacalcio-auction-bot.git](https://github.com/yourusername/fantacalcio-auction-bot.git)\
    cd fantacalcio-auction-bot\
    ```\
\
2.  **Install dependencies:**\
    ```bash\
    pip install pyTelegramBotAPI apscheduler\
    ```\
\
3.  **Configure the Token:**\
    Open `bot.py` and replace the `API_TOKEN` value with your actual Bot Token.\
\
4.  **Run the Bot:**\
    ```bash\
    python3 bot.py\
    ```\
\
## \uc0\u55356 \u57262  How to Use\
\
1.  **Join:** Users click `\uc0\u55356 \u57262  Registrati` to enter the league with a starting budget (default: 500).\
2.  **Start Auction:** Click `\uc0\u55357 \u56960  Inizia Asta`, follow the prompts to enter the player name, role, and base price.\
3.  **Bid:** Click `\uc0\u9917  Fai Offerta`, select an active player, and enter your amount.\
4.  **Status:** Click `\uc0\u55357 \u56496  Status / Crediti` to see all active auctions and the ranking of remaining budgets.\
5.  **Withdraw:** If a mistake is made, click `\uc0\u9194  Ritira Offerta` to roll the auction back to the previous state.\
\
## \uc0\u55357 \u56430  Admin Commands\
\
| Command | Description |\
| :--- | :--- |\
| `/chiudi_forzato [nome]` | Instantly ends an auction and assigns the player. |\
| `/set_crediti [nome] [quantit\'e0]` | Manually updates a user's budget. |\
\
## \uc0\u55357 \u56541  License\
\
This project is open-source and available under the MIT License.}