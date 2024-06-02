from javascript import require, On, Once, AsyncTask, once, off
from smart_bot import SmartBot
import asyncio

mineflayer = require("mineflayer")

class ControlBot:

    def __init__(self, bot_name, server_host, server_port, target_bot: SmartBot=None):
        self.server_host = server_host
        self.server_port = server_port

        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False
        }

        self.bot_name = bot_name
        self.target_bot = target_bot
        self.bot_list = []

        self.start_bot()

    def start_bot(self):
        self.bot = mineflayer.createBot(self.bot_args)

        self.start_event()

    # Attach mineflayer events to bot
    def start_event(self):
        
        @On(self.bot, "login")
        def login(this):
            bot_socket = self.bot._client.socket
            print(f"{self.bot_name} Logged in to {bot_socket.server if bot_socket.server else bot_socket._host}")

        # Chat event
        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat":

                if "quit" in message:
                    this.quit()

                elif "action" in message and self.target_bot:
                    action_id = int(message.split(" ")[2])
                    self.target_bot.bot_action(action_id)

                elif "observe" in message and self.target_bot:
                    for obs in self.target_bot.get_observations():
                        self.bot.chat(str(obs))

                elif "random" in message and self.target_bot:
                    self.target_bot.random_action()

                elif "fight" in message:
                    self.create_bots(5)
                    self.random_all()

        # Disconnected from server
        @On(self.bot, "end")
        def end(this, reason):
            print(f"{self.bot_name} Disconnected: {reason}")

            # Turn off event listeners
            off(self.bot, "login", login)
            off(self.bot, "end", end)
            off(self.bot, "messagestr", messagestr)

    def create_bots(self, amount):
        self.bot.chat(f"Creating {amount} bots...")
        for i in range(amount):
            created_bot = SmartBot(f"Create-Test-{i}", self.server_host, self.server_port)
            self.bot_list.append(created_bot)

    # Random action for all bots
    def random_all(self):

        # Wait for all bots to be ready before executing any actions
        while (self.count_ready() < len(self.bot_list)):
            pass


        for bot_intance in self.bot_list:
            bot_intance.random_action()

    def count_ready(self):
        count = 0
        for bot_intance in self.bot_list:
            if (bot_intance.bot_ready):
                count += 1

        return count