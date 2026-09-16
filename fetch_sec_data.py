import time
import requests
import sqlite3
from pathlib import Path
from datetime import date, timedelta
import os
from dotenv import load_dotenv
DB_PATH = Path(__file__).parent / "fin_data.db"



load_dotenv()

HEADERS = {'User-Agent': os.environ.get("SEC_USER_AGENT", "Your Name your.email@example.com")}
MIN_YEAR = 2019

INSERT_SQL = """
    INSERT OR IGNORE INTO fin_data
        (cik, ticker, tag, fiscal_year, filed_fy, fiscal_period, form_type,
         filing_date, end_of_period, start_of_period, frame, unit, value, metric)
    VALUES
        (:cik, :ticker, :tag, :fiscal_year, :filed_fy, :fiscal_period, :form_type,
         :filing_date, :end_of_period, :start_of_period, :frame, :unit, :value, :metric)
"""


def fetch_company_data(cik, ticker, tag, metric, namespace="us-gaap"):
    if ":" in tag: 
        namespace, tag = tag.split(":", 1)
    
    
     # 1. build the URL: zero-pad the CIK to 10 digits
    URL= f"https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json"
    
    # 2. make the GET request with HEADERS, then call .json() on the response
    response= requests.get(URL, headers=HEADERS)
    data = response.json()
    entries= data["facts"].get(namespace, {}).get(tag, {}).get("units", {}).get("USD", [])
    # 4. create an empty list called rows
    rows=[]
    entries = sorted(entries, key=lambda e: e["filed"], reverse=True)
    for entry in entries:
      if (
      entry["form"] == "10-K" 
      and entry["fp"] == "FY" 
      and int(entry["end"][:4]) >= MIN_YEAR 
      and (date.fromisoformat(entry["end"]) - date.fromisoformat(entry["start"])) > timedelta(days=350)
      ):
        rows.append({
            "filed_fy": entry["fy"],
            "form_type" : entry["form"],
            "filing_date": entry["filed"],
            "fiscal_period": entry["fp"],
            "end_of_period": entry["end"],
            "start_of_period": entry["start"],
            "frame": entry.get("frame"),
            "value": entry["val"],
            "fiscal_year": int(entry["end"][:4]),
            "tag": tag,
            "cik": cik,
            "unit": "USD",
            "ticker": ticker,
            "metric": metric,
        })

    return rows
        
def create_table(conn):
     cursor = conn.cursor()
     cursor.execute("""
          CREATE TABLE IF NOT EXISTS fin_data (
               cik          INTEGER NOT NULL,
               ticker       TEXT,
               tag          TEXT NOT NULL,
               fiscal_year  INTEGER NOT NULL,
               filed_fy     INTEGER,
               fiscal_period    TEXT,
               form_type    TEXT,
               filing_date TEXT,
               end_of_period TEXT,
               start_of_period TEXT,
               frame TEXT,
               unit TEXT NOT NULL,
               value INTEGER NOT NULL,
               metric TEXT NOT NULL,
               PRIMARY KEY (cik, metric, fiscal_year) 
          );
          """)
     conn.commit()

def load_rows(conn, rows):
     cursor = conn.cursor()
     cursor.executemany(INSERT_SQL, rows)
     conn.commit()

COMPANIES = [
    {"ticker": "MSFT", "cik": 789019},
    {"ticker": "GOOGL", "cik": 1652044},
    {"ticker": "AMZN", "cik": 1018724},
    {"ticker": "ORCL", "cik": 1341439},
    {"ticker": "META", "cik": 1326801},
]
TAG_MAP= {

     "GOOGL":  {"capex": ["PaymentsToAcquirePropertyPlantAndEquipment"], "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"]},
     "MSFT": {"capex": ["PaymentsToAcquirePropertyPlantAndEquipment"], "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax"]},
     "AMZN": {"capex": ["PaymentsToAcquireProductiveAssets"], "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax"]},
     "ORCL": {"capex": ["PaymentsToAcquirePropertyPlantAndEquipment"], "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax"]},
     "META": {"capex": [ "PaymentsToAcquirePropertyPlantAndEquipment"], "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax"]},
}
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)
    for company in COMPANIES:
          ticker=company["ticker"]
          for metric, tags in TAG_MAP[ticker].items():
               for tag in tags:
                    rows = fetch_company_data(company["cik"], ticker, tag, metric)
                    load_rows(conn, rows)
                    time.sleep(0.2)
    for row in conn.execute("SELECT ticker, tag, COUNT(*), MIN(fiscal_year), MAX(fiscal_year) FROM fin_data GROUP BY ticker, metric"):
          print(row)    

    ##for row in conn.execute("SELECT ticker, fiscal_year, tag FROM fin_data WHERE ticker='GOOGL' AND metric='revenue' ORDER BY fiscal_year"):
     ##     print(row)

    ##for row in conn.execute("SELECT ticker, tag FROM fin_data GROUP BY fiscal_year, metric"):
      ## print(row) 
    conn.close()