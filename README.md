# pySEC
Python3 SEC API Client + Webscraper

## Features
- ThreadPoolExecutor client to webscrape and download SEC EDGAR filings at the maximum available access rate of 10 requests per second
- Simple to use, OS-agnostic, CLI client

## Installation
```bash
$ pip install -r requirements.txt
```

## Usage
```bash
python main.py $YEAR $QUARTER
```