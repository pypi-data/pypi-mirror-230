import re

from urllib.parse import urlparse
from ac_core.utils import remove_suffix


def url_2_contest_id(url: str) -> str:
  """
  :param url: example: ``https://atcoder.jp/contests/agc030``
  :returns: contest id. e.g. 'agc030'

  Examples:

  .. code-block:: 

      from ac_core.url import url_2_contest_id
      print(url_2_contest_id('https://atcoder.jp/contests/abc260/tasks/abc260_b'))
  """

  result = urlparse(url)
  if result.hostname is None:
    return ""

  # example: https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d
  if result.scheme in ('', 'http', 'https') and result.hostname.endswith('.contest.atcoder.jp'):
    return remove_suffix(result.hostname, '.contest.atcoder.jp')

  # example: https://atcoder.jp/contests/agc030
  if result.scheme in ('', 'http', 'https') and result.hostname in ('atcoder.jp', 'beta.atcoder.jp'):
    m = re.match(r'/contests/([\w\-_]+)/?.*', result.path)
    if m:
      return m.group(1)
  assert False
