import subprocess
import re
import webbrowser


APPLICATIONS = {
    "calculator": {
        "keywords": ["calculator", "calc"],
        "command": "calc.exe"
    },

    "notepad": {
        "keywords": ["notepad"],
        "command": "notepad.exe"
    },

    "paint": {
        "keywords": ["paint", "mspaint"],
        "command": "mspaint.exe"
    },

    "chrome": {
        "keywords": ["chrome", "google chrome"],
        "command": "chrome"
    },

    "vs code": {
        "keywords": [
            "vs code",
            "vscode",
            "visual studio code"
        ],
        "command": "code"
    },

    # MySQL Workbench
    "sql": {
        "keywords": [
            "sql",
            "mysql",
            "mysql workbench"
        ],
        "command": None,
        "url": "https://www.mysql.com/products/workbench/"
    },

    # ChatGPT
    "chatgpt": {
        "keywords": [
            "chatgpt",
            "chat gpt"
        ],
        "command": None,
        "url": "https://chatgpt.com/"
    },

    # Streamlit
    "streamlit": {
        "keywords": [
            "streamlit"
        ],
        "command": None,
        "url": "https://streamlit.io/"
    },

    # YouTube
    "youtube": {
        "keywords": [
            "youtube",
            "you tube"
        ],
        "command": None,
        "url": "https://www.youtube.com/"
    },

    # WhatsApp
    "whatsapp": {
        "keywords": [
            "whatsapp",
            "whats app"
        ],
        "command": None,
        "url": "https://web.whatsapp.com/"
    }
}


def find_application(text):

    text = text.lower().strip()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", " ", text)

    # Check longer names first
    sorted_apps = sorted(
        APPLICATIONS.items(),
        key=lambda item: max(
            len(keyword)
            for keyword in item[1]["keywords"]
        ),
        reverse=True
    )

    for app_name, data in sorted_apps:

        for keyword in data["keywords"]:

            if keyword in text:
                return app_name

    return None


def open_application(app_name):

    app_name = app_name.lower().strip()

    if app_name not in APPLICATIONS:
        return f"I don't know how to open {app_name} yet."

    app = APPLICATIONS[app_name]

    try:

        # Browser/Web application
        if app["command"] is None:

            webbrowser.open(app["url"])

            return f"Opening {app_name}."

        # Windows application
        subprocess.Popen(app["command"])

        return f"Opening {app_name}."

    except FileNotFoundError:

        return f"I couldn't find {app_name} on this computer."

    except Exception as error:

        return f"I couldn't open {app_name}: {error}"


def handle_automation(text):

    app_name = find_application(text)

    if app_name is None:
        return None

    return open_application(app_name)


if __name__ == "__main__":

    print("=" * 55)
    print("JARVIS SMART AUTOMATION")
    print("=" * 55)

    print("\nSupported applications:")

    for app in APPLICATIONS:
        print("-", app)

    print("\nType a command or 'exit'.")

    while True:

        command = input("\nYou: ").strip()

        if command.lower() in ["exit", "quit"]:
            break

        result = handle_automation(command)

        if result:
            print("JARVIS:", result)
        else:
            print("JARVIS: I couldn't identify an application.")