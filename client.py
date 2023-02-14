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