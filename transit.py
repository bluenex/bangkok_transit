import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
from itertools import groupby
from operator import itemgetter
from difflib import get_close_matches


def get_all_station_links(link='http://www.transitbangkok.com/bangkok_bus_routes.php'):
    """
    Get all Bus stations from Bangkok Bus Routes
    """
    body = requests.get(link)
    soup = BeautifulSoup(body.text, "lxml")
    stations = []
    for link in soup.find_all('a'):
        if '/stations/' in link.get('href'):
            stations.append(link.get('href'))
    stations = list(set(stations))
    return stations

def get_all_stations(link='http://www.transitbangkok.com/bangkok_bus_routes.php'):
    """
    Load all unique stations available and
    get all stations details
    """
    stations_links = get_all_station_links()
    stations_links = list(set(['http://www.transitbangkok.com' + s for s in stations_links]))
    station_soup = []
    for station_link in stations_links:
        body = requests.get(station_link)
        soup = BeautifulSoup(body.text, "lxml")
        station_soup.append([station_link, soup])

    stations = []
    for (station_link, soup) in stations_soup:
        station_name = soup.find('span', attrs={'itemprop': 'name'}).get_text()
        for tag in soup.find_all("b"):
            if 'Name in Thai' in tag.text:
                station_thai_name = tag.next_sibling.replace(":", "").strip()
        connecting_lines = []
        c_lines = soup.find('span', attrs={'itemprop': 'description'})
        for c_line in c_lines.find_all('a'):
            if '/lines/bangkok-bus-line/' in (c_line.get('href')):
                connecting_lines.append('http://www.transitbangkok.com' + c_line.get('href'))
        stations.append({'station_link': station_link,
                         'station_name': station_name,
                         'station_thai_name': station_thai_name,
                         'connecting_lines': connecting_lines})
    return stations

def get_all_stations_dataframe(link='http://www.transitbangkok.com/bangkok_bus_routes.php'):
    stations = get_all_stations(link)
    stations_expand = []
    for station in stations:
        for ct in station['connecting_lines']:
            stations_expand.append({'station_link': station['station_link'],
                                    'station_name': station['station_name'],
                                    'station_thai_name': station['station_thai_name'],
                                    'connecting_line': ct})
    stations_df = pd.DataFrame(stations_expand)
    return stations_df

def read_stations(path='data/stations.csv'):
    reader = list(csv.DictReader(open(path)))
    grouper = itemgetter("station_link", "station_thai_name", "station_name")
    stations = []
    for key, group in groupby(sorted(t, key=grouper), grouper):
        temp_dict = dict(zip(["station_link", "station_thai_name", "station_name"], key))
        temp_dict["connecting_lines"] = [item for item in group]
        stations.append(temp_dict)
    return stations

def query_station(query, stations):
    """
    Get closest bus or train station for given query
    """
    stations_enlish = [station['station_name'] for station in stations]
    stations_thai = [station['station_thai_name'] for station in stations]
    _station = get_close_matches(query , stations_thai, n=1, cutoff=0.6)
    _station.extend(get_close_matches(query, stations_enlish, n=1, cutoff=0.6))
    query_st = [station for station in stations if (query == station['station_name'] or query in station['station_thai_name'])]
    if query_st is not None:
        query_first = query_st[0]
        query_text = '+'.join(query_first['station_name'].split())
        query_first.update({'query': query_text})
        return query_first
    else:
        return None

def get_commute_instruction_link(start, end, stations):
    query_link = ''
    station_start = query_station(start, stations)
    station_end = query_station(end, stations)
    if not station_start:
        print('something wrong with start location')
        return None
    if not station_end:
        print('something wrong with end location')
        return None
    if station_start and station_end:
        query_link = 'http://www.transitbangkok.com/showBestRoute.php?from=%s&to=%s&originSelected=false&destinationSelected=false' \
                    % (station_start['query'], station_end['query'])
    return query_link

def get_commute_instruction(start, end, stations):
    query_link = get_commute_instruction_link(start, end, stations)
    if query_link:
        route_request = requests.get(query_link)
        soup_route = BeautifulSoup(route_request.content, 'lxml')
        descriptions = soup_route.find('div', attrs={'id': 'routeDescription'})

        route_descriptions = []
        for description in descriptions.find_all('img'):
            action = description.next_sibling
            station = action.next_sibling.get_text()
            if 'travel' in action.lower():
                lines = [a.text for a in descriptions.find_all('a') if a.text.isdigit()]
            else:
                lines = []
            route_descriptions.append({'action': action.strip(),
                                       'station': station.strip(),
                                       'lines': lines})
    else:
        route_descriptions = None
    return route_descriptions
