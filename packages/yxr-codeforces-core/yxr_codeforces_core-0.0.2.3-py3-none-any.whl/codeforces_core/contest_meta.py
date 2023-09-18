from dataclasses import dataclass, field
from enum import Enum
from typing import List, cast
from bs4 import BeautifulSoup
import bs4
from lxml import html
from lxml.etree import _Element
from lxml.html import HtmlMixin

from .interfaces.AioHttpHelper import AioHttpHelperInterface
from .util import soup_find_bs4Tag


class E_STATUS(str, Enum):
  NOT_SUBMITTED = ""
  AC = "AC"
  ERROR = "ERROR"


@dataclass
class ProblemMeta:
  id: str = ''
  url: str = ''
  name: str = ''
  passed: str = ''  # number of passed submission in contest
  status: E_STATUS = E_STATUS.NOT_SUBMITTED
  time_limit_msec: int = 0
  memory_limit_kb: int = 0
  contest_id: str = ''


@dataclass
class ContestMeta:
  id: str = ''
  url: str = ''
  problems: List[ProblemMeta] = field(default_factory=lambda: [])


@dataclass
class Questions:
  when: str
  Q: str
  A: str


@dataclass
class Materials:
  text: str
  url: str


@dataclass
class ContestPage:
  id: str
  url: str
  title: str
  problems: List[ProblemMeta]
  # questions: List[Questions]
  materials: List[Materials]


def parse_problems(resp: str) -> List[ProblemMeta]:
  soup = BeautifulSoup(resp, 'lxml')
  currentContestList = soup.find('div', class_='datatable')

  assert isinstance(currentContestList, bs4.Tag)
  trs: List[BeautifulSoup] = currentContestList.find_all('tr')
  ret = []
  for i in range(1, len(trs)):
    tds = trs[i].find_all('td')
    namediv = tds[1].div.div
    row = ProblemMeta(
        id=tds[0].get_text().strip(),
        url=tds[0].find('a')['href'],
        name=namediv.get_text().strip(),
        passed=tds[3].get_text().split('x')[-1].strip(),
    )

    if 'class' in trs[i].attrs:
      classes: str = trs[i].attrs['class']  # mypy ?, List[str]
      if 'accepted-problem' in classes:
        row.status = E_STATUS.AC
      elif 'rejected-problem' in classes:
        row.status = E_STATUS.ERROR
    limit = tds[1].find('div', class_="notice").get_text().strip()
    if limit.startswith('standard input/output'):
      limit = limit[len('standard input/output'):].strip()
      try:
        t, m = limit.split(',')
        row.time_limit_msec = int(float(t.strip().split(' ')[0]) * 1000)
        row.memory_limit_kb = int(float(m.strip().split(' ')[0]) * 1000)
      except:
        pass

    ret.append(row)
  return ret


def parse_materials(resp: str) -> List[Materials]:
  doc = html.fromstring(resp)
  captions = cast(List[_Element], doc.xpath('.//div[@class="caption titled"]'))
  ret = []
  for c in captions:
    title = c.text[1:].strip()
    if title != 'Contest materials':
      continue
    links = cast(List[_Element], c.getparent().xpath('.//a[@href]'))
    for a in links:
      title_text = str(cast(HtmlMixin, html.fromstring(a.get('title'))).text_content())
      ret.append(Materials(text=title_text, url=a.get('href')))
  return ret


async def async_contest_meta(http: AioHttpHelperInterface, contest_id: str, **kw) -> ContestPage:
  """
    This method will use ``http`` to request ``/contest/<contest_id>``, and parse to struct result

    :param http: AioHttpHelperInterface 
    :param contest_id: contest id in url

    :returns: parsed structured result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.contest_meta import async_contest_meta

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          # you can login before request
          result = await async_contest_meta(http=http, contest_id = '1779')
          print(result.id)
          print(result.title)
          print(result.url)
          print(result.problems)
          print(result.materials)
          await http.close_session()

        asyncio.run(demo())
  """

  url = f"/contest/{contest_id}"
  resp = await http.async_get(url)
  soup = BeautifulSoup(resp, 'lxml')
  ogtitle = soup_find_bs4Tag(soup, 'meta', property="og:title")['content']
  assert isinstance(ogtitle, str)
  title = ogtitle[len('Dashboard -'):-len('- Codeforces')].strip()
  problems = parse_problems(resp)
  for problem in problems:
    problem.contest_id = contest_id

  return ContestPage(
      id=contest_id,
      # resp = resp,
      url=url,
      title=title,
      problems=problems,
      # questions=[],  # TODO
      materials=parse_materials(resp))
