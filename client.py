from strategies.exporters import ExportHTMLStrategy, ExportDataFrameStrategy
from strategies.downloaders import MasterStrategy, SearchLoanAgreementStrategy, DownloadLoanAgreementStrategy

class Client:
    def __init__(self):
        self.downloader = None
        self.exporter = None
    
    def set_downloader(self, strategy: 'DownloaderStrategy') -> 'Client':
        self.downloader = strategy
        return self

    def set_exporter(self, strategy: 'ExporterStrategy') -> 'Client':
        self.exporter = strategy
        return self
    
    def download(self):
        if self.downloader == None:
            raise Exception("No current DownloaderStrategy")
        else:
            return self.downloader.download()

    def export(self, *args, **kwargs) -> None:
        if self.exporter == None:
            raise Exception("No current ExporterStrategy")
        else:
            return self.exporter.export(*args, **kwargs)


if __name__ == "__main__":
    for YEAR in [2020, 2021, 2022]:
        for QTR in [1,2,3,4]:
            client = Client()

            client.set_downloader(DownloadLoanAgreementStrategy(YEAR, QTR))
            client.set_exporter(ExportHTMLStrategy())
            
            loan_agreements = client.download()
            client.export(loan_agreements, f"loan_agreements/{YEAR}/{QTR}/")
            print("")