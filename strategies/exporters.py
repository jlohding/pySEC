from .strategy import ExporterStrategy
import os
from bs4 import BeautifulSoup

class ExportDataFrameStrategy(ExporterStrategy):
    '''
    Exports dataframe to path as csv
    '''
    def export(self, df, destination_path: str):
        self._mkdir_if_not_exist(destination_path)
        df.to_csv(destination_path)


class ExportHTMLStrategy(ExporterStrategy):
    '''
    Exports list of (url, html data) to txt file + cleans up html tags with bs4
    '''
    def export(self, data: list, destination_path: str):
        self._mkdir_if_not_exist(destination_path)

        for url, html in data:
            cleaned = self.__clean_url(url)
            path = os.path.join(destination_path, cleaned)

            with open(path, "w+") as f:
                f.write(self.__parse_html(html))

    def __clean_url(self, url):
        '''
        Cleans the url name for SEC filings
        '''
        cleaned = "_".join(url.split(sep="/")[-2:])
        return cleaned
    
    def __parse_html(self, html: str) -> str:
        '''
        Parses html string and removes tags
        '''
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # remove
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text


