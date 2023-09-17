from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup, Tag

from ac_core.constant import _SITE_URL
from ac_core.interfaces.HttpUtil import HttpUtilInterface


@dataclass
class LanguageKV:
  value: str
  text: str


def fetch_language(http_util: HttpUtilInterface) -> List[LanguageKV]:
  """Fetch language key and values, need to have logged into atcoder. You can use :py:func:`ac_core.auth.fetch_login()` for login.

    :param http_util: e.g. ``requests.session()``

    :examples:

    .. code-block::

        import requests
        from ac_core.auth import fetch_login, is_logged_in
        from ac_core.language import fetch_language
        h = requests.session()
        fetch_login(h, 'username', 'password')
        assert(is_logged_in(h))
        print(fetch_language(h))
  """
  url = _SITE_URL + '/contests/practice/submit'
  resp = http_util.get(url)
  assert resp.status_code == 200
  soup = BeautifulSoup(resp.text, 'lxml')
  result: List[LanguageKV] = []
  tag = soup.find('div', attrs={'id': 'select-lang-practice_1'}).find('select')
  if isinstance(tag, Tag):
    options = tag.find_all('option')
    for child in options:
      result.append(LanguageKV(value=child.get('value'), text=child.string))
  return result


# TODO get language list
# TODO add test
