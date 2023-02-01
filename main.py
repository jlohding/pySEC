import argparse
from client import Client

def main(year, qtr):
    client = Client()
    client.set_master(year, qtr)
    res = client.search_loan_agreements()
    res.to_csv(f"filings/{year}_{qtr}.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download loan filings")
    parser.add_argument("period", type=int, nargs="+")
    args = parser.parse_args() 
    year, qtr = args.date

    main(year, qtr)
