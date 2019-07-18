import schedule
import bot_upd
import time

schedule.every().day.at("21:00").do(bot_upd.notify)

while True:
    schedule.run_pending()
    time.sleep(1)