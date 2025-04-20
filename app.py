import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import requests
import random
from demo import generate_content

def say(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + 30)
    print(text)
    engine.say(text)
    engine.runAndWait()

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
    except sr.RequestError:
        say("There seems to be an issue with my speech recognition service.")
        return "Sorry, an error occurred."

def get_news():
    api_key = "c3637363cc1740ca9f5c0f954f291a53"
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return "I'm having trouble fetching the news right now."

    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        return "No news articles found."

    headlines = [article["title"] for article in articles[:5]]
    return "Here are the top 5 headlines: " + ". ".join(headlines)

def search_news(keyword):
    api_key = "c3637363cc1740ca9f5c0f954f291a53"
    url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=popularity&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Couldn't fetch news about {keyword} right now."

    data = response.json()
    articles = data.get("articles", [])
    if not articles:
        return f"No news articles found for {keyword}."

    headlines = [article["title"] for article in articles[:5]]
    return f"Top news for {keyword}: " + ". ".join(headlines)

def get_weather(city):
    api_key = "34ac881b51c347aa816172342240907"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    if response.status_code != 200:
        return "I'm having trouble fetching the weather right now."

    data = response.json()
    current = data.get("current", {})
    location = data.get("location", {}).get("name", city)
    temp = current.get("temp_c", "unknown")
    condition = current.get("condition", {}).get("text", "unknown")
    return f"The weather in {location} is {temp}°C with {condition}."

def greet_user():
    greetings = [
        "Hello there! I'm Zenith. How can I assist you today?",
        "Hi! I'm Zenith, your assistant. What can I do for you?",
        "Greetings! Zenith at your service.",
        "Hey! Need any help? Zenith is listening."
    ]
    say(random.choice(greetings))

def respond_human_like(query):
    responses = {
        "how are you": [
            "I'm just a bunch of code, but thanks for asking!",
            "I'm functioning as expected. How about you?",
            "Doing great! What's up?"
        ],
        "who are you": [
            "I'm Zenith, your virtual assistant and companion.",
            "They call me Zenith. I'm here to make your life easier.",
            "I'm Zenith, your AI assistant. Ask me anything!"
        ],
        "what is your name": [
            "My name is Zenith.",
            "You can call me Zenith.",
            "Zenith at your service!"
        ],
        "what can you do": [
            "I can tell you the news, weather, time, open websites, and chat about random stuff too.",
            "From current events to escaping John Wick—try me!",
            "I can help with news, weather, websites, and fun stuff too!"
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

            elif "exit" in query or "stop" in query:
                say("Goodbye!")
                break

            else:
                say("Let me think about that...")
                response = generate_content(query)
                say(response)

        else:
            say("I didn't quite catch that. Could you try again?")
