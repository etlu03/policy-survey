from bs4 import BeautifulSoup as bs
from bs4.element import Comment
from datetime import datetime
import requests
import json
import re
import argparse
import os

concepts_src = "../storage/" + "objects.json"
concepts_dst = "../storage/" + "concepts.txt"

metadata_dst = "metadata/"

def retrieve_keywords():
  if os.path.isfile(concepts_dst) == False:
    with open(concepts_src, "r") as json_file:
      json_dict = json.load(json_file)
      objects = [re.sub("[_]", " ", json_key).strip() for json_key in json_dict]

    objects.sort(key=len)
    objects = list(filter(lambda concept: " " in concept, objects))

    with open(concepts_dst, "w") as text_file:
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

def find_overlap(concept_spans, span):
  (span_start, span_end) = span
  for (start, end) in concept_spans:
    if start <= span_start and span_end <= end:
      return True
  return False

def renew_audit(page_title, page_timestamp):
  if os.path.isfile(f"metadata/{page_title}.json"):
    with open(f"metadata/{page_title}.json", "r") as json_file:
      json_dict = json.load(json_file)
      yesterday = json_dict["_page_timestamp"].split(" ")[1]
      today = page_timestamp.split(" ")[1]

      t1 = datetime.strptime(yesterday, "%H:%M:%S")
      t2 = datetime.strptime(today, "%H:%M:%S")

      delta = t2 - t1
      if delta.days > 30:
        return True

      return False

  return True

def main(page_url):
  r = requests.get(page_url)
  soup = bs(r.content, features="html.parser")

  page_title = " ".join(soup.title.get_text().split())
  page_timestamp = retrieve_timestamp()
  
  if renew_audit(page_title, page_timestamp) == True:
    nodes = soup.findAll(text=True)
    visible_text = filter(is_visible, nodes)

    text = " ".join(t.strip() for t in visible_text)

    page_concepts = set()
    concept_spans = []
    with open(concepts_dst, "r") as f:
      for unstripped_line in f:
        concept = unstripped_line.strip()
        match = re.search(rf"(?i)\b{concept}\b", text)
        if match != None:
          span = match.span()
          if find_overlap(concept_spans, span) == False:
            page_concepts.add(concept.lower())
            concept_spans.append(span)

    number_of_concepts = len(page_concepts)

    found_concepts = list(page_concepts)
    found_concepts.sort(key=len, reverse=True)

    json_object = {"_url": page_url,
                  "_title": page_title,
                  "_page_timestamp": page_timestamp,
                  "_found_concepts": found_concepts,
                  "_number_of_concepts": number_of_concepts}
    print(found_concepts)
    
    with open(f"{metadata_dst}{page_title}.json", "w") as f:
      json.dump(json_object, f)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Feed privacy notice to audit")
  parser.add_argument(
        "--url", "-u", action="store", help="URL of privacy notice", required=True
  )
  args = parser.parse_args()
  url = args.url

  retrieve_keywords()

  main(url)