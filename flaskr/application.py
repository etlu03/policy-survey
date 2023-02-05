from flask import Flask, render_template
from bs4 import BeautifulSoup as bs
import requests
import argparse
import os 

app = Flask(__name__)
storage_directory = "static/"

# view as name (templates)
@app.route("/")
def build(files):
  return render_template(storage_directory + files)

if __name__ == "__main__":
  # this could moved into a function to call (convention stuff)
  '''
  app.run()?
  '''
  '''
  #!/bin/sh

  export FLASK_APP=application.py
  export FLASK_DEBUG=1
  export FLASK_RUN_PORT=5001

  flask run
  '''
  parser = argparse.ArgumentParser(description="Feed privacy notice to audit")
  parser.add_argument(
        "--url", "-u", action="store", help="URL of privacy notice", required=True
  )
  args = parser.parse_args()

  url = args.url
  r = requests.get(url)
  soup = bs(r.content, features="html.parser")

  page_title = " ".join(soup.title.get_text().split())

  for files in os.listdir(storage_directory):
    if page_title in files:
      build(files)
      break