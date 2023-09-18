from dataclasses import dataclass
from enum import Enum
from typing import List, cast
from lxml import html
from lxml.etree import _Element

from .interfaces.AioHttpHelper import AioHttpHelperInterface
from . import util


class RegisterResultMsg(str, Enum):
  HaveBeenRegistered = 'You have been successfully registered'  # first time message
  AlreadyRegistered = 'You are already registered for the contest'
  NoRegistrationIsOpenedNow = 'No registration is opened now'
  Empty = ''


@dataclass
class RegisterResult:
  title: str = ''
  msg: RegisterResultMsg = RegisterResultMsg.Empty  # example: already register, TODO 有些比赛会 None


# TODO 统一参数命名
# Take part as individual participant
async def async_register(http: AioHttpHelperInterface, contest_id: str, **kw) -> RegisterResult:
  """
    This method will use ``http`` for register request, you need login before

    :param contest_id: Codeforces contest_id in url

    :returns: the result 

    Examples:

    .. code-block::

        import asyncio
        from codeforces_core.account import async_login
        from codeforces_core.httphelper import HttpHelper
        from codeforces_core.contest_register import async_register, RegisterResultMsg

        async def demo():
          # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
          http = HttpHelper(token_path='', cookie_jar_path='')
          await http.open_session()
          result = await async_login(http=http, handle='<handle>', password='<password>')
          assert(result.success)
          result = await async_register(http=http,contest_id='1811')
          print(result)
          # assert result.msg == RegisterResultMsg.HaveBeenRegistered
          # assert result.msg == RegisterResultMsg.AlreadyRegistered
          # assert result.msg == RegisterResultMsg.NoRegistrationIsOpenedNow
          await http.close_session()

        asyncio.run(demo())
  """
  url = f'/contestRegistration/{contest_id}'
  resp = await http.async_get(url)
  doc = html.fromstring(resp)
  title = cast(List[_Element], doc.xpath('.//title'))[0].text
  msg = util.show_message(resp)  # AlreadyRegistered
  if msg:
    return RegisterResult(title=title, msg=msg)
  token = http.get_tokens()
  resp = await http.async_post(
      url,
      data=http.create_form({
          'csrf_token': token['csrf'],
          'action': 'formSubmitted',
          'takePartAs': 'personal',  # Take part as individual participant
          'backUrl': '',
      }))
  msg = util.show_message(resp)  # HaveBeenRegistered
  return RegisterResult(title=title, msg=msg)
