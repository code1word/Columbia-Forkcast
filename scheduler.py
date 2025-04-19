from apscheduler.schedulers.blocking import BlockingScheduler
from scraper import scrape_website
from database import init_db
import datetime
import logging

# Initialize logging
# logging.basicConfig(
#     filename="scheduler.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
# )


scheduler = BlockingScheduler()

def update_dining_data():
  """Scrapes dining hall data every hour and updates the database."""
  # Re-initialize the database
  init_db()
  
  # logging.info("Starting dining hall data scrape...")
  dining_data = scrape_website("https://dining.columbia.edu")
  
  if dining_data:
    print(f"Dining hall data updated successfully at {datetime.datetime.now()}")
  else:
    print("No dining data was scraped.")
  

def hello():
  print("hello")

scheduler.add_job(update_dining_data, "interval", hours=1)
scheduler.start()