#!/usr/bin/python3
#export FLASK_APP=testSite.py

#$ flask run
# * Running on http://127.0.0.1:5000/
from flask import Flask
from flask import render_template, url_for, request, redirect
#import pymongo
#from user import *

app = Flask(__name__)

@app.route('/')
def hello_world():
	return render_template('./index.html')

@app.route('/about')
def about():
	return render_template('./about.html')
	
@app.route('/estimate', methods = ['GET', 'POST'])
def estimate():
	user = '1234'
	if request.method == 'GET':

		return render_template('./estimate.html', user=user)
	else:
		data = request.form.to_dict()
		try:
			if data['radius'] and data['height']:
				pi = 3.14
				topArea = float(pi*(float(data['radius'])**2))
				sideArea = float(2.00*(pi*(float(data['radius'])*float(data['height']))))
				totalArea = topArea + sideArea
				totalEst = (totalArea*25.00)+(totalArea*15.00)
				gotEstimate = True
				est = str(totalEst)
				return render_template('./estimate.html', gotEstimate=gotEstimate, est=est)
			else:
				raise Exception("Missing either radius or height data")
		except Exception as e:
			gotEstimate = False
			print(e)
			error = 'Error Checking Estimate'
			return render_template('./estimate.html', gotEstimate=gotEstimate, error=error)
"""
@app.route('/login', methods = ['GET'])
def login():
	if flask.request.method == "POST"
		user = '1234'
		return render_template('./login.html', user=user)
	else:
		user = None
		return render_template('./login.html', user=user)
@app.route('/register', methods = ['GET'])
def register():
	user = '1234'
	return render_template('./register.html', user=user)
	"""