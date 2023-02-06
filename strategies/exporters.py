from .strategy import ExporterStrategy
import os

class ExportDataFrameStrategy(ExporterStrategy):
    '''
    Exports dataframe to path as csv
    '''
    def export(self, df, destination_path: str):
        self._mkdir_if_not_exist(destination_path)
        df.to_csv(destination_path)


class ExportHTMLStrategy(ExporterStrategy):
    '''
    Exports list of (url, html data) to txt file
    '''
    def export(self, data: list, destination_path: str):
        self._mkdir_if_not_exist(destination_path)

        for url, html in data:
            cleaned = self.__clean_url(url)
            path = os.path.join(destination_path, cleaned)

            with open(path, "w+") as f:
                f.write(html)

    def __clean_url(self, url):
        '''
        Cleans the url name for SEC filings
        '''
        cleaned = "_".join(url.split(sep="/")[-2:])
        return cleaned