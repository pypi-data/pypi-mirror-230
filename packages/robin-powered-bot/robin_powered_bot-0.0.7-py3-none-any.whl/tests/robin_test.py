from datetime import datetime

import pook

from robot.reservations import Reservation
from robot.robin import Robin
from robot.user import UserInfo
from tests.constants import (DURATION, EMPTY_JSON_RESPONSE, JSON_RESPONSE,
                             START_TIME, SUCCESSFUL_CHECK_IN,
                             SUCCESSFUL_RESERVATION, RESERVATION_CHECKED_IN_BODY)


@pook.on
def test_robin_reservation():
    users_info = [UserInfo("dbarone@factset.com", START_TIME, DURATION, 111, 619521, "Etc/UTC")]
    r = Robin(users_info)
    pook.get(Reservation.build_list_reservations_url(datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 111),
             reply=200, response_json=EMPTY_JSON_RESPONSE)
    pook.get(Reservation.build_list_reservations_url(datetime(2022, 9, 23, 11), datetime(2022, 9, 23, 19), 111),
             reply=200, response_json=EMPTY_JSON_RESPONSE)
    url, body = Reservation.build_reserve_request(
        datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 111, 619521, "dbarone@factset.com", "Etc/UTC")
    pook.post(url, json=body, reply=200, response_json=SUCCESSFUL_RESERVATION)
    url, body = Reservation.build_reserve_request(
        datetime(2022, 9, 23, 11), datetime(2022, 9, 23, 19), 111, 619521, "dbarone@factset.com", "Etc/UTC")
    pook.post(url, json=body,
              reply=200, response_json=SUCCESSFUL_RESERVATION)
    results = r.reserve(datetime(2022, 9, 22), datetime(2022, 9, 25))
    assert results == {619521: {'2022-09-22': True, '2022-09-23': True}}


@pook.on
def test_checkin_reservation():

    users_info = [UserInfo("dbarone@factset.com", START_TIME, DURATION, 111, 1, "Etc/UTC"),
                  UserInfo("doe@factset.com", START_TIME, DURATION, 222, 2, "Etc/UTC")]
    r = Robin(users_info)
    pook.get(Reservation.build_list_reservations_url(datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 111),
             reply=200, response_json=JSON_RESPONSE)
    pook.get(Reservation.build_list_reservations_url(datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 222),
             reply=200, response_json=EMPTY_JSON_RESPONSE)
    url, body = Reservation.build_checkin_request(
        1, "2254519933545219475")
    pook.put(url, json=body, reply=200,
             response_json=SUCCESSFUL_CHECK_IN)
    results = r.check_in(datetime(2022, 9, 22))
    assert results == {1: True}


@pook.on
def test_already_checkedin_reservation():

    users_info = [UserInfo("dbarone@factset.com", START_TIME, DURATION, 111, 1, "Etc/UTC")]
    r = Robin(users_info)
    pook.get(Reservation.build_list_reservations_url(datetime(2022, 9, 22, 11), datetime(2022, 9, 22, 19), 111),
             reply=200, response_json=RESERVATION_CHECKED_IN_BODY)
    results = r.check_in(datetime(2022, 9, 22))
    assert results == {1: False}
