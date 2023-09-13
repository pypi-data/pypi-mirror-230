import http.cookies


def parse_cookie_str(cookie_str: str) -> dict[str, str]:
    """
    convert cookie_str to cookie dict
    :param cookie_str:
    :return:
    """
    cookies = http.cookies.SimpleCookie()
    cookies.load(cookie_str)
    return {k: v.value for k, v in cookies.items()}
