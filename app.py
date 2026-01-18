import streamlit as st
import PyPDF2
import pdfplumber
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain.schema import HumanMessage
from langchain_core.messages import HumanMessage
from tavily import TavilyClient
import json

# Load environment variables
load_dotenv()

# Initialize APIs
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# App title
st.set_page_config(page_title="Fact-Checker", page_icon="🔍")
st.title("Fact-Checking Web App")
st.write("Upload a PDF to verify claims against live web data")

# File uploader
uploaded_file = st.file_uploader("Drag & drop PDF here", type="pdf")

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF"""
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        # Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_claims(text):
    """Use LLM to extract factual claims"""
    prompt = f"""
    Extract ALL factual claims, statistics, dates, financial figures, 
    and specific statements from this text. Return ONLY a JSON array where 
    each item has "claim" and "category" (e.g., "statistic", "date", "financial", "fact").
    
    Text: {text[:3000]}  # Limit text to avoid token limits
    
    Return format: [{{"claim": "Bitcoin is $42,500", "category": "financial"}}, ...]
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        claims_data = json.loads(response.content)
        return [item["claim"] for item in claims_data]
    except:
        # Simple fallback: extract sentences with numbers
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        claims = [s for s in sentences if any(char.isdigit() for char in s)]
        return claims[:10]  # Limit to 10 claims

def search_claim(claim):
    """Search web for claim verification"""
    try:
        search_results = tavily.search(query=claim, max_results=3)
        return search_results
    except:
        return {"error": "Search failed"}

def verify_claim(claim, search_results):
    """Use LLM to verify claim against search results"""
    if "error" in search_results:
        return "Search Error", "Could not search"
    
    evidence_text = "\n".join([
        f"Source {i+1}: {result['title']}\n{result['content'][:200]}..."
        for i, result in enumerate(search_results.get('results', []))
    ])
    
    prompt = f"""
    Claim: "{claim}"
    
    Search Results:
    {evidence_text}
    
    Based ONLY on the search results above, classify the claim as:
    1. "Verified" - Claim matches current data
    2. "Inaccurate" - Partially true but outdated/wrong numbers
    3. "False" - No evidence or contradicts evidence
    4. "Unverifiable" - Not enough information
    
    Also provide a brief reason (1 sentence).
    
    Return format: {{"verdict": "Verified", "reason": "Matches current data from reliable sources"}}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)
        return result.get("verdict", "Error"), result.get("reason", "")
    except:
        return "Error", "Verification failed"

# Main app logic
if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        text = extract_text_from_pdf(uploaded_file)
    
    st.subheader("Extracted Text (Preview)")
    st.text_area("Full text", text, height=200, disabled=True)
    
    with st.spinner("Extracting claims..."):
        claims = extract_claims(text)
    
    st.subheader(f"Found {len(claims)} Claims")
    
    if claims:
        st.write("Verifying claims... This may take a minute.")
        
        results = []
        for i, claim in enumerate(claims):
            with st.spinner(f"Checking claim {i+1}/{len(claims)}: {claim[:50]}..."):
                search_data = search_claim(claim)
                verdict, reason = verify_claim(claim, search_data)
                
                results.append({
                    "Claim": claim,
                    "Verdict": verdict,
                    "Reason": reason
                })
        
        # Display results
        st.subheader("Verification Results")
        
        # Color coding
        verdict_colors = {
            "Verified": "✅",
            "Inaccurate": "⚠️",
            "False": "🚫",
            "Unverifiable": "❓",
            "Error": "❌"
        }
        
        for result in results:
            emoji = verdict_colors.get(result["Verdict"], "🔸")
            with st.expander(f"{emoji} {result['Claim'][:80]}..."):
                st.write(f"**Verdict:** {result['Verdict']}")
                st.write(f"**Reason:** {result['Reason']}")
        
        # Summary
        st.subheader("Summary")
        verdict_counts = {}
        for r in results:
            verdict_counts[r["Verdict"]] = verdict_counts.get(r["Verdict"], 0) + 1
        
        for verdict, count in verdict_counts.items():
            st.write(f"{verdict_colors.get(verdict, '🔸')} {verdict}: {count}")
    
else:
    st.info("Upload a PDF file to start fact-checking")

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("This app extracts claims from PDFs and verifies them against live web data.")
    st.write("**How it works:**")
    st.write("1. Upload PDF")
    st.write("2. AI extracts claims")
    st.write("3. Searches web for evidence")
    st.write("4. AI compares & verifies")
    
    st.header("Settings")
    use_gpt4 = st.checkbox("Use GPT-4 (more accurate but slower/expensive)", False)
    
    # st.header("Try Sample")
    # if st.button("Use Sample PDF (Market Report)"):
    #     # Will implement sample loading
    #     st.info("Sample feature coming soon!")