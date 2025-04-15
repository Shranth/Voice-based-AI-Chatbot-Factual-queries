import requests
from bs4 import BeautifulSoup
import wikipediaapi
from serpapi import GoogleSearch
import pyttsx3
import speech_recognition as sr
import threading
from datetime import datetime
import re

WEATHER_API_KEY = 'Enter you weather Api key here'

def load_responses(filename='responses.txt'):
    responses = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if '|' in line:
                    question, answer = line.strip().split('|', 1)
                    responses[question.lower()] = answer.strip()
    except FileNotFoundError:
        pass
    return responses

def save_response(question, answer, filename='responses.txt'):
    responses = load_responses(filename)
    responses[question.lower()] = answer.strip()
    with open(filename, 'w', encoding='utf-8') as f:
        for q, a in responses.items():
            f.write(f"{q}|{a}\n")
    return responses

def casual_responses(question):
    greetings = {
        "hello": "Hi there!",
        "hi": "Hello!",
        "how are you": "All good!",
        "what's up": "Not much, how about you?",
        "goodbye": "See you later!",
        "bye": "Take care!",
        "what can you do": "I mainly answer factual questions.",
        "who are you": "I am an AI chatbot for answering factual questions.",
        "what time is it": get_current_time,
        "time": get_current_time,
        "what is the current time": get_current_time,
        "what is the time right now": get_current_time
    }
    return greetings.get(question.lower())

def get_current_time():
    now = datetime.now()
    return now.strftime("It's %H:%M on %A, %B %d.")

def is_gibberish(text):
    return len(text) < 2 or sum(not c.isalpha() for c in text) > len(text) // 2

def search_duckduckgo(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'Abstract' in data and data['Abstract'] != '':
        sentences = data['Abstract'].split('. ')
        return '. '.join(sentences[:2]) + '.' if len(sentences) > 1 else sentences[0]
    return None

def search_serpapi(query):
    params = {
        "q": query,
        "api_key": "Enter you serp api key here",
        "num": 5
    }
    search = GoogleSearch(params)
    result = search.get_dict()
    if 'organic_results' in result and result['organic_results']:
        full_answer = ""
        for res in result['organic_results']:
            if 'snippet' in res:
                snippet = res['snippet']
                sentences = re.split(r'(?<=[.!?]) +', snippet)
                for sentence in sentences:
                    full_answer += sentence.strip() + " "
                    if sentence.strip().endswith('.'):
                        break
        if not full_answer.strip().endswith('.'):
            for res in result['organic_results']:
                if 'snippet' in res:
                    snippet = res['snippet']
                    sentences = re.split(r'(?<=[.!?]) +', snippet)
                    for sentence in sentences:
                        full_answer += sentence.strip() + " "
                        if sentence.strip().endswith('.'):
                            break
                    if full_answer.strip().endswith('.'):
                        break
        return full_answer.strip() if full_answer else None
    return None

def search_wikipedia(query):
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent="YourUserAgent/1.0"
    )
    page = wiki_wiki.page(query)
    if page.exists():
        sentences = page.summary.split('. ')
        max_sentences = 3
        limited_summary = '. '.join(sentences[:max_sentences]) + ('.' if len(sentences) > max_sentences else '')
        return limited_summary
    return None

def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"
    response = requests.get(url)
    data = response.json()
    if 'error' not in data:
        temperature = data['current']['temp_c']
        weather_desc = data['current']['condition']['text']
        return f"The temperature in {city} is {temperature}°C with {weather_desc}."
    else:
        return f"Sorry, I couldn't find weather data for {city}."

def is_pronunciation_request(question):
    return "pronounce" in question.lower() or "how to pronounce" in question.lower()

is_speaking = False

def speak(text):
    global is_speaking
    is_speaking = True
    engine = pyttsx3.init()
    
    def on_end(name, completed):
        global is_speaking
        is_speaking = False
    
    engine.connect('finished-utterance', on_end)
    engine.say(text)
    engine.runAndWait()

def listen(timeout=10):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... (timeout in 10 seconds)")
        audio = recognizer.listen(source, timeout=timeout)
        try:
            question = recognizer.recognize_google(audio)
            print("You said:", question)
            return question
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None

def get_answer(question, responses):
    question_lower = question.lower()
    if is_gibberish(question_lower):
        return "That seems like gibberish. Please provide a clearer question."
    if is_pronunciation_request(question_lower):
        word_to_pronounce = question_lower.replace("pronounce", "").replace("how to", "").strip()
        return f"The pronunciation of {word_to_pronounce} is...{word_to_pronounce}"
    if question_lower in responses:
        return responses[question_lower]
    
    if "weather" in question_lower:
        city_match = re.search(r'weather in (\w+)', question_lower)
        if city_match:
            city = city_match.group(1)
            return get_weather(city)
        else:
            return "Please specify a city to check the weather."
    
    response = casual_responses(question_lower)
    if response:
        if "what time is it" in question_lower or "time" in question_lower or "what is the time right now" in question_lower:
            return response if isinstance(response, str) else response()
        return response if isinstance(response, str) else response()
    
    answer = search_wikipedia(question)
    if answer:
        responses = save_response(question_lower, answer)
        return responses[question_lower]
    
    answer = search_serpapi(question)
    if not answer:
        print("Using DuckDuckGo as fallback...")
        answer = search_duckduckgo(question)

    if answer:
        responses = save_response(question_lower, answer)
        return responses[question_lower]

    return "Sorry, I couldn't find an answer."

def main():
    responses = load_responses()
    while True:
        question_choice = input("Do you want to ask by typing or speaking? (type/speak): ").strip().lower()
        if question_choice == 'speak':
            question = listen()
            if question is None:
                continue
        elif question_choice == 'type':
            question = input("Ask a question: ")
        else:
            print("Invalid option. Please choose 'type' or 'speak'.")
            continue

        if question.lower() == 'exit':
            break

        answer = get_answer(question, responses)
        print("Answer:", answer)

        threading.Thread(target=speak, args=(answer,)).start()

        while is_speaking:
            interrupt = input("Press Enter to stop speaking and ask another question, or wait for it to finish: ")
            if interrupt == '':
                pyttsx3.init().stop()
                break

        better_response = input("Do you want to provide a better response? (yes/no): ").strip().lower()
        if better_response == 'yes':
            if question.lower() in responses:
                print("This question already exists in the database. Current answer:")
                print(f"Existing answer: {responses[question.lower()]}")
                print("Do you want to overwrite it with the new answer? (yes/no): ", end="")
                overwrite = input().strip().lower()
                if overwrite == 'yes':
                    user_response = input("Please provide your answer: ")
                    responses = save_response(question.lower(), user_response)
            else:
                user_response = input("Please provide your answer: ")
                responses = save_response(question.lower(), user_response)
        else:
            if not (("weather" in question.lower()) or 
                    ("what time is it" in question.lower()) or 
                    ("time" in question.lower()) or 
                    ("what is the time right now" in question.lower()) or 
                    is_pronunciation_request(question.lower())):
                responses = save_response(question.lower(), answer)

if __name__ == "__main__":
    main()
