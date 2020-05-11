# -*- coding: utf-8 -*-

import sys


from chatterbot.logic import LogicAdapter
from chatterbot import ChatBot
from textblob.classifiers import NaiveBayesClassifier
from chatterbot.conversation import Statement
from chatterbot.trainers import ChatterBotCorpusTrainer
#from chatterbot.database import Database
import os
import json
import inspect
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier

from gtts import gTTS
import speech_recognition as sr
from functions import *
from database import Database

greetbot = ChatBot('greetings')
greet_trainer = ChatterBotCorpusTrainer(greetbot)
blockPrint()
greet_trainer.train(
    "chatterbot.corpus.english.greetings",
    "chatterbot.corpus.english.conversations"
)

database_path = os.path.dirname(os.path.realpath(inspect.getfile(Database.__init__)))
training_database = json.load(open(database_path + "/" + "query_adapter_training.json"))['data']

training_data = [(data,int(classe)) for classe in ["0", "1"] for data in training_database[classe]]

nb_clf = NaiveBayesClassifier(training_data)

qdata = Database('query_data', database_path, parse_db = True)

fields = Database('fields', database_path)

clf_trained, vectorizer, class_names = train_feature_finder(fields.db, RandomForestClassifier(n_estimators=20))


def run():
    say_it("Can i help you find joining dates of personnel ?")

    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index = 1)
    
    
    guess = recognize_speech_from_mic(recognizer, microphone)
    
    if not guess["success"]:
        print("I didn't catch that. What did you say?\n")
    
    print(guess["transcription"])
    statement = Statement(guess["transcription"].lower())
    
    confidence = nb_clf.classify(statement.text)
    
    if confidence > 0.5 :
        entry_list = predict_filter_key(statement.text, qdata)
        query = predict_feature(statement.text, vectorizer, clf_trained, class_names)
        output = respond(entry_list, query, qdata)
    else :
        output = greetbot.get_response(statement.text).text
    
    say_it(output)

if __name__ == '__main__':
    while True:
        try:
            run()
        except(KeyboardInterrupt, EOFError, SystemExit):
            break
        


