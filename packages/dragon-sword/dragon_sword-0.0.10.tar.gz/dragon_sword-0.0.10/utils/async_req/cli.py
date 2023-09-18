import urllib.request
from urllib.parse import urljoin

from m3u8.httpclient import HTTPSHandler
from .header import AntiHeader


class DefaultHTTPClient:
    def __init__(self, proxies=None):
        self.proxies = proxies

    def download(self, uri, timeout=5, headers=None, verify_ssl=True):
        if not headers:
            headers = AntiHeader
        proxy_handler = urllib.request.ProxyHandler(self.proxies)
        https_handler = HTTPSHandler(verify_ssl=verify_ssl)
        opener = urllib.request.build_opener(proxy_handler, https_handler)
        opener.addheaders = headers.items()
        resource = opener.open(uri, timeout=timeout)
        base_uri = urljoin(resource.geturl(), ".")
        content = resource.read().decode(
            resource.headers.get_content_charset(failobj="utf-8")
        )
        return content, base_uri
