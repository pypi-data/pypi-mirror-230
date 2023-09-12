'''
parse lat lon string and return tupple
'''
import regex as re

def lat_lon_from_str(coordinates):
    '''
    Recieve lat lon in format "28°45′44″N 17°52′45″W" and return a tupple

    Parameters
    -----------

    coordinates : string
        string in format "28°45′44″N 17°52′45″W"

    Returns
    --------
    lat : float
        latitude in decimal degrees
    lon : float
        longitude in decimal degrees
    '''
    if not isinstance(coordinates, str):
        raise TypeError("Expected a string for 'coordinates'.")
    
    # split string into lat and lon
    lat, lon = coordinates.split(' ')

    # split lat into degrees, minutes, seconds and hemisphere with one regex
    lat_deg, lat_min, lat_sec, lat_hem = re.split(r'°|′|″', lat)
    lon_deg, lon_min, lon_sec, lon_hem = re.split(r'°|′|″', lon)

    # convert to float
    if lat_hem == 'S':
        lat_deg = -float(lat_deg) - float(lat_min)/60 - float(lat_sec)/3600
    else:
        lat_deg = float(lat_deg) + float(lat_min)/60 + float(lat_sec)/3600
    
    if lon_hem == 'W':
        lon_deg = -float(lon_deg) - float(lon_min)/60 - float(lon_sec)/3600
    else:
        lon_deg = float(lon_deg) + float(lon_min)/60 + float(lon_sec)/3600

    return lat_deg, lon_deg
