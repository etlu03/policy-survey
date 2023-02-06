from flask import Flask
from bs4 import BeautifulSoup as bs

import os
import argparse
import requests

seperator = " -- ";
templates_directory = "templates/"

def issue_report(html):
  return f"<p>{html}</p>"

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Feed privacy notice to audit")
  parser.add_argument(
        "--url", "-u", action="store", help="URL of privacy notice", required=True
  )
  args = parser.parse_args()

  url = args.url

  r = requests.get(url)
  soup = bs(r.content, features="html.parser")

  page_title = " ".join(soup.title.get_text().split())

  for filename in os.scandir(templates_directory):
    html = filename.path.split("/")[1]
    title = html.split(seperator)[0]
    if title == page_title:
      issue_report(html)
      break