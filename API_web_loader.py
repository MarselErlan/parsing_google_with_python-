import requests
from langchain_core.documents import Document
from langchain_community.document_loaders import JSONLoader

url = "https://api.github.com/repos/langchain-ai/langchain/issues?state=open"
response = requests.get(url, timeout=15)
response.raise_for_status()

loader = JSONLoader(
    json_content=response.json(),      # raw list/dict already in memory
    text_content_key="body",               # GitHub issue body
    metadata_keys=["html_url", "title", "state", "user"]  # copied verbatim
)

docs = loader.load()