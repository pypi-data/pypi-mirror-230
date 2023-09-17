from typing import Protocol


class HttpRespInterface(Protocol):
  status_code: int
  text: str


class HttpUtilInterface(Protocol):

  def get(self, url: str, allow_redirects=True) -> HttpRespInterface:
    assert (False)

  def post(self, url: str, data: object, allow_redirects=True) -> HttpRespInterface:
    assert (False)
