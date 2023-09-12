from urllib.error import URLError
from urllib.request import urlretrieve
import sys

class ProgressBar:
    def __init__(self) -> None:
        self.old_percent = 0
        self.already_printed = False

    def init_print(self, total_sz: float) -> None:
        if not self.already_printed:
            print(f"Total file size: {round(total_sz * 1e-6, 2)} MB")
            print('_' * 50)
            self.already_printed = True

    def download_progress_hook(self, count: int, block_sz: float, total_sz: float) -> None:
        self.init_print(total_sz)
        percent = int(count * block_sz * 100 / total_sz)
        if percent >= 2 + self.old_percent:
            self.old_percent = percent
            print('>', end='')
            sys.stdout.flush()

def download_url(url: str, fpath: str) -> None:
    try:
        print('Downloading ' + url + ' to ' + fpath)
        urlretrieve(url, fpath, reporthook=ProgressBar().download_progress_hook)
    except (URLError, IOError) as err:
        print(err)
        if url[:5] == 'https':
            url = url.replace('https:', 'http:')
            print('Failed download. Trying https -> http instead.'
                    ' Downloading ' + url + ' to ' + fpath)
            urlretrieve(url, fpath, reporthook=ProgressBar().download_progress_hook)