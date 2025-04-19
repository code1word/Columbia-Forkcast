import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from database import connect_db
import time
import json

BASE_URL = "https://dining.columbia.edu"
DB_FILE = "dining_halls.db"


def scrape_website(website):
  chrome_driver_path = "./chromedriver.exe"
  options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

  try:
    driver.get(website)
    print("Page loaded...")
    html = driver.page_source
    dining_data = scrape_dining_data(html)
  finally:
    driver.quit()
  
  if dining_data:
    store_dining_halls(dining_data)
    for hall in dining_data:
      if hall["status"] != "Closed":
        active_meal, menu_data = get_current_menu(hall["menu_url"])
        if menu_data:
          store_menu_in_db(hall["name"], active_meal, menu_data)
    return dining_data
  else:
    raise Exception("No dining data scraped")


def scrape_dining_data(html):
  soup = BeautifulSoup(html, "html.parser")
  dining_halls = []

  open_wrapper = soup.find("div", class_="row open-dining-wrapper")
  if open_wrapper:
    dining_halls += extract_dining_halls(open_wrapper, default_status="Open/Closing Soon")

  closed_wrapper = soup.find("div", class_="row closed-dining-wrapper")
  if closed_wrapper:
    dining_halls += extract_dining_halls(closed_wrapper, default_status="Closed")
  
  return dining_halls


def extract_dining_halls(wrapper, default_status):
  """Extracts dining hall data from a specific wrapper (open/closing soon/closed)."""
  dining_halls = []

  for section in wrapper.find_all("div"):
    # Determine if this section is "Dining Halls" or "Retail Cafes"
    header = section.find("h5", class_="location")
    if not header:
      continue  # Skip sections without a valid header

    section_type = header.text.strip()[:-2]  # Dining Halls or Retail Cafes

    for hall in section.find_all("div", class_="location"):
      name_tag = hall.find("a")
      if not name_tag:
        continue  # Skip if no name found

      name = name_tag.text.strip()
      hours_tag = hall.find("span", class_="open-time")
      status_tag = hall.find("span", class_="status")

      # Extract hours (if available)
      hours = hours_tag.text.strip() if hours_tag else "N/A"

      # Determine status based on class
      status = default_status
      if status_tag:
        status_class = status_tag.get("class", [])
        if "open" in status_class:
          status = "Open"
        elif "closing" in status_class:
          status = "Closing Soon"
        elif "closed" in status_class:
          status = "Closed"

      # Extract menu link
      relative_link = name_tag["href"]
      menu_url = BASE_URL + relative_link if relative_link.startswith("/") else relative_link

      dining_halls.append({
        "name": name,
        "hours": hours,
        "status": status,
        "type": section_type,
        "menu_url": menu_url
      })

  return dining_halls


def store_dining_halls(dining_data):
  with connect_db() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dining_halls")
    for hall in dining_data:
      cursor.execute("""
        INSERT INTO dining_halls (name, status, hours, type, menu_url)
        VALUES (?, ?, ?, ?, ?)""",
        (hall["name"], hall["status"], hall["hours"], hall["type"], hall["menu_url"])  
      )
    conn.commit()


def scrape_menu_page(menu_url):
  chrome_driver_path = "./chromedriver.exe"
  options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

  try:
    driver.get(menu_url)
    print(f"Menu page {menu_url} loaded...")
    # time.sleep(3)
    html = driver.page_source
  finally:
    driver.quit()
  
  return html


def get_active_meal(html):
  soup = BeautifulSoup(html, "html.parser")
  menu_tabs = soup.find("div", class_="cu-dining-menu-tabs")

  if not menu_tabs:
    return "N/A"

  active_tab = menu_tabs.find("button", class_="active")
  return active_tab.text.strip() if active_tab else "N/A"


def extract_menu_items(html):
  soup = BeautifulSoup(html, "html.parser")

  active_meal = get_active_meal(html)
  
  menu_items = []
  menu_sections = soup.find_all("div", class_="menus")

  for section in menu_sections:
    stations = section.find_all("div", class_="wrapper")

    for station in stations:
      station_name = station.find("h2", class_="station-title").text.strip()
      items = []

      for meal_item in station.find_all("div", class_="meal-item"):
        item_name = meal_item.find("h5", class_="meal-title").text.strip()
        
        prefs_tag = meal_item.find("div", class_="meal-prefs")
        meal_prefs = prefs_tag.text.strip() if prefs_tag else None

        allergens_tag = meal_item.find("div", class_="meal-allergens")
        meal_allergens = allergens_tag.text.strip() if allergens_tag else None  
        
        items.append({
          "name": item_name,
          "preferences": meal_prefs,
          "allergens": meal_allergens
        })
      
      if items:
        menu_items.append({"station": station_name, "items": items})

  return active_meal, menu_items


def get_current_menu(menu_url):
  html = scrape_menu_page(menu_url)
  active_meal, menu_data = extract_menu_items(html)

  if not menu_data:
    return (None, [])
  
  return active_meal, menu_data


def store_menu_in_db(location_name, active_meal, menu_data):
  with connect_db() as conn:
    cursor = conn.cursor()

    menu_json = json.dumps(menu_data)

    cursor.execute("""
      INSERT OR REPLACE INTO menus (location_name, meal_time, menu_items)
      VALUES (?, ?, ?)
    """, (location_name, active_meal, menu_json))

    conn.commit()


if __name__ == "__main__":
  try:
    dining_data = scrape_website(BASE_URL)
    print("Dining hall data updated in the database")
  except Exception as e:
    print(f"Error: {e}")