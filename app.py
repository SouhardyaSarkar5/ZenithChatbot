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
    except sr.RequestError as e:
        say("There seems to be an issue with my speech recognition service.")
        return "Sorry, an error occurred."

def get_news():
    api_key = "be18c630f62142b59dbb14b36bbd5227"
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
    api_key = "be18c630f62142b59dbb14b36bbd5227"
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
    print('PyCharm')
    greet_user()

    while True:
        query = takeCommand()

        if query != "Sorry, I could not understand that.":
            if not respond_human_like(query):
                say(f"You said: {query}")

            if "the time" in query:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M")
                say(f"The time is {current_time}")

            elif "news" in query:
                if "about" in query:
                    keyword = query.split("about")[-1].strip()
                    say(f"Fetching news about {keyword}, please wait.")
                    news = search_news(keyword)
                else:
                    say("Fetching the latest news, please wait.")
                    news = get_news()
                say(news)

            elif "current affairs" in query:
                say("Fetching the latest current affairs, please wait.")
                news = get_news()
                say(news)

            elif "weather" in query:
                city = query.split("weather in")[-1].strip()
                say(f"Fetching weather for {city}, please wait.")
                weather = get_weather(city)
                say(weather)

            elif "open" in query:
                website = query.split("open")[-1].strip()
                url = f"http://{website}" if not website.startswith("http") else website
                say(f"Opening {website}...")
                webbrowser.open(url)

            elif "generate" or "tell me" or "what is" in query or "write" in query:
                prompt = query
                say("Generating content, please wait.")
                generated_response = generate_content(prompt)
                say(generated_response)

            elif "stop" in query or "exit" in query:
                say("Goodbye! Have a great day.")
                break

            else:
                say("I'm not sure I understand that command. Could you please repeat?")

        else:
            say("I didn't quite catch that. Could you please repeat?")
