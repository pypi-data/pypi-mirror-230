from datetime import datetime, timedelta
from typing import Dict, List

from robot.reservations import AlreadyCheckedInError, Reservation


class Robin:
    def __init__(self, users_info: List):
        self.users_info = users_info

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def reserve(self, start: datetime, end: datetime = None) -> Dict:
        # there will always be only one seat_id for now
        results = {}
        for user_info in self.users_info:
            seat_id, reserver_id = user_info.seat_id, user_info.reserver_id
            results[reserver_id] = {}
            for current in self.daterange(start, end):
                try:
                    if current.weekday() > 4:
                        print(f"skip weekends {current.strftime('%Y-%m-%d')}")
                        continue

                    print(
                        f"make a reservation seat_id: {seat_id} date: {current.strftime(f'%Y-%m-%d')}")
                    reservation = Reservation(user_info, current)
                    if "-1" != reservation._get_id():
                        continue

                    reservation_id = reservation._reserve()
                    if "-1" == reservation_id:
                        print(f"reservation {reservation_id} too far in the future. stop going through dates")
                        break
                    print(f"reservation successful with id {reservation_id}")
                    results[reserver_id][current.strftime("%Y-%m-%d")] = True
                except AlreadyCheckedInError as e:
                    print(f"error whilst reserving desk in: {e}")
                    results[reserver_id][current.strftime("%Y-%m-%d")] = False
                    pass
        return results

    def check_in(self, current: datetime) -> Dict:
        results = {}
        for user_info in self.users_info:
            try:
                _, reserver_id = user_info.seat_id, user_info.reserver_id
                reservation = Reservation(user_info, current)
                reservation_id = reservation._get_id()
                if "-1" == reservation_id:
                    print(f"no reservation to confirm for {reserver_id}")
                    continue

                reservation._check_in(reservation_id)
                print(f"check in successful for {reservation_id}")
                results[reserver_id] = True
            except AlreadyCheckedInError as e:
                print(f"error whilst checking in: {e}")
                results[reserver_id] = False
                pass
        return results
