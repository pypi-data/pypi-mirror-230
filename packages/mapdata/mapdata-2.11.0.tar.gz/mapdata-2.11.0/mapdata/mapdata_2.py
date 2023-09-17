#!/usr/bin/python
#
# mapdata.py
#
# PURPOSE
#	Create a simple map of data points that can be saved to a static
#	image file.
#
# COPYRIGHT AND LICENSE
#	Copyright (c) 2022, R. Dreas Nielsen
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
# 	The GNU General Public License is available at <http://www.gnu.org/licenses/>
##
# NOTES
#	1. 
#
# AUTHOR
#	Dreas Nielsen (RDN)
#
# HISTORY
#	 Date		 Remarks
#	----------	-----------------------------------------------------
#	2022-01-15	Created.  RDN.
#	2022-06-28	Modified background selection and image creation,
#				using code from map_cormix.py.  RDN.
#	2022-06-29	Fixes and tweaks.  Added 'annot_zoom', 'width', and
#				'height' as parameters to make_map() and as
#				command-line options.  RDN.
# ==================================================================

__version__ = "0.3.0"
__vdate = "2022-06-28"


import argparse
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


def geo_bounds(df, lat, lon):
	# Return min, max X (lon) and Y (lat)
	x = list(df[lon])
	y = list(df[lat])
	return min(x), max(x), min(y), max(y)

def zoomedbounds(bounds, zoom=2):
	# bounds is a tuple of xmin, xmax, ymin, ymax.
	xrange = bounds[1] - bounds[0]
	yrange = bounds[3] - bounds[2]
	xmid = (bounds[0] + bounds[1]) / 2
	ymid = (bounds[2] + bounds[3]) / 2
	if yrange > xrange:
		ofs = zoom * (ymid - bounds[2])
	else:
		ofs = zoom * (xmid - bounds[0])
	return xmid-ofs, xmid+ofs, ymid-ofs, ymid+ofs


def make_map(points_dataframe, lat="y_coord", lon="x_coord", name="location_id",
		background="OSM", outfile_name="location_map.png", width=8.0, height=8.0,
		data_zoom=2, annot_zoom=7, show=False):
	if background == "OSM":
		bkgd = cimgt.OSM()
	elif background == "GoogleStreet":
		bkgd = cimgt.GoogleTiles(style="street")
	elif background == "GoogleSatellite":
		bkgd = cimgt.GoogleTiles(style="satellite")
	elif background == "GoogleTerrain":
		bkgd = cimgt.GoogleTiles(style="terrain")
	else:
		bkgd = cimgt.Stamen(background)
	fig = plt.figure(figsize=(width, height))
	ax = fig.add_subplot(1, 1, 1, projection=bkgd.crs)
	fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
	bounds = zoomedbounds(geo_bounds(points_dataframe, lat, lon), data_zoom)
	ax.set_extent([*bounds], crs=ccrs.PlateCarree())
	sc = ax.scatter(
			x = points_dataframe[lon],
			y = points_dataframe[lat],
			color = "red",
			s = 4,
			alpha = 0.6,
            transform = ccrs.PlateCarree()
			)
	ax.add_image(bkgd, annot_zoom)
	if outfile_name is not None:
		plt.savefig(outfile_name)
	if show:
		# Hover code from https://stackoverflow.com/questions/7908636/how-to-add-hovering-annotations-in-matplotlib 
		annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
				bbox=dict(boxstyle="round", fc="w"),
				arrowprops=dict(arrowstyle="->"))
		annot.set_visible(False)
		def update_annot(ind):
			pos = sc.get_offsets()[ind["ind"][0]]
			annot.xy = pos
			text = " ".join(points_dataframe[name][n] for n in ind["ind"])
			annot.set_text(text)
			annot.get_bbox_patch().set_alpha(0.4)
		def hover(event):
			vis = annot.get_visible()
			if event.inaxes == ax:
				cont, ind = sc.contains(event)
				if cont:
					update_annot(ind)
					annot.set_visible(True)
					fig.canvas.draw_idle()
				else:
					if vis:
						annot.set_visible(False)
						fig.canvas.draw_idle()
		fig.canvas.mpl_connect("motion_notify_event", hover)
		plt.show()





def clparser():
	desc_msg = "Create a static map image displaying points read from a CSV file. Version %s, %s" % (__version__, __vdate)
	parser = argparse.ArgumentParser(description=desc_msg)
	parser.add_argument('point_data_file',
			help="The name of a data file containing latitude and longitude coordinates, and an identifier")
	parser.add_argument('output_image_file',
			help="The name of the image file to create")
	parser.add_argument('-a', '--annot_zoom', type=int, default=7,
			help="Map annotation zoom level; good values are 6-8.")
	parser.add_argument('-b', '--background', choices=['OSM', 'terrain', 'toner', 'watercolor', 
			'GoogleStreet', 'GoogleSatellite', 'GoogleTerrain'],
			default='OSM',
			help='The name of the background layer to use.')
	parser.add_argument('-i', '--identifier', default='location_id', dest='id',
			help="The name of the column in the data file containing location identifiers")
	parser.add_argument('-s', '--show', default=False, action='store_true', dest='show',
			help="Whether or not to display the map as well as saving it to a file")
	parser.add_argument('-t', '--height', type=float, default=8.0,
			help="The height of the figure, in inches")
	parser.add_argument('-w', '--width', type=float, default=8.0,
			help="The width of the figure, in inches")
	parser.add_argument('-x', '--lon', default='x_coord', dest='lon',
			help="The name of the column in the data file containing longitude values")
	parser.add_argument('-y', '--lat', default='y_coord', dest='lat',
			help="The name of the column in the data file containg latitude values")
	parser.add_argument('-z', '--data_zoom', type=float, default=2.0,
			help="With a data zoom factor of 1.0, the points will span the image; larger numbers zoom out.")

	return parser



def main():
	p= clparser().parse_args()
	pts = pd.read_csv(p.point_data_file)
	make_map(pts, lat=p.lat, lon=p.lon, name=p.id, background=p.background,
			outfile_name=p.output_image_file, width=p.width, height=p.height,
			data_zoom=p.data_zoom, annot_zoom=p.annot_zoom, show=p.show)


main()


