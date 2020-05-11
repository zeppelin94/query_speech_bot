# -*- coding: utf-8 -*-

import os
import sys
from sklearn.feature_extraction.text import CountVectorizer

from gtts import gTTS
import speech_recognition as sr
#from playsound import playsound
from mutagen.mp3 import MP3
import time


def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def recognize_speech_from_mic(recognizer, microphone):
    
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #     update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def train_feature_finder(training_db, clf):
    training_sentences = []
    c = 0
    training_classes = []
    class_names = []
    vectorizer = CountVectorizer(analyzer = "word",   \
                          tokenizer = None,    \
                          preprocessor = None, \
                          stop_words = None,   \
                          max_features = 500)
    for key, value in training_db.items():
        training_sentences += value
        training_classes += [c for i in range(len(value))] 
        c+=1
        class_names.append(key)
    train_data_features = vectorizer.fit_transform(training_sentences)
    train_data_features = train_data_features.toarray()
    clf = clf.fit( train_data_features, training_classes)
    return clf, vectorizer, class_names


def predict_feature(sentence, vectorizer, clf, class_names):
    sentence_vect = vectorizer.transform([sentence])
    sentence_vect = sentence_vect.toarray()
    class_id = clf.predict(sentence_vect)
    class_id = class_id[0]
    feature = class_names[class_id]
    return feature


def predict_filter_key(sentence, qdata):
    lst = []
    for chunk in sentence.split():
        if is_in_field_of_value(chunk, qdata.index['name']):
            lst.append(chunk)
    return lst


def is_in_field_of_value(chunk, list_of_values):
    return (chunk in list_of_values)

def build_query(statement, qdata, vectorizer, clf, class_names):
    entry = None
    query = None
    query = predict_feature(statement)
    entry = predict_filter_key(statement)

    return entry, query

def list_to_sent(lt):
    if(len(lt)>1):
        sent = " ".join(nm for nm in lt)
        #sent = sent [:-1]
    else:
        sent = lt[0]
    return sent

def read_all_names(lt):
    read = ", ".join(nms for nms in lt)
    #read = read[2:]
    return read


def get_element(entry_list, query, qdata):
    element_count = 0
    names_list = []
    join_date = []
    for partner in qdata.db:
        if sorted(entry_list) == sorted(list(set(entry_list) & set(partner['name']))) :
            element_count += 1
            names_list.append(list_to_sent(partner['name']))
            join_date.append(partner[query])            
    if(element_count>1):
        return True, names_list
    else:
        return False, join_date
    
    

def respond(entry_list, query ,qdata):
    multi_entry_flag, result = get_element(entry_list, query, qdata)
    if multi_entry_flag:
        return ("i have found multiple entries of %s. %s. Can you give the full name" % (
            list_to_sent(entry_list), read_all_names(result)))
    else:
        return ("The joining date of %s is %s" % (list_to_sent(entry_list), list_to_sent(result)))
    
    
def say_it(msg):
    print(msg)
    language = 'en'
    myobj = gTTS(text=msg, lang=language, slow=False)
    myobj.save("msg_temp.mp3")
    length = MP3("msg_temp.mp3").info.length
    #playsound("msg_temp.mp3")
    os.system("msg_temp.mp3")
    time.sleep(length)
    
    
    
    