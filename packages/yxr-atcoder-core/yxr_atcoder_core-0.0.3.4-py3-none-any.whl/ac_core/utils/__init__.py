from datetime import datetime
import time

import bs4

HTML_PARSER = 'lxml'


def remove_prefix(s: str, prefix: str) -> str:
  assert s.startswith(prefix)
  return s[len(prefix):]


def remove_suffix(s: str, suffix: str) -> str:
  assert s.endswith(suffix)
  return s[:-len(suffix)]


# https://www.unixtimestamp.com/
def time_str_2_timestamp(s: str) -> int:
  assert (s.endswith('+0900'))
  TIME_FORMART = "%Y-%m-%d %H:%M:%S%z"  # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
  return int(datetime.strptime(s, TIME_FORMART).timestamp())


def get_direct_children_text(tag: bs4.Tag) -> str:
  """get_direct_children_text collects the text which are direct children of the given tag.

    For example, this returns "A - Hello world " for a tag ``<h2>A - Hello world <a href="...">Editorial</a></h2>``.
    """

  assert isinstance(tag, bs4.Tag)
  text = ''
  for child in tag.children:
    if isinstance(child, bs4.NavigableString):
      # print("check mypy child.string or child.strings")
      text += child.string  # type: ignore # TODO
    elif isinstance(child, bs4.Tag) and child.name == 'br':
      text += '\n'
    else:
      pass
  return text
