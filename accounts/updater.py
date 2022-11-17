from apscheduler.schedulers.background import BackgroundScheduler
from .views import send_24_hr_delay_email


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_24_hr_delay_email, 'interval', seconds=21600)#21600 sceonds = 6 hours
    scheduler.start()