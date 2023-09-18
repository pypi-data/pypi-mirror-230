from dataclasses import dataclass, field
from enum import Enum
from typing import List
from bs4 import BeautifulSoup
import bs4

from .interfaces.AioHttpHelper import AioHttpHelperInterface


@dataclass
class TestCase:
  in_data: str
  out_data: str


@dataclass
class ProblemInfo:
  # testcases: List[TestCase]
  title: str
  level: str
  time_limit_seconds: str
  memory_limit_mb: str
  desc: str
  in_tc: List[str]
  out_tc: List[str]
  note: str


@dataclass
class ParseProblemResult(object):

  class Status(str, Enum):
    AC = 'AC'
    FAILED = 'FAILED'
    NOTVIS = 'NOTVIS'

  status: Status = Status.NOTVIS
  title: str = ''
  test_cases: List[TestCase] = field(default_factory=lambda: [])
  id: str = ''
  oj: str = ''
  description: str = ''
  time_limit: str = ''
  mem_limit: str = ''
  url: str = ''
  html: str = ''
  file_path: str = ''


async def async_problem(http: AioHttpHelperInterface, contest_id: str, level: str, **kw) -> ParseProblemResult:
  """
    This method will use ``http`` to request ``/contest/<contest_id>/problems``, and parse to struct result

    :param http: AioHttpHelperInterface 
    :param contest_id: contest id in url

    :returns: parsed structured result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.problem import async_problem

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          # you can login before request
          result = await async_problem(http=http, contest_id='1779', level='F')
          print(result)
          await http.close_session()

        asyncio.run(demo())
  """
  resp = await http.async_get(f'/contest/{contest_id}/problem/{level}')
  problem = ParseProblemResult(html=resp)
  soup = BeautifulSoup(resp, 'lxml')

  # TODO implememt soup_find function to assert type for mypy
  match_groups = soup.find('div', attrs={'class': 'title'})
  assert isinstance(match_groups, bs4.Tag)
  problem.title = str(match_groups.string)[2:].strip(" \r\n")

  match_groups = soup.find(name='div', attrs={'class': 'time-limit'})
  assert isinstance(match_groups, bs4.Tag)
  problem.time_limit = str(match_groups.contents[-1]).strip()

  match_groups = soup.find(name='div', attrs={'class': 'memory-limit'})
  assert isinstance(match_groups, bs4.Tag)
  problem.mem_limit = str(match_groups.contents[-1]).strip()

  match_groups = soup.find(name='div', attrs={'class': 'problem-statement'})

  problem.status = ParseProblemResult.Status.NOTVIS  # TODO for show progress

  match_groups = soup.find(name='div', attrs={'class': 'sample-test'})
  assert isinstance(match_groups, bs4.Tag)
  problem.test_cases.clear()
  if match_groups:
    test_case_inputs = match_groups.find_all(name='div', attrs={'class': 'input'})
    test_case_outputs = match_groups.find_all(name='div', attrs={'class': 'output'})
    assert (len(test_case_inputs) == len(test_case_outputs))  # may not? in April fool contest
    for i in range(len(test_case_inputs)):
      t_in = test_case_inputs[i].find(name='pre').get_text("\n").strip(" \r\n")
      t_out = test_case_outputs[i].find(name='pre').get_text("\n").strip(" \r\n")
      problem.test_cases.append(TestCase(t_in, t_out))

  return problem
