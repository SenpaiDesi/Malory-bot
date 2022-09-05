# Mali bot
# Made by Senpai_Desi#8565
# Date created: 05/09/2022

import argparse
import assets
import uttilities as utilities

dev_mode = True

parser = argparse.ArgumentParser(description="Run bot in live mode.")
parser.add_argument("--live", action="store_true")
args = parser.parse_args()

if args.live:
    dev_mode = False

from datetime import datetime

start_date = datetime.now()
start_date_pretty = start_date.strftime("%d/%m/%Y %H:%M:%S")
print(f"Initiating, start date: {start_date_pretty}\n")


import bot
bot.run(dev_mode)