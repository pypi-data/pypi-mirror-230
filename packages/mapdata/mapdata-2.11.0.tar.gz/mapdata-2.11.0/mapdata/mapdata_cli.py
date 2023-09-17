#!/usr/bin/python
# mapdata.py
#
# PURPOSE
# 	Create a simple map of data points that can be saved to a static
# 	image or HTML file.
#
# COPYRIGHT AND LICENSE
# 	Copyright (c) 2022,2023 R. Dreas Nielsen
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
# 	The GNU General Public License is available at <http://www.gnu.org/licenses/>
#
# NOTES
# 	1.
#
# AUTHOR
# 	Dreas Nielsen (RDN)
# 	Caleb Grant (CG)
#
# HISTORY
# 	 Date		 Remarks
# 	----------	-----------------------------------------------------
# 	2022-01-15	Created.  RDN.
# 	2023-01-11	Set default show arg to False. CG.
# 				Allow HTML output format. CG.
# 				Formatting, update version. CG.
#   2023-03-01  Added arguments for color category id and zoom level. CG.
# ==================================================================

__version__ = "0.2.1"
__vdate = "2023-03-01"


import argparse
import os

import pandas as pd
import plotly.express as px

accepted_outfile_formats = [
    ".html",
    ".jpg",
    ".jpeg",
    ".json",
    ".pdf",
    ".png",
    ".svg",
    ".webp",
    # ".eps"  # requires poppler lib
]


def mapdata(
    points_dataframe: pd.DataFrame,
    lat: str = "y_coord",
    lon: str = "x_coord",
    name: str = "location_id",
    color: str | None = None,
    basemap_layer: str = "carto-positron",
    outfile: str = "location_map.png",
    outwidth: int = 1600,
    outheight: int = 1600,
    zoom: int = 8,
    show: bool = False,
) -> None:
    if color:
        colors = dict(color=color)
    else:
        colors = dict(color_discrete_sequence=["red"])
    mapfig = px.scatter_mapbox(
        points_dataframe,
        lat=lat,
        lon=lon,
        zoom=zoom,
        hover_name=name,
        hover_data=[c for c in points_dataframe.columns if c != name],
        **colors,
    )
    mapfig.update_layout(
        mapbox_style=basemap_layer,
        geo=dict(projection_type="transverse mercator", fitbounds="locations"),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(
            yanchor="top",
            xanchor="left",
            y=0.99,
            x=0.01,
            title=dict(
                font=dict(
                    family="Arial Black",
                    size=14,
                    color="black",
                )
            ),
            font=dict(
                size=12,
                color="black",
            ),
            bgcolor="#ffffff",
            bordercolor="Black",
            borderwidth=1,
        ),
    )
    if os.path.splitext(outfile)[-1] == ".html":
        mapfig.write_html(outfile)
    else:
        mapfig.write_image(outfile, width=outwidth, height=outheight)
    if show:
        mapfig.show()


def clparser() -> argparse.ArgumentParser:
    desc_msg = (
        "Create a static map displaying points read from a CSV file. Version %s, %s"
        % (__version__, __vdate)
    )
    parser = argparse.ArgumentParser(description=desc_msg)
    parser.add_argument(
        "point_data_file",
        help="The name of a data file containing latitude and longitude coordinates, and an identifier",
    )
    parser.add_argument(
        "outfile",
        help=f"The name of the file to create. Accepted formats include {accepted_outfile_formats}",
    )
    parser.add_argument(
        "-y",
        "--lat",
        default="y_coord",
        dest="lat",
        help="The name of the column in the data file containing latitude values",
    )
    parser.add_argument(
        "-x",
        "--lon",
        default="x_coord",
        dest="lon",
        help="The name of the column in the data file containing longitude values",
    )
    parser.add_argument(
        "-i",
        "--identifier",
        default="location_id",
        dest="id",
        help="The name of the column in the data file containing location identifiers",
    )
    parser.add_argument(
        "-c",
        "--color-id",
        default=None,
        dest="color_id",
        help="The name of the column in the data file to categorize point colors",
    )
    parser.add_argument(
        "-z",
        "--zoom",
        choices=[i for i in range(1, 21)],
        type=int,
        default=8,
        dest="zoom",
        help="Initial zoom level for the map",
    )
    parser.add_argument(
        "-b",
        "--baselayer",
        choices=[
            "open-street-map",
            "carto-positron",
            "carto-darkmatter",
            "stamen-terrain",
            "stamen-toner",
            "stamen-watercolor",
        ],
        default="carto-positron",
        dest="baselayer",
        help="The name of the basemap layer to use",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=1600,
        dest="width",
        help="The width of the output image, in pixels",
    )
    parser.add_argument(
        "-t",
        "--height",
        type=int,
        default=1600,
        dest="height",
        help="The height of the output image, in pixels",
    )
    parser.add_argument(
        "-s",
        "--show",
        type=bool,
        default=False,
        dest="show",
        help="Whether or not to show the map in the browser as well as saving it to a file",
    )
    return parser


if __name__ == "__main__":
    parser = clparser().parse_args()
    df = pd.read_csv(parser.point_data_file)
    mapdata(
        df,
        lat=parser.lat,
        lon=parser.lon,
        name=parser.id,
        color=parser.color_id,
        basemap_layer=parser.baselayer,
        outfile=parser.outfile,
        outwidth=parser.width,
        outheight=parser.height,
        zoom=parser.zoom,
        show=parser.show,
    )
