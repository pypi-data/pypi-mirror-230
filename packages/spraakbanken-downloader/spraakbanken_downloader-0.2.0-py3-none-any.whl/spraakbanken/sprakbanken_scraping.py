import re
import zlib
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup as BS  # type: ignore
from bs4 import ResultSet, Tag

SPRAKBANKEN_KEYS = {
    "updated": "Oppdatert",
    "docs": "Dokumentasjon"
}

SPRAKBANKEN = "https://www.nb.no/SPRAKBANKEN/ressurskatalog/"

dataset_ids = {
    "nst":"oai-nb-no-sbr-54",
    "storting": "oai-nb-no-sbr-84",
    "nbtale": "oai-nb-no-sbr-31",
    "nbsamtale": "oai-nb-no-sbr-85",
}

def make_url(dataset: str) -> str:
    return f"{SPRAKBANKEN}/{dataset_ids[dataset]}/"

def get_content(url: str) -> BS:
    page = requests.get(url, timeout=5)
    if page.status_code == 200:
        return BS(page.text, features="html.parser")

def make_metadata(from_soup: BS) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}

    meta_box: ResultSet = from_soup.find_all("aside")[0]
    for m in meta_box:
        meta_type = m.text.split(":")[0]

        if meta_type == SPRAKBANKEN_KEYS["updated"]:
            datestr = m.text.split(":")[-1]
            dateobj = datetime.strptime(datestr, "%d.%m.%Y").date()
            metadata["updated"] = dateobj

        if meta_type == SPRAKBANKEN_KEYS["docs"]:
            doc_links: List[Tag] = m.find_all("a", href=True)
            metadata["docs"] = [a["href"] for a in doc_links]
            
    return metadata

def is_valid_file(link: ResultSet) -> bool:
    link = link["href"]
    return ".tar.gz" in link or ".zip" in link

def make_download_links(from_soup: BS) -> List[str]:
    # download_class = "teft-link-list-item__link"
    download_class = "t2-link-list-item__link"
    downloads: ResultSet = from_soup.find_all(class_=download_class)
    tarfiles = [a["href"] for a in downloads if is_valid_file(a)]
    return tarfiles

def extract_metadata_info(soup: BS, section_title: str) -> Dict[str, str]:
    info = {}
    accordion_title = soup.find('h2', text=section_title)
    if accordion_title:
        accordion = accordion_title.find_parent('div', class_='t2-accordion')
        for li in accordion.find_all('li'):
            label = li.find('span', class_='node-label')
            if label:
                key = label.text.strip()
                value = li.text.strip().replace(key + ':', '').strip()
                info[key] = value
    return info

def make_meta(body: BS) -> Optional[Dict[str, str]]:
    # 1. extract the "main" element:
    main = body.find('main')
    # 2. find the "Utvidet metadata" h2 tag, and the following "div" class directly after it:
    utvidet_metadata = main.find('h2', text='Utvidet metadata')
    if not utvidet_metadata:
        return None
    utvidet_metadata = utvidet_metadata.find_next_sibling()
    items = utvidet_metadata.find_all('div', class_='t2-accordion-item')

    meta_dict = {}

    for item in items:
        # find the h2 title
        title = item.find('h2').text.strip()
        if title.lower() not in ["resource common info", "corpus info"]:
            continue
        item_data = item.find('div', class_='t2-accordion-item__inner-container')
        ul = item_data.find('ul')
        for li in ul.find_all('li'):
            if li.find("ul"):
                continue
            key = li.find('span', class_='node-label').text.strip()
            value = li.text.strip().replace("\n", " ").replace(key + ':', '').strip()
            value = re.sub(r"\s+", " ", value)
            if value and len(value) > 0:
                meta_dict[key] = value

    return meta_dict

def make_checksum(metadata: Dict[str, str] | None) -> int:
    """ create a checksum based on hashes of all items within the metadata

    Args:
        metadata (dict): dictionary of metadata

    Returns:
        int: a unique checksum for the metadata
    """
    if not metadata:
        return 0
    checksum = 0
    for i in metadata.items():
        csum = 1
        for _i in i:
            csum = zlib.adler32(bytes(repr(_i), "utf-8"), csum)
        checksum = checksum ^ csum
    return checksum

def make_dataset_object(dataset: str) -> Dict[str, Any]:
    url = make_url(dataset.lower())
    soup = get_content(url)
    meta = make_meta(body=soup.find_all("body")[0])
    data = dict(
        url=url,
        meta=meta,
        checksum=make_checksum(meta),
        downloads=make_download_links(soup),
        updated=make_metadata(soup)["updated"].isoformat()
    )
    return data
