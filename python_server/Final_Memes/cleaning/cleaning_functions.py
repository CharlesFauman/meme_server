import numpy as np
import re

from unidecode import unidecode

import string

import language_check

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('S'):
        return wordnet.ADJ_SAT
    else:
        return wordnet.NOUN # idk what to return here

def get_sentiment_pos(pos):
    if pos == wordnet.ADJ:
        return 'adj'
    elif pos == wordnet.NOUN:
        return 'noun'
    elif pos == wordnet.ADV:
        return 'adv'
    elif pos == wordnet.VERB:
        return 'verb'
    return None

def get_sentiment(meta_dict, lemma, pos):
    possible_sentiment = meta_dict["sentiments"][(meta_dict["sentiments"]['word'] == lemma).values]
    right_pos = set([pos, 'anypos'])
    right_sent = [(sent in right_pos) for sent in possible_sentiment['POS'].values]
    if pos is not None: possible_sentiment = possible_sentiment[right_sent]
    if(len(possible_sentiment) > 0):
        if(possible_sentiment.iloc[0]['priorpolarity'] == 'negative'):
            return 'negative'
        elif(possible_sentiment.iloc[0]['priorpolarity'] == 'positive'):
            return 'positive'
        else:
            return 'neutral'
    return 'neutral'

def get_lemma(meta_dict, tag):
    if tag[0] in meta_dict["stop_words_en"]:
        lemma = tag[0]
    else:
        lemma = meta_dict["lemmatizer"].lemmatize(tag[0], get_wordnet_pos(tag[1]))
    return (lemma, tag[1], get_sentiment(meta_dict, tag[0], get_sentiment_pos(tag[1])))

def clean_sentence(meta_dict, sentence):
	text = sentence
	# get text and remove the artificial newlines and numbers
	#text = re.sub("0|1|2|3|4|5|6|7|8|9", "", sentence.replace('\\n',' '))
	# spell correct the text and make unicode consistent
	text = unidecode(language_check.correct(text, meta_dict["language_check_tool"].check(text)).lower())
	# remove all punctuation
	#text = text.translate(str.maketrans('','',string.punctuation))
	# get treebank tokens
	tokens = word_tokenize(text)
	# get part of speech tags
	tags = nltk.pos_tag(tokens)
	# get lemmas and sentiment for tokens
	lemmas = [get_lemma(meta_dict, tag) for tag in tags]
	if len(lemmas) >= 3 and np.sum(np.array([x[0] for x in lemmas[-3:]]) == np.array(['make', 'on', 'imgur'])) >= 2:
		lemmas = lemmas[:-3]
	return lemmas