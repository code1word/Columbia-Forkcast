# COMS W2132 Intermediate Computing in Python, Final Project

## Columbia Forkcast: Dining Hall Live Status Monitor

### Author:

- [Dhruv Yalamanchi](https://github.com/code1word), <dy2444@columbia.edu>

## Project Description

This project automates the process of checking which Columbia dining halls are currently open and displays their real-time menus. Instead of manually navigating Columbia's slow dining website, this tool will scrape and organize all the relevant information in one place. Core features include:

- **Live Dining Hall Status** – View a real-time list of currently open dining halls, with optional filters
- **Dynamic Menu Retrieval** – Click on any dining hall to expand its current offerings for breakfast, lunch, or dinner — all pulled directly from the live menu
- **Automatic and Manual Updates** – Menu data and dining hall availability refresh automatically every 30 minutes. Users can also manually refresh at any time with a single click. A configurable background scheduler is provided in `scheduler.py`, allowing automated scraping and database updates at user-defined intervals
- **AI-Powered Q&A** _(Optional)_ – Ask natural-language questions like "What are the best vegetarian options right now?" and receive context-aware responses powered by OpenAI's GPT. The AI intelligently processes all current menu data to provide relevant answers

This tool will be implemented as a Python-based web scraper with a Flask API and a simple web dashboard for easy access.

## Requirements

The project will require the following software and services:

### **🖥️ Backend (Python)**

- **BeautifulSoup / Selenium** – Used for scraping dining hall hours and live menu data
- **Flask** – Serves real-time dining hall availability and menu data through accessible API routes
- **SQLite** – Lightweight database used to store and quickly access the latest dining data
- **APScheduler** – Schedules automated scraping and database updates every hour (configurable frequency). See `scheduler.py`
- **OpenAI API (GPT-3.5 Turbo)** _(Optional)_ – Integrates an AI-powered Q&A feature that intelligently processes current menu information and answers natural language queries

### **🖼️ Frontend**

- **HTML** – Powers the basic web dashboard for displaying real-time dining hall status and menu data
- **Bootstrap** _(Optional)_ – Provides clean, responsive styling with minimal effort
- **Font Awesome** _(Optional)_ – Adds intuitive icons to enhance user experience and visual clarity
- **JavaScript** _(Optional)_ – Planned for minor interactivity or dynamic enhancements if time permits; the core UI remains simple and mostly static

## Milestones

### Milestone 1: Backend and Web Scraper Core

- Build a web scraper using `BeautifulSoup` (or `Selenium` if needed)
- Extract open/closed status of all dining halls in real time
- Parse current menus for breakfast/lunch/dinner
- Store data in a local `SQLite` database
- Create a Flask API with endpoints like `/refresh`, `/menu`, and `/dining-halls`
- Use `APScheduler` to refresh data hourly

### Milestone 2: Enhanced Web Interface with Bootstrap + JavaScript and AI Q&A Feature

- Build a user-friendly web interface using Flask + HTML + CSS + Bootstrap
- Display real-time dining hall open/closed status using visual badges (e.g., green/red indicators)
- Implement optional filters (e.g., "Dining Hall" vs. "Retail Café" or "Open" vs. "Closing Soon" vs. "Closed")
- Dynamically show current menus for each dining hall using JavaScript (expand/collapse sections)
- Include icons (e.g., meal type, dining hall logos) with Font Awesome
- Integrate OpenAI’s API for an AI-powered Q&A interface based on current menus
- Add a basic prompt input field to ask dining-related questions
- Provide ability for user to manually refresh data

## Requirements

Make sure the following are installed:

**System Requirements**

- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (version matching your Chrome browser) - https://googlechromelabs.github.io/chrome-for-testing/#stable

Note: You should add ChromeDriver to your system PATH, or specify its path in the script.

**Python Dependencies**  
Install all dependencies by running:  
`pip install -r requirements.txt`

This includes:

- Flask
- BeautifulSoup4
- Selenium
- APScheduler
- openai
- python-dotenv

## How to Run

1. Clone the repository and navigate into the project directory.

2. If using the AI feature, create a `.env` file:  
   `OPENAI_API_KEY=your_openai_key_here`

3. Install all dependencies:  
   `pip install -r requirements.txt`

4. Download ChromeDriver:

   - Match your local Chrome version
   - Add it to your system PATH
   - Or update line 13 of `scraper.py` to accordingly (`chrome_driver_path = "YOUR PATH HERE"`)

5. Perform an initial run of the scraper:  
   `python scraper.py`
6. Then start the Flask server:  
   `python app.py`

7. Visit `http://localhost:5000` in your browser.
