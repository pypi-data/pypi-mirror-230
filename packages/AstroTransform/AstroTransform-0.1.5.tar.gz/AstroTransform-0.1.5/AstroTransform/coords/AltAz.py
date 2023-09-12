""" 
convert target to alt az
"""

import numpy as np
from datetime import datetime, timedelta
from AstroTransform.time import JD, lst
from AstroTransform.coords import hour_angle

def to_alt_az(RA, DEC, Lat, Lon, obs_time):
    """
    Convert a target's RA and DEC to Altitude and Azimuth.
    
    Parameters
    ----------
    RA : float
        The right ascension of the target in hours.
    DEC : float
        The declination of the target in degrees.
    Lat : float
        The latitude of the observer in degrees.
    Lon : float
        The longitude of the observer in degrees.
    obs_time : datetime.datetime
        The local time of the observation
    
    Returns
    -------
    float
        The altitude of the target in degrees.
    float
        The azimuth of the target in degrees.
        
    """

    if not isinstance(RA, (int, float)):
        raise TypeError("Expected a float or int for 'RA'.")
    if not isinstance(DEC, (int, float)):
        raise TypeError("Expected a float or int for 'DEC'.")
    if not isinstance(Lat, (int, float)):
        raise TypeError("Expected a float or int for 'Lat'.")
    if not isinstance(Lon, (int, float)):
        raise TypeError("Expected a float or int for 'Lon'.")
    if not isinstance(obs_time, datetime):
        raise TypeError("Expected a datetime.datetime object for 'obs_time'.")
    
    #convert to radians
    RA_rad = np.deg2rad(RA * 15.0)
    DEC_rad = np.deg2rad(DEC)
    Lat_rad = np.deg2rad(Lat)
    Lon_rad = np.deg2rad(Lon)

    #calculate LST
    LST = lst.local_sidereal_time(obs_time, Lon)
    
    #calculate hour angle
    HA = hour_angle.hourangle(LST, RA)
    HA_rad = np.deg2rad(HA*15.0)
    LSTrad = np.deg2rad(LST*15.0)

    #calculate altitude
    sin_alt = np.sin(DEC_rad)*np.sin(Lat_rad) + np.cos(DEC_rad)*np.cos(Lat_rad)*np.cos(HA_rad)
    alt = np.arcsin(sin_alt)

    #calculate azimuth
    sin_az = -np.sin(HA_rad)*np.cos(DEC_rad)/np.cos(alt)

    #convert to degrees
    alt = np.rad2deg(alt)
    az = np.rad2deg(az)

    
    return alt, az

