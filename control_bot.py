from javascript import require, On, Once, AsyncTask, once, off
from smart_bot import SmartBot
import threading
import neat
import neat.config
import os
import pickle
import random
import string
import json
import numpy as np
import time

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

        self.unique_list_path = "unique_list.npy"
        if (os.path.exists(self.unique_list_path)):
            self.unique_list = np.load(self.unique_list_path).tolist()
        else:
            self.unique_list = []

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
                    
                    thread = threading.Thread(target=self.random_all, name="RandomAll", args=[200])
                    thread.start()

                elif "neat" in message:
                    thread = threading.Thread(target=self.start_neat, name="StartNeat")
                    thread.start()

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
            bot_name = self.generate_bot_unique()
            created_bot = SmartBot(bot_name, self.server_host, self.server_port)
            self.bot_list.append(created_bot)

    # Random action for all bots
    def random_all(self, steps):

        # Wait for all bots to be ready before executing any actions
        while (self.count_ready() < len(self.bot_list)):
            # asyncio.sleep(0.01)
            pass

        
        for step in range(steps):
            for bot_intance in self.bot_list:
                bot_intance.random_action()
            self.bot.waitForTicks(1)

    def count_ready(self, bot_list):
        count = 0
        for bot_intance in bot_list:
            if (bot_intance.bot_ready):
                count += 1

        return count
    
    def generate_unique(self, length=5):

        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        # unique = ""
        # characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        # for _ in range(length):
        #     unique += characters

    def generate_bot_unique(self, length=5):

        bot_unique = self.generate_unique(length)

        while (bot_unique in self.unique_list):
                bot_unique = self.generate_unique(5)
        self.unique_list.append(bot_unique)

        np.save(self.unique_list_path, self.unique_list)

        return bot_unique

    def eval_genomes(self, genomes, config):

        max_steps = 20
        population_list = []

        gen_unique = self.generate_bot_unique()
        for i, (genome_id, genome) in enumerate(genomes):
            bot_name = f"GEN{self.gen}ID{genome_id}_{gen_unique}"
            bot_instance = SmartBot(bot_name, self.server_host, self.server_port, genome)

            @On(bot_instance.bot, "login")
            def login(this):
                bot_socket = bot_instance.bot._client.socket
                print(f"{bot_instance.bot_name} Logged in to {bot_socket.server if bot_socket.server else bot_socket._host}")
                bot_instance.init_bot()

            @On(bot_instance.bot, "respawn")
            def lose(this):
                this.quit()

            @On(bot_instance.bot, "death")
            def on_dead(this):
                bot_instance.is_dead = True
                bot_instance.survive_time = time.time() - self.spawn_time

            # Disconnected from server
            @On(bot_instance.bot, "end")
            def end(this, reason):
                print(f"{self.bot_name} Disconnected: {reason}")

                # Turn off event listeners
                off(bot_instance.bot, "login", login)
                off(bot_instance.bot, "end", end)
                off(bot_instance.bot, "respawn", lose)
                off(bot_instance.bot, "death", on_dead)

            population_list.append(bot_instance)

        # Wait for all bots to be ready before executing any actions
        while (self.count_ready(population_list) < len(population_list)):
            pass

        # Start
        for step in range(max_steps):
            for bot_i in population_list:
                bot_i.brain_action(config)
            self.bot.waitForTicks(1)

        # Finish
        for bot_i in population_list:
            bot_i.set_fitness()

        self.gen += 1

    def run_neat(self, config):
        # p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-39") # load checkpoint
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(2))

        self.gen = 1
        winner = p.run(self.eval_genomes, 5)

        # save the best genome
        with open("best.pickle", "wb") as f:
            pickle.dump(winner, f)

    def start_neat(self):
        # config
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, "config.txt")

        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)

        # Train with NEAT
        self.run_neat(config)