# !/usr/bin/env python

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
		user_id = request.form['user_id']
		contacts = {}
		start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
		end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() +  timedelta(days=1)
		user = session.query(User).filter_by(id=int(user_id)).one()

		places = session.query(Location).filter(Location.date >= start_date).\
					filter(Location.date <= end_date).filter_by(user_id=user.id).all()
		moves = session.query(Location).all()
		allUsers = session.query(User).all()
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
								for u in allUsers:
									if u.id == move.user_id:
										temp.append(u.id)
										temp.append(u.name)
										temp.append(u.phone)
				if len(temp):
					tempDict[place.id].append(temp)
			contacts.update(tempDict)


		return render_template('results.html',
			user = user,
			places = places,
			start_date = start_date,
			end_date = end_date,
			contacts = contacts)
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
	contacts = [[] for i in range(int(length))]
	if(length):
		for i in range(int(length)):
			contacts[i].append(request.form['cont'+ str(i)+'lat'])
			contacts[i].append(request.form['cont'+ str(i)+'lng'])
			contacts[i].append(request.form['cont'+ str(i)+'name'])

		for lst in contacts:
			lats.append(lst[0])
			lons.append(lst[1])
			names.append(lst[2])

		

	show = ShowMap(float(mlat), float(mlng), lats, lons, names)
	show.getMap()


	return render_template('testMap.html',
			mname = mname,
			mlat = mlat,
			mlng = mlng,
			length = length,
			lons = lons,
			lats = lats,
			names = names,
			contacts = contacts)


if __name__ == "__main__":
	app.secret_key = 'Coro4321Track'
	app.run(debug=True)