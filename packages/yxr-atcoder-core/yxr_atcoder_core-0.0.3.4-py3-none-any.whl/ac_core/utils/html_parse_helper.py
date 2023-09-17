from typing import Tuple, cast
from bs4 import BeautifulSoup
import bs4

from ac_core.utils import time_str_2_timestamp


def parse_start_end(soup: BeautifulSoup) -> Tuple[int, int]:
  time_range = cast(bs4.Tag, soup.find(class_="contest-duration")).find_all(class_="fixtime-full")
  return time_str_2_timestamp(time_range[0].text), time_str_2_timestamp(time_range[1].text)


def parse_url(soup: BeautifulSoup) -> str:
  return cast(bs4.Tag, soup.find("meta", property="og:url")).attrs["content"]
