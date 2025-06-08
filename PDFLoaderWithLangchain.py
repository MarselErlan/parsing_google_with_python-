import os
from pathlib import Path
import pdfplumber
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Step 1: Extract clean PDF text
pdf_path = Path("docs/Eric_Abram_1.pdf")
with pdfplumber.open(pdf_path) as pdf:
    full_resume = "\n\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# Step 2: Wrap in LangChain Document
doc = Document(page_content=full_resume, metadata={"source": str(pdf_path)})

# Step 3: Initialize GPT-4o
llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=OPENAI_API_KEY)

# Step 4: Create resume parsing prompt
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert resume parser. Read the document and extract key details."),
    ("user", "Resume text:\n\n{resume}\n\n"
             "Extract the following:\n"
             "- Full Name\n"
             "- Email\n"
             "- Phone Number\n"
             "- LinkedIn\n"
             "- Skills (categorized)\n"
             "- Experience (company, role, dates, bullets)")
])

# Step 5: Format prompt with the document content
filled_prompt = prompt_template.invoke({"resume": doc.page_content})

# Step 6: Run with GPT-4o
response = llm.invoke(filled_prompt)

# Step 7: Output structured result
print("\n📄 Structured Resume Information:\n")
print(response.content)
