"""
Package for calculating Local Sidereal Time.
"""

import numpy as np
from datetime import datetime, timedelta
from AstroTransform.time import JD

def local_to_ut(local_time, longitude):
    """
    Convert a local time to a Universal Time.

    Parameters
    ----------
    local_time : datetime.datetime
        The local time to convert to Universal Time.
    longitude : float
        The longitude of the observer in degrees.

    Returns
    -------
    datetime.datetime
        The Universal Time.
    """
    if not isinstance(local_time, datetime):
        raise TypeError("Expected a datetime.datetime object for 'local_time'.")
    if not isinstance(longitude, (int, float)):
        raise TypeError("Expected a float or int for 'longitude'.")

    # Calculate the offset in hours
    offset = longitude / 15.0

    # Convert to UT
    ut = local_time - timedelta(hours=offset)

    return ut

def ut_to_local(ut, longitude):
    """
    Convert a Universal Time to a local time.

    Parameters
    ----------
    ut : datetime.datetime
        The Universal Time to convert to local time.  
    longitude : float
        The longitude of the observer in degrees.
    
    Returns
    -------
    datetime.datetime
        The local time.
    """

    if not isinstance(ut, datetime):
        raise TypeError("Expected a datetime.datetime object for 'ut'.")
    if not isinstance(longitude, (int, float)):
        raise TypeError("Expected a float or int for 'longitude'.")

    # Calculate the offset in hours
    offset = longitude / 15.0

    # Convert to local time
    local_time = ut + timedelta(hours=offset)

    return local_time

def lst(date_time, longitude):
    """
    Calculate the Local Sidereal Time.

    Parameters
    ----------
    date_time : datetime.datetime
        The datetime object to calculate the LST for.
    longitude : float
        The longitude of the observer in degrees.
    
    Returns
    -------
    float
        The Local Sidereal Time in hours.
    """

    #convert to UT
    ut = local_to_ut(date_time, longitude)

    # Calculate the Julian Date
    jd = JD.to_jd(ut)

    # calculate the number of days since 1st january 2000 at 12:00 UT
    D = (jd - 2451545.0)

    # calculate GMST
    GMST = (18.697374558 + (24.06570982441908 * D)) % 24

    # calculate LST
    #if east of Greenwich, add longitude
    if longitude > 0:
        LST = (GMST + (longitude / 15))
    #if west of Greenwich, subtract longitude
    else:
        LST = (GMST - (abs(longitude) / 15))

    return LST





