START_TIME = 11
DURATION = 8

USER_FOUND_RESPONSE = {
    "meta": {
        "status_code": 200,
        "status": "OK",
        "message": "",
        "more_info": {},
        "errors": []
    },
    "data": {
        "id": 619521,
        "name": "Donato Barone",
        "family_name": "Barone",
        "given_name": "Donato",
        "slug": "donato-barone",
        "avatar": "https://static.robinpowered.com/reimagine/images/blahblah.jpg",
        "time_zone": "Etc/UTC",
        "created_at": "2019-12-03T19:42:46+0000",
        "updated_at": "2021-12-03T14:17:02+0000",
        "is_pending": False,
        "primary_email": {
            "email": "dbarone@factset.com",
            "is_verified": True
        },
        "working_hours": None
    }
}

USER_NOT_FOUND = {
    "meta": {
        "status_code": 404,
        "status": "NOT_FOUND",
        "message": "Object does not exist",
        "more_info": {},
        "errors": []
    },
    "data": {}
}

JSON_RESPONSE = {
    "meta": {
        "status_code": 200,
        "status": "OK",
        "message": "",
        "more_info": {},
        "errors": []
    },
    "data": [
        {
            "id": "2254519933545219475",
            "group_seat_reservation_id": None,
            "seat_id": 196962,
            "reserver_id": 619521,
            "type": "hoteled",
            "title": None,
            "start": {
                "date_time": "2022-08-22T11:00:00+0100",
                "time_zone": "Etc/UTC"
            },
            "end": {
                "date_time": "2022-08-22T19:00:00+0100",
                "time_zone": "Etc/UTC"
            },
            "recurrence": None,
            "series_id": None,
            "recurrence_id": None,
            "created_at": "2022-08-19T15:28:39+0000",
            "updated_at": "2022-08-19T15:28:39+0000",
            "reservee": {
                "email": "dbarone@factset.com",
                "user_id": 619521,
                "visitor_id": None,
                "participation_status": "not_responded"
            },
            "confirmation": None
        }
    ],
    "paging": {
        "page": 1,
        "per_page": 10,
        "has_next_page": False
    }
}

RESERVATION_CHECKED_IN_BODY = {
    "meta": {
        "status_code": 200,
        "status": "OK",
        "message": "",
        "more_info": {},
        "errors": []
    },
    "data": [{
        "id": "2498667793369531480",
        "group_seat_reservation_id": None,
        "seat_id": 196962,
        "reserver_id": 619521,
        "type": "hoteled",
        "title": None,
        "start": {
            "date_time": "2022-08-22T11:00:00+0100",
            "time_zone": "Etc/UTC"
        },
        "end": {
            "date_time": "2022-08-22T19:00:00+0100",
            "time_zone": "Etc/UTC"
        },
        "recurrence": None,
        "series_id": None,
        "recurrence_id": None,
        "created_at": "2023-07-22T12:06:52+0000",
        "updated_at": "2023-08-04T13:00:49+0000",
        "reservee": {
            "email": "dbarone@factset.com",
            "user_id": 619521,
            "visitor_id": None,
            "participation_status": "accepted"
        },
        "confirmation": {
            "seat_reservation_id": "2498667793369531480",
            "device_id": None,
            "user_id": 619521,
            "confirmed_at": {
                "date": "2023-08-04 13:00:49.000000",
                "timezone_type": 3,
                "timezone": "UTC"
            }
        }
    }],
    "paging": {
        "page": 1,
        "per_page": 10,
        "has_next_page": False
    }
}

EMPTY_JSON_RESPONSE = {
    "meta": {
        "status_code": 200,
        "status": "OK",
        "message": "",
        "more_info": {},
        "errors": []
    },
    "data": [],
    "paging": {
        "page": 1,
        "per_page": 10,
        "has_next_page": False
    }
}

