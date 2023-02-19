import typer
from client import Client
from strategies.exporters import ExportHTMLStrategy, ExportDataFrameStrategy
from strategies.downloaders import MasterStrategy, SearchLoanAgreementStrategy, DownloadLoanAgreementStrategy

app = typer.Typer()

@app.command()
def update(year: int, qtr: int):
    client = Client()

    # update master.idx
    client.set_downloader(MasterStrategy(year, qtr))
    master_data = client.download()

    # search for loan agreements
    client.set_downloader(SearchLoanAgreementStrategy(master_data))
    updated_master_data = client.download()    

    # export to csv
    client.set_exporter(ExportDataFrameStrategy())
    client.export(updated_master_data, f"masterfiles/{year}_{qtr}.csv")

@app.command()
def loans(year: int, qtr: int):
    client = Client()

    client.set_downloader(DownloadLoanAgreementStrategy(year, qtr, "masterfiles/"))
    client.set_exporter(ExportHTMLStrategy())
    
    loan_agreements = client.download()
    client.export(loan_agreements, f"loan_agreements/{year}/{qtr}/")

if __name__ == "__main__":
    app()