import streamlit as st
import json
from docx import Document
import base64
import xmltodict
import requests
from bs4 import BeautifulSoup

# Streamlit App Interface
st.title("File Converters and Web Scraper")

def sitemap_to_scraped_json(sitemap_content):
    sitemap = xmltodict.parse(sitemap_content)
    urls = [url['loc'] for url in sitemap['urlset']['url']]
    total_urls = len(urls)
    st.write(f"Total URLs to scrape: {total_urls}")
    progress_bar = st.progress(0)
    data = []
    for i, url in enumerate(urls, start=1):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        page_data = {
            'url': url,
            'title': soup.title.string if soup.title else 'No Title Found',
            'content': soup.get_text()
        }
        data.append(page_data)
        progress_bar.progress(i / total_urls)
    st.write("Scraping completed.")
    return json.dumps(data, indent=4)

sitemap_file = st.file_uploader("XML Sitemap to JSON", type=['xml'])
if sitemap_file is not None:
    sitemap_content = sitemap_file.getvalue().decode()
    st.write("File uploaded. Starting to process...")
    json_data = sitemap_to_scraped_json(sitemap_content)
    st.text(json_data)

def xml_to_json(xml_file):
    st.write("Converting XML to JSON...")
    xml_content = xml_file.read()
    data_dict = xmltodict.parse(xml_content)
    st.write("Conversion completed.")
    return json.dumps(data_dict, indent=4)

def docx_to_json(docx_file):
    doc = Document(docx_file)
    data = []
    for para in doc.paragraphs:
        data.append({"text": para.text, "style": para.style.name})
    return json.dumps(data, indent=4)

def scrape_content(urls):
    scraped_data = []
    for url in urls:
        page_data = {"url": url, "title": None, "publish_date": None, "content": None}
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            page_data["title"] = title_tag.get_text() if title_tag else 'No Title Found'
            date_tag = soup.find(lambda tag: tag.name == "meta" and "publish" in tag.get("name", "").lower())
            if date_tag:
                page_data["publish_date"] = date_tag["content"]
            page_data["content"] = soup.get_text()
        except requests.RequestException as e:
            page_data["content"] = f"Failed to retrieve content: {e}"
        scraped_data.append(page_data)
    return scraped_data

def extract_urls_from_json(json_data):
    valid_urls = []
    for item in json_data:
        if isinstance(item, dict):
            url_candidate = item.get("text", "")
            if url_candidate.startswith("http://") or url_candidate.startswith("https://"):
                valid_urls.append(url_candidate)
    return valid_urls

uploaded_docx_file = st.file_uploader("DOCX to JSON", type=["docx"], key="docx_uploader")
if uploaded_docx_file is not None:
    json_data = docx_to_json(uploaded_docx_file)
    st.json(json_data)
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="converted.json">Download JSON File</a>'
    st.markdown(href, unsafe_allow_html=True)

uploaded_xml_file = st.file_uploader("XML to JSON", type=["xml"], key="xml_uploader")
if uploaded_xml_file is not None:
    json_data = xml_to_json(uploaded_xml_file)
    st.json(json_data)
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="converted.json">Download JSON File</a>'
    st.markdown(href, unsafe_allow_html=True)

uploaded_json_file = st.file_uploader("JSON file with URLs Web Scrapper", type=["json"], key="json_uploader")
if uploaded_json_file is not None:
    json_content = json.load(uploaded_json_file)
    urls = extract_urls_from_json(json_content)
    scraped_data = scrape_content(urls)
    st.json(scraped_data)
    scraped_data_json = json.dumps(scraped_data, indent=4)
    b64 = base64.b64encode(scraped_data_json.encode()).decode()
    download_href = f'<a href="data:file/json;base64,{b64}" download="scraped_data.json">Download Scraped Data JSON File</a>'
    st.markdown(download_href, unsafe_allow_html=True)