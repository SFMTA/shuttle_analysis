import os
import psycopg2
import json
import pandas as pd
from ipywidgets import Dropdown, HBox, VBox, Button, DatePicker, ColorPicker, IntSlider
from ipyleaflet import Map, Polyline, GeoJSON, Circle, basemaps
import datetime
import sfmta

def time_drop_down():
    values = {'12:00am': '00:00:00', '12:30am': '00:30:00', '1:00am': '01:00:00',
              '1:30am': '01:30:00', '2:00am': '02:00:00', '2:30am': '02:30:00',
              '3:00am': '03:00:00', '3:30am': '03:30:00', '4:00am': '04:00:00',
              '4:30am': '04:30:00', '5:00am': '05:00:00', '5:30am': '05:30:00',
              '6:00am': '06:00:00', '6:30am': '06:30:00', '7:00am': '07:00:00',
              '7:30am': '07:30:00', '8:00am': '08:00:00', '8:30am': '08:30:00',
              '9:00am': '09:00:00', '9:30am': '09:30:00', '10:00am': '10:00:00',
              '10:30am': '10:30:00', '11:00am': '11:00:00', '11:30am': '11:30:00',
              '12:00pm': '12:00:00', '12:30pm': '12:30:00', '1:00pm': '13:00:00',
              '1:30pm': '13:30:00', '2:00pm': '14:00:00', '2:30pm': '14:30:00',
              '3:00pm': '15:00:00', '3:30pm': '15:30:00', '4:00pm': '16:00:00',
              '4:30pm': '16:30:00', '5:00pm': '17:00:00', '5:30pm': '17:30:00',
              '6:00pm': '18:00:00', '6:30pm': '18:30:00', '7:00pm': '19:00:00',
              '7:30pm': '19:30:00', '8:00pm': '20:00:00', '8:30pm': '20:30:00',
              '9:00pm': '21:00:00', '9:30pm': '21:30:00', '10:00pm': '22:00:00',
              '10:30pm': '22:30:00', '11:00pm': '23:00:00', '11:30pm': '23:30:00'}
    dd = Dropdown(description='Time', options=values, value='07:00:00')
    return dd

def main(conn):

    def clear_map():
        if 'm' in globals():
            m.close()
        else:
            pass

    def clear_lat_longs():
        if 'lat_longs' in globals():
            lat_longs = None
        else:
            pass

    def clear_time_slider():
        if 'time_slider' in globals():
            time_slider = None
        else:
            pass

    def draw_update_map(b):
        clear_map()
        clear_lat_longs()
        plate = plate_dropdown.value
        start_date_time = str(start_date.value) + ' ' + start_time_dropdown.value
        end_date_time = str(end_date.value) + ' ' + end_time_dropdown.value
        global locations
        locations = sfmta.get_points_for_shuttle(conn, 
                                                 plate, 
                                                 start_date_time,
                                                 end_date_time)

        zip_locations = zip(locations['lng'], locations['lat'], locations.index)
        global lat_longs
        lat_longs = [(x[0], x[1]) for x in zip_locations]
        index_value = find_index(lat_longs, time_slider.value)
        global m
        m = draw_map(lat_longs[:index_value])
        display(m)

    button = Button(description="Draw/Update Map")
    button.on_click(draw_update_map)
    time_slider = IntSlider(min=0, max=100, step=1, description='% of Data', value=100)

    def find_index(lat_longs, value):
        length = len(lat_longs)
        index = int(length * value/100)
        return index

    def draw_map(lat_longs):
        center = [37.79481, -122.41186]
        zoom = 12
        m = Map(center=center, zoom=zoom, basemap=basemaps.Hydda.Full)
        m.layout.height = '650px'
        pl = Polyline(locations=lat_longs)
        pl.color = path_color.value
        pl.fill_color = path_color.value
        m.add_layer(pl)
        return m

    plates = sfmta.get_all_shuttles(conn)['LICENSE_PLATE'].unique()
    plate_dropdown = Dropdown(options=plates, description='Plate')

    def show_restrictions(b):
        polygons = './vehiclerestrictions_wgs.json'

        with open(polygons) as f:
            polygons_json = json.load(f)

        global geojson
        geojson = GeoJSON(data=polygons_json)
        m.add_layer(geojson)

    def remove_restrictions(b):
        if 'geojson' in globals():
            m.remove_layer(geojson)
        else:
            pass

    def download_data(b):
        if 'lat_longs' in globals():
            df = pd.DataFrame(data=lat_longs)
            df.to_excel('output.xlsx')
        else:
            pass

    button_restrictions = Button(description="Show Restrictions")
    button_restrictions.on_click(show_restrictions)

    button_remove_restrictions = Button(description="Hide Restrictions")
    button_remove_restrictions.on_click(remove_restrictions)

    path_color = ColorPicker(description='Color')

    export_data = Button(description="Download Data")
    export_data.on_click(download_data)


    def top_n_stops(b):
        from collections import Counter
        count_lat_longs = Counter(lat_longs).most_common()
        for lat_long in count_lat_longs[0:10]:
            location = lat_long[0]
            circle = Circle(location=location, radius=300)
            m.add_layer(circle)
        return m

    button_add_top_stops = Button(description="Display Bus Idling")
    button_add_top_stops.on_click(top_n_stops)

    # Remove map button needs its own function with a single argument
    def remove_map(b):
        clear_map()

    button_clear_map = Button(description="Remove Map")
    button_clear_map.on_click(remove_map)

    start = datetime.date.today()
    end = datetime.date.today()
    start_date = DatePicker(description='Start Date',value=start)
    end_date = DatePicker(description='End Date', value=end)

    start_time_dropdown = time_drop_down()
    start_time_dropdown.description = 'Start Time'
    end_time_dropdown = time_drop_down()
    end_time_dropdown.description = 'End Time'

    companies = sfmta.get_shuttles_companies(conn)['NAME'].unique()
    company = Dropdown(options=companies, value='WeDriveU', description='Company')

    return VBox([HBox([company, button, button_restrictions, button_remove_restrictions]),
          HBox([plate_dropdown, export_data, button_add_top_stops, button_clear_map]),
          HBox([path_color]),
          HBox([start_date, start_time_dropdown]),
          HBox([end_date, end_time_dropdown]),
          HBox([time_slider]),
               ])