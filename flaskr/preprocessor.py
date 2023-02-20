from bs4 import BeautifulSoup as bs
from bs4.element import Comment as comment
from datetime import datetime

import json
import requests
import re
import os

objects_json = "../storage/objects.json"
concepts_txt = "../storage/concepts.txt"

metadata = "../storage/metadata/"

def visible(element):
  nonvisible_elements = {"style", "script", "head", "title", "meta", "[document]"}
  if element.parent.name in nonvisible_elements:
    return False
  
  if isinstance(element, comment):
    return False
  
  return True

def retrieve_keywords():
  if os.path.isfile(concepts_txt) == False:
    with open(objects_json, "r") as json_file:
      json_dict = json.load(json_file)
      objects = [re.sub("[_]", " ", json_key).strip() for json_key in json_dict]

    objects.sort(key=len)
    objects = filter(lambda keyword: " " in keyword, objects)
    objects = list(objects)

    with open(concepts_txt, "w") as text_file:
      while 0 < len(objects):
        text_file.write(objects.pop() + "\n")

def stamp():
  now = datetime.now()
  date = now.today().strftime("%Y-%m-%d")
  time = now.strftime("%H:%M:%S")
  
  return " ".join([date, time])

def has_overlap(spans, current_span):
  span_start, span_end = current_span
  for start, end in spans:
    if start <= span_start and span_end <= end:
      return True
  
  return False

def renew(title, timestamp):
  src = f"metadata/{title}.json"
  if os.path.isfile(src):
    with open(src, "r") as json_file:
      json_dict = json.load(json_file)
      yesterday = json_dict["__timestamp"].split(" ")[1]
      today = timestamp.split(" ")[1]

      t1, t2 = datetime.strptime(yesterday, "%H:%M:%S"), datetime.strptime(today, "%H:%M:%S")
      difference = t2 - t1

      if 30 < abs(difference.days):
        return True
      
      return False

  return True
  
def audit(url):
  retrieve_keywords()

  r = requests.get(url)
  soup = bs(r.content, features="html.parser")

  title = " ".join(soup.title.get_text().split())
  timestamp = stamp()

  if renew(title, timestamp) == True:
    nodes = soup.findAll(text=True)
    visible_content = filter(visible, nodes)

    text = " ".join(t.strip() for t in visible_content)
    spans = []
    concepts = set()
    with open(concepts_txt, "r") as text_file:
      for unstripped_line in text_file:
        concept = unstripped_line.strip()
        match = re.search(rf"(?i)\b{concept}\b", text)
        if match is not None:
          current_span = match.span()
          if has_overlap(spans, current_span) == False:
            concepts.add(concept.lower())
            spans.append(current_span)
 
    number_of_concepts = len(concepts)
    found_concepts = list(concepts)
    found_concepts.sort(key=len, reverse=True)

    json_object = {"__url": url,
                   "__title": title,
                   "__timestamp": timestamp,
                   "__number_of_concepts": number_of_concepts,
                   "__found_concepts": found_concepts}
    
    with open(metadata + title + ".json", "w") as dst:
      json.dump(json_object, dst)