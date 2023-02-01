import os
import http
import time
import urllib
import concurrent.futures
from ratelimit import sleep_and_retry, limits
import pandas as pd

class Client:
    def __init__(self):
        self.headers = {
            "User-Agent" : "Samples Company Name AdminContact@<sample company domain>.com"
        }
        self.base_path = "https://www.sec.gov/Archives/edgar/full-index/"
        self.master_df = None
        self.urls = []

    def set_master(self, year: int, qtr: int) -> pd.DataFrame:
        '''
        Returns master.idx DataFrame

        year: int
            Year of filing
        qtr: int
            Choices: {1, 2, 3, 4}

        rtype: pd.DataFrame
            DataFrame of cleaned master.idx data
        '''
        
        master_path = self.__get_master_path(year, qtr)
        url, text = self.load_url(master_path)

        data_split = text.split("--------------------------------------------------------------------------------")
        data = data_split[1].strip().split("\n")
        df = pd.DataFrame([x.split("|") for x in data], columns=["CIK","Company Name","Form Type","Date Filed","Filename"]) 
        df["Filename"] = df["Filename"].apply(lambda s: "https://www.sec.gov/Archives/" + s)
        
        self.master_df = df
        return df        

    def search_loan_agreements(self):
        keywords = {
                "CREDIT AGREEMENT", "LOAN AGREEMENT", "CREDIT FACILITY", "LOAN AND SECURITY AGREEMENT", "LOAN & SECURITY AGREEMENT", "CREDIT AND GUARANTEE AGREEMENT", 
                "CREDIT & GUARANTEE AGREEMENT", "CREDIT AND GUARANTY AGREEMENT", "CREDIT & GUARANTY AGREEMENT", "LOAN AND GUARANTEE AGREEMENT", "LOAN & GUARANTEE AGREEMENT",
                "LOAN AND GUARANTY AGREEMENT", "LOAN & GUARANTY AGREEMENT", "CREDIT AND SECURITY AGREEMENT", "CREDIT & SECURITY AGREEMENT", "LOAN AND SECURITY AGREEMENT",
                "LOAN & SECURITY AGREEMENT", "REVOLVING CREDIT", "FINANCING AND SECURITY AGREEMENT", "FINANCING & SECURITY AGREEMENT", "FACILITY AGREEMENT"
        }

        df = self.master_df.copy()
        df = df[df["Form Type"] == "8-K"]

        print(f"{df.shape[0]} filings to scrape...")

        out = self.download(urls=df["Filename"].to_list())
        downloads_df = pd.DataFrame(out, columns=["Filename", "Text"])

        downloads_df["Is Loan Agreement"] = any(keyword in downloads_df["Text"] for keyword in keywords)
        
        return df.merge(downloads_df, how="left", on="Filename").drop(columns="Text")        


    def download(self, urls):
        out = []
        

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = (executor.submit(self.load_url, url) for url in urls)
                
            time_0 = time.time()

            count = 0
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    url, text = future.result()
                    #self.export(text, url.replace("/", "\\"))
                    out.append((url, text))
                except Exception as exc:
                    text = str(type(exc))
                    print(text)
                finally:
                    count += 1
                    print(count, time.time() - time_0)

        print(f'Took {time.time()-time_0:.2f} seconds')

        return out
    
    def export(self, text, path):
        with open(path, "w+") as f:
            f.write(text)

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

    def __get_master_path(self, year: int, qtr: int) -> str:
        url = os.path.join(self.base_path, str(year), "QTR" + str(qtr), "master.idx")

        return url