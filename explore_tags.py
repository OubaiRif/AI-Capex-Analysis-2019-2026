
import requests

HEADERS = {'User-Agent': 'Oubai Rifai oubai.rifai@gmail.com'}

def fetch_company_tags(cik, year, keyword):
     # 1. build the URL: zero-pad the CIK to 10 digits
    URL= f"https://data.sec.gov/api/xbrl/companyfacts/CIK{str(cik).zfill(10)}.json"
    
    # 2. make the GET request with HEADERS, then call .json() on the response
    response= requests.get(URL, headers=HEADERS)
    data = response.json()
    rows=[]
    for namespace, tags in data["facts"].items():
        for tag, body in tags.items():
        # existing logic — but append namespace to the row too
            if keyword in tag:
              for entry in body.get("units", {}).get("USD", []):
                  if entry["fp"] == "FY" and entry["form"] == "10-K" and int(entry["end"][:4]) == year:
                        rows.append({
                        "tag": tag,
                        "data": entry,
                        "namespace": namespace,
                        })
    print(list(data["facts"].keys()))                    
    return rows
COMPANIES = [
    {"ticker": "MSFT", "cik": 789019},
    {"ticker": "GOOGL", "cik": 1652044},
    {"ticker": "AMZN", "cik": 1018724},
    {"ticker": "ORCL", "cik": 1341439},
    {"ticker": "META", "cik": 1326801},
]
if __name__ == "__main__":
    results = fetch_company_tags("789019", 2019,"RevenueFromContractWithCustomerExcludingAssessedTax")
    for r in results:
        print(f"{r['namespace']:<10} {r['tag']:<70} {r['data']['end']}  {r['data']['val']:>18,}")
        
        

