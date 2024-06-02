from javascript import require, On, Once, AsyncTask, once, off
import random
import time

mineflayer = require("mineflayer")

class SmartBot:

    def __init__(self, bot_name, server_host, server_port):
        self.bot_args = {
            "host": server_host,
            "port": server_port,
            "username": bot_name,
            "hideErrors": False
        }
        self.bot_name = bot_name
        self.actionSize = 8
        self.bot_ready = False
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
            self.init_bot()


        # Chat event
        @On(self.bot, "messagestr")
        def messagestr(this, message, messagePosition, jsonMsg, sender, verified=None):
            if messagePosition == "chat" and "quit" in message:
                this.quit()

        @On(self.bot, "respawn")
        def lose(this):
            this.quit()

        # Disconnected from server
        @On(self.bot, "end")
        def end(this, reason):
            print(f"{self.bot_name} Disconnected: {reason}")

            # Turn off event listeners
            off(self.bot, "login", login)
            off(self.bot, "end", end)
            off(self.bot, "messagestr", messagestr)
            off(self.bot, "respawn", lose)

    def init_bot(self):
        randX = random.randrange(-209, -203)
        randZ = random.randrange(177, 183)

        self.bot.chat(f"/tp {self.bot_name} {randX} -60 {randZ}")

        self.spawn_time = time.time()

        self.bot_ready = True

    def get_observations(self):
        if (not self.bot or not self.bot.entity):
            return
        

        # Find nearest bot or player
        nearest_entity = self.bot.nearestEntity(lambda e: "ID" in e.name or
            e.type == "player" or
            e.type == "hostile" )

        # [ myPos, otherPos, myHealth ]
        if (not nearest_entity):
            return [
                self.bot.entity.position.x,
                self.bot.entity.position.y,
                self.bot.entity.position.z,

                0,
                0,
                0,

                self.bot.health
            ]
        

        return [ 
            self.bot.entity.position.x,
            self.bot.entity.position.y,
            self.bot.entity.position.z,

            nearest_entity.position.x,
            nearest_entity.position.y,
            nearest_entity.position.z,

            self.bot.health
        ]

    # Bot takes some action
    def bot_action(self, action_id):
        if (not self.bot or not self.bot.entity):
            return

        # 0 -> forward, 1 -> back, 2 -> left, 3 -> right, 4 -> jump, 5 -> sprint, 6 -> sneak, 7 -> hit
        if (action_id + 1 > self.actionSize):
            self.bot.chat(f"No {action_id} action.")
            return
        
        # Reset Control State
        control_state_list = ["forward", "back", "left", "right", "jump", "sprint", "sneak"]
        for control in control_state_list:
            self.bot.setControlState(control, False)

        # Action
        if (action_id < 7):
            self.bot.setControlState(control_state_list[action_id], True)
        else:
            # Hit
            # Find nearest bot or player
            nearest_entity = self.bot.nearestEntity(lambda e: "ID" in e.name or
            e.type == "player" or
            e.type == "hostile" )
            
            if (nearest_entity):
                self.bot.lookAt(nearest_entity.position.offset(0, nearest_entity.height, 0))
                self.bot.attack(nearest_entity)

    def random_action(self):
        rand_action = random.randrange(0, self.actionSize)
        self.bot_action(rand_action)