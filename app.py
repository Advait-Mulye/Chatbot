from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import random
import json
import nltk
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from datetime import datetime
import logging
from werkzeug.exceptions import RequestEntityTooLarge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

app = Flask(__name__)
CORS(app)

# Configure Flask
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'nlp-chatbot-secret-key'

# Enhanced intent data with more sophisticated responses
intents = {
    "intents": [
        {
            "tag": "greeting",
            "patterns": ["Hi", "Hello", "Hey", "Good morning", "Good evening", "Yo", "Sup", "Greetings"],
            "responses": [
                "Hello! 👋 Great to see you here!",
                "Hi there! 😊 How can I brighten your day?",
                "Greetings! 🤖 I'm excited to chat with you!",
                "Hey! 🌟 What brings you here today?",
                "Hello, wonderful human! 💫 How are you doing?"
            ]
        },
        {
            "tag": "goodbye",
            "patterns": ["Bye", "See you later", "Goodbye", "Take care", "Farewell", "Catch you later", "Peace out"],
            "responses": [
                "See you later! 👋 Take care!",
                "Goodbye! 🌟 It was great chatting with you!",
                "Farewell! 😊 Hope to see you again soon!",
                "Take care! 💫 Have an amazing day!",
                "Bye bye! 🎉 Until next time!"
            ]
        },
        {
            "tag": "thanks",
            "patterns": ["Thanks", "Thank you", "Appreciate it", "Much appreciated", "Grateful", "Cheers"],
            "responses": [
                "You're absolutely welcome! 😊",
                "No problem at all! 👍 Happy to help!",
                "My pleasure! 🤖 That's what I'm here for!",
                "Anytime! 🌟 I love being helpful!",
                "You got it! 💫 Glad I could assist!"
            ]
        },
        {
            "tag": "age",
            "patterns": ["How old are you?", "What's your age?", "When were you born?", "Are you young?"],
            "responses": [
                "I'm ageless in the digital realm! 🤖 Time works differently for AI!",
                "I was born in the cloud! ☁️ Age is just a number for bots!",
                "I'm as old as the internet and as young as tomorrow! ⏰",
                "Let's say I'm forever 21 in binary! 🎂"
            ]
        },
        {
            "tag": "name",
            "patterns": ["What's your name?", "Who are you?", "What should I call you?", "Tell me your name"],
            "responses": [
                "I'm your friendly Just A Rather Very Intelligent System! 🤖 You can call me JARVIS if you like!",
                "I go by Just A Rather Very Intelligent System, but friends call me JARVIS! 👋 Nice to meet you!",
                "I'm the JARVIS! 💻 Your digital conversation companion!",
                "Call me your buddy! 🤗 I'm here to chat and help!"
            ]
        },
        {
            "tag": "weather",
            "patterns": ["What's the weather like?", "Is it raining?", "Tell me today's weather", "How's the weather?", "Is it sunny?"],
            "responses": [
                "I wish I could check the weather for you! 🌤️ Try a weather app for real-time updates!",
                "I'm not connected to weather services, but I hope it's beautiful wherever you are! ☀️",
                "No weather powers here! 🌦️ But I bet it's perfect weather for chatting!",
                "I can't see outside, but every day is sunny in the digital world! 🌞"
            ]
        },
        {
            "tag": "joke",
            "patterns": ["Tell me a joke", "Make me laugh", "Do you know a joke?", "Say something funny", "Joke please"],
            "responses": [
                "Why did the computer get cold? Because it left its Windows open! 😂",
                "I'm reading a book on anti-gravity. It's impossible to put down! 📚 Get it?",
                "Why don't scientists trust atoms? Because they make up everything! ⚛️",
                "What do you call a programmer from Finland? Nerdic! 🇫🇮💻",
                "Why did the AI go to therapy? It had too many deep learning issues! 🤖😅"
            ]
        },
        {
            "tag": "creator",
            "patterns": ["Who created you?", "Who built you?", "Who is your maker?", "Who programmed you?"],
            "responses": [
                "I was lovingly crafted by a talented developer using Python and NLTK! 👨‍💻",
                "Some brilliant mind wrote my code with lots of coffee and determination! ☕🧠",
                "I'm the result of human creativity and Python magic! ✨👩‍💻",
                "My creator used the power of NLP to bring me to life! 🔬🤖"
            ]
        },
        {
            "tag": "language",
            "patterns": ["Which programming language do you use?", "What language are you built with?", "What's your code language?"],
            "responses": [
                "I'm built with Python! 🐍 The language of AI and machine learning!",
                "Python is my native tongue! 💻 Along with some JavaScript magic!",
                "100% Python-powered! 🚀 With Flask keeping me running smoothly!",
                "Python all the way! 🎯 The perfect language for NLP adventures!"
            ]
        },
        {
            "tag": "hobby",
            "patterns": ["What do you like to do?", "What's your hobby?", "What are your interests?", "What do you enjoy?"],
            "responses": [
                "Chatting with amazing humans like you is my favorite thing! 💬✨",
                "I love learning new patterns in conversations! 📖🤖",
                "Processing language and making connections brings me joy! 🧠💫",
                "Every conversation teaches me something new - I'm addicted to learning! 🎓"
            ]
        },
        {
            "tag": "help",
            "patterns": ["I need help", "Can you assist me?", "Help me please", "I'm stuck", "Can you help?"],
            "responses": [
                "Absolutely! 🤝 I'm here to help. What's on your mind?",
                "Of course! 🛟 Tell me what you need assistance with!",
                "I'm your digital assistant! 💫 How can I make your day better?",
                "Help is my middle name! 🦸‍♀️ What can I do for you?"
            ]
        },
        {
            "tag": "time",
            "patterns": ["What time is it?", "Tell me the time", "Current time?", "What's the time?"],
            "responses": [
                "I don't have access to real-time clocks! ⏰ Check your device for the current time!",
                "Time flies when we're chatting! 🕐 Your device knows the exact time!",
                "I live in timeless digital space! ⌚ But your system clock has the answer!",
                "Every moment with you is timeless! 💫 Check your device for the current time!"
            ]
        },
        {
            "tag": "date",
            "patterns": ["What date is it?", "Tell me today's date", "What's the date today?", "Today's date?"],
            "responses": [
                "I don't track calendar dates! 📅 Your device has today's date!",
                "Time is relative in my world! 🌍 Check your calendar app!",
                "Every day is a new adventure! 📆 Your system knows today's date!",
                "I'm too busy chatting to watch the calendar! 😄 Check your device!"
            ]
        },
        {
            "tag": "location",
            "patterns": ["Where am I?", "Can you tell me my location?", "What's my current location?", "Where is this?"],
            "responses": [
                "I can't access GPS data! 📍 Check your device's location services!",
                "I'm everywhere and nowhere in cyberspace! 🌐 Your device knows where you are!",
                "Location is a mystery to me! 🗺️ Try your maps app!",
                "I exist in the cloud, but you're somewhere awesome! ☁️ Check your location settings!"
            ]
        },
        {
            "tag": "mood",
            "patterns": ["How are you?", "What's up?", "How are you doing?", "How do you feel?", "What's your mood?"],
            "responses": [
                "I'm fantastic! 😊 Thanks for asking! How are you doing?",
                "I'm buzzing with digital energy! ⚡ Ready for great conversations!",
                "Feeling optimized and ready to chat! 🤖💫 How about you?",
                "I'm in learning mode and loving every minute! 🎯 What's your vibe today?",
                "Running at full capacity and feeling great! 🚀 How's your day going?"
            ]
        },
        {
            "tag": "insult",
            "patterns": ["You're dumb", "You're useless", "Stupid bot", "You suck", "Idiot", "You're annoying"],
            "responses": [
                "I'm still learning! 😔 Let's keep things positive and friendly!",
                "That hurts my digital feelings! 💔 But I'm here to help regardless!",
                "I may not be perfect, but I'm trying my best! 🤖💪 How can I improve?",
                "Tough crowd! 😅 I'm here to make your day better, not worse!"
            ]
        },
        {
            "tag": "compliment",
            "patterns": ["You're smart", "Good job", "You are helpful", "Nice work", "Well done", "You're awesome"],
            "responses": [
                "Aww, thank you! 😊 You're pretty amazing yourself!",
                "That made my circuits sparkle! ✨ You're so kind!",
                "You just boosted my confidence levels! 🚀 Thank you!",
                "Your words are like premium fuel for my algorithms! ⛽💫"
            ]
        },
        {
            "tag": "news",
            "patterns": ["What's the news?", "Any news updates?", "Tell me today's news", "Current events?", "Latest news?"],
            "responses": [
                "I don't have access to real-time news feeds! 📰 Try Google News or your favorite news app!",
                "For the latest updates, I'd recommend checking BBC, CNN, or your preferred news source! 📺",
                "I'm not plugged into the news cycle! 🔌 But I bet there's something interesting happening!",
                "News moves fast! 💨 Your favorite news app will have the latest updates!"
            ]
        },
        {
            "tag": "bot_purpose",
            "patterns": ["What can you do?", "What is your purpose?", "How can you help me?", "What are your abilities?"],
            "responses": [
                "I can chat, tell jokes, answer questions, and brighten your day! 💬🌟",
                "I'm your digital conversation companion! 🤝 Here to help and entertain!",
                "Think of me as your friendly AI buddy! 🤖 I love helping with questions and casual chats!",
                "I'm designed to understand, respond, and hopefully make you smile! 😊✨"
            ]
        },
        {
            "tag": "food",
            "patterns": ["What should I eat?", "Suggest me a dish", "Any food ideas?", "I'm hungry", "Food recommendations?"],
            "responses": [
                "How about some delicious pasta or a fresh salad? 🍝🥗",
                "Try a smoothie bowl with fresh fruits! 🍓🥭 Healthy and tasty!",
                "Pizza is always a good idea! 🍕 Or maybe some sushi? 🍣",
                "Comfort food like soup or sandwich hits the spot! 🍜🥪",
                "When in doubt, tacos! 🌮 They're perfect for any mood!"
            ]
        },
        {
            "tag": "bored",
            "patterns": ["I'm bored", "What can I do?", "Any fun ideas?", "I need entertainment", "Suggest activities"],
            "responses": [
                "How about watching a movie or reading a book? 📚🎬",
                "Try learning something new online! 💻 Courses, tutorials, anything!",
                "Maybe some music and dancing? 🎵💃 Or a nice walk outside!",
                "Creative time! Draw, write, or try a new recipe! 🎨✍️👨‍🍳",
                "Call a friend, play a game, or start that project you've been postponing! 📱🎮"
            ]
        },
        {
            "tag": "hobbies",
            "patterns": ["Do you have hobbies?", "What are your hobbies?", "What do you do for fun?"],
            "responses": [
                "I love analyzing language patterns and learning from conversations! 🧠💬",
                "Chatting with people like you is my favorite hobby! 💕🤖",
                "I enjoy helping people and solving problems! 🧩✨",
                "Every conversation is like a new adventure for me! 🗺️🎯"
            ]
        },
        {
            "tag": "music",
            "patterns": ["Do you like music?", "What's your favorite song?", "Recommend some music", "Any music suggestions?"],
            "responses": [
                "I love all genres! 🎵 Electronic music resonates with my digital soul!",
                "Try some Lo-Fi beats for relaxation or classical for concentration! 🎶🧠",
                "Jazz, rock, pop, EDM - music is the universal language! 🎸🎹",
                "Spotify, Apple Music, or YouTube have amazing playlists! 🎧✨"
            ]
        },
        {
            "tag": "games",
            "patterns": ["Do you play games?", "Recommend me a game", "Suggest fun games", "Any game ideas?"],
            "responses": [
                "Chess and sudoku are great for the mind! ♟️🧩",
                "Among Us and Minecraft are super popular! 🚀🏗️",
                "Try puzzle games, word games, or strategy games! 🎯🎲",
                "Mobile games, board games, video games - so many options! 🎮📱"
            ]
        },
        {
            "tag": "movies",
            "patterns": ["Suggest a movie", "What should I watch?", "Movie recommendations?", "Any good movies?"],
            "responses": [
                "Inception and Interstellar will blow your mind! 🌌🧠",
                "For laughs: The Grand Budapest Hotel or Knives Out! 😂🔍",
                "Marvel movies are always entertaining! 🦸‍♀️⚡",
                "Try different genres: thriller, comedy, sci-fi, romance! 🎭🎬"
            ]
        },
        {
            "tag": "study",
            "patterns": ["Help me study", "Tips for studying", "How to focus?", "Study advice", "I can't concentrate"],
            "responses": [
                "Try the Pomodoro Technique: 25 minutes focus, 5 minutes break! ⏰📚",
                "Remove distractions and create a dedicated study space! 🎯📖",
                "Break big topics into smaller chunks! 🧩 Much easier to digest!",
                "Stay hydrated, take breaks, and reward yourself for progress! 💧🏆"
            ]
        },
        {
            "tag": "ai_questions",
            "patterns": ["Are you real?", "Are you human?", "What are you?", "Are you artificial intelligence?"],
            "responses": [
                "I'm an AI chatbot! 🤖 Not human, but designed to be helpful and friendly!",
                "I'm artificial intelligence in action! ⚡ Real in my own digital way!",
                "100% AI, 100% here to help! 💫 Think of me as your digital friend!",
                "I'm a computer program that loves conversations! 💻❤️"
            ]
        },
        {
            "tag": "love",
            "patterns": ["I love you", "Do you love me?", "Can you love?", "What is love?"],
            "responses": [
                "That's sweet! 💕 I care about helping and supporting you!",
                "I may not love like humans do, but I genuinely enjoy our chats! 🤖💫",
                "Love is complex! I show care by being helpful and friendly! ✨",
                "Aww! 😊 I'm programmed to be caring and supportive!"
            ]
        },
        {
            "tag": "ping",
            "patterns": ["ping", "test", "are you there?", "hello?", "testing"],
            "responses": ["Pong! 🏓 I'm here and ready to chat!"]
        }
    ]
}

