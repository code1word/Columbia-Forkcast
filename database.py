import sqlite3
import json

DB_FILE = "dining_halls.db"


def connect_db():
  return sqlite3.connect(DB_FILE)


def init_db():
  """Initializes the database with necessary tables"""
  with connect_db() as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menus (
      location_name TEXT PRIMARY KEY,
      meal_time TEXT NOT NULL,
      menu_items TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dining_halls (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      status TEXT NOT NULL,
      hours TEXT NOT NULL,
      type TEXT NOT NULL,
      menu_url TEXT NOT NULL
    )
    """)

    conn.commit()


def get_all_menu_data():
    """Return AI-readable summary of all dining hall statuses and menus"""
    with connect_db() as conn:
        cursor = conn.cursor()

        # Fetch dining hall info
        cursor.execute("SELECT name, status, hours, type FROM dining_halls")
        hall_info_map = {
            row[0]: {
                "status": row[1],
                "hours": row[2],
                "type": row[3]
            }
            for row in cursor.fetchall()
        }

        # Fetch menu info
        cursor.execute("SELECT location_name, meal_time, menu_items FROM menus")
        menus = cursor.fetchall()

    if not hall_info_map:
        return "There is no dining hall data currently available."

    output = ["Columbia University Dining Summary:\n"]

    for location, info in hall_info_map.items():
        status = info.get("status", "Unknown")
        hours = info.get("hours", "N/A")
        hall_type = info.get("type", "Dining Hall")

        # Header
        output.append(f"- Location: {location}")
        output.append(f"  Type: {hall_type}")
        output.append(f"  Status: {status}")
        output.append(f"  Hours: {hours}")

        # Closed halls
        if status == "Closed":
            output.append(f"  Menu: (Closed — no items available)\n")
            continue

        # Match and parse menu data
        matched_menus = [m for m in menus if m[0] == location]
        if not matched_menus:
            output.append(f"  Menu: No data available.\n")
            continue

        for _, meal_time, menu_json in matched_menus:
            try:
                menu_items = json.loads(menu_json)
            except json.JSONDecodeError:
                continue

            output.append(f"  Current Meal: {meal_time}")
            for station in menu_items:
                output.append(f"    Station: {station['station']}")
                for item in station["items"]:
                    line = f"      - {item['name']}"
                    if item.get("preferences"):
                        line += f" ({item['preferences']})"
                    if item.get("allergens"):
                        line += f" [Allergens: {item['allergens']}]"
                    output.append(line)
            output.append("")  # Extra line

    return "\n".join(output)


if __name__ == "__main__":
  init_db()
  print("Database initialized")