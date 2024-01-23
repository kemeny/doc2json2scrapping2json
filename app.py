import streamlit as st
import docx
import json
import base64
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Initialize an empty container for logs at the start of your app
log_container = st.empty()

# Function to update logs
def update_log(message):
    # Get current log value, if not set, initialize with an empty string
    current_log = log_container.empty() if log_container else ""
    new_log = f"{current_log}\n{message}"
    log_container.markdown(new_log)

# Function to read DOCX file and convert its content to JSON
def docx_to_json(docx_file):
    update_log("Reading DOCX file...")
    doc = docx.Document(docx_file)
    data = []
    for para in doc.paragraphs:
        data.append({"text": para.text, "style": para.style.name})
    update_log("DOCX file processed.")
    return json.dumps(data, indent=4)

# Function to scrape content from URLs
def scrape_content(urls):
    update_log("Starting web scraping...")
    scraped_data = []
    for url in urls:
        page_data = {"url": url, "title": None, "publish_date": None, "content": None}
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extracting title
            title_tag = soup.find('title')
            page_data["title"] = title_tag.get_text() if title_tag else 'No Title Found'

            # Attempting to extract publish date
            date_tag = soup.find(lambda tag: tag.name == "meta" and "publish" in tag.get("name", "").lower())
            if date_tag:
                page_data["publish_date"] = date_tag["content"]

            # Extracting content
            page_data["content"] = soup.get_text()
            update_log(f"Scraped URL: {url}")

        except requests.RequestException as e:
            page_data["content"] = f"Failed to retrieve content: {e}"
            update_log(f"Error scraping {url}: {e}")
        
        scraped_data.append(page_data)
    update_log("Web scraping completed.")
    return scraped_data

# Function to extract valid URLs from JSON data
def extract_urls_from_json(json_data):
    update_log("Extracting URLs from JSON...")
    valid_urls = []
    for item in json_data:
        url_candidate = item.get("text", "")
        if url_candidate.startswith("http://") or url_candidate.startswith("https://"):
            valid_urls.append(url_candidate)
    update_log("URL extraction completed.")
    return valid_urls

# Streamlit App Interface
st.title("DOCX to JSON Converter and Web Scraper")

# File Uploader for DOCX
uploaded_docx_file = st.file_uploader("Upload a DOCX file", type=["docx"], key="docx_uploader")

if uploaded_docx_file is not None:
    json_data = docx_to_json(uploaded_docx_file)
    st.json(json_data)
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="converted.json">Download JSON File</a>'
    st.markdown(href, unsafe_allow_html=True)

# File Uploader for JSON containing URLs
uploaded_json_file = st.file_uploader("Upload a JSON file with URLs", type=["json"], key="json_uploader")

if uploaded_json_file is not None:
    json_content = json.load(uploaded_json_file)
    urls = extract_urls_from_json(json_content)
    scraped_data = scrape_content(urls)
    st.json(scraped_data)
    scraped_data_json = json.dumps(scraped_data, indent=4)
    b64 = base64.b64encode(scraped_data_json.encode()).decode()
    download_href = f'<a href="data:file/json;base64,{b64}" download="scraped_data.json">Download Scraped Data JSON File</a>'
    st.markdown(download_href, unsafe_allow_html=True)
