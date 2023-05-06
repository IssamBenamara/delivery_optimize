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
	for latlong in latlongs:
		lat, long = latlong.split(',')
		lats.append(lat.strip())
		longs.append(long.strip())
	print(lats)
	print(longs)
	return 'Success'

@app.route('/read_orders_ids', methods=['POST'])
def read_orders_ids():
	response = request.json
	date = response['orders_ids']
	print(date)
	return 'Success'

@app.route("/about")
def about():
	return "HELLO about"
