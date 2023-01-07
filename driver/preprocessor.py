import re
import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from bs4.element import Comment

def retrieve_keywords():
  if os.path.isfile("concepts.txt") == False:
    with open("objects.json", "r") as json_file:
      json_dict = json.load(json_file)
      objects = [re.sub("[_]", " ", json_key).strip() for json_key in json_dict]

    objects.sort(key=lambda concept: len(concept))

    with open("concepts.txt", "w") as text_file:
      while 0 < len(objects):
        text_file.write(f"{objects.pop()}\n")

def retrieve_timestamp():
  now = datetime.now()
  date = now.today().strftime("%Y-%m-%d")
  time = now.strftime("%H:%M:%S")

  return date + " " + time

def is_visible(element):
  non_visible = {"style", "script", "head", "title", "meta", "[document]"}
  if element.parent.name in non_visible:
    return False

  if isinstance(element, Comment):
    return False
  
  return True

if __name__ == "__main__":
  page_url = "https://www.cmu.edu/legal/privacy-notice.html"
  retrieve_keywords()
  
  r = requests.get(page_url)
  soup = bs(r.content, features="html.parser")

  nodes = soup.findAll(text=True)
  visible_text = filter(is_visible, nodes)

  text = " ".join(t.strip() for t in visible_text)

  page_title = " ".join(soup.title.get_text().split())
  page_timestamp = retrieve_timestamp()
  
  page_concepts = []
  with open("concepts.txt", "r") as f:
    for unstripped_line in f:
      concept = unstripped_line.strip()
      if re.search(rf"\b{concept}\b", text):
        page_concepts.append(concept)
  
  number_of_concepts = len(page_concepts)

  json_object = {"_url": page_url,
                 "_title": page_title,
                 "_found_concepts": page_concepts, 
                 "_number_of_concepts": number_of_concepts}
  
  with open(f"metadata/{page_title}", "w") as f:
    json.dump(json_object, f)