from dataclasses import dataclass
from typing import List
from bs4 import BeautifulSoup
import bs4

from .interfaces.AioHttpHelper import AioHttpHelperInterface


@dataclass
class Lang:
  text: str
  value: str


async def async_language(http: AioHttpHelperInterface, **kw) -> List[Lang]:
  """
    This method will use ``http`` to request ``/problemset/submit``, and parse language options

    :returns: parsed structured result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.account import async_login
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.language import async_language

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_login(http=http, handle='<handle>', password='<password>')
          assert(result.success)
          result = await async_language(http)
          for item in result:
            print(item)
          await http.close_session()

        asyncio.run(demo())
  """
  # login before
  resp = await http.async_get(f'/problemset/submit')
  ret: List[Lang] = []
  soup = BeautifulSoup(resp, 'lxml')
  tags = soup.find('select', attrs={'name': 'programTypeId'})
  if isinstance(tags, bs4.Tag):
    for child in tags.find_all('option'):
      ret.append(Lang(value=child.get('value'), text=child.string))
  return ret
