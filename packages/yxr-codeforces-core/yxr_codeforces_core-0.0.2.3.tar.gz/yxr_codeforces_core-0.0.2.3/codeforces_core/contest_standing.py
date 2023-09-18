from dataclasses import dataclass, field
import re
from typing import List, Optional
from bs4 import BeautifulSoup
import bs4

from .interfaces.AioHttpHelper import AioHttpHelperInterface

# TODO post toggle showunofficial


@dataclass
class StandingProblem:
  id: str = ''
  score: str = ''
  time: str = ''


@dataclass
class StandingRow:
  rank: str = ''
  who: str = ''
  passed: Optional[str] = None
  score: str = ''
  hack: str = ''
  penalty: str = ''
  problems: List[StandingProblem] = field(default_factory=lambda: [])


@dataclass
class Standing:
  head: List[str]
  rows: List[StandingRow]
  url: str = ''


def parseStandingHtml(html) -> Standing:
  soup = BeautifulSoup(html, 'lxml')
  currentContestList = soup.find('div', class_='datatable')
  assert isinstance(currentContestList, bs4.Tag)
  rows: List[StandingRow] = []
  trs: List[BeautifulSoup] = currentContestList.find_all('tr')
  ths: List[BeautifulSoup] = trs[0].find_all('th')
  h: List[str] = ['' for i in ths]  # head: get info from th
  for i in range(len(ths)):
    text = ths[i].get_text().strip()
    if text == '#':
      h[i] = 'rank'
    elif text == 'Who':
      h[i] = 'who'
    elif text == '=':
      h[i] = 'score'
    elif text == '*':
      h[i] = 'hack'
    elif text == 'Penalty':
      h[i] = 'penalty'
    else:
      a = ths[i].find('a')
      if a is not None:
        h[i] = a.get_text().strip()

  for i in range(1, len(trs) - 1):  # ignore first(head) and last line(total accepted TODO)
    tds = trs[i].find_all('td')
    row = StandingRow()
    for j in range(len(h)):
      if h[j] == 'rank':
        row.rank = tds[j].get_text().strip()
        # '4\xa0(13)' => '13'
        inbracket = re.search("\\(([0-9]*)\\)", row.rank)
        if inbracket:
          row.rank = inbracket.group(1)
      elif h[j] == 'who':
        row.who = tds[j].get_text().strip()
      elif h[j] == 'score':
        row.score = tds[j].get_text().strip()
      elif h[j] == 'hack':
        row.hack = tds[j].get_text().strip()
      elif h[j] == 'penalty':
        row.penalty = tds[j].get_text().strip()
      else:  # problems
        passScore = tds[j].find_all('span', class_='cell-passed-system-test')
        problem = StandingProblem(id=h[j])
        if passScore and len(passScore) > 0:
          problem.score = passScore[0].get_text().strip()
          problem.time = tds[j].find('span', class_="cell-time").get_text().strip()
        else:
          problem.score = tds[j].get_text().strip()
        row.problems.append(problem)
    rows.append(row)

  # TODO add pagenation
  return Standing(head=h, rows=rows)


async def async_friends_standing(http: AioHttpHelperInterface, contest_id: str, **kw) -> Standing:
  """
    This method will use ``http`` to request ``/contest/<contest_id>/standings/friends/true``, and parse to struct result

    :param contest_id: contest id in url

    :returns: parsed structured result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.account import async_login
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.contest_standing import async_friends_standing

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_login(http=http, handle='<handle>', password='<password>')
          assert(result.success)
          result = await async_friends_standing(http=http, contest_id='1779')
          print(result.head)
          print(len(result.rows))
          print(result.rows[3])
          await http.close_session()

        asyncio.run(demo())
  """
  url = f'/contest/{contest_id}/standings/friends/true'
  resp = await http.async_get(url)
  result = parseStandingHtml(resp)
  result.url = url
  return result


async def async_common_standing(http: AioHttpHelperInterface, contest_id: str, page: str = '1', **kw) -> Standing:
  """
    This method will use ``http`` to request ``/contest/<contest_id>/standings/page/<page>``, and parse to struct result

    :param contest_id: contest id in url
    :param page: pagination 1-index

    :returns: parsed structured result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.contest_standing import async_common_standing

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_common_standing(http=http, contest_id='1779', page='2')
          print(result.head)
          print(len(result.rows))
          print(result.rows[3])
          await http.close_session()

        asyncio.run(demo())
  """
  url = f'/contest/{contest_id}/standings/page/{page}'
  resp = await http.async_get(url)
  result = parseStandingHtml(resp)
  result.url = url
  return result
