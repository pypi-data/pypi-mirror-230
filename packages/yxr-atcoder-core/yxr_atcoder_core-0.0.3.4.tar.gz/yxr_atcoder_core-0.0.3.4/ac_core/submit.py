from dataclasses import dataclass
from typing import Dict, cast

from bs4 import BeautifulSoup
import bs4

from ac_core.constant import _SITE_URL
from ac_core.interfaces.HttpUtil import HttpUtilInterface, HttpRespInterface
from ac_core.url import url_2_contest_id
from ac_core.utils import HTML_PARSER


@dataclass
class SubmitResult:
  url: str


def fetch_fields(html: str) -> Dict[str, str]:
  """parse necessary fields for requests header such as 'csrf_token'

    :param html: the html source from ``https://atcoder.jp/contests/{contest_id}/submit``
  """
  soup = BeautifulSoup(html, HTML_PARSER)
  return {'csrf_token': cast(bs4.Tag, soup.find('input', attrs={'name': 'csrf_token'})).attrs['value']}


def problem_url_2_submit_url(problem_url: str) -> str:
  """covert tool for problem_url to submit_url.

    :param problem_url: e.g. ``'https://atcoder.jp/contests/abc285/tasks/abc285_a'``
    :returns: problem_url e.g. ``'https://atcoder.jp/contests/abc285/submit'``

    :examples:

    .. code-block::

        from ac_core.submit import problem_url_2_submit_url
        print(problem_url_2_submit_url('https://atcoder.jp/contests/abc285/tasks/abc285_a'))
  """
  contest_id = url_2_contest_id(problem_url)
  return _SITE_URL + '/contests/' + contest_id + '/submit'


def fetch_submit(http_util: HttpUtilInterface, problem_url: str, lang_id: str, source_code: str) -> HttpRespInterface:
  """Submit code. You need logged in before using this method.

    :param http_util: e.g. requests.session()
    :param problem_url: e.g. ``'https://atcoder.jp/contests/abc285/tasks/abc285_a'``
    :param lang_id: e.g. ``'4003'`` for ``C++ (GCC 9.2.1)``, use :py:func:`ac_core.language.fetch_language()` to get language list
    :param source_code: the code text


    :examples:

    .. code-block::

        import requests
        from ac_core.auth import fetch_login, is_logged_in
        from ac_core.submit import fetch_submit

        h = requests.session()
        fetch_login(h, 'username', 'password')
        assert(is_logged_in(h))
        print(fetch_submit(h,'https://atcoder.jp/contests/abc285/tasks/abc285_a','4006','print("hello world.")'))
  """
  problem_id = problem_url.split('/')[-1]
  submit_url = problem_url_2_submit_url(problem_url)
  html = (http_util.get(submit_url)).text
  post_data = {
      'sourceCode': source_code,
      'data.LanguageId': lang_id,
      'data.TaskScreenName': problem_id,
  }
  fields = fetch_fields(html)
  for key, val in fields.items():
    post_data[key] = val

  # TODO add test
  return http_util.post(url=submit_url, data=post_data)
