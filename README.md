# Fact-Checking Web App

This Streamlit app extracts factual claims from uploaded PDFs and verifies them using live web search and LLMs.

## Features
- PDF text extraction
- Automatic claim extraction
- Live web verification using Tavily
- Verdict classification (Verified, False, etc.)

## How It Works
1. Upload a PDF
2. Claims are extracted using LLM
3. Web search is performed for each claim
4. AI verifies claims against evidence

## Tech Stack
- Python, Streamlit
- OpenAI GPT API
- Tavily Search API
- LangChain

## Deployment
Deployed on Streamlit Cloud: [https://fact-checking-app23.streamlit.app/]

## Setup
1. Clone repo: `git clone https://github.com/YOUR-USERNAME/fact-checking-app`
2. Install: `pip install -r requirements.txt`
3. Add API keys to `.env` file
4. Run: `streamlit run app.py`
