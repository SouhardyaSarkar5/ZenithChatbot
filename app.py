import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
import requests
import random
import re
from demo import generate_content
import time

last_generated_response = None
conversation_context = {
    "last_topic": None,
    "last_entities": [],
    "last_query": "",
    "last_response": "",
    "original_constraints": {}
}

def say(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate + 30)
    print(text)
    engine.say(text)
    engine.runAndWait()

def clean_text(text):
    text = re.sub(r'\*+', '', text)  
    text = re.sub(r'[`~_<>]', '', text)  
    return text

def extract_main_topic(query):
    """Extract the main topic from a query, ignoring format instructions."""
    topic_patterns = [
        r"(?:tell me about|about|who is|what is|describe)\s+(.+?)(?:\s+in one line|\s+briefly|\s+in detail|$)",
        r"(.+?)(?:\s+in one line|\s+briefly|\s+in detail|$)"
    ]
    
    for pattern in topic_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return query

def update_conversation_context(query, response=None):
    global conversation_context
    
    conversation_context["last_query"] = query
    
    main_topic = extract_main_topic(query)
    
    if main_topic and len(main_topic) > 0:
        conversation_context["last_topic"] = main_topic
        conversation_context["last_entities"] = [main_topic]
        print(f"Updated conversation topic to: '{main_topic}'")
    
    constraints = {}
    if "in one line" in query:
        constraints["format"] = "one line"
    elif "briefly" in query:
        constraints["format"] = "brief"
    elif "in detail" in query:
        constraints["format"] = "detailed"
        
    conversation_context["original_constraints"] = constraints
    
    if response:
        conversation_context["last_response"] = response

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        print("Listening...")
        audio = r.listen(source, timeout=10)
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
    api_key = "5d6230e07235698ce9e856373a584a54" 
    url = f"https://gnews.io/api/v4/top-headlines?lang=en&token={api_key}"
    try:
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            say(f"News API error: {response.status_code}")
            return "Sorry, I couldn't fetch the news."

        news_data = response.json()
        if "articles" not in news_data or not news_data["articles"]:
            say("I couldn't find any news articles at the moment.")
            return "Sorry, I couldn't find any news articles."
            
        articles = news_data["articles"]
        headlines = [article["title"] for article in articles[:5]]
        news_summary = "Here are the top 5 news headlines: " + ". ".join(headlines)
        return news_summary
    except Exception as e:
        print(f"Error fetching news: {e}")
        return "Sorry, I encountered an error while fetching the news."

def search_news(keyword):
    api_key = "5d6230e07235698ce9e856373a584a54"
    url = f"https://gnews.io/api/v4/search?q={keyword}&lang=en&token={api_key}"
    try:
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
    except Exception as e:
        print(f"Error searching news for {keyword}: {e}")
        return f"Sorry, I encountered an error while searching news about {keyword}."

def get_weather(city):
    if not city or city.strip() == "":
        say("Please specify a city for the weather information.")
        return "No city specified for weather."
    
    api_key = "34ac881b51c347aa816172342240907"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            say(f"I'm having trouble fetching the weather for {city} right now. Please try again later.")
            return f"Sorry, I couldn't fetch the weather for {city}."
        
        weather_data = response.json()
        if "current" not in weather_data:
            say(f"I couldn't find the weather data for {city} at the moment.")
            return f"Sorry, I couldn't find the weather data for {city}."
        
        location = weather_data["location"]["name"]
        temp_c = weather_data["current"]["temp_c"]
        condition = weather_data["current"]["condition"]["text"]
        weather_summary = f"The current weather in {location} is {temp_c}°C with {condition}."
        return weather_summary
    except Exception as e:
        print(f"Error fetching weather for {city}: {e}")
        return f"Sorry, I encountered an error while fetching weather for {city}."

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
            response = random.choice(responses[key])
            say(response)
            update_conversation_context(query, response)
            return True
    return False

