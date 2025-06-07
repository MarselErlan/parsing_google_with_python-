import os
import requests
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load env
load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Init GPT
llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=OPENAI_API_KEY)

# Build refined query
job_title = "AI Engineer"
refined_query = f'"{job_title}" apply now site:linkedin.com/jobs OR site:indeed.com OR site:lever.co OR site:greenhouse.io OR site:smartrecruiters.com'

print(f"🔍 Search Query: {refined_query}")

# Get 50 filtered results
url = "https://www.googleapis.com/customsearch/v1"
filtered_items = []

for start_index in range(1, 51, 10):
    params = {
        "q": refined_query,
        "key": API_KEY,
        "cx": CSE_ID,
        "num": 10,
        "start": start_index
    }
    response = requests.get(url, params=params)
    data = response.json()
    items = data.get("items", [])

    for item in items:
        link = item.get("link", "")
        title = item.get("title", "").lower()
        snippet = item.get("snippet", "").lower()

        # Filter logic: must contain "apply", "careers", or similar
        if any(keyword in link.lower() for keyword in ["apply", "jobs", "careers", "position"]):
            filtered_items.append(item)

# Summarize
summarize_prompt = ChatPromptTemplate.from_messages([
    ("system", "You summarize job application links."),
    ("user", "Summarize:\n{title}\n\n{snippet}")
])

summaries = []
for item in filtered_items:
    title = item.get("title", "")
    snippet = item.get("snippet", "")
    link = item.get("link", "")

    if title and snippet:
        summary_prompt = summarize_prompt.invoke({"title": title, "snippet": snippet})
        summary = llm.invoke(summary_prompt).content.strip()
    else:
        summary = "No summary available."

    summaries.append((link, summary))

# Save to file
output_file = "ai_engineer_filtered_jobs.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Filtered job application links for: {job_title}\n")
    f.write(f"Total saved: {len(summaries)}\n\n")
    for url, summary in summaries:
        f.write(f"{url}\nSummary: {summary}\n\n")

print(f"\n✅ Saved {len(summaries)} filtered real job application links to {output_file}")
