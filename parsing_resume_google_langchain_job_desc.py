import os
import requests
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
import re

from playwright_for_full_job_description import extract_job_description_from_url_and_html_analysis

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
CSE_ID = os.getenv("CSE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize GPT-4o
llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=OPENAI_API_KEY)

# Query
job_title = "AI Engineer"
refined_query = f'"{job_title}" apply now site:linkedin.com/jobs OR site:indeed.com OR site:lever.co OR site:greenhouse.io OR site:smartrecruiters.com'
print(f"🔍 Search Query: {refined_query}")

# Prompt for summarizing
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You summarize job links and extract structured fields."),
    ("user", "Based on the title and snippet below, extract:\n"
             "- Summary (1 sentence)\n"
             "- Company name\n"
             "- Location\n"
             "- Job description (if available)\n\n"
             "Title: {title}\nSnippet: {snippet}")
])

# Search and extract
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
        title = item.get("title", "")
        snippet = item.get("snippet", "")

        if any(k in link.lower() for k in ["apply", "jobs", "careers", "position"]):
            filtered_items.append({
                "link": link,
                "title": title,
                "snippet": snippet
            })

# Prepare output directories
Path("job_descriptions").mkdir(exist_ok=True)

# Extract info and write files
results = []
for i, item in enumerate(filtered_items, 1):
    title = item["title"]
    snippet = item["snippet"]
    link = item["link"]

    # Ask GPT to extract summary, company, location, description
    prompt_input = {"title": title, "snippet": snippet}
    summary_msg = summary_prompt.invoke(prompt_input)
    response = llm.invoke(summary_msg).content.strip()

    # Parse response using regex (lightweight method)
    def extract(field):
        match = re.search(f"{field}:(.*)", response, re.IGNORECASE)
        return match.group(1).strip() if match else "Not found"

    summary = extract("Summary")
    company = extract("Company name")
    location = extract("Location")

    # Get full job description from the job page
    description = extract_job_description_from_url_and_html_analysis(link, file_index=i)


    if description.lower() != "no job description available." and len(description.strip()) > 10:
        desc_filename = f"job_descriptions/description_{i}.txt"
        with open(desc_filename, "w", encoding="utf-8") as f:
            f.write(description)
    else:
        desc_filename = "No job description available."

    # Store result
    results.append({
        "url": link,
        "summary": summary,
        "company": company,
        "location": location,
        "description_file": desc_filename
    })

# Save final output
output_file = "ai_engineer_structured_jobs.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Structured Job Listings for '{job_title}'\n")
    f.write(f"Total saved: {len(results)}\n\n")
    for r in results:
        f.write(f"URL: {r['url']}\n")
        f.write(f"Company: {r['company']}\n")
        f.write(f"Location: {r['location']}\n")
        f.write(f"Summary: {r['summary']}\n")
        f.write(f"Description file: {r['description_file']}\n\n")

print(f"\n✅ Saved {len(results)} job listings to '{output_file}'")
