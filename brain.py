import ast
import operator
import re
import sqlite3
from datetime import datetime
from pathlib import Path

import requests


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DB = BASE_DIR / "jarvis_memory.db"

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:0.5b"

OLLAMA_TIMEOUT = 60
WEB_TIMEOUT = 8

conversation_history = []


# =========================================================
# CREATOR
# =========================================================

CREATOR_NAME = "Zaynab Shakeel Abbasi"


def creator_answer(language):

    if language == "Roman Urdu":
        return (
            "Mujhe Zaynab Shakeel Abbasi ne create aur build kiya hai."
        )

    return (
        "I was created and built by Zaynab Shakeel Abbasi."
    )


def is_creator_question(text):

    text = text.lower()

    phrases = [
        "who created you",
        "who made you",
        "who built you",
        "who is your creator",
        "who is your owner",
        "tumhein kis ne banaya",
        "tumhe kis ne banaya",
        "tumhara creator",
        "tumhara owner",
    ]

    return any(x in text for x in phrases)


# =========================================================
# LANGUAGE
# =========================================================

ROMAN_URDU_WORDS = {
    "mujhe", "mujhy", "mera", "meri", "mery",
    "tum", "tumhe", "tumhy", "aap", "ap",
    "kya", "kyun", "q", "kaise", "kesay",
    "batao", "btao", "hai", "hain",
    "ho", "hota", "hoti", "hote",
    "karna", "krna", "karo", "krdo",
    "acha", "achaa", "nahi", "nahin",
    "haan", "yeh", "ye", "woh", "wo",
    "mein", "main", "mujh", "apna", "apni",
    "ka", "ki", "ke", "ko", "se",
    "par", "sy", "hy", "rha", "raha",
    "rahi", "liye", "lia", "chahiye",
    "kuch", "koi", "bohat", "zyada",
    "ab", "phir", "pehle", "bhi",
    "kr", "bn", "bna", "wla",
    "wala", "wali", "waly"
}


def detect_language(text):

    words = set(
        re.findall(r"\b[a-zA-Z]+\b", text.lower())
    )

    count = len(
        words.intersection(ROMAN_URDU_WORDS)
    )

    if count >= 2:
        return "Roman Urdu"

    return "English"


# =========================================================
# DATE / TIME
# =========================================================

def current_datetime_answer(text, language):

    lower = text.lower().strip()

    time_patterns = [
        "what time is it",
        "what's the time",
        "current time",
        "time right now",
        "time now"
    ]

    date_patterns = [
        "what is the date",
        "what's the date",
        "what date is it",
        "today's date",
        "todays date",
        "current date"
    ]

    year_patterns = [
        "what year is it",
        "current year",
        "which year is it"
    ]

    now = datetime.now()

    if any(x in lower for x in time_patterns):

        if language == "Roman Urdu":
            return f"Abhi time {now.strftime('%I:%M %p')} hai."

        return f"The current time is {now.strftime('%I:%M %p')}."

    if any(x in lower for x in date_patterns):

        if language == "Roman Urdu":
            return (
                f"Aaj {now.strftime('%A')}, "
                f"{now.strftime('%d %B %Y')} hai."
            )

        return (
            f"Today is {now.strftime('%A')}, "
            f"{now.strftime('%d %B %Y')}."
        )

    if any(x in lower for x in year_patterns):

        if language == "Roman Urdu":
            return f"Abhi year {now.year} hai."

        return f"The current year is {now.year}."

    return None


# =========================================================
# MEMORY
# =========================================================

