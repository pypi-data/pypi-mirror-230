from abc import abstractmethod
from typing import Any, Callable, Dict, Protocol, Tuple, AsyncIterator
import aiohttp


class AioHttpHelperInterface(Protocol):

  @abstractmethod
  def create_form(self, form_data: Dict[str, Any]) -> aiohttp.FormData:
    raise NotImplementedError

  @abstractmethod
  async def async_get(self, url: str, **kwargs) -> str:
    raise NotImplementedError

  @abstractmethod
  async def async_post(self, url: str, data: Any, **kwargs) -> str:
    raise NotImplementedError

  @abstractmethod
  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    raise NotImplementedError

  @abstractmethod
  async def open_session(self) -> aiohttp.ClientSession:
    raise NotImplementedError

  @abstractmethod
  def get_tokens(self) -> Any:
    raise NotImplementedError

  @abstractmethod
  async def close_session(self) -> None:
    raise NotImplementedError

  # TODO move call back out
  @abstractmethod
  async def websockets(self, url: str, callback: Callable[[Any], Tuple[bool, Any]]) -> AsyncIterator[Any]:
    raise NotImplementedError
    # mypy type hint https://github.com/python/mypy/issues/5070
    yield 0
