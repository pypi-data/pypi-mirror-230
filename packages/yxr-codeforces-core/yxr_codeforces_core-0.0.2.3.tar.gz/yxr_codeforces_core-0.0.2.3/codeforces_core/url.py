import re
from typing import Tuple


def pid2url(problem_id: str) -> str:
  contest_id, problem_key = pid2split(problem_id)
  return f'/contest/{contest_id}/problem/{problem_key}'


def pid2split(problem_id) -> Tuple[str, str]:
  """
    problem id to [contest id, problem key]
    
    pid2split('1843F2') == ['1843','F2']
  """
  result = re.match('^(\\d+)([A-Z]\\d?)$', problem_id)
  if result is None:
    raise Exception('problem id[' + problem_id + '] ERROR')
  return str(result.group(1)), str(result.group(2))


def problem_url_parse(problem_url: str) -> Tuple[str, str]:
  """
    https://codeforces.com/contest/1740/problem/G

    convert to

    ['1740', 'G']
  """
  result = re.match('^.*contest/(.*)/problem/(.*)$', problem_url)
  assert result is not None
  return str(result.group(1)), str(result.group(2))