# pySEC
Python3 SEC API Client + Webscraper

## Features
- ThreadPoolExecutor client to webscrape and download SEC EDGAR filings at the maximum available access rate of 10 requests per second
- Simple to use, OS-agnostic, CLI client

## Installation
```bash
$ pip install -r requirements.txt
```

## Updating masterfiles:
Update and search for loan filings in a given quarter
- This is already done for Q1_2020 to Q4_2022.
- Warning: Takes ~30min per quarter
```bash
python main.py update {year} {qtr} 
```

## Downloading loan filings from masterfile:
Downloads all 10-K loan filings in a given quarter
 - Note: `update {year} {qtr}` should be used first
 - The files will be downloaded to `loan_agreements/{year}/{qtr}`
```bash
python main.py loans {year} {qtr} 
```