import os
from typing import Optional, Union, List, Tuple, Dict, NewType
import logging
import webbrowser
from datetime import datetime
import pandas as pd
from math import degrees

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

import gmplot

import folium
from folium.plugins import MiniMap
from folium.features import DivIcon

from ..gpx_elements import Gpx, WayPoint
from ..gpx_parser import Parser
from ..gpx_writer import GPXWriter
from ..kml_writer import KMLWriter
from ..utils import EARTH_RADIUS

GPX = NewType("GPX", object) # GPX forward declaration for type hint

class GPX():
    """
    High level GPX object.
    """

    def __init__(self, file_path: Optional[str] = None, check_schemas: bool = True, extensions_schemas: bool = False) -> None:
        """
        Initialise GPX instance.

        Parameters
        ----------
        file_path : Optional[str], optional
            Path to the file to parse, by default None
        check_schemas : bool, optional
            Toggle schema verification during parsing, by default True
        extensions_schemas : bool, optional
            Toggle extensions schema verificaton during parsing, by default False
        """
        if file_path is not None and os.path.exists(file_path):
            self.file_path: str = file_path
            self.parser: Parser = Parser(file_path, check_schemas, extensions_schemas)
            self.gpx: Gpx = self.parser.gpx
            self.gpx_writer: GPXWriter = GPXWriter(
                self.gpx, precisions=self.parser.precisions, time_format=self.parser.time_format)
            self.kml_writer: KMLWriter = KMLWriter(
                self.gpx, precisions=self.parser.precisions, time_format=self.parser.time_format)
        else:
            logging.warning("File path does not exist")
            pass

    def __str__(self) -> str:
        return f"file_path = {self.file_path}\nparser = {self.parser}\ngpx = {self.gpx}\ngpx_writer = {self.gpx_writer}\nkml_writer = {self.kml_writer}"
    
    def check_schemas(self, extensions_schemas: bool = False) -> bool:
        """
        Check XML schema.

        Parameters
        ----------
        extensions_schemas : bool, optional
            Toggle extensions schema verificaton. Requires internet connection and is not guaranted to work, by default False

        Returns
        -------
        bool
            True if the file follows XML schemas.
        """
        return self.gpx.check_schemas(self.file_path, extensions_schemas)
        
    def file_name(self) -> Union[str, None]:
        """
        Return .gpx file name.

        Returns
        -------
        Union[str, None]
            File name.
        """
        return os.path.basename(self.file_path)

    def name(self) -> str:
        """
        Return activity name.

        Returns
        -------
        str
            Activity name.
        """
        return self.gpx.name()
    
    def set_name(self, new_name: str) -> None:
        """
        Set name.

        Parameters
        ----------
        new_name : str
            New name.
        """
        self.gpx.set_name(new_name)

    def nb_points(self) -> int:
        """
        Return the number of points in the GPX.

        Returns
        -------
        int
            Number of points in the GPX.
        """
        return self.gpx.nb_points()

    def first_point(self) -> WayPoint:
        """
        Return GPX first point.

        Returns
        -------
        WayPoint
            First point.
        """
        return self.gpx.first_point()

    def last_point(self) -> WayPoint:
        """
        Return GPX last point.

        Returns
        -------
        WayPoint
            Last point.
        """
        return self.gpx.last_point()

    def bounds(self) -> Tuple[float, float, float, float]:
        """
        Find minimum and maximum latitude and longitude.

        Returns
        -------
        Tuple[float, float, float, float]
            Min latitude, min longitude, max latitude, max longitude.
        """
        return self.gpx.bounds()

    def center(self) -> Tuple[float, float]:
        """
        Return the coordinates of the center point.

        Returns
        -------
        Tuple[float, float]
            Latitude and longitude of the center point.
        """
        return self.gpx.center()

    def distance(self) -> float:
        """
        Returns the distance (meters) of the tracks contained in the GPX.

        Returns
        -------
        float
            Distance (meters).
        """
        return self.gpx.distance()

    def ascent(self) -> float:
        """
        Returns the ascent (meters) of the tracks contained in the GPX.

        Returns
        -------
        float
            Ascent (meters).
        """
        return self.gpx.ascent()

    def descent(self) -> float:
        """
        Returns the descent (meters) of the tracks contained in the GPX.

        Returns
        -------
        float
            Descent (meters).
        """
        return self.gpx.descent()
    
    def compute_points_ascent_rate(self) -> None:
        """
        Compute ascent rate at each point.
        """
        self.gpx.compute_points_ascent_rate()

    def min_ascent_rate(self) -> float:
        """
        Return activity minimum ascent rate.

        Returns
        -------
        float
            Minimum ascent rate.
        """
        return self.gpx.min_ascent_rate()
    
    def max_ascent_rate(self) -> float:
        """
        Return activity maximum ascent rate.

        Returns
        -------
        float
            Maximum ascent rate.
        """
        return self.gpx.max_ascent_rate()

    def min_elevation(self) -> float:
        """
        Returns the minimum elevation (meters) in the tracks contained in the GPX.

        Returns
        -------
        float
            Minimum elevation (meters).
        """
        return self.gpx.min_elevation()

    def max_elevation(self) -> float:
        """
        Returns the maximum elevation (meters) in the tracks contained in the GPX.

        Returns
        -------
        float
            Maximum elevation (meters).
        """
        return self.gpx.max_elevation()

    def start_time(self) -> datetime:
        """
        Return the activity start time.

        Returns
        -------
        datetime
            Start time.
        """
        return self.gpx.start_time()

    def stop_time(self) -> datetime:
        """
        Return the activity stop time.

        Returns
        -------
        datetime
            Stop time.
        """
        return self.gpx.stop_time()

    def total_elapsed_time(self) -> datetime:
        """
        Return the total elapsed time during the activity.

        Returns
        -------
        datetime
            Total elapsed time.
        """
        return self.gpx.total_elapsed_time()

    def stopped_time(self) -> datetime:
        """
        Return the stopped time during the activity.

        Returns
        -------
        datetime
            Stopped time.
        """
        return self.gpx.stopped_time()

    def moving_time(self) -> datetime:
        """
        Return the moving time during the activity.

        Returns
        -------
        datetime
            Moving time.
        """
        return self.gpx.moving_time()

    def avg_speed(self) -> float:
        """
        Return average speed (kilometers per hour) during the activity.

        Returns
        -------
        float
            Average speed (kilometers per hour).
        """
        return self.gpx.avg_speed()

    def avg_moving_speed(self) -> float:
        """
        Return average moving speed (kilometers per hour) during the activity.

        Returns
        -------
        float
            Average moving speed (kilometers per hour).
        """
        return self.gpx.avg_moving_speed()
    
    def compute_points_speed(self) -> None:
        """
        Compute speed (kilometers per hour) at each track point.
        """
        self.gpx.compute_points_speed()

    def min_speed(self) -> float:
        """
        Return the minimum speed during the activity.

        Returns
        -------
        float
            Minimum speed.
        """
        return self.gpx.min_speed()

    def max_speed(self) -> float:
        """
        Return the maximum speed during the activity.

        Returns
        -------
        float
            Maximum speed.
        """
        return self.gpx.max_speed()
    
    def avg_pace(self) -> float:
        """
        Return average pace (minutes per kilometer) during the activity.

        Returns
        -------
        float
            Average pace (minutes per kilometer).
        """
        return self.gpx.avg_pace()

    def avg_moving_pace(self) -> float:
        """
        Return average moving pace (minutes per kilometer) during the activity.

        Returns
        -------
        float
            Average moving pace (minutes per kilometer).
        """
        return self.gpx.avg_moving_pace()
    
    def compute_points_pace(self) -> None:
        """
        Compute pace at each track point.
        """
        self.gpx.compute_points_pace()

    def min_pace(self) -> float:
        """
        Return the minimum pace during the activity.

        Returns
        -------
        float
            Minimum pace.
        """
        return self.gpx.min_pace()

    def max_pace(self) -> float:
        """
        Return the maximum pace during the activity.

        Returns
        -------
        float
            Maximum pace.
        """
        return self.gpx.max_pace()
    
    def compute_points_ascent_speed(self) -> None:
        """
        Compute ascent speed (kilometers per hour) at each track point.
        """
        self.gpx.compute_points_ascent_speed()

    def remove_metadata(self):
        """
        Remove metadata (ie: metadata will not be written when saving the GPX object as a .gpx file).
        """
        self.gpx_writer.metadata = False

    def remove_elevation(self):
        """
        Remove elevation data (ie: elevation data will not be written when saving the GPX object as a .gpx file).
        """
        self.gpx_writer.ele = False

    def remove_time(self):
        """
        Remove time data (ie: time data will not be written when saving the GPX object as a .gpx file).
        """
        self.gpx_writer.time = False

    def remove_gps_errors(self):
        """
        Remove GPS errors.
        """
        self.gpx.remove_gps_errors()

    def remove_close_points(self, min_dist: float = 1, max_dist: float = 10):
        """
        Remove points that are to close together.

        Parameters
        ----------
        min_dist : float, optional
            Minimal distance between two points, by default 1
        max_dist : float, optional
            Maximal distance between two points, by default 10
        """
        self.gpx.remove_close_points(min_dist, max_dist)

    def simplify(self, tolerance: float = 2):
        """
        Simplify the tracks using Ramer-Douglas-Peucker algorithm.

        Parameters
        ----------
        tolerance : float, optional
            Tolerance (meters). Corresponds to the minimum distance between the
            point and the track before the point is removed, by default 2
        """
        epsilon = degrees(tolerance/EARTH_RADIUS)
        self.gpx.simplify(epsilon)

    def merge(self, gpx: GPX):
        """
        _summary_

        Parameters
        ----------
        gpx : GPX
            _description_
        """
        # TODO
        if self.gpx.tag is None:
            self.gpx.tag = gpx.gpx.tag
        if self.gpx.creator is None:
            self.gpx.creator = gpx.gpx.creator
        if self.gpx.xmlns is None:
            self.gpx.xmlns = gpx.gpx.xmlns
        if self.gpx.version is None:
            self.gpx.version = gpx.gpx.version
        if self.gpx.xmlns_xsi is None:
            self.gpx.xmlns_xsi = gpx.gpx.xmlns_xsi
        self.gpx.xsi_schema_location.extend(gpx.gpx.xsi_schema_location)
        if self.gpx.xmlns_gpxtpx is None:
            self.gpx.xmlns_gpxtpx = gpx.gpx.xmlns_gpxtpx
        if self.gpx.xmlns_gpxx is None:
            self.gpx.xmlns_gpxx = gpx.gpx.xmlns_gpxx
        if self.gpx.xmlns_gpxtrk is None:
            self.gpx.xmlns_gpxtrk = gpx.gpx.xmlns_gpxtrk
        if self.gpx.xmlns_wptx1 is None:
            self.gpx.xmlns_wptx1 = gpx.gpx.xmlns_wptx1
        if self.gpx.metadata is None:
            self.gpx.metadata = gpx.gpx.metadata
        self.gpx.wpt.extend(gpx.gpx.wpt)
        self.gpx.rte.extend(gpx.gpx.rte)
        self.gpx.tracks.extend(gpx.gpx.tracks)
        if self.gpx.extensions is None:
            self.gpx.extensions = gpx.gpx.extensions

    def to_gpx_string(self) -> str:
        """
        Convert the GPX object to a string.

        Returns
        -------
        str
            String representingth GPX object.
        """
        return self.gpx_writer.gpx_to_string(self.gpx)
    
    def to_dataframe(
            self,
            projection: bool = False,
            elevation: bool = True,
            speed: bool = False,
            pace: bool = False,
            ascent_rate: bool = False,
            ascent_speed: bool = False) -> pd.DataFrame:
        """
        Convert GPX object to Pandas Dataframe.

        Parameters
        ----------
        projection : bool, optional
            Toggle projection, by default False
        elevation : bool, optional
            Toggle elevation, by default True
        speed : bool, optional
            Toggle speed, by default False
        pace : bool, optional
            Toggle pace, by default False
        ascent_rate : bool, optional
            Toggle ascent rate, by default False
        ascent_speed : bool, optional
            Toggle ascent speed, by default False

        Returns
        -------
        pd.DataFrame
            Dataframe containing data from GPX.
        """
        return self.gpx.to_dataframe(projection, elevation, speed, pace, ascent_rate, ascent_speed)

    def to_csv(
            self,
            path: str = None,
            sep: str = ",",
            columns: List[str] = None,
            header: bool = True,
            index: bool = False) -> Union[str, None]:
        """
        Write the GPX object track coordinates to a .csv file.

        Parameters
        ----------
        path : str, optional
            Path to the .csv file, by default None
        sep : str, optional
            Separator, by default ","
        columns : List[str], optional
            List of columns to write, by default None
        header : bool, optional
            Toggle header, by default True
        index : bool, optional
             Toggle index, by default False

        Returns
        -------
        str
            CSV like string if path is set to None.
        """
        return self.gpx.to_csv(path, sep, columns, header, index)
    
    def to_gpx(self, path: str, check_schemas: bool = True, extensions_schemas: bool = False) -> bool:
        """
        Write the GPX object to a .gpx file.

        Parameters
        ----------
        path : str
            Path to the .gpx file.
        check_schemas : bool, optional
            Toggle schema verification after writting, by default True
        extensions_schemas : bool, optional
            Toggle extensions schema verificaton after writing. Requires internet connection and is not guaranted to work, by default False

        Returns
        -------
        bool
            Return False if written file does not follow checked schemas. Return True otherwise.
        """
        return self.gpx_writer.write(path, check_schemas, extensions_schemas)
    
    def to_kml(self, path: str, styles: Optional[List[Tuple[str, Dict]]] = None, check_schemas: bool = True) -> bool:
        """
        Write the GPX object to a .kml file.

        Parameters
        ----------
        path : str
            Path to the .gpx file.
        styles : List[Tuple[str, Dict]], optional
            List of (style_id, style) tuples, by default None
        check_schemas : bool, optional
            Toggle schema verification after writting, by default True

        Returns
        -------
        bool
            Return False if written file does not follow checked schemas. Return True otherwise.
        """
        return self.kml_writer.write(path, styles, check_schemas)

    def _matplotlib_plot_text(
            self,
            fig: Figure,
            duration: Optional[Tuple[float, float]] = (0, 0),
            distance: Optional[Tuple[float, float]] = (0.5, 0),
            ascent: Optional[Tuple[float, float]] = (1, 0),
            pace: Optional[Tuple[float, float]] = (1, 0),
            speed: Optional[Tuple[float, float]] = (1, 0),
            text_parameters: Optional[dict] = None):
        """
        Plot text on Matplotlib plot.

        Parameters
        ----------
        fig : Figure
            Matplotlib figure.
        duration : Optional[Tuple[float, float]], optional
            Duration text plot coordinates, by default (0, 0)
        distance : Optional[Tuple[float, float]], optional
            Distance text plot coordinates, by default (0.5, 0)
        ascent : Optional[Tuple[float, float]], optional
            Ascent text plot coordinates, by default (1, 0)
        pace : Optional[Tuple[float, float]], optional
            Pace text plot coordinates, by default (1, 0)
        speed : Optional[Tuple[float, float]], optional
            Speed text plot coordinates, by default (1, 0)
        text_parameters : Optional[dict], optional
            Text parameters, by default None
        """
        # Handle text parameters
        if text_parameters is None:
            text_parameters = dict(ha='center', va='center', fontsize=10,
                                   transform=fig.axes[0].transAxes, bbox=dict(facecolor='gray', alpha=0.5))
        else:
            text_parameters["transform"] = fig.axes[0].transAxes

        if duration is not None:
            plt.text(duration[0], duration[1],
                     f"Duration:\n{self.total_elapsed_time()}", **text_parameters)

        if distance is not None:
            plt.text(distance[0], distance[1],
                     f"Distance:\n{self.distance()/1000:.2f} km", **text_parameters)

        if ascent is not None:
            plt.text(ascent[0], ascent[1],
                     f"Ascent:\n{self.ascent():.2f} m", **text_parameters)

        elif pace is not None:
            plt.text(pace[0], pace[1],
                     f"Pace:\n{self.avg_pace():.2f} min/km", **text_parameters)

        elif speed is not None:
            plt.text(speed[0], speed[1],
                     f"Speed:\n{self.avg_speed():.2f} km/h", **text_parameters)

    def matplotlib_axes_plot(
            self,
            axes: Axes,
            projection: Optional[str] = None,
            color: str = "#101010",
            colorbar: bool = False,
            start_stop_colors: Optional[Tuple[str, str]] = None,
            way_points_color: Optional[str] = None,
            title: Optional[str] = None,
            duration: Optional[Tuple[float, float]] = None,
            distance: Optional[Tuple[float, float]] = None,
            ascent: Optional[Tuple[float, float]] = None,
            pace: Optional[Tuple[float, float]] = None,
            speed: Optional[Tuple[float, float]] = None):
        """
        Plot GPX on Matplotlib axes.

        Parameters
        ----------
        axes : Axes
            Axes to plot on.
        projection : Optional[str], optional
            Projection, by default None
        color : str, optional
            A color string (ie: "#FF0000" or "red") or a track attribute
            ("elevation", "speed", "pace", "vertical_drop", "ascent_rate",
            "ascent_speed"), by default "#101010"
        colorbar : bool, optional
            Colorbar Toggle, by default False
        start_stop_colors : Optional[Tuple[str, str]], optional
            Start and stop points colors, by default None
        way_points_color : Optional[str], optional
            Way point color, by default None
        title : Optional[str], optional
            Title, by default None
        duration : Optional[Tuple[float, float]], optional
            Display duration, by default None
        distance : Optional[Tuple[float, float]], optional
            Display distance, by default None
        ascent : Optional[Tuple[float, float]], optional
            Display ascent, by default None
        pace : Optional[Tuple[float, float]], optional
            Display pace, by default None
        speed : Optional[Tuple[float, float]], optional
            Display speed, by default None
        """
        # Clear axes
        axes.clear()

        # Handle projection (select dataframe columns to use and project if needed)
        if projection is None:
            column_x = "lon"
            column_y = "lat"
        else:
            column_x = "x"
            column_y = "y"
            self.gpx.project(projection)  # Project all track points

        # Create dataframe containing data from the GPX file
        gpx_df = self.to_dataframe(projection=True, elevation=True, speed=True, pace=True, ascent_rate=True, ascent_speed=True)

        # Scatter all track points
        if color == "elevation":
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["green","blue"])
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y],
                        c=gpx_df["ele"], cmap=cmap)
        elif color == "speed":
            # cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightskyblue", "deepskyblue", "blue", "mediumblue", "midnightblue"])
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightskyblue", "mediumblue", "midnightblue"])
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y],
                        c=gpx_df["speed"], cmap=cmap)
        elif color == "pace":
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightskyblue", "midnightblue"])
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y],
                        c=gpx_df["pace"], cmap=cmap)
        elif color == "vertical_drop":
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["yellow", "orange", "red", "purple", "black"])
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y],
                        c=abs(gpx_df["ascent_rate"]), cmap=cmap)
        elif color == "ascent_rate":
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["darkgreen", "green", "yellow", "red", "black"])
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y],
                        c=gpx_df["ascent_rate"], cmap=cmap)
        elif color == "ascent_speed":
            cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["deeppink", "lightpink", "lightcoral", "red", "darkred"])
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y],
                        c=gpx_df["ascent_speed"], cmap=cmap)
        else:
            im = axes.scatter(gpx_df[column_x], gpx_df[column_y], color=color)
        
        # Colorbar
        if colorbar:
            plt.colorbar(im)

        # Scatter start and stop points with different color
        if start_stop_colors is not None:
            axes.scatter(gpx_df[column_x][0],
                        gpx_df[column_y][0], color=start_stop_colors[0])
            axes.scatter(gpx_df[column_x][len(gpx_df[column_x])-1],
                        gpx_df[column_y][len(gpx_df[column_x])-1], color=start_stop_colors[1])

        # Scatter way points with different color
        if way_points_color:
            for way_point in self.gpx.wpt:
                if projection:
                    way_point.project(projection)
                    axes.scatter(way_point._x, way_point._y, color=way_points_color)
                else:
                    axes.scatter(way_point.lon, way_point.lat, color=way_points_color)

        # Add title
        if title is not None:
            axes.set_title(title, size=20)

        # Add text elements
        self._matplotlib_plot_text(axes.get_figure(), duration, distance, ascent, pace, speed)

        # Add ticks
        axes.set_xticks([min(gpx_df[column_x]), max(gpx_df[column_x])])
        axes.set_yticks([min(gpx_df[column_y]), max(gpx_df[column_y])])

        # Add axis limits (useless??)
        if projection is not None:
            axes.set_xlim(left=min(gpx_df[column_x]),
                        right=max(gpx_df[column_x]))
            axes.set_ylim(bottom=min(gpx_df[column_y]),
                        top=max(gpx_df[column_y]))

    def matplotlib_plot(
        self,
        projection: Optional[str] = None,
        color: str = "#101010",
        colorbar: bool = False,
        start_stop_colors: Optional[Tuple[str, str]] = None,
        way_points_color: Optional[str] = None,
        title: Optional[str] = None,
        duration: Optional[Tuple[float, float]] = None,
        distance: Optional[Tuple[float, float]] = None,
        ascent: Optional[Tuple[float, float]] = None,
        pace: Optional[Tuple[float, float]] = None,
        speed: Optional[Tuple[float, float]] = None,
        file_path: Optional[str] = None):
        """
        Plot GPX using Matplotlib.

        Parameters
        ----------
        projection : Optional[str], optional
            Projection, by default None
        color : str, optional
            A color string (ie: "#FF0000" or "red") or a track attribute
            ("elevation", "speed", "pace", "vertical_drop", "ascent_rate",
            "ascent_speed"), by default "#101010"
        colorbar : bool, optional
            Colorbar Toggle, by default False
        start_stop_colors : Optional[Tuple[str, str]], optional
            Start and stop points colors, by default None
        way_points_color : Optional[str], optional
            Way point color, by default None
        title : Optional[str], optional
            Title, by default None
        duration : Optional[Tuple[float, float]], optional
            Display duration, by default None
        distance : Optional[Tuple[float, float]], optional
            Display distance, by default None
        ascent : Optional[Tuple[float, float]], optional
            Display ascent, by default None
        pace : Optional[Tuple[float, float]], optional
            Display pace, by default None
        speed : Optional[Tuple[float, float]], optional
            Display speed, by default None
        """
        # Create figure with axes
        fig = plt.figure(figsize=(14, 8))
        fig.add_subplot(111)

        # Plot on axes
        self.matplotlib_axes_plot(fig.axes[0],
                                  projection,
                                  color,
                                  colorbar,
                                  start_stop_colors,
                                  way_points_color,
                                  title,
                                  duration,
                                  distance,
                                  ascent,
                                  pace,
                                  speed)
        
        # Save or display plot
        if file_path is not None:
            directory_path = os.path.dirname(os.path.realpath(file_path))
            if not os.path.exists(directory_path):
                logging.error("Provided path does not exist")
                return
            plt.savefig(file_path)
        else:
            plt.show()

    def matplotlib_basemap_plot(
            self,
            projection: str = "cyl",
            service: str = "World_Shaded_Relief",
            color: str = "#101010",
            start_stop_colors: Optional[Tuple[str, str]] = None,
            way_points_color: Optional[str] = None,
            title: Optional[str] = None,
            duration: Optional[Tuple[float, float]] = None,
            distance: Optional[Tuple[float, float]] = None,
            ascent: Optional[Tuple[float, float]] = None,
            pace: Optional[Tuple[float, float]] = None,
            speed: Optional[Tuple[float, float]] = None,
            file_path: str = None):
        """
        Plot GPX using Matplotlib Basemap Toolkit.

        Parameters
        ----------
        projection : str, optional
            Projection, by default "cyl"
        service : str, optional
            Service used to fetch map background. Currently supported services:
            "World_Shaded_Relief". Defaults to "World_Shaded_Relief",
            by default "World_Shaded_Relief"
        color : str, optional
            Track color, by default "#101010"
        start_stop_colors : Optional[Tuple[str, str]], optional
            Start and stop points colors, by default None
        way_points_color : Optional[str], optional
            Way point color, by default None
        title : Optional[str], optional
            Title, by default None
        duration : Optional[Tuple[float, float]], optional
            Display duration, by default None
        distance : Optional[Tuple[float, float]], optional
            Display distance, by default None
        ascent : Optional[Tuple[float, float]], optional
            Display ascent, by default None
        pace : Optional[Tuple[float, float]], optional
            Display pace, by default None
        speed : Optional[Tuple[float, float]], optional
            Display speed, by default None
        file_path : str, optional
            Path to save plot, by default None
        """
        # Create figure
        fig = plt.figure(figsize=(14, 8))

        # Create square map
        center_lat, center_lon = self.center()
        min_lat, min_lon, max_lat, max_lon = self.bounds()
        offset = 0.001
        min_lat, min_lon = max(0, min_lat - offset), max(0, min_lon - offset)
        max_lat, max_lon = min(max_lat + offset, 90), min(max_lon + offset, 90)

        delta_lat = max_lat - min_lat
        delta_lon = max_lon - min_lon

        if delta_lat > delta_lon:
            min_lon = max(0, center_lon - delta_lat/2)
            max_lon = min(90, center_lon + delta_lat/2)
        else:
            min_lat = max(0, center_lat - delta_lon/2)
            max_lat = min(90, center_lat + delta_lon/2)

        map = Basemap(projection=projection,
                      llcrnrlon=min_lon,
                      llcrnrlat=min_lat,
                      urcrnrlon=max_lon,
                      urcrnrlat=max_lat)

        # map.drawmapboundary(fill_color='aqua')
        # map.fillcontinents(color='coral',lake_color='aqua')
        # map.drawcoastlines()

        # map.bluemarble()
        # map.shadedrelief()
        # map.etopo()
        map.arcgisimage(service=service,
                        xpixels=2000, dpi=200, verbose=True)

        # Create dataframe containing data from the GPX file
        gpx_df = self.to_dataframe()

        # Project track points
        x, y = map(gpx_df["lon"], gpx_df["lat"])
        
        # Plot track points on the map
        x = x.tolist()
        y = y.tolist()
        map.plot(x, y, marker=None, color=color)

        # Scatter start and stop points with different color
        if start_stop_colors:
            map.plot(x[0], y[0], marker="^", color=start_stop_colors[0])
            map.plot(x[-1], y[-1], marker="h", color=start_stop_colors[1])

        # Project and scatter way points with different color
        if way_points_color:
            for way_point in self.gpx.wpt:
                x, y = map(way_point.lon, way_point.lat)
                map.plot(x, y, marker="D", color="waypoint_color")

        # Add title
        if title is not None:
            plt.title(title, size=20)

        # Add text elements
        self._matplotlib_plot_text(fig, duration, distance, ascent, pace, speed)

        # Save or display plot
        if file_path is not None:
            # Check if provided path exists
            directory_path = os.path.dirname(os.path.realpath(file_path))
            if not os.path.exists(directory_path):
                logging.error("Provided path does not exist")
                return
            plt.savefig(file_path)
        else:
            plt.show()

    def gmplot_plot(
            self,
            color: str = "#110000",
            start_stop_colors: Optional[Tuple[str, str]] = None,
            way_points_color: Optional[str] = None,
            zoom: float = 10.0,
            title: Optional[str] = None,
            file_path: str = None,
            open: bool = True,
            scatter: bool = False,
            plot: bool = True):
        """
        Plot GPX using gmplot.

        Parameters
        ----------
        color : str, optional
            Track color, by default "#110000"
        start_stop_colors : Optional[Tuple[str, str]], optional
            Start and stop points colors, by default None
        way_points_color : Optional[str], optional
            Way points color, by default None
        zoom : float, optional
            Zoom, by default 10.0
        title : Optional[str], optional
            Title, by default None
        file_path : str, optional
            Path to save plot, by default None
        open : bool, optional
            Open the plot in the default web browser, by default True
        scatter : bool, optional
            Scatter track points, by default False
        plot : bool, optional
            Plot track points, by default True
        """
        # Create plotter
        center_lat, center_lon = self.center()
        map = gmplot.GoogleMapPlotter(center_lat, center_lon, zoom)

        # Create dataframe containing data from the GPX file
        gpx_df = self.to_dataframe()

        # Scatter track points
        if scatter:
            map.scatter(gpx_df["lat"], gpx_df["lon"],
                        color, size=5, marker=False)
        if plot:
            map.plot(gpx_df["lat"], gpx_df["lon"],
                     color, edge_width=2.5)
        
        # Scatter start and stop points with different color
        if start_stop_colors:
            map.scatter([self.gpx.tracks[0].trkseg[0].trkpt[0].lat],
                        [self.gpx.tracks[0].trkseg[0].trkpt[0].lon],
                        start_stop_colors[0], size=5, marker=True)
            map.scatter([self.gpx.tracks[-1].trkseg[-1].trkpt[-1].lat],
                        [self.gpx.tracks[-1].trkseg[-1].trkpt[-1].lon],
                        start_stop_colors[1], size=5, marker=True)
            
        # Scatter way points with different color
        if way_points_color:
            for way_point in self.gpx.wpt:
                map.scatter([way_point.lat], [way_point.lon],
                            way_points_color, size=5, marker=True)
        
        # Add title
        if title is not None:
            map.text(center_lat, center_lon, self.name(), color="#FFFFFF")

        # Save map
        map.draw(file_path)

        # Open map in web browser
        if open:
            webbrowser.open(file_path)

    def folium_plot(
            self,
            tiles: str = "OpenStreetMap",  # "OpenStreetMap", "Stamen Terrain", "Stamen Toner"
            color: str = "#110000",
            start_stop_colors: Optional[Tuple[str, str]] = None,
            way_points_color: Optional[str] = None,
            minimap: bool = False,
            coord_popup: bool = False,
            title: Optional[str] = None,
            zoom: float = 12.0,
            file_path: str = None,
            open: bool = True):
        """
        Plot GPX using folium.

        Parameters
        ----------
        tiles : str, optional
            Map tiles. Supported tiles: "OpenStreetMap", "Stamen Terrain",
            "Stamen Toner", by default "OpenStreetMap"
        start_stop_colors : Optional[Tuple[str, str]], optional
            Start and stop points colors, by default None
        way_points_color : Optional[str], optional
            Way points color, by default None
        minimap : bool, optional
            Add minimap, by default False
        coord_popup : bool, optional
            Add coordinates pop-up when clicking on the map, by default False
        title : Optional[str], optional
            Title, by default None
        zoom : float, optional
            Zoom, by default 12.0
        file_path : str, optional
            Path to save plot, by default None
        open : bool, optional
            Open the plot in the default web browser, by default True
        """
        # Create map
        center_lat, center_lon = self.center()
        m = folium.Map(location=[center_lat, center_lon],
                       zoom_start=zoom,
                       tiles=tiles)
        
        # Plot track points
        gpx_df = self.to_dataframe()
        gpx_df["coordinates"] = list(
            zip(gpx_df.latitude, gpx_df.longitude))
        folium.PolyLine(gpx_df["coordinates"],
                        tooltip=self.name(), color=color).add_to(m)

        # Scatter start and stop points with different color
        if start_stop_colors:
            folium.Marker([self.gpx.tracks[0].trkseg[0].trkpt[0].lat, self.gpx.tracks[0].trkseg[0].trkpt[0].lon],
                          popup="<b>Start</b>", tooltip="Start", icon=folium.Icon(color=start_stop_colors[0])).add_to(m)
            folium.Marker([self.gpx.tracks[-1].trkseg[-1].trkpt[-1].lat, self.gpx.tracks[-1].trkseg[-1].trkpt[-1].lon],
                          popup="<b>Stop</b>", tooltip="Stop", icon=folium.Icon(color=start_stop_colors[1])).add_to(m)
        
        # Scatter way points with different color
        if way_points_color:
            for way_point in self.gpx.wpt:
                folium.Marker([way_point.lat, way_point.lon], popup="<i>Way point</i>",
                              tooltip="Way point", icon=folium.Icon(icon="info-sign", color=way_points_color)).add_to(m)

        # Add minimap
        if minimap:
            minimap = MiniMap(toggle_display=True)
            minimap.add_to(m)

        # Add latitude-longitude pop-up
        if coord_popup:
            m.add_child(folium.LatLngPopup())

        # Title
        if title is not None:
            folium.map.Marker(
                [center_lat, center_lon],
                icon=DivIcon(
                    icon_size=(250, 36),
                    icon_anchor=(0, 0),
                    html=f'<div style="font-size: 20pt">{title}</div>',
                )
            ).add_to(m)

        # Save map
        m.save(file_path)

        # Open map in web browser
        if open:
            webbrowser.open(file_path)