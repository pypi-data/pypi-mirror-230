import numpy as np
from datetime import datetime, timedelta
from AstroTransform.time import JD, lst

"""
calculate hour angle
"""

def hourangle(LST, RA):
    """
    Calculate the hour angle of an object.

    Parameters
    ----------
    LST : float
        The local sidereal time in hours.
    RA : float
        The right ascension of the object in hours.

    Returns
    -------
    float
        The hour angle in hours.
    """
    if not isinstance(LST, (int, float)):
        raise TypeError("Expected a float or int for 'LST'.")
    if not isinstance(RA, (int, float)):
        raise TypeError("Expected a float or int for 'RA'.")

    HA = LST - RA
    #normalise HA between -12 and 12
    if HA > 12:
        HA = HA - 24
    elif HA < -12:
        HA = HA + 24

    return HA

def ha_to_deg(HA):
    """
    Convert an hour angle to degrees.

    Parameters
    ----------
    HA : float
        The hour angle in hours.

    Returns
    -------
    float
        The hour angle in degrees.
    """
    if not isinstance(HA, (int, float)):
        raise TypeError("Expected a float or int for 'HA'.")

    return HA * 15.0

def deg_to_ha(HA):
    """
    Convert an hour angle to degrees.

    Parameters
    ----------
    HA : float
        The hour angle in degrees.

    Returns
    -------
    float
        The hour angle in hours.
    """
    if not isinstance(HA, (int, float)):
        raise TypeError("Expected a float or int for 'HA'.")

    return HA / 15.0