def is_followup_query(query):
    """Check if a query is likely to be a follow-up question."""
    followup_indicators = [
        r"^(tell me )?more( about)?",
        r"^(tell me )?additional",
        r"^continue",
        r"^go on",
        r"^elaborate",
        r"^explain (more|further)",
        r"^what else",
        r"^and\?",
        r"^(what|who) (is|are) (he|she|it|they|them|that|this|those)",
        r"^(him|her|it|them|they|that|this|those)",
    ]
    
    return any(re.search(pattern, query.strip(), re.IGNORECASE) for pattern in followup_indicators)

def handle_followup_query(query):
    global conversation_context, last_generated_response
    
    if is_followup_query(query) and conversation_context["last_topic"]:
        print(f"Detected follow-up query: '{query}' about topic: '{conversation_context['last_topic']}'")
        
        prompt = f"""
        This is a follow-up query about {conversation_context['last_topic']}. 
        The user previously received this information: "{conversation_context['last_response']}"
        
        Now they're asking for more details with: "{query}"
        
        Please provide a detailed, comprehensive response about {conversation_context['last_topic']} 
        that builds upon but doesn't repeat the previous information.
        """
        
        say(f"Finding more information about {conversation_context['last_topic']}, please wait.")
        generated_response = generate_content(prompt)
        
        last_generated_response = generated_response
        update_conversation_context(query, generated_response)
        
        say(clean_text(generated_response))
        return True
    
    return False

def parse_query_intent(query):
    """Analyze the query to determine the user's likely intent and any missing information."""
    intent_info = {
        "likely_intent": None,
        "missing_parts": [],
        "complete": True
    }
    
    if re.search(r"tell me about (.+)", query, re.IGNORECASE):
        intent_info["likely_intent"] = "information"
    elif re.search(r"weather (in|for|of)", query, re.IGNORECASE) and not re.search(r"weather (in|for|of) \w+", query, re.IGNORECASE):
        intent_info["likely_intent"] = "weather"
        intent_info["missing_parts"] = ["location"]
        intent_info["complete"] = False
    elif re.search(r"news about", query, re.IGNORECASE) and not re.search(r"news about \w+", query, re.IGNORECASE):
        intent_info["likely_intent"] = "news"
        intent_info["missing_parts"] = ["topic"]
        intent_info["complete"] = False
    elif query.startswith("open") and len(query.split()) < 2:
        intent_info["likely_intent"] = "open_website"
        intent_info["missing_parts"] = ["website"]
        intent_info["complete"] = False
        
    return intent_info

def preprocess_query(query):
    intent_info = parse_query_intent(query)
    if not intent_info["complete"]:
        if "weather" == intent_info["likely_intent"]:
            say("Which city would you like the weather for?")
            city = takeCommand()
            if city not in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
                query = f"weather in {city}"
        elif "news" == intent_info["likely_intent"]:
            say("What topic would you like news about?")
            topic = takeCommand()
            if topic not in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
                query = f"news about {topic}"
        elif "open_website" == intent_info["likely_intent"]:
            say("Which website would you like to open?")
            website = takeCommand()
            if website not in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
                query = f"open {website}"
    
    pronouns = ["him", "her", "it", "them", "they", "that", "this", "those"]
    
    simple_followups = ["more", "continue", "go on", "and", "then", "next", "also"]
    
    if ((query in simple_followups or 
         query.startswith("more about") or 
         query in pronouns or
         any(query == p for p in pronouns)) and 
        conversation_context["last_topic"]):
        enhanced_query = f"tell me more about {conversation_context['last_topic']}"
        print(f"Enhanced query: '{query}' → '{enhanced_query}'")
        return enhanced_query
    
    common_prefixes = ["tell me", "show me", "give me", "what is", "who is"]
    for prefix in common_prefixes:
        if query.startswith(prefix.split()[-1]):
            print(f"Detected potential partial capture. Original: '{query}'")
            inferred_query = f"{prefix} {query[len(prefix.split()[-1]):].strip()}"
            print(f"Inferred query: '{inferred_query}'")
            return inferred_query
    
    if not any(verb in query for verb in ["tell", "show", "give", "what", "who", "how", "when", "where", "why", "is", "are", "was", "were", "will", "can", "could", "should", "would", "do", "does", "did"]):
        enhanced_query = f"tell me about {query}"
        print(f"Added context to query: '{query}' → '{enhanced_query}'")
        return enhanced_query
    
    return query

