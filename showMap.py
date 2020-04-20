import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
"""
To plot on Mapbox maps with Plotly you may need a Mapbox account and a public 
Mapbox Access Token (https://studio.mapbox.com). 
See our Mapbox Map Layers documentation (https://plotly.com/python/mapbox-layers) for more information.
"""
class ShowMap():
	mapbox_access_token = "pk.eyJ1Ijoia2doYXppIiwiYSI6ImNrOTVkeXdiajBqeDMzZm8xYTMzcm9sZG4ifQ.x2gdCAn4-4_dnJ_H9-hiOg"
	"""docstring for ShowMap"""
	def __init__(self, mlat, mlng, lats, lons, names ):
		self.mlat = mlat
		self.mlng = mlng
		self.lats = lats
		self.lons = lons
		self.names = names

	def getMap(self):
		
		fig = go.Figure(go.Scattermapbox(
		        lat=self.lats,
		        lon=self.lons,
		        mode='markers',
		        marker=go.scattermapbox.Marker(
		            size=9
		        ),
		        text=self.names,
		    ))

		fig.update_layout(
			title="Saudi Arabia",
		    autosize=True,
		    hovermode='closest',
		    mapbox=dict(
		        accesstoken=mapbox_access_token,
		        bearing=0,
		        center=dict(
		            lat=self.mlat,
		            lon=self.mlng
		        ),
		        pitch=0,
		        zoom=10
		    ),
		)

		fig.show()