import logging
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple, cast
from lxml import html
from lxml.etree import _Element
from os import path
import asyncio
import aiohttp
import pyaes
import json
import re

from .constants import CF_HOST
from .interfaces.AioHttpHelper import AioHttpHelperInterface
from .kwargs import extract_common_kwargs

default_headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip',
    # 'User-Agent': config.conf['user_agent'], TODO
    'User-Agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}


class RCPCRedirectionError(Exception):

  def __init__(self):
    super().__init__("RCPC redirection detected")


def add_header(newhdr, headers: Dict[str, str]) -> Dict[str, str]:
  headers.update(newhdr)
  return headers


async def on_request_end(session, trace_request_ctx, params):
  elapsed = asyncio.get_event_loop().time() - trace_request_ctx.start
  print("[*] Request end : {}".format(elapsed))


class HttpHelper(AioHttpHelperInterface):
  session: Optional[aiohttp.ClientSession] = None
  cookie_jar_path = ''
  cookie_jar: Optional[aiohttp.CookieJar] = None
  token_path = ''
  tokens: Dict[str, str] = {}
  headers: Dict[str, str] = {}  # TODO
  logger: logging.Logger

  def __init__(self,
               cookie_jar_path: str = '',
               token_path: str = '',
               headers=default_headers,
               host=CF_HOST,
               **kw) -> None:
    # if path is empty string then won't save to any file, just store in memory
    self.cookie_jar_path = cookie_jar_path
    # if path is empty string then won't save to any file, just store in memory
    self.token_path = token_path
    self.headers = headers
    # TODO support cf mirror site?
    self.host = host
    self.logger = extract_common_kwargs(**kw).logger

  @staticmethod
  def load_tokens(token_path: str) -> Dict[str, Any]:
    if token_path and path.isfile(token_path):
      with open(token_path, 'r') as f:
        return json.load(f)
    return {}

  @staticmethod
  def load_cookie_jar(cookie_jar_path: str) -> aiohttp.CookieJar:
    jar = aiohttp.CookieJar()
    if cookie_jar_path:
      if path.isfile(cookie_jar_path):
        jar.load(file_path=cookie_jar_path)
      else:
        jar.save(file_path=cookie_jar_path)
    return jar

  async def open_session(self) -> aiohttp.ClientSession:
    self.cookie_jar = HttpHelper.load_cookie_jar(self.cookie_jar_path)
    self.tokens = HttpHelper.load_tokens(self.token_path)
    self.session = await aiohttp.ClientSession(cookie_jar=self.cookie_jar).__aenter__()
    return self.session

  async def close_session(self) -> None:
    await self.session.__aexit__(None, None, None)
    self.tokens = {}
    self.cookie_jar = None
    self.session = None

  def update_tokens(self, csrf: str, ftaa: str, bfaa: str, uc: str, usmc: str) -> None:
    self.tokens = {'csrf': csrf[:32], 'ftaa': ftaa, 'bfaa': bfaa, 'uc': uc, 'usmc': usmc}
    if self.token_path:
      with open(self.token_path, 'w') as f:
        json.dump(self.tokens, f)

  async def async_get(self, url, headers=None, csrf=False):
    if self.session is None:
      raise Exception('Please open_session() before async_get()')
    if headers == None: headers = default_headers
    if csrf and 'csrf' in self.tokens:
      headers = add_header({'X-Csrf-Token': self.tokens['csrf']}, headers=headers)
    # TODO remove the feature
    if url.startswith('/'): url = self.host + url
    try:
      async with self.session.get(url, headers=headers) as response:
        assert response.status == 200
        text = await response.text()
        self.check_rcpc(text)
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)  # TODO move auto save to file out
        return text
    except RCPCRedirectionError:
      async with self.session.get(url, headers=headers) as response:
        assert response.status == 200
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)
        return await response.text()
    except Exception as e:
      self.logger.error(e)

  async def async_post(self, url, data, headers=default_headers, csrf=False, **kwargs: Any):
    if self.session is None:
      raise Exception('Please open_session() before async_get()')
    if headers == None: headers = default_headers
    if csrf and 'csrf' in self.tokens:
      headers = add_header({'X-Csrf-Token': self.tokens['csrf']}, headers=headers)

    # TODO remove the feature
    if url.startswith('/'): url = self.host + url
    try:
      async with self.session.post(url, headers=headers, data=data, **kwargs) as response:
        assert response.status == 200
        self.check_rcpc(await response.text())
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)
        return await response.text()
    except RCPCRedirectionError:
      async with self.session.post(url, headers=headers, data=data) as response:
        assert response.status == 200
        if self.cookie_jar_path:
          self.cookie_jar.save(file_path=self.cookie_jar_path)
        return await response.text()
    except Exception as e:
      self.logger.error(e)

  def get_tokens(self):
    return self.tokens

  def check_rcpc(self, html_data: str):
    doc = html.fromstring(html_data)
    aesmin = cast(List[_Element], doc.xpath(".//script[@type='text/javascript' and @src='/aes.min.js']"))
    if len(aesmin) > 0:
      print("[+] RCPC redirection detected")
      js = cast(List[_Element], doc.xpath(".//script[not(@type)]"))
      assert len(js) > 0
      keys = re.findall(r'[abc]=toNumbers\([^\)]*', js[0].text)
      for k in keys:
        if k[0] == 'a':
          key = bytes.fromhex(k.split('"')[1])
        elif k[0] == 'b':
          iv = bytes.fromhex(k.split('"')[1])
        elif k[0] == 'c':
          ciphertext = bytes.fromhex(k.split('"')[1])
      assert len(key) == 16 and len(iv) == 16 and len(ciphertext) == 16, 'AES decryption error'
      c = pyaes.AESModeOfOperationCBC(key, iv=iv)
      plaintext = c.decrypt(ciphertext)
      rcpc = plaintext.hex()
      self.cookie_jar.update_cookies({'RCPC': rcpc})
      self.cookie_jar.save(file_path=self.cookie_jar_path)
      raise RCPCRedirectionError()

  def create_form(self, form_data) -> aiohttp.FormData:
    form = aiohttp.FormData()
    for k, v in form_data.items():
      form.add_field(k, v)
    return form

  # callback return (end watch?, transform result)
  async def websockets(self, url: str, callback: Callable[[Any], Tuple[bool, Any]]) -> AsyncIterator[Any]:
    try:
      async with self.session.ws_connect(url) as ws:
        async for msg in ws:
          if msg.type == aiohttp.WSMsgType.TEXT:
            js = json.loads(msg.data)
            js['text'] = json.loads(js['text'])

            endwatch, obj = callback(js)
            yield obj
            if endwatch:
              return

          else:
            self.logger.error('wrong msg type?', msg.type)
            break
        return
    except Exception as e:
      self.logger.error(e)
      return