RESERVATION_BODY = {
    "type": "hoteled",
    "start": {
        "date_time": "2022-09-22T11:00:00Z",
        "time_zone": "Etc/UTC"
    },
    "end": {
        "date_time": "2022-09-22T19:00:00Z",
        "time_zone": "Etc/UTC"
    },
    "reservee": {
        "email": "dbarone@factset.com"
    },
    "reserver_id": 619521
}


SUCCESSFUL_RESERVATION = {
    "meta": {
        "status_code": 200,
        "status": "OK",
        "message": "",
        "more_info": {},
        "errors": []
    },
    "data": {
        "id": "2254543828679656478",
        "group_seat_reservation_id": None,
        "seat_id": 196962,
        "reserver_id": 619521,
        "type": "hoteled",
        "title": None,
        "start": {
            "date_time": "2022-08-23T11:00:00+0100",
            "time_zone": "Etc/UTC"
        },
        "end": {
            "date_time": "2022-08-23T19:00:00+0100",
            "time_zone": "Etc/UTC"
        },
        "recurrence": None,
        "series_id": None,
        "recurrence_id": None,
        "created_at": "2022-08-19T16:16:08+0000",
        "updated_at": "2022-08-19T16:16:08+0000",
        "reservee": {
            "email": "dbarone@factset.com",
            "user_id": 619521,
            "visitor_id": None,
            "participation_status": "not_responded"
        },
        "confirmation": None
    }
}

TOO_FAR_RESERVATION = {
    "meta": {
        "status_code": 400,
        "status": "BAD_REQUEST",
        "message": "The reservation is too far in the future. Reservations for seat `196962` cannot be more than 14 days in advance.",
        "more_info": {},
        "errors": [
            {
                "domain": "scheduling",
                "reason": "seat_booking_policy_violation",
                "message": "The reservation is too far in the future. Reservations for seat `196962` cannot be more than 14 days in advance.",
                "details": {
                    "policy": "advanced_booking_threshold",
                    "booking_threshold": "P14D"
                }
            }
        ]
    },
    "data": {}
}
UNSUCCESSFUL_RESERVATION = {
    "meta": {
        "status_code": 400,
        "status": "BAD_REQUEST",
        "message": "Something else. Reservations for seat `196962`.",
        "more_info": {},
        "errors": [
            {
                "domain": "scheduling",
                "reason": "seat_booking_policy_violation",
                "message": "Something else. Reservations for seat `196962`.",
                "details": {
                    "policy": "another_error",
                    "booking_threshold": "P14D"
                }
            }
        ]
    },
    "data": {}
}

ALREADY_CHECKED_IN = {
    "meta": {
        "status_code": 400,
        "status": "BAD_REQUEST",
        "message": "Cannot confirm desk with ID `2259583504062875574`. Confirmation already exists.",
        "more_info": {},
        "errors": [
            {
                "domain": "scheduling",
                "reason": "event_already_confirmed",
                "message": "Cannot confirm desk with ID `2259583504062875574`. Confirmation already exists."
            }
        ]
    },
    "data": {}
}

CHECK_IN_PAST = {
    "meta": {
        "status_code": 400,
        "status": "BAD_REQUEST",
        "message": "You cannot confirm a seat reservation in the past.",
        "more_info": {},
        "errors": [
            {
                "domain": "scheduling",
                "reason": "too_late_to_confirm_event",
                "message": "You cannot confirm a seat reservation in the past."
            }
        ]
    },
    "data": {}
}

SUCCESSFUL_CHECK_IN = {
    "meta": {
        "status_code": 200,
        "status": "OK",
        "message": "",
        "more_info": {},
        "errors": []
    },
    "data": {
        "seat_reservation_id": "2259587448109532436",
        "device_id": None,
        "user_id": 619521,
        "confirmed_at": {
            "date": "2022-08-26 15:19:16.111562",
            "timezone_type": 3,
            "timezone": "UTC"
        }
    }
}
