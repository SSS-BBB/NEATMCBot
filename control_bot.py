from javascript import require, On, Once, AsyncTask, once, off

mineflayer = require("mineflayer")

class ControlBot:

    def __init__(self, bot_name, server_host, server_port):
        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False
        }
        self.bot_name = bot_name
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
            if messagePosition == "chat" and "quit" in message:
                this.quit()

        # Disconnected from server
        @On(self.bot, "end")
        def end(this, reason):
            print(f"{self.bot_name} Disconnected: {reason}")

            # Turn off event listeners
            off(self.bot, "login", login)
            off(self.bot, "end", end)
            off(self.bot, "messagestr", messagestr)