from abc import ABC, abstractmethod
import os
import http
import urllib.request
import concurrent.futures
from ratelimit import sleep_and_retry, limits
from tqdm import tqdm


class ExporterStrategy(ABC):
    '''
    Strategy abstract class for client export behaviour
    '''
    @abstractmethod
    def export(self, *args, **kwargs):
        raise NotImplementedError()

    def _mkdir_if_not_exist(self, path):
        path = os.path.dirname(path)

        try:
            os.makedirs(path)
        except OSError:
            pass

class DownloaderStrategy(ABC):
    '''
    Strategy abstract class for client download behaviour
    '''
    def __init__(self):
        self.headers = {
            "User-Agent" : "Samples Company Name AdminContact@<sample company domain>.com"
        }
        self.base_path = "https://www.sec.gov/Archives/edgar/full-index/"

    @abstractmethod
    def download(self, *args, **kwargs):
        raise NotImplementedError()

    @sleep_and_retry
    @limits(calls=10, period=1)
    def load_url(self, url):
        req = urllib.request.Request(url, headers=self.headers)

        try:
            resp = urllib.request.urlopen(req)

            if resp.getcode() != 200:
                raise Exception(f"error not 200, {resp.getcode()}") 

            data = resp.read()
        except (http.client.IncompleteRead) as e:
            data = e.partial
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTPError on {url}")

        text = data.decode("utf-8")
        
        return url, text

    def batch_load_url(self, urls):
        out = []
        total_urls = len(urls)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = (executor.submit(self.load_url, url) for url in urls)
            for future in tqdm(concurrent.futures.as_completed(future_to_url),
                               total=total_urls, 
                               colour="green", 
                               desc = "Download Progress"):
                try:
                    url, result = future.result()
                    out.append((url, result))
                except Exception as exc:
                    result = str(type(exc))
                    out.append((url, result))
        return out