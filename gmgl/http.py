# GMG Copyright 2022 - Alexandre Díaz
import json
import base64
from lxml import etree
from io import StringIO, BytesIO
from urllib.request import build_opener, urlopen, Request, HTTPHandler
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError


class Http(object):
    _protocol = 'https://'
    _domain = None
    _session_cookie_key = None
    _page_cache = {}

    def __init__(
        self,
        session_hash: str,
        max_tries: int = 3,
        debuglevel=0,
        post_per_page: int = 30,
    ):
        self._max_tries = max_tries
        self._htmlparser = etree.HTMLParser()
        self._opener = build_opener(HTTPHandler(debuglevel=debuglevel))
        headers = [
            ('Origin', f'{self._protocol}{self._domain}'),
        ]
        if session_hash:
            headers.append(('Cookie', f'{self._session_cookie_key}={session_hash}'))
        self._opener.addheaders = headers
        self.post_per_page = post_per_page

    def get(self, url: str, cache: bool = False) -> etree.ElementTree:
        """Send a HTTP Get request"""
        try:
            if cache and url in self._page_cache:
                return self._page_cache[url]
            req = Request(f'{self._protocol}{self._domain}/{url}', method='GET')
            resp = self._opener.open(req, timeout=30)
        except (URLError, HTTPError) as err:
            print(err)
            return None
        page_etree = etree.parse(
            StringIO(resp.read().decode('utf-8')), self._htmlparser
        )
        if cache:
            self._page_cache[url] = page_etree
        return page_etree

    def post(self, url: str, data: dict, xmlhttprequest: bool = False) -> bool:
        """Send a HTTP Post request
        All is done successfully if the server redirect to the edited post
        """
        try:
            parsed_data = urlencode(data).encode('utf-8')
            req_headers = {}
            if xmlhttprequest:
                req_headers['X-Requested-With'] = 'XMLHttpRequest'
            req = Request(
                f'{self._protocol}{self._domain}/{url}',
                method='POST',
                data=parsed_data,
                headers=req_headers,
            )
            resp = self._opener.open(req, timeout=30)
        except (URLError, HTTPError) as err:
            print(err)
            return None
        if xmlhttprequest:
            return json.loads(resp.read().decode('utf-8'))
        return etree.parse(StringIO(resp.read().decode('utf-8')), self._htmlparser)

    def download(self, url: str):
        return urlopen(url).read()

    def download64(self, url: str):
        return base64.b64encode(self.download(url=url)).decode('utf-8')
