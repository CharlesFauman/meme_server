# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@jemma.png 'http://localhost:5000/predict'
# Submita a request via Python:
#	python simple_request.py 

# import the necessary packages
import numpy as np
from threading import Thread
import flask
import redis
import uuid
import time
import json
import sys
import io

# initialize constants used for server queuing
PROCESSING_QUEUE = "processing_queue"
BATCH_SIZE = 32
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25

# initialize our Flask application, Redis server, and Keras model
app = flask.Flask(__name__)
db = redis.StrictRedis(host="localhost", port=6379, db=0)
db.flushdb()

print("* Loading model...")

import meme_model as model

print("* Model loaded")


def classify_process():

	# continually pool for new inputs to classify
	while True:
		# attempt to grab a batch of inputs from the database, then
		# initialize the input IDs and batch of inputs themselves
		queue = db.lrange(PROCESSING_QUEUE, 0, BATCH_SIZE - 1)
		inputIDs = []
		batch = None

		# loop over the queue
		for q in queue:
			# deserialize the object and obtain the input
			q = json.loads(q)
			input_ = model.preprocess_deserialize(q["input"])

			# check to see if the batch list is None
			if batch is None:
				batch = input_

			# otherwise, stack the data
			else:
				batch = np.vstack([batch, input_])

			# update the list of input IDs
			inputIDs.append(q["id"])

		# check to see if we need to process the batch
		if len(inputIDs) > 0:
			# classify the batch
			print("* Batch size: {}".format(batch.shape))
			preds = model.process(batch)
			preds = model.postprocess_serialize(preds)

			# loop over the image IDs and their corresponding set of
			# results from our model
			for (inputID, result) in zip(inputIDs, preds):
				db.set(inputID, json.dumps(result))

			# remove the set of images from our queue
			db.ltrim(PROCESSING_QUEUE, len(inputIDs), -1)

		# sleep for a small amount
		time.sleep(SERVER_SLEEP)

@app.route("/predict", methods=["POST"])
def predict():
	# initialize the data dictionary that will be returned from the
	# view
	data = {"success": False}

	print("predicting!")

	# ensure an input was properly uploaded to our endpoint
	if flask.request.method == "POST":
		print("was post!")
		input_form = None
		input_files = None
		if(flask.request.form.get("input")):
			input_form = flask.request.form.get("input")
		if(flask.request.files.get("input")):
			input_files = flask.request.files.get("input").read()
		if input_form or input_files:
			input_ = model.preprocess_serialize(input_form, input_files)

			# generate an ID for the classification then add the
			# classification ID + input to the queue
			k = str(uuid.uuid4())
			d = {"id": k, "input": input_}

			db.rpush(PROCESSING_QUEUE, json.dumps(d))

			# keep looping until our model server returns the output
			# predictions
			while True:
				# attempt to grab the output predictions
				output = db.get(k)

				# check to see if our model has classified the input
				if output is not None:
 					# add the output predictions to our data
 					# dictionary so we can return it to the client
					data["predictions"] = json.loads(output)

					# delete the result from the database and break
					# from the polling loop
					db.delete(k)
					break

				# sleep for a small amount to give the model a chance
				# to classify the input
				time.sleep(CLIENT_SLEEP)

			# indicate that the request was a success
			data["success"] = True

	# return the data dictionary as a JSON response
	return flask.jsonify(data)

# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	# load the function used to classify input images in a *separate*
	# thread than the one used for main classification
	print("* Starting model service...")
	t = Thread(target=classify_process, args=())
	t.daemon = True
	t.start()

	# start the web server
	print("* Starting web service...")
	app.run()