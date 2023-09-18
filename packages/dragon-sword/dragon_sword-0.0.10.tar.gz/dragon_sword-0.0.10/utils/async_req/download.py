import aiofiles
import aiohttp

from utils.errno import Error, OK
from utils.log import logger
from .header import AntiHeader


# TODO：add url check
async def async_download(url: str, filepath: str, params: dict = None, headers: dict = None,
                         timeout: int = 30 * 60) -> Error:
    if not headers:
        headers = {}

    session_timeout = aiohttp.ClientTimeout(
        total=None, sock_connect=timeout, sock_read=timeout)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        headers.update(AntiHeader)
        async with session.get(url, params=params, timeout=timeout, headers=headers) as res:
            logger.debug(f"async_download {url} to {filepath}")
            async with aiofiles.open(filepath, 'wb') as f:
                while True:
                    chunk = await res.content.read(1024)
                    if not chunk:
                        break
                    await f.write(chunk)
    return OK


async def async_download_binary(url: str, params: dict = None, headers: dict = None,
                                timeout: int = 100) -> bytes:
    if not headers:
        headers = {}

    async with aiohttp.ClientSession() as session:
        headers.update(AntiHeader)
        async with session.get(url, params=params, timeout=timeout, headers=headers) as resp:
            data = []
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break
                data.append(chunk)
            return b"".join(data)
