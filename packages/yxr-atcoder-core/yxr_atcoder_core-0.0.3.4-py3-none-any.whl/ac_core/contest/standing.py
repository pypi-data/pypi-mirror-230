from dataclasses import dataclass, field
import json
from typing import Any, Dict, List
from dataclasses_json import dataclass_json
from ac_core.interfaces.HttpUtil import HttpUtilInterface


@dataclass_json
@dataclass
class TaskInfoStruct:
  Assignment: str = "A"
  TaskName: str = "Middle  Letter"
  TaskScreenName: str = "abc266_a"


@dataclass_json
@dataclass
class TaskResultsStruct:
  Additional: Any = None
  Count: int = 1
  Elapsed: int = 84000000000
  Failure: int = 1
  Frozen: bool = False
  Penalty: int = 0
  Pending: bool = False
  Score: int = 10000
  Status: int = 1
  SubmissionID: int = 34368488


@dataclass_json
@dataclass
class TotalResultStruct:
  Accepted: int = 8
  Additional: Any = None
  Count: int = 8
  Elapsed: int = 2079000000000
  Frozen: bool = False
  Penalty: int = 0
  Score: int = 320000


@dataclass_json
@dataclass
class StandingsDataStruct:
  Additional: Any = None
  Affiliation: str = "Peking University"
  AtCoderRank: int = 18
  Competitions: int = 21
  Country: str = "CN"
  IsRated: bool = False
  IsTeam: bool = False
  OldRating: int = 3337
  Rank: int = 1
  Rating: int = 3337
  TaskResults: Dict[str, TaskResultsStruct] = field(default_factory=lambda: {})
  TotalResult: TotalResultStruct = field(default_factory=lambda: TotalResultStruct())
  UserIsDeleted: bool = False
  UserName: str = "jiangly"
  UserScreenName: str = "jiangly"


@dataclass_json
@dataclass
class StandingStruct:
  AdditionalColumns: Any = None
  Fixed: bool = False
  StandingsData: List[StandingsDataStruct] = field(default_factory=lambda: [])
  TaskInfo: List[TaskInfoStruct] = field(default_factory=lambda: [])
  Translation: Any = None

  @staticmethod
  def from_dict(o) -> 'StandingStruct':  # https://github.com/lidatong/dataclasses-json/issues/23
    assert (False)


def parse_standing(html: str) -> StandingStruct:
  """parse json standings to struct

    :param html: the html data get from ``https://atcoder.jp/contests/{contest_id}/standings/json``

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import parse_standing
        r = requests.get('https://atcoder.jp/contests/abc260/standings/json')
        if r.status_code == 200:
            print(parse_standing(r.text)) # pass html
  """
  json_res = json.loads(html)
  return StandingStruct.from_dict(json_res)


def fetch_standing(http_util: HttpUtilInterface, contest_id: str) -> StandingStruct:
  """parse standings with http_util to struct

    :param http_util: e.g. ``requests.session()``
    :param contest_id: the number in contest url, e.g. ``abc123``

    :examples:

    .. code-block::

        import requests
        from ac_core.contest import fetch_standing
        print(fetch_standing(requests.session(), 'abc260'))
  """
  url = f'https://atcoder.jp/contests/{contest_id}/standings/json'
  res = http_util.get(url)
  assert res.status_code == 200
  return parse_standing(res.text)