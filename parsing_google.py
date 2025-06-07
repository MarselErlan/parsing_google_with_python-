import requests
import os
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")

query = "Erlan Abduraimov"

url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}"

response = requests.get(url)
data = response.json()

result_count = data.get("searchInformation", {}).get("totalResults")
print(f"{query} appears in about {int(result_count):,} search results.")

