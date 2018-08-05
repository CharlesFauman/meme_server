import pickle

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

import pandas as pd
import numpy as np
from keras.models import load_model

from Final_Memes.cleaning import cleaning_functions
from Final_Memes.analysis import analysis_functions

cleaning_meta_dict = pickle.load(open( "Final_Memes/cleaning/meta_dict.p", "rb" ))
analysis_meta_dict = pickle.load(open( "Final_Memes/analysis/meta_dict.p", "rb" ))
keras_model = load_model("Final_Memes/analysis/model.hdf5")
keras_model.summary()
keras_model.predict(np.zeros((1,) + keras_model.input_shape[1:]))

def preprocess_serialize(input_form, input_files):
	sentence = input_form
	cleaned = cleaning_functions.clean_sentence(cleaning_meta_dict, sentence)
	cleaned_as_df = pd.DataFrame(cleaned, columns = ["token", "pos", "sentiment"])
	sentence_matrix = np.expand_dims(analysis_functions.vectorize_sentence(analysis_meta_dict, cleaned_as_df), 0)
	return sentence_matrix.tolist()

def preprocess_deserialize(input_):
	return np.array(input_)

def process(batch):

	predictions = keras_model.predict(batch)
	meme_predictions = list()
	for prediction in predictions:
		scores = list()
		for index, val in enumerate(prediction):
			scores.append(tuple((analysis_meta_dict["meme_names"][index], np.float64(val))))
			
		meme_predictions.append(sorted(scores, key=lambda tup: tup[1], reverse=True))

	return meme_predictions

def postprocess_serialize(preds):
	return preds