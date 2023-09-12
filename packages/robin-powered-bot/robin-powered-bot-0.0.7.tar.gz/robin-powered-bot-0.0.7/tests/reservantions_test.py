

from datetime import datetime

import pook
import pytest

from robot.reservations import Reservation
from robot.user import UserInfo
from tests.constants import (ALREADY_CHECKED_IN, CHECK_IN_PAST, DURATION,
                             EMPTY_JSON_RESPONSE, JSON_RESPONSE, START_TIME,
                             SUCCESSFUL_CHECK_IN, SUCCESSFUL_RESERVATION,
                             TOO_FAR_RESERVATION, UNSUCCESSFUL_RESERVATION)


def test_format_datetime():
    formatted = Reservation.format_datetime(datetime(2022, 8, 22, 11), 'Etc/UTC')
    assert formatted == "2022-08-22T11:00:00Z"
    formatted = Reservation.format_datetime(datetime(2022, 8, 22, 15))
    assert formatted == "2022-08-22T15:00:00Z"
    formatted = Reservation.format_datetime(datetime(2022, 8, 22, 15), 'America/New_York')
    assert formatted == "2022-08-22T15:00:00-0500"


def test_build_reservation_url():
    url = Reservation.build_list_reservations_url(datetime(2022, 8, 22, 11), datetime(2022, 8, 22, 19), 1)
    assert url == "https://api.robinpowered.com/v1.0/reservations/seats?before=2022-08-22T19:00:00Z&after=2022-08-22T11:00:00Z&seat_ids=1"
    url = Reservation.build_list_reservations_url(datetime(2022, 8, 22, 11, 22, 56), datetime(2022, 8, 22, 19, 14, 32), 1)
    assert url == "https://api.robinpowered.com/v1.0/reservations/seats?before=2022-08-22T19:00:00Z&after=2022-08-22T11:00:00Z&seat_ids=1"


@pook.on
def test_get_reservation_id():
    url = 'https://api.robinpowered.com/v1.0/reservations/seats?before=2022-08-22T19:00:00Z&after=2022-08-22T11:00:00Z&seat_ids=196962'
    pook.get(url, reply=200, response_json=JSON_RESPONSE)
    user_info = UserInfo("doe@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 8, 22))
    assert reservation._get_id() == "2254519933545219475"


@pook.on
def test_no_reservations():
    url = 'https://api.robinpowered.com/v1.0/reservations/seats?before=2022-08-23T19:00:00Z&after=2022-08-23T11:00:00Z&seat_ids=196962'
    pook.get(url, reply=200, response_json=EMPTY_JSON_RESPONSE)
    user_info = UserInfo("doe@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 8, 23))
    assert reservation._get_id() == "-1"


@pook.on
def test_successful_reservation():
    url, body = Reservation.build_reserve_request(
        datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 196962, 619521, "dbarone@factset.com", "Etc/UTC")
    pook.post(url, json=body, reply=200, response_json=SUCCESSFUL_RESERVATION)
    user_info = UserInfo("dbarone@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 9, 22))
    assert reservation._reserve() == "2254543828679656478"


@pook.on
def test_reservation_too_far_in_future():
    url, body = Reservation.build_reserve_request(
        datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 196962, 619521, "dbarone@factset.com", "Etc/UTC")
    pook.post(url, json=body, reply=400, response_json=TOO_FAR_RESERVATION)
    user_info = UserInfo("dbarone@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 9, 22))
    assert reservation._reserve() == "-1"


@pook.on
def test_unsuccessful_reservation():
    url, body = Reservation.build_reserve_request(
        datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 196962, 619521, "dbarone@factset.com", "Etc/UTC")
    pook.post(url, json=body, reply=400,
              response_json=UNSUCCESSFUL_RESERVATION)
    user_info = UserInfo("dbarone@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 9, 22))
    with pytest.raises(Exception, match=r"request .* failed with .* and err: .*"):
        reservation._reserve()


@pook.on
def test_check_in():
    url, body = Reservation.build_checkin_request(
        619521, "2259587448109532436")
    pook.put(url, json=body, reply=200,
             response_json=SUCCESSFUL_CHECK_IN)
    user_info = UserInfo("dbarone@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 8, 23))
    assert reservation._check_in(2259587448109532436) == ["2259587448109532436", "2022-08-26 15:19:16.111562"]


@pook.on
def test_check_in_past():

    url, body = Reservation.build_checkin_request(
        619521, "2254543828679656478")
    pook.put(url, json=body, reply=400,
             response_json=CHECK_IN_PAST)
    user_info = UserInfo("dbarone@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 8, 23))
    with pytest.raises(Exception, match=r"request .* failed with .* and err: .*") as e:
        reservation._check_in(2254543828679656478)
    expected_exception_message = "request https://api.robinpowered.com/v1.0/reservations/seats/2254543828679656478" \
        "/confirmation {'user_id': 619521} failed with 400 and err: You cannot confirm a seat reservation in the past."
    assert expected_exception_message == str(e.value)


@pook.on
def test_check_in_already_exists():
    url, body = Reservation.build_checkin_request(619521, "2254543828679656478")
    pook.put(url, json=body, reply=204000,
             response_json=ALREADY_CHECKED_IN)
    user_info = UserInfo("dbarone@factset.com", START_TIME, DURATION, 196962, 619521, "Etc/UTC")
    reservation = Reservation(user_info, datetime(2022, 8, 23))
    with pytest.raises(Exception, match=r"request .* failed with .* and err: .*") as e:
        reservation._check_in(2254543828679656478)

    expected_exception_message = "request https://api.robinpowered.com/v1.0/reservations/seats/2254543828679656478/" \
        "confirmation {'user_id': 619521} failed with 204000 and err: Cannot confirm desk with ID `2259583504062875574`. Confirmation already exists."
    assert expected_exception_message == str(e.value)