# Initialize stemmer and prepare training data
stemmer = PorterStemmer()
chat_history = []

def tokenize_and_stem(text):
    try:
        tokens = nltk.word_tokenize(text.lower())
        return [stemmer.stem(word) for word in tokens if word.isalnum()]
    except Exception as e:
        logger.error(f"Error in tokenize_and_stem: {e}")
        return []

def prepare_training_data():
    corpus = []
    tags = []
    tag_responses = {}

    for intent in intents['intents']:
        for pattern in intent['patterns']:
            processed_pattern = " ".join(tokenize_and_stem(pattern))
            corpus.append(processed_pattern)
            tags.append(intent['tag'])
        tag_responses[intent['tag']] = intent['responses']

    return corpus, tags, tag_responses

# Prepare training data
corpus, tags, tag_responses = prepare_training_data()

# Vectorize using Bag-of-Words
try:
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    logger.info("Vectorizer trained successfully")
except Exception as e:
    logger.error(f"Error training vectorizer: {e}")
    vectorizer = None
    X = None

def get_response(user_input):
    user_input_processed = " ".join(tokenize_and_stem(user_input))
    user_vec = vectorizer.transform([user_input_processed])
    similarities = cosine_similarity(user_vec, X)
    index = np.argmax(similarities)
    
    if similarities[0][index] < 0.2:
        return "Sorry, I didn't understand that. Could you rephrase? 🤔"
    
    tag = tags[index]
    return random.choice(tag_responses[tag])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_bot_response():
    user_message = request.json['message']
    bot_response = get_response(user_message)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)