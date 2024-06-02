from javascript import require, On, Once, AsyncTask, once, off
from smart_bot import SmartBot
from control_bot import ControlBot

mineflayer = require("mineflayer")

SERVER_HOST = "localhost"
SERVER_PORT = 49931

if __name__ == "__main__":
    # test_bot = SmartBot("Test_1", SERVER_HOST, SERVER_PORT)
    control_bot = ControlBot("Control_Bot", SERVER_HOST, SERVER_PORT)