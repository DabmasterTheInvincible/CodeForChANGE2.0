import streamlit as st
import nltk
import pickle
import json
import random
import numpy as np
from nltk.stem import WordNetLemmatizer
from keras.models import load_model

# Initialize the lemmatizer
nltk.download('punkt_tab')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# Load model and necessary files
model = load_model("model.h5")
intents = json.loads(open("intents.json").read())
words = pickle.load(open("texts.pkl", "rb"))
classes = pickle.load(open("labels.pkl", "rb"))

# Function to clean and preprocess user input
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Convert sentence to bag of words
def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

# Predict class from model
def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

# Get chatbot response
def get_response(ints, intents_json):
    if ints:
        tag = ints[0]["intent"]
        for intent in intents_json["intents"]:
            if intent["tag"] == tag:
                return random.choice(intent["responses"])
    return "I'm here for you. How can I help?"

# Streamlit App Interface
st.title("🧠 Mental Health Chatbot")
st.write("Chat with me! I'm here to listen.")

# Chat UI
user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        intent_prediction = predict_class(user_input, model)
        chatbot_response = get_response(intent_prediction, intents)
        st.text_area("Chatbot:", chatbot_response, height=100, disabled=True)
    else:
        st.warning("Please enter a message.")

st.write("🩵 Remember, I'm just a chatbot. If you're struggling, consider seeking professional help.")
