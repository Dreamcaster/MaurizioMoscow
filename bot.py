import telebot
from telebot import types
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

# --- CONFIGURATION ---
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)
scheduler = BackgroundScheduler()
scheduler.start()

# --- DATABASE SETUP ---
def get_db():
    return sqlite3.connect('fantacalcio.db', check_same_thread=False)

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        credits INTEGER DEFAULT 500)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS auctions (
                        player_name TEXT PRIMARY KEY,
                        current_bid INTEGER,
                        highest_bidder_id INTEGER,
                        highest_bidder_name TEXT,
                        mode TEXT,
                        role TEXT,
                        chat_id INTEGER,
                        end_time DATETIME,
                        previous_bid INTEGER,
                        previous_bidder_id INTEGER,
                        previous_bidder_name TEXT)''')
    db.commit()
    db.close()

init_db()

# --- KEYBOARD MENU ---
def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('💰 Status / Crediti', '⚽ Fai Offerta')
    markup.row('🚀 Inizia Asta', '🎮 Registrati (/join)')
    markup.row('🔨 Chiudi Asta', '⏪ Ritira Offerta')
    return markup

# --- CORE LOGIC ---
def close_auction_logic(player_name, chat_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT current_bid, highest_bidder_id, highest_bidder_name, role FROM auctions WHERE player_name=?", (player_name,))
    row = cursor.fetchone()
    if row:
        bid, user_id, user_name, role = row
        if user_id is None or user_name == "Nessuno":
            bot.send_message(chat_id, f"❌ L'asta per **{player_name.capitalize()}** è chiusa senza offerte.")
        else:
            cursor.execute("SELECT credits FROM users WHERE user_id=?", (user_id,))
            user_res = cursor.fetchone()
            if user_res and user_res[0] >= bid:
                cursor.execute("UPDATE users SET credits = credits - ? WHERE user_id = ?", (bid, user_id))
                bot.send_message(chat_id, f"🔨 **VENDUTO!**\n⚽ {player_name.upper()} ({role})\n👤 Vincitore: {user_name}\n💰 Prezzo: {bid} crediti", reply_markup=main_menu_keyboard())
            else:
                bot.send_message(chat_id, f"⚠️ {user_name} non ha crediti sufficienti per chiudere l'acquisto!")
        cursor.execute("DELETE FROM auctions WHERE player_name = ?", (player_name,))
        db.commit()
    db.close()

# --- COMMANDS ---
@bot.message_handler(commands=['join'])
def join_game(message):
    db = get_db()
    cursor = db.cursor()
    user_id = message.from_user.id
    username = message.from_user.first_name
    cursor.execute("SELECT credits FROM users WHERE user_id=?", (user_id,))
    res = cursor.fetchone()
    if res:
        bot.reply_to(message, f"✅ Sei già registrato!\n💰 Budget: {res[0]}", reply_markup=main_menu_keyboard())
    else:
        cursor.execute("INSERT INTO users (user_id, username, credits) VALUES (?, ?, ?)", (user_id, username, 500))
        db.commit()
        bot.reply_to(message, f"🎮 Benvenuto {username}! Ti sono stati assegnati 500 crediti.", reply_markup=main_menu_keyboard())
    db.close()

@bot.message_handler(commands=['status'])
def show_status(message):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT player_name, current_bid, highest_bidder_name, role FROM auctions")
    auctions = cursor.fetchall()
    cursor.execute("SELECT username, credits FROM users ORDER BY credits DESC")
    users = cursor.fetchall()
    db.close()
    response = "📊 **SITUAZIONE ATTUALE**\n\n"
    if auctions:
        for a in auctions:
            response += f"• **{a[0].capitalize()}** ({a[3]})\n  💰 Ultima offerta: {a[1]} ({a[2]})\n\n"
    else: response += "📭 Nessuna asta attiva al momento.\n\n"
    response += "💰 **CREDITI RESIDUI:**\n" + "\n".join([f"• {u[0]}: {u[1]}" for u in users])
    bot.send_message(message.chat.id, response, parse_mode="Markdown", reply_markup=main_menu_keyboard())

# --- AUCTION START FLOW ---
@bot.message_handler(commands=['start_asta'])
def start_asta_step1(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Live (30s)', 'Delayed (24h)')
    msg = bot.reply_to(message, "⏳ Che tipo di asta vuoi iniziare?", reply_markup=markup)
    bot.register_next_step_handler(msg, start_asta_step2)

def start_asta_step2(message):
    mode = "live" if "Live" in message.text else "delayed"
    msg = bot.reply_to(message, "📝 Inserisci il NOME del calciatore:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, start_asta_step3, mode)

def start_asta_step3(message, mode):
    player_name = message.text.lower()
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Portiere', 'Difensore', 'Centrocampista', 'Attaccante')
    msg = bot.reply_to(message, f"Ruolo di **{player_name.capitalize()}**?", reply_markup=markup)
    bot.register_next_step_handler(msg, start_asta_step4, mode, player_name)

def start_asta_step4(message, mode, player_name):
    role = message.text.capitalize()
    msg = bot.reply_to(message, f"💰 Prezzo base per {player_name.capitalize()}?", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, start_asta_final, mode, player_name, role)

def start_asta_final(message, mode, player_name, role):
    try:
        base_price = int(message.text.strip())
        end_time = datetime.now() + (timedelta(seconds=30) if mode == "live" else timedelta(hours=24))
        db = get_db(); cursor = db.cursor()
        cursor.execute("INSERT INTO auctions (player_name, current_bid, highest_bidder_name, mode, role, chat_id, end_time) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (player_name, base_price, "Nessuno", mode, role, message.chat.id, end_time))
        db.commit(); db.close()
        scheduler.add_job(close_auction_logic, 'date', run_date=end_time, args=[player_name, message.chat.id], id=player_name)
        bot.send_message(message.chat.id, f"🚀 **ASTA INIZIATA!**\n⚽ {player_name.upper()} ({role})\n💰 Base: {base_price}", reply_markup=main_menu_keyboard())
    except: bot.reply_to(message, "⚠️ Errore. Riprova /start_asta.")

# --- OFFERTA FLOW ---
@bot.message_handler(commands=['offerta'])
def choose_player_step(message):
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT player_name, current_bid, role FROM auctions")
    rows = cursor.fetchall(); db.close()
    if not rows:
        bot.reply_to(message, "📭 Nessuna asta attiva.", reply_markup=main_menu_keyboard())
        return
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for row in rows: markup.add(f"{row[0].capitalize()} ({row[2]})")
    msg = bot.reply_to(message, "Seleziona il calciatore per cui fare l'offerta:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_player_choice)

def process_player_choice(message):
    try:
        player_name = message.text.split(" (")[0].lower()
        msg = bot.reply_to(message, f"Quanto offri per **{player_name.capitalize()}**?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_bid_amount, player_name)
    except: bot.reply_to(message, "⚠️ Errore. Riprova /offerta.")

def process_bid_amount(message, player_name):
    try:
        amount = int(message.text.strip())
        user_id = message.from_user.id
        db = get_db(); cursor = db.cursor()
        
        # Check if user exists
        cursor.execute("SELECT credits FROM users WHERE user_id=?", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            bot.reply_to(message, "❌ Devi prima registrarti con il tasto Registrati!", reply_markup=main_menu_keyboard())
            db.close(); return

        # Get auction data including previous bidder columns
        cursor.execute("""SELECT current_bid, highest_bidder_id, highest_bidder_name, chat_id 
                          FROM auctions WHERE player_name=?""", (player_name,))
        auction = cursor.fetchone()
        
        if auction:
            curr_price, old_id, old_name, chat_id = auction
            if amount > curr_price and amount <= user_data[0]:
                cursor.execute("""UPDATE auctions SET 
                                  current_bid=?, highest_bidder_id=?, highest_bidder_name=?, 
                                  previous_bid=?, previous_bidder_id=?, previous_bidder_name=? 
                                  WHERE player_name=?""", 
                               (amount, user_id, message.from_user.first_name, curr_price, old_id, old_name, player_name))
                db.commit()
                bot.send_message(chat_id, f"🔥 **RILANCIO!**\n⚽ {player_name.capitalize()}\n💰 {amount} crediti da {message.from_user.first_name}!", reply_markup=main_menu_keyboard())
            else:
                bot.reply_to(message, f"❌ Offerta non valida (troppo bassa o crediti insufficienti). Budget: {user_data[0]}", reply_markup=main_menu_keyboard())
        db.close()
    except: bot.reply_to(message, "⚠️ Inserisci un numero valido.")

# --- ADMIN / UTILITY FLOWS ---
@bot.message_handler(commands=['chiudi_forzato'])
def force_close_step1(message, ask=False):
    parts = message.text.split()
    if not ask and len(parts) >= 2 and not parts[1].startswith('@'):
        process_force_close(message, parts[1].lower())
    else:
        msg = bot.reply_to(message, "🔨 Digita il NOME del calciatore da chiudere:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, lambda m: process_force_close(m, m.text.strip().lower()))

def process_force_close(message, player_name):
    if player_name.startswith('/'):
        bot.reply_to(message, "❌ Annullato.", reply_markup=main_menu_keyboard()); return
    db = get_db(); cursor = db.cursor()
    cursor.execute("SELECT chat_id FROM auctions WHERE player_name=?", (player_name,))
    row = cursor.fetchone()
    if row:
        try: scheduler.remove_job(player_name)
        except: pass
        close_auction_logic(player_name, row[0])
        bot.reply_to(message, f"✅ Asta {player_name.capitalize()} chiusa.", reply_markup=main_menu_keyboard())
    else: bot.reply_to(message, "❌ Asta non trovata.", reply_markup=main_menu_keyboard())
    db.close()

@bot.message_handler(commands=['ritira'])
def withdraw_step1(message, ask=False):
    parts = message.text.split()
    if not ask and len(parts) >= 2 and not parts[1].startswith('@'):
        process_withdraw(message, parts[1].lower())
    else:
        msg = bot.reply_to(message, "⏪ Per quale calciatore vuoi ritirare?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, lambda m: process_withdraw(m, m.text.strip().lower()))

def process_withdraw(message, player_name):
    if player_name.startswith('/'):
        bot.reply_to(message, "❌ Operazione annullata.", reply_markup=main_menu_keyboard())
        return

    db = get_db()
    cursor = db.cursor()
    # We select EVERYTHING including the previous bid and the base price info
    cursor.execute("""SELECT current_bid, highest_bidder_id, previous_bid, 
                      previous_bidder_id, previous_bidder_name 
                      FROM auctions WHERE player_name=?""", (player_name,))
    row = cursor.fetchone()
    
    if row:
        curr_bid, curr_bidder, prev_bid, prev_id, prev_name = row
        
        # Check if the person trying to withdraw is actually the leader
        if message.from_user.id == curr_bidder:
            if prev_id and prev_name != "Nessuno":
                # SCENARIO: There was someone before you.
                # Roll back the price AND the bidder to the previous state.
                cursor.execute("""UPDATE auctions SET 
                                  current_bid=?, 
                                  highest_bidder_id=?, 
                                  highest_bidder_name=?, 
                                  previous_bid=NULL, 
                                  previous_bidder_id=NULL, 
                                  previous_bidder_name=NULL 
                                  WHERE player_name=?""", 
                               (prev_bid, prev_id, prev_name, player_name))
                bot.reply_to(message, f"⏪ Offerta ritirata! **{prev_name}** torna in testa con **{prev_bid}**.", reply_markup=main_menu_keyboard())
            else:
                # SCENARIO: You were the ONLY bidder.
                # We revert the bidder to Nessuno, but what about the price?
                # Usually, 'previous_bid' for the first bidder is the BASE price.
                new_price = prev_bid if prev_bid is not None else curr_bid
                
                cursor.execute("""UPDATE auctions SET 
                                  current_bid=?,
                                  highest_bidder_id=NULL, 
                                  highest_bidder_name='Nessuno', 
                                  previous_bid=NULL 
                                  WHERE player_name=?""", (new_price, player_name))
                bot.reply_to(message, f"⏪ Offerta annullata. **{player_name.capitalize()}** torna al prezzo base di {new_price} senza offerte.", reply_markup=main_menu_keyboard())
            
            db.commit()
        else:
            bot.reply_to(message, "❌ Puoi ritirare solo se sei l'attuale miglior offerente!")
    else:
        bot.reply_to(message, f"❌ Asta per '{player_name}' non trovata.")
    db.close()
@bot.message_handler(commands=['set_crediti'])
def set_credits_cmd(message):
    try:
        args = message.text.split()
        db = get_db(); cursor = db.cursor()
        cursor.execute("UPDATE users SET credits = ? WHERE username = ?", (int(args[2]), args[1]))
        db.commit(); db.close()
        bot.reply_to(message, f"✅ Budget {args[1]} aggiornato.", reply_markup=main_menu_keyboard())
    except: bot.reply_to(message, "Usa: /set_crediti Nome 500")

# --- MAIN HANDLER ---
@bot.message_handler(func=lambda message: True)
def handle_menu_buttons(message):
    text = message.text.strip()
    if text == '💰 Status / Crediti': show_status(message)
    elif text == '⚽ Fai Offerta': choose_player_step(message)
    elif text == '🚀 Inizia Asta': start_asta_step1(message)
    elif text == '🎮 Registrati (/join)': join_game(message)
    elif 'Chiudi Asta' in text: force_close_step1(message, ask=True)
    elif 'Ritira Offerta' in text: withdraw_step1(message, ask=True)

print("Bot is running...")
bot.infinity_polling()