# !/usr/bin/env python

from flask import Flask, render_template, request, redirect, flash
from setupdb import Base, User, Location
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, func
from datetime import datetime, timedelta


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
	# try:
	start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
	end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() +  timedelta(days=1)
	user = session.query(User).filter_by(id=request.form['user_id']).one()

	places = session.query(Location).filter(Location.date >= start_date).filter(Location.date <= end_date).filter_by(user_id=user.id).all()
	contacts = []

	return render_template('results.html',
		user = user,
		places = places,
		start_date = start_date,
		end_date = end_date)
	# except:
	# 	message = "No data is found for \"" + str(request.form['user_id']) +'"'
	# 	flash(message)
	# 	return redirect('/')

if __name__ == "__main__":
	app.secret_key = 'Coro4321Track'
	app.run(debug=True)