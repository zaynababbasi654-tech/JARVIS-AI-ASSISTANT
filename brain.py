import os
import re
import ast
import operator
import sqlite3
from pathlib import Path
from datetime import datetime

import requests
from google import genai


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DB = BASE_DIR / "jarvis_memory.db"


# =========================================================
# GEMINI CONFIG
# =========================================================

def get_gemini_key():
    """
    Get Gemini API key from Streamlit Secrets when running
    on Streamlit Cloud, otherwise from environment variables.
    """

    try:
        import streamlit as st

        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]

    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY")


GEMINI_API_KEY = get_gemini_key()

gemini_client = None

if GEMINI_API_KEY:
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY
    )


MODEL = "gemini-3.6-flash"


# =========================================================
# JARVIS IDENTITY
# =========================================================

CREATOR_NAME = "Zaynab Shakeel Abbasi"

SYSTEM_INSTRUCTION = f"""
You are JARVIS, a helpful personal AI assistant.

Your creator is {CREATOR_NAME}.

Personality:
- Helpful
- Intelligent
- Friendly
- Concise
- Professional when needed
- You may understand Roman Urdu and Urdu
- If the user speaks Roman Urdu, reply naturally in Roman Urdu
- If the user speaks English, reply in English
- Do not claim to perform actions that you cannot actually perform
- Give clear and useful answers
"""


# =========================================================
# DATABASE / MEMORY
# =========================================================

def init_memory():
    try:
        connection = sqlite3.connect(MEMORY_DB)

        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                assistant_response TEXT,
                created_at TEXT
            )
        """)

        connection.commit()
        connection.close()

    except Exception:
        pass


init_memory()


def save_memory(user_message, assistant_response):
    try:
        connection = sqlite3.connect(MEMORY_DB)

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO memories
            (user_message, assistant_response, created_at)
            VALUES (?, ?, ?)
            """,
            (
                user_message,
                assistant_response,
                datetime.now().isoformat()
            )
        )

        connection.commit()
        connection.close()

    except Exception:
        pass


def get_recent_memory(limit=6):
    try:
        connection = sqlite3.connect(MEMORY_DB)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_message, assistant_response
            FROM memories
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        connection.close()

        rows.reverse()

        return rows

    except Exception:
        return []


# =========================================================
# ROMAN URDU DETECTION
# =========================================================

def is_roman_urdu(text):
    roman_words = [
        "hai",
        "hain",
        "ho",
        "kya",
        "kyun",
        "mujhe",
        "mera",
        "meri",
        "ap",
        "aap",
        "tum",
        "kaise",
        "kesay",
        "btao",
        "batao",
        "chahiye",
        "kr",
        "karo",
        "kar",
        "acha",
        "achha",
        "bhai",
        "haan",
        "nahi",
        "nahin"
    ]

    text_lower = text.lower()

    matches = 0

    for word in roman_words:
        if re.search(r"\b" + re.escape(word) + r"\b", text_lower):
            matches += 1

    return matches >= 1


# =========================================================
# DATE / TIME
# =========================================================

def handle_datetime_query(user_message):
    text = user_message.lower()

    date_words = [
        "what is the date",
        "today's date",
        "todays date",
        "date today",
        "aaj ki date",
        "aaj ki tareekh"
    ]

    time_words = [
        "what time",
        "current time",
        "time right now",
        "abhi kitne bajay",
        "abhi kitnay bajy",
        "kitne bajay"
    ]

    now = datetime.now()

    if any(word in text for word in date_words):
        return f"Today's date is {now.strftime('%d %B %Y')}."

    if any(word in text for word in time_words):
        return f"The current time is {now.strftime('%I:%M %p')}."

    return None


# =========================================================
# CREATOR QUERY
# =========================================================

def handle_creator_query(user_message):
    text = user_message.lower()

    creator_patterns = [
        "who created you",
        "who made you",
        "who is your creator",
        "who built you",
        "tumhein kis ne banaya",
        "tumhe kisne banaya",
        "tumhara creator kon hai",
        "tumhara creator kaun hai"
    ]

    if any(pattern in text for pattern in creator_patterns):

        return (
            f"I was created by {CREATOR_NAME}. "
            "I am JARVIS, her personal AI assistant."
        )

    return None


# =========================================================
# SAFE CALCULATOR
# =========================================================

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression):

    expression = expression.replace("^", "**")

    if len(expression) > 100:
        raise ValueError("Expression too long.")

    tree = ast.parse(
        expression,
        mode="eval"
    )

    def evaluate(node):

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Invalid number.")

        if isinstance(node, ast.BinOp):

            operation = ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError("Operator not allowed.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            operation = ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError("Operator not allowed.")

            return operation(
                evaluate(node.operand)
            )

        raise ValueError("Invalid expression.")

    return evaluate(tree.body)


def handle_calculator(user_message):

    text = user_message.lower()

    calculator_words = [
        "calculate",
        "calculator",
        "what is",
        "solve",
        "kitna hoga",
        "hisab"
    ]

    math_pattern = re.search(
        r"[\d\s\+\-\*\/\%\^\(\)\.]+",
        user_message
    )

    if not math_pattern:
        return None

    expression = math_pattern.group().strip()

    if not any(word in text for word in calculator_words):
        return None

    if not re.search(r"\d", expression):
        return None

    try:
        result = safe_calculate(expression)

        return f"The answer is {result}"

    except Exception:
        return None


# =========================================================
# WEATHER
# =========================================================

def get_weather(city):

    try:

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        geo_response = requests.get(
            geo_url,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        geo_data = geo_response.json()

        results = geo_data.get("results")

        if not results:
            return f"I couldn't find weather information for {city}."

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]
        name = location.get("name", city)

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        weather_response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "weather_code"
                ),
                "timezone": "auto"
            },
            timeout=10
        )

        weather_data = weather_response.json()

        current = weather_data.get("current", {})

        temperature = current.get(
            "temperature_2m"
        )

        feels_like = current.get(
            "apparent_temperature"
        )

        humidity = current.get(
            "relative_humidity_2m"
        )

        weather_code = current.get(
            "weather_code"
        )

        descriptions = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "foggy",
            51: "light drizzle",
            53: "drizzle",
            55: "heavy drizzle",
            61: "light rain",
            63: "rain",
            65: "heavy rain",
            71: "light snow",
            73: "snow",
            75: "heavy snow",
            80: "rain showers",
            81: "rain showers",
            82: "heavy rain showers",
            95: "thunderstorm",
            96: "thunderstorm with hail",
            99: "thunderstorm with hail"
        }

        description = descriptions.get(
            weather_code,
            "unknown conditions"
        )

        return (
            f"Weather in {name}: "
            f"{temperature}°C, {description}. "
            f"Feels like {feels_like}°C. "
            f"Humidity is {humidity}%."
        )

    except Exception as error:

        return (
            "I couldn't retrieve the weather right now. "
            f"Error: {error}"
        )


