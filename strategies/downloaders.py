from .strategy import DownloaderStrategy
import os
import pandas as pd

class MasterStrategy(DownloaderStrategy):
    def __init__(self, year: int, qtr: int):
        super().__init__()
        self.year = year
        self.qtr = qtr

    def download(self) -> pd.DataFrame:
        '''
        Returns master.idx DataFrame

        year: int
            Year of filing YYYY
        qtr: int
            Choices: {1, 2, 3, 4}

        rtype: pd.DataFrame
            DataFrame of cleaned master.idx data
        '''
        
        master_path = self.__get_master_path(self.year, self.qtr)
        url, text = self.load_url(master_path)

        data_split = text.split("--------------------------------------------------------------------------------")
        data = data_split[1].strip().split("\n")
        df = pd.DataFrame([x.split("|") for x in data], columns=["CIK","Company Name","Form Type","Date Filed","Filename"]) 
        df["Filename"] = df["Filename"].apply(lambda s: "https://www.sec.gov/Archives/" + s)
        
        self.master_df = df
        return df   

    def __get_master_path(self, year: int, qtr: int) -> str:
        url = os.path.join(self.base_path, str(year), "QTR" + str(qtr), "master.idx")

        return url
    
class SearchLoanAgreementStrategy(DownloaderStrategy):
    def __init__(self, master_df: pd.DataFrame):
        super().__init__()
        self.master_df = master_df

    def download(self) -> pd.DataFrame:
        '''
        Given self.master_df master.idx dataframe, scrapes all filings with FormType 8-K, and checks if the filings are loan agreements
        Returns dataframe of 8-K filings with "Is Loan Agreement" boolean column indicating if the filing is a loan agreement

        rtype: pd.DataFrame
            DataFrame of 8-K filings info
        '''

        def is_loan_agreement(text) -> bool:
            keywords = {
                    "CREDIT AGREEMENT", "LOAN AGREEMENT", "CREDIT FACILITY", "LOAN AND SECURITY AGREEMENT", "LOAN & SECURITY AGREEMENT", "CREDIT AND GUARANTEE AGREEMENT", 
                    "CREDIT & GUARANTEE AGREEMENT", "CREDIT AND GUARANTY AGREEMENT", "CREDIT & GUARANTY AGREEMENT", "LOAN AND GUARANTEE AGREEMENT", "LOAN & GUARANTEE AGREEMENT",
                    "LOAN AND GUARANTY AGREEMENT", "LOAN & GUARANTY AGREEMENT", "CREDIT AND SECURITY AGREEMENT", "CREDIT & SECURITY AGREEMENT", "LOAN AND SECURITY AGREEMENT",
                    "LOAN & SECURITY AGREEMENT", "REVOLVING CREDIT", "FINANCING AND SECURITY AGREEMENT", "FINANCING & SECURITY AGREEMENT", "FACILITY AGREEMENT"
            }
            return any(keyword in text for keyword in keywords)

        df = self.master_df.copy()
        df = df[df["Form Type"] == "8-K"]

        print(f"{df.shape[0]} filings to scrape...")

        out = self.batch_load_url(urls=df["Filename"].to_list())
        downloads_df = pd.DataFrame(out, columns=["Filename", "Text"])

        downloads_df["Is Loan Agreement"] = downloads_df["Text"].apply(is_loan_agreement)

        return df.merge(downloads_df, how="left", on="Filename").drop(columns="Text")     

class DownloadLoanAgreementStrategy(DownloaderStrategy):
    def __init__(self, year: int, qtr: int, filings_path: str = "filings/"):
        super().__init__()
        self.year = year
        self.qtr = qtr
        self.filings_path = filings_path

    def download(self):
        '''
        Given dataframe of 8-K filings at self.filings_path, downloads all HTML from {filings_path}.csv where is_loan_agreement = True 

        rtype: List[Tuple[url,html]]
            List of tuples of pairs (url, html) of downloaded filings from SEC website
        '''
        path = os.path.join(self.filings_path, f"{self.year}_{self.qtr}.csv")
        filings = pd.read_csv(path)

        loan_filings = filings[filings["Is Loan Agreement"] == True]

        out = self.batch_load_url(urls=loan_filings["Filename"].to_list())

        return out