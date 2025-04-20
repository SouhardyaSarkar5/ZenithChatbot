import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import requests
import random
import re
from demo import generate_content


last_generated_response = None

def say(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + 30)
    print(text)
    engine.say(text)
    engine.runAndWait()
def clean_text(text):
    # Remove any unwanted characters like asterisks or markdown symbols
    text = re.sub(r'\*+', '', text)  # Remove asterisks
    text = re.sub(r'[`~_<>]', '', text)  # Remove other special characters
    return text

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        print("Listening...")
        audio = r.listen(source, timeout=7)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        say("I didn't quite catch that. Could you please repeat?")
        return "Sorry, I could not understand that."
    except sr.RequestError as e:
        say("There seems to be an issue with my speech recognition service.")
        return "Sorry, an error occurred."

def get_news():
    api_key = "c3637363cc1740ca9f5c0f954f291a53"
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        say("I'm having trouble fetching the news right now. Please try again later.")
        return "Sorry, I couldn't fetch the news."

    news_data = response.json()
    if "articles" not in news_data or not news_data["articles"]:
        say("I couldn't find any news articles at the moment.")
        return "Sorry, I couldn't find any news articles."
    articles = news_data["articles"]
    headlines = [article["title"] for article in articles[:5]]
    news_summary = "Here are the top 5 news headlines: " + ". ".join(headlines)
    return news_summary

def search_news(keyword):
    api_key = "c3637363cc1740ca9f5c0f954f291a53"
    url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=popularity&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        say(f"I'm having trouble fetching news about {keyword} right now.")
        return f"Sorry, I couldn't fetch the news for {keyword}."
    news_data = response.json()
    if "articles" not in news_data or not news_data["articles"]:
        say(f"I couldn't find any news articles about {keyword} at the moment.")
        return f"Sorry, I couldn't find any news articles for {keyword}."
    articles = news_data["articles"]
    headlines = [article["title"] for article in articles[:5]]
    news_summary = f"Here are the top 5 news headlines for {keyword}: " + ". ".join(headlines)
    return news_summary

def get_weather(city):
    api_key = "34ac881b51c347aa816172342240907"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    if response.status_code != 200:
        say("I'm having trouble fetching the weather right now. Please try again later.")
        return "Sorry, I couldn't fetch the weather."
    weather_data = response.json()
    if "current" not in weather_data:
        say("I couldn't find the weather data at the moment.")
        return "Sorry, I couldn't find the weather data."
    location = weather_data["location"]["name"]
    temp_c = weather_data["current"]["temp_c"]
    condition = weather_data["current"]["condition"]["text"]
    weather_summary = f"The current weather in {location} is {temp_c}°C with {condition}."
    return weather_summary

def greet_user():
    greetings = [
        "Hello there! How can I assist you today?",
        "Hi! What can I do for you?",
        "Greetings! How may I help you?",
        "Hey! Need any help?"
    ]
    say(random.choice(greetings))

def respond_human_like(query):
    responses = {
        "how are you": [
            "I'm just a bunch of code, but thanks for asking! How can I help you today?",
            "I'm functioning as expected. How about you?",
            "Doing great! What's up?",
            "I'm here and ready to assist you. How can I help?"
        ],
        "who are you": [
            "I'm your friendly chatbot, here to help you with various tasks.",
            "I'm a virtual assistant created to assist you. What can I do for you today?",
            "I'm a chatbot, here to make your life easier. How can I assist?"
        ],
        "what can you do": [
            "I can provide you with news updates, weather forecasts, and even open websites for you.",
            "I can help you with news, weather, and browsing the internet. Just let me know what you need.",
            "I can fetch the latest news, tell you the weather, and open websites. What do you need?"
        ]
    }

    for key in responses:
        if key in query:
            say(random.choice(responses[key]))
            return True
    return False

if __name__ == "__main__":
    print("Zenith is ready.")
    greet_user()

    while True:
        query = takeCommand()

        if query != "Sorry, I could not understand that.":
            if respond_human_like(query):
                continue

            if "the time" in query:
                time = datetime.datetime.now().strftime("%H:%M")
                say(f"The time is {time}")

            elif "news" in query:
                if "about" in query:
                    keyword = query.split("about")[-1].strip()
                    say(f"Getting news about {keyword}")
                    news = search_news(keyword)
                else:
                    say("Fetching top news")
                    news = get_news()
                say(news)

            elif "current affairs" in query:
                say("Fetching current affairs")
                news = get_news()
                say(news)

            elif "weather" in query:
                if "in" in query:
                    city = query.split("in")[-1].strip()
                else:
                    city = "your city"
                say(f"Getting weather for {city}")
                weather = get_weather(city)
                say(weather)

            elif "open" in query:
                site = query.split("open")[-1].strip()
                url = f"https://{site}" if not site.startswith("http") else site
                say(f"Opening {site}")
                webbrowser.open(url)

            else:
                # Handle any random or creative input using Gemini
                 say("Let me think about that...")
                 response = generate_content(query)
                 say(response)
                 
        elif any(kw in query for kw in ["generate", "tell me", "what is", "about", "write"]):
                prompt = query
                say("Generating content, please wait.")
                generated_response = generate_content(prompt)
                last_generated_response = generated_response
                say(generated_response)

        elif any(kw in query for kw in ["be more", "make it", "change it", "edit it", "modify it", "make this", "improve this", "make it more", "the previous", "previous content"]) and last_generated_response:
                followup_instruction = query
                full_prompt = f"{followup_instruction}\n\nHere is the original content:\n{last_generated_response}"
                say("Modifying the previous response, please wait.")
                generated_response = generate_content(full_prompt)
                last_generated_response = generated_response
                say(generated_response)

        elif "exit" in query or "stop" in query:
                say("Goodbye!")
                break

        else:
                say("Let me think about that...")
                response = generate_content(query)
                cleaned_response = clean_text(response)  # Clean the response
                say(cleaned_response)

    else:
       say("I didn't quite catch that. Could you try again?")
