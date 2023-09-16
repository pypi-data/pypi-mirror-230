from eai_commons.utils.cryptor import base64_decode, UTF_8_ENCODING


def parse_basic_auth(
    auth_base64_string: str, encoding: str = UTF_8_ENCODING
) -> tuple[str, str]:
    assert auth_base64_string.startswith("Basic "), "invalid basic auth."

    try:
        credentials = base64_decode(auth_base64_string[6:], encoding)
    except Exception as e:
        raise Exception("base64_decode error. maybe you should set the encoding? ")

    # 提取用户名和密码
    username, password = credentials.split(":", 1)
    return username, password


def parse_bearer_token(bearer_token_string: str) -> str:
    assert bearer_token_string.startswith("Bearer "), "invalid bearer token."
    return bearer_token_string[7:].strip()
