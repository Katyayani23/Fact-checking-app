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
- Streamlit
- LangChain
- OpenAI GPT
- Tavily Search API

## Setup
pip install -r requirements.txt  
streamlit run app.py
