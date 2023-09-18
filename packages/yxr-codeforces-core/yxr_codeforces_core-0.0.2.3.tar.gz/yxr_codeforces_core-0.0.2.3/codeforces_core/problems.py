from dataclasses import dataclass
import logging
from typing import Any, List, cast
from lxml import html

from .interfaces.AioHttpHelper import AioHttpHelperInterface
from .kwargs import extract_common_kwargs
from .util import pop_element


def extract_testcases(tags):
  ret = []
  for i in tags:
    pop_element(i.xpath('.//div[@class="title"]')[0])
    divs = i.xpath('.//div[@class]')
    if len(divs) == 0:
      ret.append("\n".join([t.strip() for t in i.itertext()]))
    else:
      l = ''
      prev = divs[0].get('class')
      lines = []
      for d in divs:
        if d.get('class') == prev:
          l += d.text + '\n'
        else:
          lines.append(l)
          prev = d.get('class')
          l = d.text + '\n'
      if l: lines.append(l.strip() + '\n')
      ret.append("\n".join(lines))
  return ret


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


async def async_problems(http: AioHttpHelperInterface, contest_id: str, **kw) -> List[ProblemInfo]:
  """
    This method will use ``http`` to request ``/contest/<contest_id>/problems``, and parse to struct result

    :param http: AioHttpHelperInterface 
    :param contest_id: contest id in url

    :returns: parsed structured result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.problems import async_problems

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          # you can login before request
          result = await async_problems(http=http, contest_id='1779')
          print(len(result))
          print(result[0])
          await http.close_session()

        asyncio.run(demo())
  """
  logger = extract_common_kwargs(**kw).logger
  url = "/contest/{}/problems".format(contest_id)
  resp = await http.async_get(url)
  doc = html.fromstring(resp)
  probs = cast(List[Any], doc.xpath('.//div[@class="problemindexholder"]'))

  ret: List[ProblemInfo] = []
  for p in probs:
    try:
      # if alert: alert = alert[0].text
      level = p.get('problemindex')
      typo = p.xpath('.//div[@class="ttypography"]')[0]
      title = pop_element(typo.xpath('.//div[@class="title"]')[0])
      time_limit = typo.xpath('.//div[@class="time-limit"]')[0]
      time_limit = [t for t in time_limit.itertext()][1].split(' ')[0]
      memory_limit = typo.xpath('.//div[@class="memory-limit"]')[0]
      memory_limit = [t for t in memory_limit.itertext()][1].split(' ')[0]
      desc = typo.xpath('.//div[not(@class)]')
      if desc:
        desc = '\n'.join([t for t in desc[0].itertext()])
      else:
        desc = ""

      for j in typo.xpath('.//div[@class="section-title"]'):
        pop_element(j)

      in_spec = typo.xpath('.//div[@class="input-specification"]')
      if in_spec:
        in_spec = '\n'.join([t for t in in_spec[0].itertext()])
      else:
        in_spec = ""

      out_spec = typo.xpath('.//div[@class="output-specification"]')
      if out_spec:
        out_spec = '\n'.join([t for t in out_spec[0].itertext()])
      else:
        out_spec = ""

      in_tc = extract_testcases(typo.xpath('.//div[@class="input"]'))
      out_tc = extract_testcases(typo.xpath('.//div[@class="output"]'))
      note = typo.xpath('.//div[@class="note"]')
      if note:
        note = '\n'.join([t for t in note[0].itertext()])
      ret.append(
          ProblemInfo(title=title,
                      level=level,
                      time_limit_seconds=time_limit,
                      memory_limit_mb=memory_limit,
                      desc=desc,
                      in_tc=in_tc,
                      out_tc=out_tc,
                      note=note))
    except Exception as e:
      logger.exception(e)
  return ret
