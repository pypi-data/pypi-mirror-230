import os
from dataclasses import dataclass
from typing import List, cast
from bs4 import BeautifulSoup
import bs4

from ac_core.modal.problem_test_case import ProblemTestCase
from ac_core.interfaces.HttpUtil import HttpUtilInterface
from ac_core.problem import parse_task
from ac_core.utils import HTML_PARSER, remove_suffix
from ac_core.constant import _SITE_URL
from ac_core.utils.html_parse_helper import parse_start_end, parse_url


@dataclass
class ParserProblemResult:
  id: str
  url: str
  name: str
  time_limit_msec: int  # ms
  memory_limit_kb: int  # kb


@dataclass
class ParserResult:
  start_time: int
  end_time: int
  name: str
  url: str
  problems: List[ParserProblemResult]


@dataclass
class FetchProblemResult:
  id: str
  url: str
  name: str
  score: int
  time_limit_msec: int
  memory_limit_kb: int
  tests: List[ProblemTestCase]


@dataclass
class FetchResult:
  start_time: int
  end_time: int
  name: str
  url: str
  problems: List[FetchProblemResult]


def parse_tasks(html: str) -> ParserResult:
  """parse tasks page, this method will not parse the detail page(such as testcases) of the tasks

    :param html: the html source get from ``https://atcoder.jp/contests/{contests_id}/tasks``

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import parse_tasks

        r = requests.get('https://atcoder.jp/contests/abc260/tasks')
        if r.status_code == 200:
            print(parse_tasks(r.text)) # pass html
  """
  soup = BeautifulSoup(html, HTML_PARSER)
  problems: List[ParserProblemResult] = []

  tbody = cast(bs4.Tag, soup.find('tbody'))
  trs = tbody.find_all('tr')
  for tr in trs:
    tds = tr.find_all('td')
    assert len(tds) > 0
    url = _SITE_URL + tds[1].find('a')['href']
    alphabet = tds[0].text
    name = tds[1].text
    if tds[2].text.endswith(' msec'):
      time_limit_msec = int(remove_suffix(tds[2].text, ' msec'))
    elif tds[2].text.endswith(' sec'):
      time_limit_msec = int(float(remove_suffix(tds[2].text, ' sec')) * 1000)
    else:
      assert False
    if tds[3].text.endswith(' KB'):
      memory_limit_kb = int(remove_suffix(tds[3].text, ' KB'))
    elif tds[3].text.endswith(' MB'):
      memory_limit_kb = int(float(remove_suffix(tds[3].text, ' MB')) * 1000)  # TODO: confirm this is MB truly, not MiB
    else:
      assert False
    if len(tds) == 5:
      assert tds[4].text.strip() in ('', 'Submit', '提出')

    problems.append(
        ParserProblemResult(
            id=alphabet,
            url=url,
            name=name,
            time_limit_msec=time_limit_msec,
            memory_limit_kb=memory_limit_kb,
        ))
  url = parse_url(soup)
  name = soup.find(class_="contest-title").text
  start_time, end_time = parse_start_end(soup)

  result = ParserResult(
      url=url,
      start_time=start_time,
      end_time=end_time,
      name=name,
      problems=problems,
  )

  return result


def fetch_tasks(http_util: HttpUtilInterface, contest_id: str) -> FetchResult:
  """Fetch tasks with http_util and contest_id, this methods will parse both meta info of tasks and the detail page of tasks

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import fetch_tasks
        print(fetch_tasks(requests.session(), 'abc259')) # pass contest id
  """
  contest_url = _SITE_URL + '/contests/' + contest_id + '/tasks'
  contest_resp = http_util.get(contest_url)
  assert contest_resp.status_code == 200
  contest_result = contest_resp.text
  contest_parser_result = parse_tasks(contest_result)
  problems_meta = contest_parser_result.problems
  urls = list(map(lambda p: p.url, problems_meta))

  def fetch_p(url: str) -> FetchProblemResult:
    problem_resp = http_util.get(url)
    assert problem_resp.status_code == 200
    problem_result = problem_resp.text
    problem_parser_result = parse_task(problem_result)
    return FetchProblemResult(
        id=problem_parser_result.id,
        url=problem_parser_result.url,
        name=problem_parser_result.name,
        score=problem_parser_result.score,
        time_limit_msec=problem_parser_result.time_limit_msec,
        memory_limit_kb=problem_parser_result.memory_limit_kb,
        tests=problem_parser_result.tests,
    )

  problems = [fetch_p(url) for url in urls]

  return FetchResult(
      url=contest_parser_result.url,
      start_time=contest_parser_result.start_time,
      end_time=contest_parser_result.end_time,
      name=contest_parser_result.name,
      problems=problems,
  )


def fetch_tasks_meta(http_util: HttpUtilInterface, contest_id: str) -> ParserResult:
  """fetch tasks page by *http_util* with *contest_id*, and then parse the tasks' meta info with :py:func:`parse_tasks()`

    :param http_util: e.g. ``requests.session()``
    :param contest_id: the number in contest url, e.g. ``abc123``

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import fetch_tasks_meta
        print(fetch_tasks_meta(requests.session(), 'abc260'))
  """
  url = os.path.join(_SITE_URL, 'contests', contest_id, 'tasks')
  resp = http_util.get(url)
  assert resp.status_code == 200
  return parse_tasks(resp.text)
