from logging import getLogger
from typing import cast
from bs4 import BeautifulSoup
import bs4

from ac_core.constant import _SITE_URL
from ac_core.interfaces.HttpUtil import HttpUtilInterface
from ac_core.utils import HTML_PARSER

logger = getLogger(__name__)


def is_logged_in(http_util: HttpUtilInterface) -> bool:
  """This method will use ``http_util`` for login check by visit atcoder site and parse html

    :param HttpUtilInterface http_util: a http instance, for example ``requests.session()``

    :returns: if it is successful logged in.

    :examples:

    .. code-block::

      from ac_core.auth import fetch_login, is_logged_in
      import requests
      h = requests.session()
      #h = Helper(requests.session())
      print(is_logged_in(h))
      print(fetch_login(h, 'username', 'password'))
      print(is_logged_in(h))
  """
  html = http_util.get(f"{_SITE_URL}/home").text
  soup = BeautifulSoup(html, HTML_PARSER)
  dropdown_menus = soup.find_all('ul', class_="dropdown-menu")
  found_user_link = False
  for menu in dropdown_menus:
    a_s = menu.find_all('a')
    for a in a_s:
      if a['href'].startswith('/users/'):
        found_user_link = True

  return found_user_link


def fetch_login(http_util: HttpUtilInterface, username: str, password: str) -> bool:
  """This method will use ``http_util`` for login request and :py:func:`is_logged_in()` for login check

    :param http_util: a http instance, for example ``requests.session()``
    :param username: AtCoder username
    :param password: AtCoder password 

    :returns: if it is successful post and logged

    :examples:

    .. code-block::

      from ac_core.auth import fetch_login, is_logged_in
      import requests
      h = requests.session()
      #h = Helper(requests.session())
      print(is_logged_in(h))
      print(fetch_login(h, 'username', 'password'))
      print(is_logged_in(h))
  """
  try:
    res = http_util.get(_SITE_URL + '/login')
    soup = BeautifulSoup(res.text, HTML_PARSER)
    csrf_token = cast(bs4.Tag, soup.find(attrs={'name': 'csrf_token'})).get('value')
    post_data = {
        'csrf_token': csrf_token,
        'username': username,
        'password': password,
    }
    ret = http_util.post(url='https://atcoder.jp/login', data=post_data)
    if ret.status_code == 403:
      # TODO fix???
      # 403 REVEL_CSRF: tokens mismatch. 似乎因为历史cookie导致？更新了也不能成功？
      logger.error('Atcoder 403(may need clear cookies and relogin):')
      logger.error(ret.text)
  except Exception as e:
    logger.exception(e)
    return False
  return is_logged_in(http_util)


class InvalidSessionError(Exception):
  """
    :meta private:
  """
  # not use, hide in doc now
  DEFAULT_MESSAGE = "Your login session is invalid. please relogin."

  def __init__(self, message: str = DEFAULT_MESSAGE) -> None:
    super().__init__(message)


# TODO logout support
