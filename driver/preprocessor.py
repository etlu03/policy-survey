import re
import os
import json
import requests
from bs4 import BeautifulSoup as bs

def retrieve_keywords():
  if os.path.isfile("concepts.txt") == False:
    with open("objects.json", "r") as json_file:
      json_dict = json.load(json_file)
      objects = [re.sub("[_]", " ", json_key).strip() for json_key in json_dict]

    objects.sort(key=lambda concept: len(concept))

    with open("concepts.txt", "w") as text_file:
      while 0 < len(objects):
        text_file.write(f"{objects.pop()}\n")
    
if __name__ == "__main__":
  url = "https://www.cmu.edu/legal/privacy-notice.html"

  r = requests.get(url)
  soup = bs(r.content, features="html.parser")
  text_nodes = ["p", "li"]

  policy = str()
  sentences = sentence_length = 0
  for tag in text_nodes:
    for node in soup.find_all(tag, recursive=True):
      sentence_length += len(node.text.strip())
      sentences += 1
  
  average_length = sentence_length // sentences

  for tag in text_nodes:
    for node in soup.find_all(tag, recursive=True):
      text = node.text.strip()
      if average_length <= len(text):
        policy += text