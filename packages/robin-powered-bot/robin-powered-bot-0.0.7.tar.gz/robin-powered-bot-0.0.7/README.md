# Robin Powered API Bot - RoBot

Many companies are nowadays using the [Robin](https://robinpowered.com/) platform to connect employees with desks, rooms and each other.

Robin Powered API Bot (RoBot) is a package that tries to simplify the life of employees that are not allowed to have permanent desks anymore. All that is necessary are email and seatid.

## Getting Started

Assuming that you have a supported version of Python installed, you can first set up your environment with:

```py
$ python -m venv .venv
...
$ . .venv/bin/activate
```

Then you can install robin-powered-bot
```py
python -m pip install robin-powered-bot
```

## Using RoBot

In order to use the package an API key has to be provided via the env variable *ROBIN_AUTH_TOKEN*.

### User Info

UserInfo is used to load and store all info about the user, it needs the following parameters:
- email: employee email;
- stime: start time of the working day as it would be specified in Robin;
- duration: how long is your working day, usually 8 hours;
- sid: seat id, identifier of the seat that you want to book.

```py
from src.user import UserInfo
users_info = [UserInfo("dbarone@company.com", 11, 8, 10)]
```

**Notes**: Seat Id has still to be provided, haven't found yet a more user friendly way to do it.

### Reserve

Following an example to book a desk for 5 days, from the 15th to the 20th.

```py
from datetime import datetime
from src.robin import Robin
from src.user import UserInfo

users_info = [UserInfo("dbarone@company.com", 11, 8, 10)]
r = Robin(users_info)
results = r.reserve(datetime(2022, 11, 15), datetime(2022, 11, 20))
print(results)

```

**Notes**:

The reserve method will do the following:
- Reserve all working days;
- Skip all weekends, it doesn't deal with holidays;
- Companies might enforce a limit on how much in advance a desk can be booked, the reserve method will just stop.

## Check in

Following an example of check in.

```py
from datetime import datetime
from src.robin import Robin
from src.user import UserInfo

users_info = [UserInfo("dbarone@company.com", 11, 8, 10)]
r = Robin(users_info)
results = r.check_in(datetime(2022, 11, 24))
print(results)
```


