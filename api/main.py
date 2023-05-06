from flask import Flask,request
import json

app = Flask(__name__)

@app.route("/")
def home():
	return "HELLO from vercel use flask"

@app.route('/example', methods=['POST'])
def example():
	response = request.json
	print(response, type(response))
	if request.method == 'POST':
		data = request.form.getlist('data')
		print(data)
		return f"The data you sent is: {data}"

@app.route('/optimize_route', methods=['POST'])
def optimize_route():
	response = request.json
	latlongs = response['latlongs'].split(' , ')
	lats = list()
	longs = list()
	for i in range(0, len(latlongs), 2):
		lats.append(latlongs[i])
		longs.append(latlongs[i+1])
	print(lats)
	print(longs)
	

@app.route("/about")
def about():
	return "HELLO about"