def confirm_query(query):
    """Confirm with the user if the query is what they intended."""
    say(f"I heard: {query}. Is that correct?")
    response = takeCommand()
    
    affirmative = ["yes", "yeah", "correct", "that's right", "right", "yep", "yup", "sure", "okay"]
    negative = ["no", "nope", "incorrect", "wrong", "not right", "not correct"]
    
    if any(word in response for word in affirmative):
        return query
    elif any(word in response for word in negative):
        say("Let me try again. What would you like to know?")
        new_query = takeCommand()
        if new_query not in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
            return new_query
        else:
            say("I'm having trouble understanding. Let's continue with what I heard earlier.")
            return query
    else:
        if response not in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
            return response
        else:
            return query

if __name__ == "__main__":
    print("Zenith is ready.")
    greet_user()

    while True:
        query = takeCommand()

        if query != "Sorry, I could not understand that." and query != "Error occurred." and query != "Sorry, listening timed out.":
            query = preprocess_query(query)
            
            if len(query.split()) <= 3 and not is_followup_query(query):
                query = confirm_query(query)
            
            if handle_followup_query(query):
                continue
                
            if respond_human_like(query):
                continue
            
            if "time" in query:
                now = datetime.datetime.now()
                current_time = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
                response = f"The current time is {current_time}"
                say(response)
                update_conversation_context(query, response)

            elif "news" in query:
                if "about" in query or "on" in query:
                    keyword = ""
                    if "about" in query:
                        keyword = query.split("about", 1)[1].strip()
                    elif "on" in query:
                        keyword = query.split("on", 1)[1].strip()
                    
                    if not keyword and len(query.split()) > 1:
                        keyword = " ".join(query.split()[query.split().index("news") + 1:])
                    
                    if keyword:
                        say(f"Fetching news about {keyword}, please wait.")
                        news = search_news(keyword)
                    else:
                        say("Fetching general news, please wait.")
                        news = get_news()
                else:
                    say("Fetching the latest news, please wait.")
                    news = get_news()
                
                say(news)
                update_conversation_context(query, news)

            elif "current affairs" in query:
                say("Fetching the latest current affairs, please wait.")
                news = get_news()
                say(news)
                update_conversation_context(query, news)

            elif "weather" in query:
                if "weather in" in query:
                    city = query.split("weather in")[-1].strip()
                elif "weather of" in query:
                    city = query.split("weather of")[-1].strip()
                elif "weather for" in query:
                    city = query.split("weather for")[-1].strip()
                else:
                    say("Please specify a city for the weather information.")
                    city = takeCommand()
                    if city in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
                        continue
                
                if city:
                    say(f"Fetching weather for {city}, please wait.")
                    weather = get_weather(city)
                    say(weather)
                    update_conversation_context(query, weather)

            elif "open" in query:
                website = query.split("open")[-1].strip()
                if not website:
                    say("Which website would you like to open?")
                    website = takeCommand()
                    if website in ["Sorry, I could not understand that.", "Error occurred.", "Sorry, listening timed out."]:
                        continue
                
                url = f"http://{website}" if not website.startswith("http") else website
                response = f"Opening {website}..."
                say(response)
                update_conversation_context(query, response)
                webbrowser.open(url)

            elif any(kw in query for kw in ["make it", "what if", "how to", "generate", "what is", "about", "write", "change it", "edit it", "modify it", "make this", "improve this", "make it more", "the previous", "previous content", "describe", "tell me"]):
                prompt = query
                say("Generating content, please wait.")
                generated_response = generate_content(prompt)
                last_generated_response = generated_response
                
                update_conversation_context(query, generated_response)
                
                say(clean_text(generated_response))

            elif "stop" in query or "exit" in query:
                say("Goodbye! Have a great day.")
                last_generated_response = None
                break
            else:
                say("Let me think about that...")
                response = generate_content(query)
                
                update_conversation_context(query, response)
                
                say(clean_text(response))
        else:
            say("I'm not sure I understand that command. Could you please repeat?")
