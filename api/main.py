from flask import Flask,request
import os
import googlemaps
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from itertools import permutations
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
	if len(latlongs)==0:
		print('Nothing to Optimize')
		return "Error: empty request"
	
	opti = heavy_calc(response)
	if opti == 'No Optimization':
		print('No Optimization Found')
		return "Error: no optimization found"
	
	print(opti)
	return opti

@app.route('/read_orders_ids', methods=['POST'])
def read_orders_ids():
	response = request.json
	date = response['orders_ids']
	print(response)
	return 'Success'

@app.route("/about")
def about():
	return "HELLO about"


def heavy_calc(reponse):
	
	delivery_date = response['delivery_day']
	delivery_time = response['delivery_start_time'][:5]
	orders_ids = response['orders_ids'].split(' , ')
	latlongs = [(latlng.split(',')[0].strip(), latlng.split(',')[1].strip()) for latlng in response['latlongs'].split(' , ')]
	until_times = response['until_times'].split(' , ')
	from_times = response['from_times'].split(' , ')

	df_dict = {
		'order_id': orders_ids,
		'latlng': latlongs,
		'from_time': from_times,
		'until_time': until_times
	}

	df = pd.DataFrame(df_dict)
	df.index = list(range(1, len(df)+1))
	
	maps_addresses = [
    {
        'order_id': 'Dallas Shop',
        'latlng': (36.7378861, 3.2742079)
    }]

	for i in range(len(orders_ids)):
		tmp = {
			'order_id': orders_ids[i],
			'latlng': tuple(map(float,latlongs[i]))
		}
		maps_addresses.append(tmp)


	delivery_date_time = datetime.strptime(f'{delivery_date} {delivery_time}', '%d/%m/%Y %H:%M')
	steps = maps_addresses + [maps_addresses[0]]
	print(f'Total deliveries : {len(steps)-2}')
	print('Date and time:', delivery_date_time.strftime('%d/%m/%Y %H:%M'))

	gmaps = googlemaps.Client(key=os.environ['maps_key'])

	pairs = {}
	for per in permutations(range(len(steps)-1),2):
		start_location = steps[per[0]]['latlng']
		end_location = steps[per[1]]['latlng']

		directions_result = gmaps.directions(start_location,
											end_location,
											mode="driving")
		duration = directions_result[0]['legs'][0]['duration']['value']/60
		pairs[per] = duration
	
	def ftw(tw):
		return datetime.strptime(f'{delivery_date_time.strftime("%d/%m/%y")} {tw}', '%d/%m/%y %H:%M')
	
	constraints = dict()
	for row_id, row in df.iterrows():
		if not(row['from_time'] or row['until_time']):
			continue
		from_h = '09:00'
		to_h = '22:00'

		if row['from_time']:
			from_h = row['from_time']
		if row['until_time']:
			to_h = row['until_time']

		constraints[row_id] = {'from': ftw(from_h), 'until': ftw(to_h)}


	SAMPLE = False
	SAMPLE_RATE = 0.1
	if len(orders_ids)>8:
		SAMPLE = True

	best_path = None
	best_time = 10000000
	best_arrival_times = []
	time_per_client = 10
	max_early_waiting = 30

	for combination in permutations(list(range(1,len(steps)-1)), len(steps)-2):
		if np.random.random() <= SAMPLE_RATE and SAMPLE:
			continue
		arrival_times = [delivery_date_time]
		combi = [0]+list(combination)+[0]
		combi_total_time = 0
		combi_current_time = delivery_date_time
		timedelta(minutes=duration)
		for i in range(0, len(combi)-1):
			couple = (combi[i], combi[i+1])
			road_time = pairs[couple]
			combi_total_time += road_time + time_per_client
			combi_current_time += timedelta(minutes=road_time)
			arrival_times.append(combi_current_time)
			if couple[1] in constraints and (combi_current_time >= constraints[couple[1]]['until'] or combi_current_time <= constraints[couple[1]]['from']-timedelta(minutes=max_early_waiting)):
				combi_total_time = 10000000
				break
			combi_current_time += timedelta(minutes=time_per_client)
			if combi_total_time > best_time:
				break
		if combi_total_time < best_time:
			best_path = combi
			best_time = combi_total_time
			best_arrival_times = arrival_times

	if best_time == 10000000:
		print('\n\nNo Optimization Found')
		return 'No Optimization'
	else:
		print("\nBest time", '{:2d}h {:2d}m'.format(*divmod(int(best_time), 60)).replace('  ', ' '))
	
	tmp = df.copy()
	for i, step in enumerate(best_path[1:-1]):
		tmp.loc[step, 'arrival_time'] = best_arrival_times[i+1].strftime('%H:%M')
	tmp = tmp.sort_values(['arrival_time'])
	first_row = pd.DataFrame.from_dict({'order_id': ['Depart Rouiba'], 'arrival_time': [best_arrival_times[0].strftime('%H:%M')]}, orient='columns')
	last_row = pd.DataFrame.from_dict({'order_id': ['Retour Rouiba'], 'arrival_time': [best_arrival_times[-1].strftime('%H:%M')]}, orient='columns')
	optimized_route = pd.concat([first_row, tmp, last_row]).fillna('')

	return optimized_route.iloc[1:-1].to_json(orient='index')
