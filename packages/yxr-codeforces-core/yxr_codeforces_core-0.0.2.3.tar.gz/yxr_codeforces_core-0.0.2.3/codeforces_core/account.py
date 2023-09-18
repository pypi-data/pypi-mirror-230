from dataclasses import dataclass
from typing import Optional, Tuple
from random import choice
from lxml import html
from lxml.html import HtmlElement
import logging

from .kwargs import extract_common_kwargs
from .util import typedxpath
from .interfaces.AioHttpHelper import AioHttpHelperInterface

default_login_url = "/enter?back=%2F"


@dataclass
class LoginResult:
  html: str = ''
  csrf: str = ''
  ftaa: str = ''
  bfaa: str = ''
  uc: str = ''  # user channel ?
  usmc: str = ''
  # cc: str = ''  # contest channel? TODO remove, 这个和 contest相关, 不应该和login在一起
  # pc: str = ''  # remove same reason
  success: bool = False


def is_user_logged_in(html_data: str) -> bool:
  doc = html.fromstring(html_data)
  links = typedxpath(doc, './/div[@class="lang-chooser"]/div[not(@style)]/a[@href]')
  for m in links:
    if m.text.strip() in ["Register", "Enter"]:
      return False
  return True


async def async_fetch_logged_in(http: AioHttpHelperInterface, login_url=default_login_url, **kw) -> Tuple[bool, str]:
  """
    auto update token 
    return bool(is_logged_in), html_data
  """
  logger = extract_common_kwargs(**kw).logger

  html_data = await http.async_get(login_url)
  uc, usmc, cc, pc, csrf_token, ftaa, bfaa = extract_channel(html_data, logger=logger)

  if is_user_logged_in(html_data=html_data):
    http.update_tokens(csrf=csrf_token, ftaa=ftaa, bfaa=bfaa, uc=uc, usmc=usmc)
    return True, html_data
  return False, ''


# No exception, handler inside
def extract_channel(html_data: str,
                    logger: Optional[logging.Logger] = None) -> Tuple[str, str, str, str, str, str, str]:
  doc = html.fromstring(html_data)

  def xpath_content(el: HtmlElement, s: str) -> str:
    try:
      l = typedxpath(el, s)
      return l[0].get('content') if len(l) > 0 else ''
    except Exception as e:
      if logger: logger.exception(e)
      return ''

  uc = xpath_content(doc, './/meta[@name="uc"]')
  usmc = xpath_content(doc, './/meta[@name="usmc"]')
  cc = xpath_content(doc, './/meta[@name="cc"]')
  pc = xpath_content(doc, './/meta[@name="pc"]')
  try:
    csrf_token = typedxpath(doc, './/span[@class="csrf-token"]')[0].get('data-csrf')
    assert len(csrf_token) == 32, "Invalid CSRF token"
  except Exception as e:
    if logger: logger.exception(e)
    csrf_token = ''
  ftaa = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789') for x in range(18)])
  # bfaa : Fingerprint2.x64hash128
  bfaa = ''.join([choice('0123456789abcdef') for x in range(32)])
  return uc, usmc, cc, pc, csrf_token, ftaa, bfaa


# TODO 已经登陆账号A, 再调用登陆账号B是不行的, 这个逻辑应该是由外部控制，调用时应该确保未登录状态
async def async_login(http: AioHttpHelperInterface,
                      handle: str,
                      password: str,
                      login_url=default_login_url,
                      **kw) -> LoginResult:
  """
    This method will use ``http`` for login request, and  :py:func:`is_user_logged_in()` for login check

    :param handle: Codeforces handle
    :param password: Codeforces password

    :returns: if it is successful post and logged

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.account import async_login, is_user_logged_in
        from codeforces_core.httphelper import HttpHelper

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_login(http=http, handle='<handle>', password='<password>')
          assert(result.success)

          html_data = await http.async_get('https://codeforces.com')
          assert(is_user_logged_in(html_data))

          await http.close_session()

        asyncio.run(demo())
  """
  logger = extract_common_kwargs(**kw).logger
  html_data = await http.async_get(login_url)
  csrf_token, ftaa, bfaa = extract_channel(html_data, logger=logger)[4:7]
  login_data = {
      'csrf_token': csrf_token,
      'action': 'enter',
      'ftaa': ftaa,
      'bfaa': bfaa,
      'handleOrEmail': handle,
      'password': password,
      'remember': 'on',
  }
  html_data = await http.async_post(login_url, login_data)
  # uc, usmc, cc, pc, csrf_token, ftaa, bfaa = extract_channel(html_data)
  uc, usmc, cc, pc = extract_channel(html_data, logger=logger)[0:4]

  success = False
  # if check_login(result.html):
  if is_user_logged_in(html_data=html_data):
    http.update_tokens(csrf=csrf_token, ftaa=ftaa, bfaa=bfaa, uc=uc, usmc=usmc)
    success = True
  else:
    success = False

  return LoginResult(
      html=html_data,
      csrf=csrf_token,
      ftaa=ftaa,
      bfaa=bfaa,
      uc=uc,
      usmc=usmc,
      # cc=cc,
      # pc=pc,
      success=success)