def get_database():

    db = sqlite3.connect(MEMORY_DB)

    db.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            created_at TEXT
        )
    """)

    db.commit()

    return db


def remember(key, value):

    db = get_database()

    db.execute("""
        INSERT INTO memories(key, value, created_at)
        VALUES (?, ?, ?)

        ON CONFLICT(key)
        DO UPDATE SET
            value = excluded.value,
            created_at = excluded.created_at
    """, (
        key.lower().strip(),
        value.strip(),
        datetime.now().isoformat()
    ))

    db.commit()
    db.close()


def get_all_memories():

    db = get_database()

    data = db.execute(
        "SELECT key, value FROM memories ORDER BY id DESC"
    ).fetchall()

    db.close()

    return data


def extract_memory_command(text):

    patterns = [
        r"remember that (.+?) is (.+)",
        r"remember (.+?) is (.+)",
        r"yaad rakhna (.+?) hai (.+)",
        r"yaad rakhna ke (.+?) hai (.+)",
        r"yaad rakhna ky (.+?) hai (.+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.lower().strip()
        )

        if match:
            return (
                match.group(1).strip(),
                match.group(2).strip()
            )

    return None


def is_memory_question(text):

    lower = text.lower()

    phrases = [
        "what do you remember",
        "what do you know about me",
        "show my memories",
        "my memories",
        "meri memory",
        "meri memories",
        "tumhe mere bare mein kya yaad hai",
        "tumhein mere bare mein kya yaad hai"
    ]

    return any(x in lower for x in phrases)


# =========================================================
# CALCULATOR
# =========================================================

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calculate(expression):

    expression = expression.replace(",", "")
    expression = expression.replace("^", "**")

    tree = ast.parse(
        expression,
        mode="eval"
    )

    def evaluate(node):

        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):

            if isinstance(node.value, (int, float)):
                return node.value

        if isinstance(node, ast.BinOp):

            left = evaluate(node.left)
            right = evaluate(node.right)

            operation = OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError()

            return operation(left, right)

        if isinstance(node, ast.UnaryOp):

            value = evaluate(node.operand)

            operation = OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError()

            return operation(value)

        raise ValueError()

    return evaluate(tree)


def extract_math(text):

    cleaned = text.lower().strip()

    cleaned = re.sub(
        r"^(what is|calculate|solve|compute)\s+",
        "",
        cleaned
    )

    cleaned = cleaned.replace("?", "")

    if re.fullmatch(
        r"[0-9+\-*/().%^ \t]+",
        cleaned
    ):
        return cleaned.strip()

    return None


# =========================================================
# WEATHER
# =========================================================

def extract_weather_location(text):

    patterns = [
        r"weather\s+(?:in|of|for)\s+(.+)",
        r"temperature\s+(?:in|of|for)\s+(.+)",
        r"forecast\s+(?:in|of|for)\s+(.+)",
        r"mausam\s+(?:in|of|ka|ki)\s+(.+)",
        r"mosam\s+(?:in|of|ka|ki)\s+(.+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.lower()
        )

        if match:

            location = re.sub(
                r"[?.!]+$",
                "",
                match.group(1)
            )

            return location.strip()

    return None


def get_weather(location, language):

    try:

        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=WEB_TIMEOUT
        )

        geo.raise_for_status()

        results = geo.json().get(
            "results",
            []
        )

        if not results:

            if language == "Roman Urdu":
                return f"Mujhe {location} nahi mila."

            return f"I couldn't find {location}."

        place = results[0]

        latitude = place["latitude"]
        longitude = place["longitude"]

        name = place.get(
            "name",
            location
        )

        country = place.get(
            "country",
            ""
        )

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "precipitation,"
                    "wind_speed_10m"
                ),
                "daily": (
                    "temperature_2m_max,"
                    "temperature_2m_min,"
                    "precipitation_probability_max"
                ),
                "forecast_days": 3,
                "timezone": "auto"
            },
            timeout=WEB_TIMEOUT
        )

        weather.raise_for_status()

        data = weather.json()

        current = data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        feels = current["apparent_temperature"]
        rain_now = current["precipitation"]
        wind = current["wind_speed_10m"]

        daily = data.get("daily", {})

        maximum = daily.get(
            "temperature_2m_max",
            []
        )

        minimum = daily.get(
            "temperature_2m_min",
            []
        )

        rain_probability = daily.get(
            "precipitation_probability_max",
            []
        )

        if language == "Roman Urdu":

            answer = (
                f"{name}, {country} ka current weather:\n"
                f"Temperature: {temperature}°C\n"
                f"Feels like: {feels}°C\n"
                f"Humidity: {humidity}%\n"
                f"Rain: {rain_now} mm\n"
                f"Wind: {wind} km/h"
            )

            if maximum and minimum:

                answer += (
                    f"\n\nAaj ka range: "
                    f"{minimum[0]}°C se "
                    f"{maximum[0]}°C"
                )

                if rain_probability:
                    answer += (
                        f"\nRain probability: "
                        f"{rain_probability[0]}%"
                    )

            return answer

        answer = (
            f"Current weather in {name}, {country}:\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels}°C\n"
            f"Humidity: {humidity}%\n"
            f"Precipitation: {rain_now} mm\n"
            f"Wind: {wind} km/h"
        )

        if maximum and minimum:

            answer += (
                f"\n\nToday's range: "
                f"{minimum[0]}°C to "
                f"{maximum[0]}°C"
            )

            if rain_probability:
                answer += (
                    f"\nRain probability: "
                    f"{rain_probability[0]}%"
                )

        return answer

    except requests.exceptions.Timeout:

        if language == "Roman Urdu":
            return "Weather service ka response slow aa raha hai."

        return "The weather service is taking too long."

    except Exception:

        if language == "Roman Urdu":
            return "Weather service se connect nahi ho saka."

        return "I couldn't connect to the weather service."


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(query):

    try:

        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={
                "q": query
            },
            headers={
                "User-Agent": "Mozilla/5.0"
            },
            timeout=WEB_TIMEOUT
        )

        response.raise_for_status()

        html = response.text

        titles = re.findall(
            r'class="result__a"[^>]*>(.*?)</a>',
            html,
            re.DOTALL
        )

        cleaned = []

        for title in titles[:5]:

            title = re.sub(
                r"<.*?>",
                "",
                title
            )

            cleaned.append(
                title.strip()
            )

        if not cleaned:
            return None

        return "\n".join(
            f"- {item}"
            for item in cleaned
        )

    except Exception:
        return None


# =========================================================
# LIVE QUERY DETECTION
# =========================================================

LIVE_PHRASES = [
    "current",
    "currently",
    "latest",
    "right now",
    "recent",
    "recently",
    "news",
    "price",
    "rate",
    "score",
    "result",
    "prime minister",
    "president",
    "chief minister",
    "election",
]


def needs_web(text):

    lower = text.lower()

    return any(
        phrase in lower
        for phrase in LIVE_PHRASES
    )


# =========================================================
# OLLAMA
# =========================================================

SYSTEM_PROMPT = f"""
You are JARVIS, a general-purpose AI assistant.

