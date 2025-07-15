import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import sys
import platform
import pywhatkit
import requests
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
import threading
import keyboard
import subprocess

# Initialize the recognizer and TTS engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

FOOD_SITES = {
    "swiggy": "https://www.swiggy.com",
    "zomato": "https://www.zomato.com",
    "ubereats": "https://www.ubereats.com",
    "doordash": "https://www.doordash.com",
}
TICKET_SITES = {
    "movies": "https://in.bookmyshow.com",
    "flights": "https://www.makemytrip.com/flights",
    "trains": "https://www.irctc.co.in",
    "bus": "https://www.redbus.in",
}

# Add Gemini API key handling
GEMINI_API_KEY = "AIzaSyBRqEcWSbO7gIH-SMul3H0T-WnHsVqeGmU"
if not GEMINI_API_KEY:
    print("Error: Please set the GEMINI_API_KEY environment variable.")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)

# Global interrupt flag
interrupt_flag = threading.Event()

def interrupt_listener():
    # Listen for 'esc' key to interrupt
    while True:
        if keyboard.is_pressed('esc'):
            interrupt_flag.set()
            break

# Start interrupt listener in background
interrupt_thread = threading.Thread(target=interrupt_listener, daemon=True)
interrupt_thread.start()

def speak(text):
    print(f"Atom: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        except sr.WaitTimeoutError:
            print("I didn't hear anything. Please try again.")
            return ""
    try:
        command = recognizer.recognize_google(audio)
        print(f"You: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I did not understand that. Please speak clearly.")
        return ""
    except sr.RequestError:
        print("Sorry, my speech service is down.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def open_website(url):
    speak(f"Opening {url}")
    webbrowser.open(url)

def search_web(query):
    speak(f"Searching for {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def open_app(app_name):
    current_os = platform.system().lower()
    if current_os == "windows":
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "whatsapp": r"C:\\Users\\%USERNAME%\\AppData\\Local\\WhatsApp\\WhatsApp.exe",
        }
        if app_name in apps:
            speak(f"Opening {app_name}")
            try:
                os.startfile(apps[app_name])
            except Exception as e:
                speak(f"Failed to open {app_name}: {e}")
        else:
            speak(f"Sorry, I don't know how to open {app_name} yet.")
    elif current_os == "darwin":  # macOS
        apps = {
            "textedit": "/Applications/TextEdit.app",
            "calculator": "/Applications/Calculator.app",
            "whatsapp": "/Applications/WhatsApp.app",
        }
        if app_name in apps:
            speak(f"Opening {app_name}")
            os.system(f"open '{apps[app_name]}'")
        else:
            speak(f"Sorry, I don't know how to open {app_name} yet.")
    elif current_os == "linux":
        apps = {
            "gedit": "gedit",
            "calculator": "gnome-calculator",
            "whatsapp": "whatsapp-for-linux",  # Example, may need adjustment
        }
        if app_name in apps:
            speak(f"Opening {app_name}")
            os.system(f"{apps[app_name]} &")
        else:
            speak(f"Sorry, I don't know how to open {app_name} yet.")
    else:
        speak("Unsupported operating system.")

def send_whatsapp_message(number, message):
    try:
        speak(f"Sending WhatsApp message to {number}")
        # Send message instantly (1 min from now)
        import datetime
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute + 1
        pywhatkit.sendwhatmsg(number, message, hour, minute, wait_time=10, tab_close=True)
        speak("Message scheduled. Please make sure WhatsApp Web is open and logged in.")
    except Exception as e:
        speak(f"Failed to send WhatsApp message: {e}")

def handle_natural_language_web(command):
    if command.startswith("search for"):
        query = command.replace("search for", "").strip()
        if query:
            search_web(query)
            return True
    elif command.startswith("browse to"):
        site = command.replace("browse to", "").strip()
        if site:
            open_website(f"https://{site}")
            return True
    return False

def listen_for_yes_no():
    while True:
        answer = listen()
        if 'yes' in answer:
            return True
        elif 'no' in answer:
            return False
        else:
            speak("Please say yes or no.")

def fill_fields_interactively(driver, fields):
    for field in fields:
        try:
            label = field.get_attribute('placeholder') or field.get_attribute('aria-label') or field.get_attribute('name') or 'this field'
            speak(f"Would you like me to fill {label}?")
            if listen_for_yes_no():
                speak(f"What should I enter for {label}?")
                value = listen()
                field.clear()
                field.send_keys(value)
                speak(f"Filled {label} with {value}.")
            else:
                speak(f"Skipping {label}.")
        except Exception as e:
            speak(f"Could not fill a field: {e}")

def automate_food_order(site, query=None):
    speak(f"Opening {site} for food ordering.")
    url = FOOD_SITES.get(site)
    if not url:
        speak("Sorry, I don't know that food service.")
        return
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(3)
        # Find all visible input fields
        fields = driver.find_elements(By.XPATH, "//input[not(@type='hidden') and not(@disabled)]")
        if fields:
            speak(f"I found {len(fields)} fields you can fill.")
            fill_fields_interactively(driver, fields)
        else:
            speak("No fillable fields found.")
        # Keep browser open for user to complete order
    except Exception as e:
        speak(f"Automation failed: {e}")

def automate_ticket_booking(ticket_type, query=None):
    speak(f"Opening {ticket_type} booking site.")
    url = TICKET_SITES.get(ticket_type)
    if not url:
        speak("Sorry, I don't know that ticket type.")
        return
    try:
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(3)
        fields = driver.find_elements(By.XPATH, "//input[not(@type='hidden') and not(@disabled)]")
        if fields:
            speak(f"I found {len(fields)} fields you can fill.")
            fill_fields_interactively(driver, fields)
        else:
            speak("No fillable fields found.")
    except Exception as e:
        speak(f"Automation failed: {e}")

def handle_food_ordering(command):
    for site in FOOD_SITES:
        if site in command:
            # Try to extract a query (e.g., 'order pizza from zomato')
            words = command.split()
            idx = words.index(site)
            query = None
            if idx > 0:
                query = ' '.join(words[:idx])
            automate_food_order(site, query=query)
            return True
    if "order food" in command:
        speak("Which service do you want to use? Swiggy, Zomato, Uber Eats, or DoorDash?")
        return True
    return False

def handle_ticket_booking(command):
    for key, url in TICKET_SITES.items():
        if key in command:
            # Try to extract a query (e.g., 'book tickets for delhi to mumbai flights')
            words = command.split()
            idx = words.index(key)
            query = None
            if idx > 0:
                query = ' '.join(words[:idx])
            automate_ticket_booking(key, query=query)
            return True
    if "book ticket" in command or "book tickets" in command:
        speak("Do you want to book for movies, flights, trains, or bus?")
        return True
    return False

def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"Error contacting Gemini: {e}"

def open_website_direct(site):
    # Open common sites by name
    sites = {
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "youtube": "https://www.youtube.com",
        "twitter": "https://www.twitter.com",
        "instagram": "https://www.instagram.com",
        "gmail": "https://mail.google.com",
    }
    url = sites.get(site.lower())
    if url:
        speak(f"Opening {site}")
        webbrowser.open(url)
        return True
    return False

def type_in_notepad(text):
    try:
        open_app("notepad")
        speak("Typing in Notepad.")
        import time
        time.sleep(1.5)  # Wait for Notepad to open
        pyautogui.typewrite(text, interval=0.05)
    except Exception as e:
        speak(f"Failed to type in Notepad: {e}")

def try_execute_ai_command(ai_response):
    resp = ai_response.lower()
    # Direct website opening
    for site in ["google", "facebook", "youtube", "twitter", "instagram", "gmail"]:
        if f"open {site}" in resp:
            open_website_direct(site)
            return True
    # Notepad typing
    if resp.startswith("write") and "in notepad" in resp:
        # Example: write hello world in notepad
        text = resp.replace("write", "").replace("in notepad", "").strip()
        type_in_notepad(text)
        return True
    # WhatsApp message
    if resp.startswith("send whatsapp message to"):
        try:
            parts = resp.split("saying", 1)
            if len(parts) == 2:
                contact_part = parts[0].replace("send whatsapp message to", "").strip()
                message = parts[1].strip()
                number = contact_part.replace(" ", "")
                if not number.startswith("+"):
                    speak("Please provide the full phone number with country code, like +911234567890.")
                    return True
                send_whatsapp_message(number, message)
                return True
        except Exception as e:
            speak(f"Could not parse WhatsApp message command: {e}")
            return True
    # Fallback to previous actions
    if "open notepad" in resp:
        open_app("notepad")
        return True
    if "open calculator" in resp:
        open_app("calculator")
        return True
    if "open excel" in resp:
        open_app("excel")
        return True
    if "open word" in resp:
        open_app("word")
        return True
    if "open powerpoint" in resp:
        open_app("powerpoint")
        return True
    if "open whatsapp" in resp:
        open_app("whatsapp")
        return True
    if "open chrome" in resp:
        open_app("chrome")
        return True
    if resp.startswith("search for"):
        query = resp.replace("search for", "").strip()
        search_web(query)
        return True
    if resp.startswith("open website"):
        site = resp.replace("open website", "").strip()
        open_website(f"https://{site}")
        return True
    return False

def main():
    speak("Hi, I am ATOM. How can I help you today?")
    while True:
        command = listen()    # Listen for a single command
        if not command:
            continue
        # Direct website opening
        for site in ["google", "facebook", "youtube", "twitter", "instagram", "gmail"]:
            if f"open {site}" in command.lower():
                open_website_direct(site)
                break
        else:
            # Notepad typing
            if command.lower().startswith("write") and "in notepad" in command.lower():
                text = command.lower().replace("write", "").replace("in notepad", "").strip()
                type_in_notepad(text)
                continue
            if handle_natural_language_web(command):
                continue
            if handle_food_ordering(command):
                continue
            if handle_ticket_booking(command):
                continue
            if command.startswith("send whatsapp message to"):
                try:
                    parts = command.split("saying", 1)
                    if len(parts) == 2:
                        contact_part = parts[0].replace("send whatsapp message to", "").strip()
                        message = parts[1].strip()
                        number = contact_part.replace(" ", "")
                        if not number.startswith("+"):
                            speak("Please provide the full phone number with country code, like +911234567890.")
                            continue
                        send_whatsapp_message(number, message)
                    else:
                        speak("Please say: send WhatsApp message to [number] saying [your message].")
                except Exception as e:
                    speak(f"Could not parse your WhatsApp message command: {e}")
                continue
            if "open" in command:
                if "website" in command or ".com" in command or ".in" in command:
                    words = command.split()
                    for word in words:
                        if ".com" in word or ".in" in word:
                            open_website(f"https://{word}")
                            break
                else:
                    for app in ["notepad", "calculator", "whatsapp", "textedit", "gedit", "chrome"]:
                        if app in command.lower():
                            open_app(app)
                            break
                    else:
                        speak("Which website or app do you want to open?")
            elif "exit" in command or "quit" in command or "stop" in command:
                speak("Goodbye!")
                sys.exit(0)
            else:
                # Fallback: Ask Gemini AI
                speak("Let me think...")
                ai_response = ask_gemini(command)
                print(f"AI response: {ai_response}")
                if not try_execute_ai_command(ai_response):
                    speak(ai_response)

if __name__ == "__main__":
    main()

# Test microphone
# with sr.Microphone() as source:
#     print("Say something!")
#     audio = recognizer.listen(source)
# try:
#     print("You said: " + recognizer.recognize_google(audio))
# except Exception as e:
#     print("Error:", e) 