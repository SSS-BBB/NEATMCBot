from javascript import require, On, Once, AsyncTask, once, off
from smart_bot import SmartBot
from control_bot import ControlBot

mineflayer = require("mineflayer")

SERVER_HOST = "localhost"
SERVER_PORT = 53823

if __name__ == "__main__":
    ControlBot("Control_Bot", SERVER_HOST, SERVER_PORT)