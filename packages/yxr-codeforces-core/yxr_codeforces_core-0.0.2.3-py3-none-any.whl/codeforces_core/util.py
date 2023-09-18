from typing import List, cast
import bs4
from lxml import html
from lxml.etree import ElementBase
from lxml.html import HtmlElement


def pop_element(t):
  text = t.text
  t.getparent().remove(t)
  return text


def show_message(resp):
  doc = html.fromstring(resp)
  for lines in doc.xpath('.//script[@type="text/javascript" and not(@src)]'):
    for l in lines.text.splitlines():
      if l.find('Codeforces.showMessage("') != -1:
        return l.split('"')[1]


# for mypy type check
def soup_find_bs4Tag(soup: bs4.Tag, *args, **kwargs) -> bs4.Tag:
  result = soup.find(*args, **kwargs)
  assert isinstance(result, bs4.Tag)
  return result


def typedxpath(el: HtmlElement, s: str) -> List[HtmlElement]:
  return cast(List[HtmlElement], el.xpath(s))
