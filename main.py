import argparse
from client import Client
from strategies.exporters import ExportHTMLStrategy, ExportDataFrameStrategy
from strategies.downloaders import MasterStrategy, SearchLoanAgreementStrategy, DownloadLoanAgreementStrategy

def main(YEAR, QTR):
    client = Client()

    client.set_downloader(DownloadLoanAgreementStrategy(YEAR, QTR))
    client.set_exporter(ExportHTMLStrategy())
    
    loan_agreements = client.download()
    client.export(loan_agreements, f"loan_agreements/{YEAR}/{QTR}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download loan filings")
    parser.add_argument("period", type=int, nargs="+")
    args = parser.parse_args() 
    year, qtr = args.period

    main(year, qtr)
