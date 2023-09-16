from eai_commons.utils import auth


BASIC_AUTH = "Basic aGVsbG9raXR0eTpoZWxsb2tpdHR5"
BEARER_TOKEN = "Bearer 2baf5be82ac24e57bb48b0f14e3328b5"


def test_parse_basic_auth():
    username, password = auth.parse_basic_auth(BASIC_AUTH)
    print(f"{username}:{password}")
    assert username == "hellokitty"
    assert password == "hellokitty"


def test_parse_bearer_token():
    bearer_ = auth.parse_bearer_token(BEARER_TOKEN)
    print(f"{bearer_}")
    assert bearer_ == "2baf5be82ac24e57bb48b0f14e3328b5"
