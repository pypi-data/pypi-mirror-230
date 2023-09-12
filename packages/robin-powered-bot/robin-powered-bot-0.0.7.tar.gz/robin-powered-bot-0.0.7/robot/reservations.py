import os
import requests
from datetime import datetime, timedelta
from typing import List
from robot.user import UserInfo


class AlreadyCheckedInError(Exception):
    pass


class Reservation:

    LIST_RESERVATIONS_URL_TEMPLATE = "https://api.robinpowered.com/v1.0/reservations/seats?before={}&after={}&seat_ids={}"
    SET_RESERVATION_URL_TEMPLATE = "https://api.robinpowered.com/v1.0/seats/{}/reservations"
    CHECKIN_URL_TEMPLATE = "https://api.robinpowered.com/v1.0/reservations/seats/{}/confirmation"
    EMPTY_RESERVATION_ID = "-1"

    # TODO: see if we can set the timezone properly
    TIMEZONE_FORMAT_MAPPING = {
        'America/New_York': '-0500',
        'Etc/UTC': 'Z',
    }

    def __init__(self, user_info: UserInfo, rdate: datetime = None):
        self._user_info = user_info
        current_time = rdate if rdate else datetime.utcnow()
        self._reservation_date_start = current_time.replace(hour=user_info.start_time, minute=0, second=0, microsecond=0)
        self._reservation_date_end = self._reservation_date_start + timedelta(hours=user_info.duration)
        token = os.getenv("ROBIN_AUTH_TOKEN", "")
        self._headers = {"Authorization": f"Access-Token {token}"}

    @classmethod
    def format_datetime(cls, date: datetime, timezone: str = "Etc/UTC") -> str:
        tz_str = cls.TIMEZONE_FORMAT_MAPPING[timezone]
        return f"{date.strftime('%Y-%m-%dT%H:00:00')}{tz_str}"

    @classmethod
    def build_list_reservations_url(cls, sdate: datetime, edate: datetime, sid: int):
        return cls.LIST_RESERVATIONS_URL_TEMPLATE.format(
            cls.format_datetime(edate),
            cls.format_datetime(sdate), sid)

    @classmethod
    def build_reserve_request(cls, sdate: datetime, edate: datetime, sid: int, rid: int, email: str, timezone: str) -> List:
        url = cls.SET_RESERVATION_URL_TEMPLATE.format(sid)
        body = {'type': 'hoteled',
                "start": {
                    "date_time": cls.format_datetime(sdate, timezone),
                    "time_zone": timezone
                },
                "end": {
                    "date_time": cls.format_datetime(edate, timezone),
                    "time_zone": timezone
                },
                "reservee": {
                    "email": email
                },
                "reserver_id": rid}
        return [url, body]

    @classmethod
    def build_checkin_request(cls, reserver_id: int, reservation_id: str) -> List:
        url = cls.CHECKIN_URL_TEMPLATE.format(reservation_id)
        body = {"user_id": reserver_id}
        return [url, body]

    def _get_id(self) -> str:
        url = self.build_list_reservations_url(self._reservation_date_start, self._reservation_date_end, self._user_info.seat_id)
        response = requests.get(url, headers=self._headers, verify=False)
        reservations = response.json()['data']
        if len(reservations) == 0:
            return self.EMPTY_RESERVATION_ID
        if len(reservations) > 1:
            raise Exception("should only contain 1 reservation")
        reservation = reservations[0]
        if reservation['confirmation'] is not None:
            raise AlreadyCheckedInError("desk is already checked in")
        return reservation['id']

    def _reserve(self) -> str:
        url, body = self.build_reserve_request(self._reservation_date_start, self._reservation_date_end,
                                               self._user_info.seat_id, self._user_info.reserver_id, self._user_info.email, self._user_info.timezone)
        response = requests.post(
            url, json=body, headers=self._headers, verify=False)
        if response.status_code == 200:
            return response.json()['data']['id']
        if response.status_code == 400:
            meta_response = response.json()['meta']
            try:
                errors = meta_response['errors']
                for error in errors:
                    if error['details']['policy'] == "advanced_booking_threshold":
                        return self.EMPTY_RESERVATION_ID
            except KeyError:
                pass
        raise Exception(
            f"request {url} {body} failed with {response.status_code} and err: {response.json()['meta']['message']}")

    def _check_in(self, reservation_id: int):
        url, body = self.build_checkin_request(self._user_info.reserver_id, reservation_id)
        response = requests.put(
            url, json=body, headers=self._headers, verify=False)
        if response.status_code == 200:
            data_response = response.json()['data']
            return [data_response['seat_reservation_id'], data_response['confirmed_at']['date']]
        raise Exception(
            f"request {url} {body} failed with {response.status_code} and err: {response.json()['meta']['message']}")
