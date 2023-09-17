from dataclasses import dataclass
from typing import List, cast
from bs4 import BeautifulSoup
import bs4
from dataclasses_json import dataclass_json
from ac_core.constant import _SITE_URL
from ac_core.interfaces.HttpUtil import HttpUtilInterface

from ac_core.utils import HTML_PARSER, time_str_2_timestamp


@dataclass_json
@dataclass
class ContestListItem:
  start_timestamp: int
  name: str
  url: str
  rated_range: str  # - 2799,- 1999, All
  duration: int  # min


@dataclass_json
@dataclass
class ContestListPage:
  up_comming: List[ContestListItem]
  recent: List[ContestListItem]


def parse_list(html: str) -> ContestListPage:
  """Parse tasks with http_util this methods will parse both up comming and recent

    :param html: the html data get from ``https://atcoder.jp/contests/``

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import parse_list
        r = requests.get('https://atcoder.jp/contests/')
        if r.status_code == 200:
            print(parse_list(r.text)) # pass html
  """
  soup = BeautifulSoup(html, HTML_PARSER)
  upcomming = cast(bs4.Tag, soup.find(id='contest-table-upcoming').find('tbody')).find_all('tr')
  recent = cast(bs4.Tag, soup.find(id='contest-table-recent').find('tbody')).find_all('tr')

  def transformer(tr: bs4.Tag) -> ContestListItem:
    tds: List[bs4.Tag] = tr.find_all('td')
    h, m = tds[2].text.split(':')  # hour:min, 178:00
    return ContestListItem(start_timestamp=time_str_2_timestamp(tds[0].find('time').text),
                           name=tds[1].find('a').text,
                           url=cast(str,
                                    cast(bs4.Tag, tds[1].find('a'))['href']),
                           duration=int(h) * 60 + int(m),
                           rated_range=tds[3].text)

  return ContestListPage(up_comming=[transformer(o) for o in upcomming], recent=[transformer(o) for o in recent])


def fetch_list(http_util: HttpUtilInterface) -> ContestListPage:
  """Fetch tasks with http_util this methods will parse both up comming and recent

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import fetch_list
        print(fetch_list(requests.session()))
  """
  url = _SITE_URL + '/contests/'
  resp = http_util.get(url)
  assert resp.status_code == 200
  return parse_list(resp.text)