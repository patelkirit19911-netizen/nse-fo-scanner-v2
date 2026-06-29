import requests

print("NSE FO Scanner V2 Started...")

CSV_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"

try:
    data = requests.get(CSV_URL, timeout=30)
    print("CSV Download Success")
    print("Status Code:", data.status_code)
    print("CSV Size:", len(data.text))
except Exception as e:
    print("Error:", e)
