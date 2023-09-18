from time import time
from typing import Any, Callable, Tuple, AsyncIterator

from .account import extract_channel
from .interfaces.AioHttpHelper import AioHttpHelperInterface
from .kwargs import extract_common_kwargs
from .submit import SubmissionWSResult


# return (end watch?, transform result)
def display_ws(result: Any) -> Tuple[bool, Any]:
  print(result)
  return False, result


# # {'id': 1, 'channel': '34f1ec4b729022e4b48f8d24b65c857805a90469', 'text': {'t': 's', 'd': [5973356517882654806, 200631363, 1777, 1746206, 'TESTS', None, 'OK', 86, 86, 3198, 7884800, 148217099, '21220', '04.04.2023 5:57:08', '04.04.2023 5:57:08', 2147483647, 73, 0]}}
# # 总的ws, 无法获得当前题目的 通过百分比
# def create_ws_task(http: AioHttpHelperInterface, ws_handler: Callable[[Any], Tuple[bool, Any]]) -> asyncio.Task:
#   """
#     This method will use ``http`` to create common websocket, and ``ws_handler`` to handle each ws message
#
#     this websocket cannot receive a submission running percentage, use :py:func:`create_contest_ws_task()` instead
#
#     :param http: AioHttpHelperInterface
#     :param ws_handler: function to handler messages
#
#     :returns: the task which run ws
#
#     Examples:
#
#     .. code-block::
#
#         import asyncio
#         from codeforces_core.httphelper import HttpHelper
#         from codeforces_core.account import async_login
#         from codeforces_core.websocket import create_ws_task, display_ws
#         from codeforces_core.submit import async_submit
#
#         async def demo():
#           # http = HttpHelper(token_path='/tmp/cache_token', cookie_jar_path='/tmp/cache_cookie_jar')
#           http = HttpHelper(token_path='', cookie_jar_path='')
#           await http.open_session()
#           result = await async_login(http=http, handle='<handle>', password='<password>')
#           assert(result.success)
#           task = create_ws_task(http, ws_handler=display_ws)
#           # submit code in webpage
#           try:
#             result = await asyncio.wait_for(task, timeout=60)
#             print("ws is done, result:", task.result())
#           except asyncio.TimeoutError:
#             pass
#           await http.close_session()
#
#         asyncio.run(demo())
#   """
#   epoch = int(time() * 1000)  # s -> ms
#   token = http.get_tokens()
#   ws_url = f"wss://pubsub.codeforces.com/ws/{token['uc']}/{token['usmc']}?_={epoch}&tag=&time=&eventid="
#   print(ws_url)
#   return asyncio.create_task(http.websockets(ws_url, ws_handler))


# https://codeforces.com/contest/<contest_id>/my 会多出两个 meta
#    <meta name="cc" content="xxx"/>
#    <meta name="pc" content="yyy"/>
#   TODO 设计上不太对, handler处理了数据, 结果也抛给了使用者, 应该handler 只关心是否停止, 而transform不应该在handler里处理
# 这两个可以监听 题目测试时 的通过 百分比 变化
async def create_contest_ws_task_yield(http: AioHttpHelperInterface, contest_id: str,
                                       ws_handler: Callable[[Any], Tuple[bool, Any]],
                                       **kw) -> AsyncIterator[SubmissionWSResult]:
  """
    This method will use ``http`` to create contest specific websocket, and ``ws_handler`` to handle each ws message

    :param http: AioHttpHelperInterface
    :param contest_id: contest id in the url
    :param ws_handler: function to handler messages

    :returns: the task which run ws

    Examples:

    See docstring of :py:func:`codeforces_core.submit.async_submit()`
  """
  logger = extract_common_kwargs(**kw).logger
  epoch = int(time() * 1000)  # s -> ms
  html_data = await http.async_get(f"/contest/{contest_id}/my")
  cc, pc = extract_channel(html_data, logger)[2:4]
  assert cc and pc
  ws_url = f"wss://pubsub.codeforces.com/ws/s_{pc}/s_{cc}?_={epoch}&tag=&time=&eventid="
  logger.debug(f"pc = {pc}")  # 似乎和场次有关, 可能包含别人的?
  logger.debug(f"cc = {cc}")  # 似乎只会包含自己的
  logger.debug(f"ws_url = {ws_url}")
  async for data in http.websockets(ws_url, ws_handler):
    yield data
