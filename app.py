from flask import Flask, jsonify, render_template, request
from database import init_db, connect_db, get_all_menu_data
from scraper import scrape_website
import json
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
init_db()


@app.route("/")
def home():
  return render_template("index.html")


@app.route("/api/dining-halls", methods=["GET"])
def get_dining_halls():
  conn = connect_db()
  cursor = conn.cursor()
  cursor.execute("SELECT name, status, hours, type, menu_url FROM dining_halls")
  dining_halls = [
      {"name": row[0], "status": row[1], "hours": row[2], "type": row[3], "menu_url": row[4]}
      for row in cursor.fetchall()
  ]
  conn.close()
  return jsonify(dining_halls)


@app.route("/api/menu", methods=["GET"])
def get_menu():
    location_name = request.args.get("name")
    if not location_name:
        return jsonify({"error": "Missing location name"}), 400

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT meal_time, menu_items FROM menus WHERE location_name = ?",
        (location_name,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"meal_time": row[0], "menu_items": json.loads(row[1])})
    else:
        return jsonify({"error": "Menu not found"}), 404


@app.route("/api/ask", methods=["POST"])
def ask_ai():
    data = request.json
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query cannot be empty"}), 400

    # Retrieve context
    menu_context = get_all_menu_data()
    full_prompt = f"""You are a helpful assistant answering questions about Columbia University's dining halls and their current offerings.

    Below is today's real-time menu information and hours:

    {menu_context}

    Now, answer the user's question below clearly and directly:
    "{user_query}"

    Avoid repeating the full menu unless explicitly asked. Use natural language and be very friendly, don't indicate that you've been given context, and use plaintext without formatting.
    If a portion of the response is bullet points, remember to rephrase those bullet points into a sentence!
    One note is that if it says that JJ's Place is open from 12:00PM - 10:00AM, that means it is open 22 hours a day (before 10:00AM and after 12:00PM).

    The current time is {datetime.now().strftime("%I:%M %p")}.
    """
    try:
        client = OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about Columbia University's dining halls and menus."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        print("OpenAI API error:", e)
        return jsonify({"error": "Failed to get a response from AI."}), 500


@app.route("/api/refresh", methods=["POST"])
def refresh_dining_data():
    try:
        init_db()
        scrape_website("https://dining.columbia.edu")
        return jsonify({"message": "Data refreshed successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
  app.run(debug=True)