import random
import re
import time
import requests
from bs4 import BeautifulSoup
import openai


def extract_titles(entries):
    titles = []
    for entry in entries:
        # Adjusted pattern to account for different formats, including those with a month/year and conference/journal information
        match = re.search(r'\b\d{4}(?:, [a-zA-Z]+)?\.\s(.*?)(?=\. In|\.$)', entry)
        if match:
            title = match.group(1).strip()
            titles.append(title)
        else:
            titles.append("Title not found")
    return titles

def parse_bibitems(tex_file_path):
    """
    Parses a .tex file to extract bibliography items.
    
    Parameters:
    tex_file_path (str): The path to the .tex file.
    
    Returns:
    dict: A dictionary with the bibliography keys as keys and their corresponding entries as values.
    """
    # Corrected pattern to properly escape backslashes
    bibitem_pattern = r'\\bibitem\{([^}]+)\}\s*(.*?)(?=\\bibitem|\\end\{thebibliography\})'
    bibitems = {}

    with open(tex_file_path, 'r') as file:
        content = file.read()

    matches = re.findall(bibitem_pattern, content, re.DOTALL)

    for key, value in matches:
        # Clean up the value by removing any leading or trailing whitespace and newlines
        clean_value = value.strip()
        bibitems[key] = clean_value

    return bibitems

def get_citation_from_google_scholar(paper):
    """
    https://github.com/Kildrese/scholarBibTex/blob/main/citationGrab.py
    """
    base_url = "https://scholar.google.de/scholar?hl=de&as_sdt=0%2C5&q=" + paper + "&btnG= "
    googleSearch = requests.request("GET", url=base_url)
    bs_page = BeautifulSoup(googleSearch.content, "html.parser")
    block = bs_page.find("div", {"class": "gs_ri"})
    title = block.find("h3")
    link = title.find("a")
    citation_id = link["id"]
    cite_url = "https://scholar.google.de/scholar?hl=de&q=info:" + citation_id + ":scholar.google.com/&output=cite&scirp=0"
    findLatex = requests.request("GET", url=cite_url)
    citation_view = BeautifulSoup(findLatex.content, "html.parser")
    latex_link = citation_view.find("div", {"id": "gs_citi"})
    latex_mf = latex_link.findChildren("a")[0]["href"]
    result = BeautifulSoup(requests.request("GET", url=latex_mf).content, "html.parser")
    citation = result.text
    return citation

def start_requests(bibfile):
    bibitems = parse_bibitems(bibfile)
    bib = extract_titles(bibitems.values())
    for entry in bib:
        paper = entry["title"]
        # Introduce a delay to avoid being blocked by Google
        randomdelay = random.randint(1, 10)
        time.sleep(randomdelay)
        citation = get_citation_from_google_scholar(paper)
        print(citation)

if __name__ == "__main__":
    bib = parse_bibitems("bibfile.tex")
    titles = extract_titles(bib.values())
    print(titles)