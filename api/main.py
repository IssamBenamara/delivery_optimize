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

@app.route("/about")
def about():
	return "HELLO about"
