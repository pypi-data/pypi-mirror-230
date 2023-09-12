"""
Package for handling of Julian Dates and Modified Julian Dates.
"""

import numpy as np
from datetime import datetime


def to_jd(date_time):
    """
    Convert a datetime object to a Julian Date.
    
    Parameters
    ----------
    date_time : datetime.datetime
        The datetime object to convert to a Julian Date.

    Returns
    -------
    float
        The Julian Date.
    """
    if not isinstance(date_time, datetime):
        raise TypeError("Expected a datetime.datetime object for 'date_time'.")

    year, month, day = date_time.year, date_time.month, date_time.day
    hour, minute, second = date_time.hour, date_time.minute, date_time.second

    a = np.floor(year / 100)
    b = 2 - a + np.floor(a / 4)
    c = np.floor(365.25 * year)
    d = np.floor(30.6001 * (month + 1))

    day_fraction = day + (hour + minute / 60.0 + second / 3600.0) / 24.0
    jd = b + c + d + day_fraction + 1720994.5

    return jd


def to_mjd(date_time):
    """
    Convert a datetime object to a Modified Julian Date.

    Parameters
    ----------
    date_time : datetime.datetime
        The datetime object to convert to a Modified Julian Date.

    Returns
    -------
    float
        The Modified Julian Date.
    """
    if not isinstance(date_time, datetime):
        raise TypeError("Expected a datetime.datetime object for 'date_time'.")

    return to_jd(date_time) - 2400000.5


def from_jd(jd):
    """
    Convert a Julian Date to a datetime object.

    Parameters
    ----------
    jd : float
        The Julian Date to convert to a datetime object.

    Returns
    -------
    datetime.datetime
        The datetime object.
    """
    if not isinstance(jd, (float, int)):
        raise TypeError("Expected a float or int for 'jd'.")

    jd += 0.5  # Adjusting JD to start from noon instead of midnight
    z = int(jd)
    f = jd - z

    a = z if z < 2299161 else z + 1 + int((z - 1867216.25) / 36524.25) - int((z - 1867216.25) / 36524.25) / 4

    b, c, d = a + 1524, int((a + 1524 - 122.1) / 365.25), int(365.25 * int((a + 1524 - 122.1) / 365.25))
    e = int((b - d) / 30.6001)

    day = int(b - d - int(30.6001 * e) + f)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    day_fraction = f + day - int(day)
    hour, minute = divmod(day_fraction * 24, 1)
    minute, second = divmod(minute * 60, 1)
    second, microsecond = divmod(second * 60, 1)

    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(microsecond * 1e6))


def from_mjd(mjd):
    """
    Convert a Modified Julian Date to a datetime object.

    Parameters
    ----------
    mjd : float
        The Modified Julian Date to convert to a datetime object.

    Returns
    -------
    datetime.datetime
        The datetime object.
    """
    if not isinstance(mjd, (float, int)):
        raise TypeError("Expected a float or int for 'mjd'.")

    return from_jd(mjd + 2400000.5)