def handle_weather(user_message):

    text = user_message.lower()

    weather_words = [
        "weather",
        "temperature",
        "forecast",
        "mausam",
        "mosam",
        "temperature kya hai"
    ]

    if not any(word in text for word in weather_words):
        return None

    known_cities = [
        "islamabad",
        "rawalpindi",
        "lahore",
        "karachi",
        "peshawar",
        "quetta",
        "multan",
        "faisalabad",
        "murree",
        "dubai",
        "london",
        "new york",
        "delhi",
        "riyadh"
    ]

    city = None

    for known_city in known_cities:

        if known_city in text:
            city = known_city
            break

    if city is None:

        match = re.search(
            r"(?:weather|temperature|forecast)"
            r"(?:\s+of|\s+in|\s+for)?\s+"
            r"([a-zA-Z\s]+)",
            text
        )

        if match:
            city = match.group(1).strip()

    if not city:
        return (
            "Sure. Tell me the city name, "
            "for example: weather of Islamabad."
        )

    return get_weather(city)


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(query, max_results=5):

    try:

        url = "https://html.duckduckgo.com/html/"

        response = requests.get(
            url,
            params={
                "q": query
            },
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=10
        )

        html = response.text

        results = []

        pattern = re.compile(
            r'class="result__a"[^>]*href="([^"]+)"[^>]*>'
            r'(.*?)</a>',
            re.IGNORECASE | re.DOTALL
        )

        matches = pattern.findall(html)

        for link, title in matches[:max_results]:

            clean_title = re.sub(
                r"<.*?>",
                "",
                title
            )

            results.append(
                f"{clean_title.strip()}: {link}"
            )

        if not results:
            return "No web results found."

        return "\n".join(results)

    except Exception as error:

        return f"Web search failed: {error}"


def is_web_search_query(user_message):

    text = user_message.lower()

    search_phrases = [
        "search the web",
        "search online",
        "search internet",
        "look it up",
        "google this",
        "find online",
        "latest news",
        "search for"
    ]

    return any(
        phrase in text
        for phrase in search_phrases
    )


# =========================================================
# GEMINI AI
# =========================================================

def ask_gemini(user_message):

    if not gemini_client:

        return (
            "My cloud AI brain is not configured yet. "
            "Please check GEMINI_API_KEY in Streamlit Secrets."
        )

    memory = get_recent_memory()

    conversation_context = ""

    if memory:

        conversation_context = "\n\nRecent conversation:\n"

        for user_msg, assistant_msg in memory:

            conversation_context += (
                f"User: {user_msg}\n"
                f"JARVIS: {assistant_msg}\n"
            )

    prompt = (
        SYSTEM_INSTRUCTION
        + conversation_context
        + "\n\nCurrent user message:\n"
        + user_message
    )

    try:

        response = gemini_client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        answer = response.text

        if not answer:
            return "I couldn't generate a response."

        return answer.strip()

    except Exception as error:

        return (
            "I couldn't connect to my cloud AI brain.\n\n"
            f"Error: {error}"
        )


# =========================================================
# MAIN JARVIS ROUTER
# =========================================================

def ask_jarvis(user_message):

    if not user_message:
        return "Please say something."

    user_message = user_message.strip()

    # Date / time
    response = handle_datetime_query(
        user_message
    )

    if response:
        save_memory(user_message, response)
        return response

    # Creator
    response = handle_creator_query(
        user_message
    )

    if response:
        save_memory(user_message, response)
        return response

    # Weather
    response = handle_weather(
        user_message
    )

    if response:
        save_memory(user_message, response)
        return response

    # Calculator
    response = handle_calculator(
        user_message
    )

    if response:
        save_memory(user_message, response)
        return response

    # Web search
    if is_web_search_query(user_message):

        search_result = web_search(
            user_message
        )

        prompt = (
            "Use these web search results to answer "
            "the user's question accurately.\n\n"
            f"Search results:\n{search_result}\n\n"
            f"User question:\n{user_message}"
        )

        response = ask_gemini(prompt)

        save_memory(
            user_message,
            response
        )

        return response

    # Normal AI conversation
    response = ask_gemini(
        user_message
    )

    save_memory(
        user_message,
        response
    )

    return response


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("JARVIS is online.")

    while True:

        user_input = input(
            "You: "
        ).strip()

        if user_input.lower() in [
            "exit",
            "quit",
            "bye"
        ]:
            print("JARVIS: Goodbye.")
            break

        print(
            "JARVIS:",
            ask_jarvis(user_input)
        )
