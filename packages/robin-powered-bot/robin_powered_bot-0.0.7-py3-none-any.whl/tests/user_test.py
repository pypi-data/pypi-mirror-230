import pook
import pytest

from robot.user import UserInfo
from tests.constants import (DURATION, START_TIME, USER_FOUND_RESPONSE,
                             USER_NOT_FOUND)


@pook.on
def test_user():
    pook.get(UserInfo.build_user_url("dbarone@factset.com"),
             reply=200, response_json=USER_FOUND_RESPONSE)
    user = UserInfo("dbarone@factset.com", START_TIME, DURATION, 1)
    assert user.reserver_id == 619521

    pook.get(UserInfo.build_user_url("doe@factset.com"),
             reply=404, response_json=USER_NOT_FOUND)
    with pytest.raises(Exception, match=r"user .* not found"):
        user = UserInfo("doe@factset.com", START_TIME, DURATION, 1)
