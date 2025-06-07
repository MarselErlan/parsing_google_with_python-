import requests
import os
from dotenv import load_dotenv

# Load API key and CSE ID
load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")

query = "AI Engineer job application"

# Google Custom Search API base URL
url = f"https://www.googleapis.com/customsearch/v1"
params = {
    "q": query,
    "key": API_KEY,
    "cx": CSE_ID,
    "num": 10,  # max results per page (limit is 10 per request)
}

response = requests.get(url, params=params)
data = response.json()

# Get total estimated results
total_results = int(data.get("searchInformation", {}).get("totalResults", 0))
print(f"Google estimates about {total_results:,} results for '{query}'.")

# Collect URLs from results
urls = []
for item in data.get("items", []):
    urls.append(item.get("link"))

# Save URLs to a file
output_file = "ai_engineer_jobs_01.txt"
with open(output_file, "w") as f:
    f.write(f"Job search results for: {query}\n")
    f.write(f"Total estimated results: {total_results:,}\n\n")
    for url in urls:
        f.write(url + "\n")

print(f"\nSaved {len(urls)} URLs to {output_file}")


