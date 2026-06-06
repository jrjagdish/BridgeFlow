from apscheduler.schedulers.background import BackgroundScheduler
from config import get_sync_interval
from debug import logger

scheduler = BackgroundScheduler()

def start_scheduler():
    from sync import run_sync
    interval = get_sync_interval()
    scheduler.add_job(
        run_sync,
        'interval',
        minutes = interval,
        id = 'sync_job',
        replace_existing = True
    )
    scheduler.start()
    logger.info("----Scheduler Started----")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("---Scheduler Stopped---")
