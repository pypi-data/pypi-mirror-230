#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as BS
import html2text as h2t
import hashlib
from .options import get_opts


def mkdir(output_a: str):
    # TODO make output dir as needed
    pass


def append_url(
    base_url_a: str,
    urls: list[dict[str, str]],
    url: dict[str, str],
):
    try:
        if len(url["href"].split("://")) < 2:
            if url["href"].startswith("/"):
                url["href"] = base_url_a.rpartition("/")[0] + url["href"]
            else:
                url["href"] = base_url_a.rpartition("/")[0] + "/" + url["href"]
    except KeyError:
        pass
    urls.append(url)


def make_safe_filename(name_a: str):
    # Define a set of illegal characters in filenames
    illegal_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    # Replace illegal characters with underscores
    safe_name = "".join(["_" if char in illegal_chars else char for char in name_a])

    return safe_name


def write_url(
    url_a: str,
    output_a: str,
    code_b: bool,
):
    h = h2t.HTML2Text()
    h.mark_code = code_b
    m = hashlib.md5()
    m.update(url_a.encode("utf-8"))
    hashedUrl = m.hexdigest()
    response = requests.get(url_a)
    if response.status_code == 200:
        soup = BS(response.content, "html.parser")
        titleTag = soup.find("title")
        title = make_safe_filename(titleTag.get_text() + "-") if titleTag else ""
        with open(f"{output_a}/{title}{hashedUrl}.md", "w") as data:
            data.write(h.handle(response.text))


def write_urls(urls_a: list, output_a: str, code_b: bool):
    for url in urls_a:
        if url is None:
            continue
        try:
            url_href = url["href"]
            write_url(url_href, output_a, code_b)
        except KeyError:
            continue


def get_urls(
    base_url_a: str,
    match_a: str,
) -> list:
    response = requests.get(base_url_a)
    soup = BS(response.text, "html.parser")
    urls = []
    for url in soup.findAll("a"):
        if match_a != "":
            try:
                if match_a in url["href"]:
                    append_url(base_url_a, urls, url)
            except KeyError:
                continue
        else:
            append_url(base_url_a, urls, url)
    return urls


def main():
    args = get_opts()
    # set vars
    scrape_all_b = args.all
    base_url = args.url
    match = "" if args.match is None else args.match
    output_dir = "." if args.output is None else args.output
    code_b = args.code
    # do da work
    if scrape_all_b:
        urls = get_urls(base_url, match)
        write_urls(urls, output_dir, code_b)
    else:
        write_url(base_url, output_dir, code_b)
    return 0


if __name__ == "__main__":
    exit(main())
