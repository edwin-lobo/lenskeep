import os
import json
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from scraper.scrape_vsco import scrape_vsco

STATE_FILE = "state/last_run.json"
INTERVAL_MINUTES = 30

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lenskeep.scheduler")


def get_last_run():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
        return datetime.fromisoformat(data.get("last_run"))


def save_last_run():
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_run": datetime.now().isoformat()}, f)


def should_run():
    last_run = get_last_run()
    if not last_run:
        return True
    return datetime.now() - last_run >= timedelta(minutes=INTERVAL_MINUTES)


def run_job():
    username = os.getenv("VSCO_USER", "example_user")

    if not should_run():
        logger.info("Skipping run: within cooldown window.")
        return

    logger.info(f"Running scrape job for {username}")
    scrape_vsco(username)
    save_last_run()
    logger.info("Scrape completed and state updated.")


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_job, "interval", minutes=INTERVAL_MINUTES)
    scheduler.start()

    logger.info("Scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