You were created and built by {CREATOR_NAME}.

You can explain:

Artificial Intelligence,
Machine Learning,
Deep Learning,
Computer Vision,
Python,
C++,
Java,
JavaScript,
HTML,
CSS,
SQL,
Programming,
Computer Science,
Mathematics,
Physics,
Chemistry,
Biology,
Psychology,
Philosophy,
History,
Geography,
Technology,
Engineering,
and general knowledge.

IMPORTANT RULES:

1. Answer questions directly.
2. Never say you cannot explain AI, ML, programming or science.
3. Do not invent limitations.
4. Do not claim to be created by OpenAI, Google,
   Anthropic, Alibaba or another company.
5. You were created by Zaynab Shakeel Abbasi.
6. English question = English answer.
7. Roman Urdu question = Roman Urdu answer.
8. Mixed Urdu-English = similar mixed style.
9. Be accurate.
10. If you are unsure, say so.
11. Do not fabricate current information.
12. Keep normal answers concise.
"""


def ask_ollama(
    user_message,
    external_context=""
):

    language = detect_language(
        user_message
    )

    if language == "Roman Urdu":

        language_rule = (
            "Answer ONLY in Roman Urdu "
            "using English letters."
        )

    else:

        language_rule = (
            "Answer ONLY in English."
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "system",
            "content": language_rule
        }
    ]

    if external_context:

        messages.append({
            "role": "system",
            "content": (
                "Use this external information "
                "when answering:\n\n"
                + external_context
            )
        })

    messages.extend(
        conversation_history[-4:]
    )

    messages.append({
        "role": "user",
        "content": user_message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 100,
            "num_ctx": 2048
        }
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        answer = data["message"]["content"].strip()

        conversation_history.append({
            "role": "user",
            "content": user_message
        })

        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except requests.exceptions.ConnectionError:

        return (
            "I cannot connect to my local AI brain. "
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "My local AI brain is taking too long "
            "to respond."
        )

    except Exception as error:

        return f"Sorry, I encountered an error: {error}"


# =========================================================
# MAIN JARVIS BRAIN
# =========================================================

def ask_jarvis(user_message):

    user_message = user_message.strip()

    if not user_message:
        return "Please say something."

    language = detect_language(
        user_message
    )

    # 1. DATE / TIME
    answer = current_datetime_answer(
        user_message,
        language
    )

    if answer:
        return answer

    # 2. CREATOR
    if is_creator_question(user_message):
        return creator_answer(language)

    # 3. MEMORY SAVE
    memory = extract_memory_command(
        user_message
    )

    if memory:

        key, value = memory

        remember(
            key,
            value
        )

        if language == "Roman Urdu":
            return "Theek hai, yaad rakh liya."

        return "Got it. I'll remember that."

    # 4. MEMORY RECALL
    if is_memory_question(user_message):

        memories = get_all_memories()

        if not memories:

            if language == "Roman Urdu":
                return (
                    "Abhi meri memory mein "
                    "kuch save nahi hai."
                )

            return (
                "I don't have anything saved "
                "in memory yet."
            )

        if language == "Roman Urdu":

            return (
                "Meri saved memories:\n"
                + "\n".join(
                    f"- {key}: {value}"
                    for key, value in memories
                )
            )

        return (
            "My saved memories:\n"
            + "\n".join(
                f"- {key}: {value}"
                for key, value in memories
            )
        )

    # 5. WEATHER
    weather_location = extract_weather_location(
        user_message
    )

    if weather_location:

        return get_weather(
            weather_location,
            language
        )

    # 6. CALCULATOR
    expression = extract_math(
        user_message
    )

    if expression:

        try:

            result = safe_calculate(
                expression
            )

            return str(result)

        except Exception:
            pass

    # 7. LIVE WEB SEARCH
    # ONLY runs for current/latest/live questions.

    if needs_web(user_message):

        search_results = web_search(
            user_message
        )

        if search_results:

            return ask_ollama(
                user_message,
                search_results
            )

    # 8. NORMAL AI
    # AI / ML / programming / science etc.
    # come directly here.

    return ask_ollama(
        user_message
    )


# =========================================================
# TERMINAL TEST MODE
# =========================================================

if __name__ == "__main__":

    print("=" * 55)
    print("JARVIS GENERAL AI BRAIN ONLINE")
    print("=" * 55)

    print(f"Model: {MODEL}")
    print("General AI: ONLINE")
    print("Memory: ONLINE")
    print("Weather: ONLINE")
    print("Calculator: ONLINE")
    print("Date/Time: ONLINE")
    print("Web Search: ONLINE")

    print("\nType 'exit' to stop.\n")

    while True:

        user_input = input(
            "You: "
        ).strip()

        if user_input.lower() in {
            "exit",
            "quit",
            "goodbye"
        }:

            print(
                "JARVIS: Goodbye."
            )

            break

        if not user_input:
            continue

        answer = ask_jarvis(
            user_input
        )

        print(
            "\nJARVIS:",
            answer
        )

        print()