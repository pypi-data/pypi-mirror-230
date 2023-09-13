import re
from urllib.parse import urlparse

import pandas as pd
from gspread import IncorrectCellLabel


def get_id_from_url(url: str, split_on="/", index_num=-2):
    url_id = None
    if isinstance(url, str) and split_on in url:
        split_url = url.split(split_on)
        url_id = split_url[index_num]
    return url_id


def get_post_id_from_li_url(li_url):
    if len(li_url) <= 0:
        return li_url
    if "?" in li_url:
        li_url = li_url.split("?")[0]
    if li_url[-1] == "/":
        li_url = li_url[:-1]
    return li_url.split("/")[-1]


def is_valid_premise_url(url):
    if not isinstance(url, str):
        return False
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return False
    if parsed_url.netloc != "app.copyfactory.io":
        return False
    if "premises" not in parsed_url.path:
        return False
    return True


def fix_website(site):
    if not isinstance(site, str):
        site = ""
    site = re.search(r"[\w\.\-]+\.[a-z0-9]*[a-z][a-z0-9]*(?:/[\w\.\-/]*)?", site)
    if site:
        site = site.group(0)
        if "https://" not in site:
            site = f"https://{site}"
    return site


def is_google_workflow_url_valid(url):
    """
    Check that url is a url and that its a google spreadsheet.
    """
    if not isinstance(url, str):
        return False
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        return False
    if parsed_url.netloc != "docs.google.com":
        return False
    if "spreadsheets" not in parsed_url.path:
        return False
    return True


def chunk_df(df: pd.DataFrame, chunk_size=200) -> pd.DataFrame:
    num_chunks = len(df) // chunk_size
    if len(df) % chunk_size != 0:
        num_chunks += 1
    for i in range(num_chunks):
        yield df[i * chunk_size : (i + 1) * chunk_size]


def convert_to_a1(row: int, col: int):
    row, col = int(row), int(col)

    if row < 1 or col < 1:
        raise IncorrectCellLabel("({}, {})".format(row, col))

    div = col
    column_label = ""

    while div:
        (div, mod) = divmod(div, 26)
        if mod == 0:
            mod = 26
            div -= 1
        column_label = chr(mod + 64) + column_label

    return f"{column_label}{row}"
