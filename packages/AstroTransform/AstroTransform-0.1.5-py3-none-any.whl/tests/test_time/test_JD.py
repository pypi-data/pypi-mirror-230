import pytest
from datetime import datetime, timedelta
from AstroTransform.time import JD 

# Some dates to work with as fixtures
@pytest.fixture
def date_data():
    dt = datetime(2023, 9, 5, 14, 00, 00)
    jd = 2460193.08333
    mjd = jd - 2400000.5
    return dt, jd, mjd

def test_to_jd(date_data):
    dt, jd, _ = date_data
    calculated_jd = JD.to_jd(dt)
    assert round(calculated_jd, 5) == round(jd, 5)

def test_to_mjd(date_data):
    dt, _, mjd = date_data
    calculated_mjd = JD.to_mjd(dt)
    assert round(calculated_mjd, 5) == round(mjd, 5)
# assert almost equal
def test_from_jd(date_data):
    dt, jd, _ = date_data
    calculated_dt = JD.from_jd(jd)
        #round to seconds
    if calculated_dt.microsecond >= 500000:
        calculated_dt = calculated_dt + timedelta(seconds=1)
        calculated_dt = calculated_dt.replace(microsecond=0)
    else :
        calculated_dt = calculated_dt.replace(microsecond=0)
    assert pytest.approx(calculated_dt) == pytest.approx(dt)

def test_from_mjd(date_data):
    dt, _, mjd = date_data
    calculated_dt = JD.from_mjd(mjd)
    #round to seconds
    if calculated_dt.microsecond >= 500000:
        calculated_dt = calculated_dt + timedelta(seconds=1)
        calculated_dt = calculated_dt.replace(microsecond=0)
    else :
        calculated_dt = calculated_dt.replace(microsecond=0)
    assert pytest.approx(calculated_dt) == pytest.approx(dt)

# Test exceptions for invalid input types
def test_to_jd_invalid_type():
    with pytest.raises(TypeError):
        JD.to_jd("invalid")

def test_to_mjd_invalid_type():
    with pytest.raises(TypeError):
        JD.to_mjd("invalid")

def test_from_jd_invalid_type():
    with pytest.raises(TypeError):
        JD.from_jd("invalid")

def test_from_mjd_invalid_type():
    with pytest.raises(TypeError):
        JD.from_mjd("invalid")
