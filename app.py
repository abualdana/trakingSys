# !/usr/bin/env python3

from flask import Flask, render_template, request, redirect, flash
from setupdb import Base, User, Location
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, func, or_
from datetime import datetime, timedelta
from math import sin, cos, sqrt, atan2, radians
from showMap import ShowMap

app = Flask(__name__)

engine = create_engine(
    'sqlite:///dataset.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST', 'GET'])
def search():
	try:
		# To get the distance between to locations
		def distance(lat1, lng1, lat2, lng2):
			R = 6373.0
			lat1 = radians(lat1)
			lon1 = radians(lng1)
			lat2 = radians(lat2)
			lon2 = radians(lng2)
			dlon = lon2 - lon1
			dlat = lat2 - lat1
			a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
			c = 2 * atan2(sqrt(a), sqrt(1 - a))
			distance = R * c
			# distance in KM
			distance *= 1000
			return distance
		
		# Get all places original user visited and compare the distance with specific location (1)
		def userHistoryPlaces(usr_id, lat, lng, u_date):
			history = session.query(Location).filter_by(user_id=usr_id).all()
			for place in history:
				list_location = []
				if place.date > u_date:
					time = place.date - u_date
				else:
					time = u_date - place.date
					
				if place.date.date() == u_date.date():
					if distance(float(place.lat), float(place.lng), float(lat), float(lng)) < 20:
						if time.total_seconds() / 60**2 < 1:
							list_location.append(place.lat)
							list_location.append(place.lng)
							return list_location
			return list_location
			    

		user_id = request.form['user_id']
		contacts = {}
		start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
		end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() +  timedelta(days=1)
		user = session.query(User).filter_by(id=int(user_id)).one()

		places = session.query(Location).filter(Location.date >= start_date).\
					filter(Location.date <= end_date).filter_by(user_id=user.id).all()
		moves = session.query(Location).all()
		allUsers = session.query(User).all()
		
		# Collect IDs of all contacts (2)
		id_all_contacts = []
		current_date_all_contacts = []
		
		
		for place in places:
			tempDict = {place.id: []}
			for move in moves:
				temp = []
				if place.date > move.date:
					time = place.date - move.date
				else:
					time = move.date - place.date
				if place.date.date() == move.date.date():
					if distance(float(place.lat), float(place.lng), float(move.lat), float(move.lng)) < 20:
						if time.total_seconds() / 60**2 < 1:
							if place.id != move.id:
								temp.append(move.id)
								temp.append(move.lat)
								temp.append(move.lng)
								temp.append(move.date)
								current_date_all_contacts.append(move.date)
								for u in allUsers:
									if u.id == move.user_id:
										temp.append(u.id)
										id_all_contacts.append(u.id)
										temp.append(u.name)
										temp.append(u.phone)
										temp.append(u.dob)
										temp.append(u.dplace)
										temp.append(u.nationality)
				if len(temp):
					tempDict[place.id].append(temp)
			contacts.update(tempDict)
		end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
		
		# loop through users IDs to get all history with the guy we are searching for (3)
		users_history ={}
		if len(id_all_contacts):
			for id_user in id_all_contacts:
				temp_dict = {id_user: []}
				temp_list = []
				user_history = session.query(Location).filter_by(user_id= id_user).all()
				for user_place in user_history:
					if user_place.date not in current_date_all_contacts:
						main_user = userHistoryPlaces(user_id, user_place.lat, user_place.lng, user_place.date)
						if len(main_user):
							temp_list.append(user_place.date.time())
							temp_list.append(user_place.date.date())
							temp_list.append(user_place.location)
							temp_list.append(user_place.lat)
							temp_list.append(user_place.lng)							
							temp_list.append(main_user[0]) # lat
							temp_list.append(main_user[1]) # lng
						
					if len(temp_list):
						temp_dict[id_user].append(temp_list)
					users_history.update(temp_dict)
					temp_list = []
			    
		
		return render_template('results.html',
			user = user,
			places = places,
			start_date = start_date,
			end_date = end_date,
			contacts = contacts,
			users_history = users_history)
	except:
		message = "No data is found for \"" + str(request.form['user_id']) +'"'
		flash(message)
		return redirect('/')

@app.route('/map', methods=['POST', 'GET'])
def map():
	length = request.form['length']
	mname = request.form['mname']
	mlat = request.form['mlat']
	mlng = request.form['mlng']
	lats = []
	lats.append(mlat)
	lons = []
	lons.append(mlng)
	names = []
	names.append(mname)
	if(length and length != 'history'):
		contacts = [[] for i in range(int(length))]
		for i in range(int(length)):
			contacts[i].append(request.form['cont'+ str(i)+'lat'])
			contacts[i].append(request.form['cont'+ str(i)+'lng'])
			contacts[i].append(request.form['cont'+ str(i)+'name'])

		for lst in contacts:
			lats.append(lst[0])
			lons.append(lst[1])
			names.append(lst[2])

	if(length == 'history'):
		lats.append(request.form['lat'])
		lons.append(request.form['lng'])
		names.append(request.form['name'])

	show = ShowMap(float(mlat), float(mlng), lats, lons, names)
	show.getMap()


	return render_template('testMap.html')


if __name__ == "__main__":
	app.secret_key = 'Coro4321Track'
	app.run(debug=True)
