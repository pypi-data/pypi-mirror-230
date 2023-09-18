import math
import shutil
from zipfile import ZipFile
import requests
from .config import USER_AGENT
from .logger import get_logger


log = get_logger('download')


def mask_sig(url):
    if '&sig=' not in url:
        return url
    url_parts = url.split('&')
    for i, url_part in enumerate(url_parts):
        if url_part[:4] == 'sig=':
            url_parts[i] = 'sig=[masked]'
    return '&'.join(url_parts)


def download_file(url, target, mode='wb', chunk_size=8192, logevery=10):
    text = True if 't' in mode else False
    data_streamed = 0
    last_log = 0
    headers = {'User-Agent': USER_AGENT}
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        try:
            content_length = int(r.headers.get('Content-Length', '0'))
        except ValueError:
            content_length = 0
        for chunk in r.iter_content(chunk_size=chunk_size):
            data_streamed += len(chunk)
            if text:
                chunk = chunk.decode()
            target.write(chunk)
            if content_length > 0 and logevery > 0:
                percent_complete = math.floor((data_streamed / content_length) * 100)
                if percent_complete % logevery == 0 and percent_complete > last_log:
                    log.info(f'Downloading {mask_sig(url)}: {percent_complete}%')
                    last_log = percent_complete
    return True


def unzip_file(decompress_from, decompress_to):
    with ZipFile(decompress_from) as z:
        z.extractall(decompress_to)
    return True


def move_file(src, dst):
    return shutil.move(src, dst)
