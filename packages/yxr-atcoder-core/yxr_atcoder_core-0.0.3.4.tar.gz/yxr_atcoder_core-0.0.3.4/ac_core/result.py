from dataclasses import dataclass
from enum import Enum
import json
import os
import re

from bs4 import BeautifulSoup
from ac_core.constant import _SITE_URL
from ac_core.interfaces.HttpUtil import HttpUtilInterface


@dataclass
class SubmissionResult:

  class Status(Enum):
    INIT: str = 'Init'
    PENDING: str = 'Waiting for Judging'
    RUNNING: str = 'Judging'
    RE: str = 'Runtime Error'
    AC: str = 'Accepted'
    WA: str = 'Wrong Answer'
    CE: str = 'Compilation Error'
    TLE: str = 'Time Limit Exceeded'

  id: str = ''
  url: str = ''  # json url for refetch
  score: int = 500
  status: Status = Status.INIT
  time_cost_ms: int = 0
  mem_cost_kb: int = 0
  msg_txt: str = ''


def watch_result(url: str) -> str:  # sock url, single submissions
  return ''


# title=\"Compilation Error\"\u003eCE\u003c/span\u003e\u003c/td\u003e","Score":"0"
def parse_result(resp: str) -> SubmissionResult:
  """parse submit result get from json result
    :param resp: the json result get from ``https://atcoder.jp/contests/{contest_id}/submissions/me/status/json?sids[]={submision id}``

    :examples:

    .. code-block:: 

        import requests
        from ac_core.result import parse_result

        r = requests.get('https://atcoder.jp/contests/abc101/submissions/me/status/json?sids[]=5371077')
        if r.status_code == 200:
            print(parse_result(r.text)) # pass html
  """
  res = json.loads(resp)["Result"]
  sub_id = list(res.keys())[0]
  soup = BeautifulSoup(res[sub_id]["Html"], "lxml")
  tds = soup.find_all('td')
  status = SubmissionResult.Status(str(tds[0].find('span').attrs.get('title')))
  try:
    score = int(res[sub_id]["Score"])
  except:
    score = 0
  try:
    time_cost_ms = int(tds[1].text.split(" ")[0])
  except:
    time_cost_ms = 0

  try:
    mem_cost_kb = int(tds[2].text.split(" ")[0])
  except:
    mem_cost_kb = 0

  msg_txt = ''
  if status == SubmissionResult.Status.RUNNING:
    msg_txt = soup.text.strip()
  return SubmissionResult(
      id=sub_id,
      score=score,
      status=status,
      time_cost_ms=time_cost_ms,
      mem_cost_kb=mem_cost_kb,
      msg_txt=msg_txt,
  )


def fetch_result_by_url(http_util: HttpUtilInterface, json_url: str) -> SubmissionResult:
  """parse submit result by *http_util* with submission *json_url*.
  
    :param http_util: e.g. ``requests.session()``
    :param json_url: e.g. ``https://atcoder.jp/contests/abc101/submissions/me/status/json?sids[]=5371077``

    :examples:

    .. code-block:: 

        import requests
        from ac_core.result import fetch_result_by_url
        print(fetch_result_by_url(requests.session(),'https://atcoder.jp/contests/abc101/submissions/me/status/json?sids[]=5371077'))

    the structured data returned by :py:func:`fetch_result` has the submission json url

    .. code-block:: 

        import requests
        from ac_core.auth import fetch_login, is_logged_in
        from ac_core.result import fetch_result, fetch_result_by_url

        h = requests.session()
        fetch_login(h, 'username', 'password')
        assert(is_logged_in(h))
        result = fetch_result(h,'https://atcoder.jp/contests/abc275/tasks/abc275_f')
        print(fetch_result_by_url(h,result.url))
  """
  response = http_util.get(url=json_url)
  ret = parse_result(resp=response.text)
  ret.url = json_url
  return ret


def _problem_url_to_sub_url(problem_url: str) -> str:
  # problem_url https://atcoder.jp/contests/abc275/tasks/abc275_f
  r = re.match('^(.*)/tasks/(.*)$', problem_url)
  assert r is not None
  prefix = r.group(1)
  problem_suffix = r.group(2)
  # https://atcoder.jp/contests/abc275/submissions/me?f.Task=abc275_f
  return os.path.join(prefix, f'submissions/me?f.Task={problem_suffix}')


def _parse_json_url(html: str):
  soup = BeautifulSoup(html, 'lxml')
  # <a href='/contests/abc101/submissions/5371227'>Detail</a>
  r = re.search('<td class="text-center">.*?"/contests/(.*?)/submissions/([0-9]*?)\">Detail</a>', str(soup),
                re.DOTALL | re.MULTILINE)
  assert r is not None  # no submission
  return os.path.join(_SITE_URL, f"contests/{r.group(1)}/submissions/me/status/json?sids[]={r.group(2)}")


def fetch_result(http_util: HttpUtilInterface, problem_url: str) -> SubmissionResult:
  """parse submit result by *http_util* with *problem_url*.
    
    You need logged in before using this method. This function will find your last submission for the problem.
  
    :param http_util: e.g. ``requests.session()``
    :param problem_url: e.g. ``https://atcoder.jp/contests/abc275/tasks/abc275_f``

    :examples:

    .. code-block:: 

        import requests
        from ac_core.auth import fetch_login, is_logged_in
        from ac_core.result import fetch_result

        h = requests.session()
        fetch_login(h, 'username', 'password')
        assert(is_logged_in(h))
        print(fetch_result(h,'https://atcoder.jp/contests/abc275/tasks/abc275_f'))
  """
  # https://atcoder.jp/contests/abc275/submissions/me?f.Task=abc275_f
  submission_url = _problem_url_to_sub_url(problem_url)
  # <a href='/contests/abc101/submissions/5371227'>Detail</a>
  # https://atcoder.jp/contests/abc101/submissions/me/status/json?sids[]=5371077
  resp = http_util.get(submission_url)
  json_url = _parse_json_url(resp.text)
  return fetch_result_by_url(http_util, json_url)
