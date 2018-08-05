import numpy as np

from keras.utils.np_utils import to_categorical
from gensim.models import Word2Vec

from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization, Conv1D, Flatten
from keras.models import load_model


def categorical_dict_from_list(unique_classes):
    categorical_dict = dict()
    for index, name in enumerate(unique_classes):
        categorical_dict[name] = to_categorical(index, num_classes = len(unique_classes))
    return categorical_dict

def data_dict_to_sents(data_dict):
    sentences = list()
    for meme_df in data_dict.values():
        for sentence in list(tuple(meme_df.groupby('meme_id'))):
            sentences.append(list(map(str, sentence[1]['token'])))
    return sentences

def vectorize_sentence(meta_dict, sentence_df):
	sentence_matrix = np.zeros((meta_dict["sentence_size"], meta_dict["embeddings"].vector_size + len(meta_dict["sentiment"]) + len(meta_dict["pos"])))
	sentence_index = 0
	for row in sentence_df.iterrows():
		token = row[1]["token"]
		pos = row[1]["pos"]
		sentiment = row[1]["sentiment"]
		if(token not in meta_dict["embeddings"].wv):
			sentence_matrix[sentence_index] = np.concatenate([np.zeros(meta_dict["embeddings"].vector_size), meta_dict["pos"][pos], meta_dict["sentiment"][sentiment]])
		else:
			sentence_matrix[sentence_index] = np.concatenate([meta_dict["embeddings"].wv[token], meta_dict["pos"][pos], meta_dict["sentiment"][sentiment]])
		sentence_index = sentence_index + 1
		if(sentence_index == meta_dict["sentence_size"]): break
	return(sentence_matrix)

def vectorize_meme_data(meta_dict, data_dict):
    data_list = list()
    y_list = list()
    for meme_name, meme_df in data_dict.items():
        for sentence_df in list(tuple(meme_df.groupby('meme_id'))):
            data_list.append(vectorize_sentence(meta_dict, sentence_df[1]))
            y_list.append(meta_dict["memes"][meme_name])
                
    return np.asarray(data_list), np.asarray(y_list)
	
def create_model(meta_dict):
	model = Sequential()

	model.add(BatchNormalization(input_shape = (meta_dict["sentence_size"], meta_dict["embeddings"].vector_size + len(meta_dict["sentiment"]) + len(meta_dict["pos"]))))
	model.add(Conv1D(filters = 64, kernel_size = 15, strides=1, padding='same'))
	model.add(BatchNormalization())
	model.add(Dropout(.5))
	model.add(Conv1D(filters = 32, kernel_size = 8, strides=1, padding='same'))
	model.add(BatchNormalization())
	model.add(Dropout(.5))
	model.add(Conv1D(filters = 32, kernel_size = 8, strides=2, padding='same'))
	model.add(Conv1D(filters = 32, kernel_size = 4, strides=1, padding='same'))
	model.add(Conv1D(filters = 32, kernel_size = 4, strides=1, padding='same'))

	model.add(Flatten())
	model.add(Dropout(.5))
	model.add(Dense(len(meta_dict["meme_names"]), activation='softmax'))

	model.compile(loss='categorical_crossentropy',
	              optimizer='adam',
	              metrics=['accuracy'])
	model.summary()
	
	return model
	
def create_model_old(meta_dict):
	model = Sequential()

	model.add(LSTM(units = len(meta_dict["meme_names"]), recurrent_dropout = .6, input_shape = (meta_dict["sentence_size"], meta_dict["embeddings"].vector_size + len(meta_dict["sentiment"]) + len(meta_dict["pos"]))))
	model.add(Dense(len(meta_dict["meme_names"]), activation='softmax'))

	model.compile(loss='categorical_crossentropy',
				  optimizer='adam',
				  metrics=['accuracy'])
	model.summary()

	return model
	
def eval_top_k(model, data, y, k):
    y_ = model.predict(data).argsort()[:,-k:]
    y_real = np.argmax(y, axis = 1)[:,None]
    sol = np.any(y_ == y_real, axis = 1)
    return(sum(sol)/len(sol))