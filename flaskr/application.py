from flask import Flask, request, render_template
from bs4 import BeautifulSoup as bs

import asyncio
import requests
import os

import preprocessor

app = Flask(__name__)
seperator = " -- "

destination = None

# @app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET"])
def home():
  return render_template("./default/base.html", title="test")
  '''
  if request.method == "POST":
    item = request.form.get("url")
    asyncio.run(retrieve(item))

    while destination is None:
      return render_template("./default/waiting.html")
    else:
      return render_template("./policies/" + destination)
          
  return render_template("./default/home.html")
  '''

async def producer(item, queue):
  # print("Producer: Running")
  await queue.put(item)
  
  await queue.put(None)
  # print("Producer: Done")

async def consumer(queue):
  # print("Consumer: Running")
  while True:
    try:
      item = queue.get_nowait()
    except asyncio.QueueEmpty:
      await asyncio.sleep(0.5)
      continue

    if item is None:
      break

    walk(item)

    print(f'> got item: {destination}')
  
  # print("Consumer: Done")

async def retrieve(item):
  queue = asyncio.Queue()
  await asyncio.gather(producer(item, queue), consumer(queue))

def walk(url):
  # print("walking")
  global destination
  
  try:
    r = requests.get(url)
  except requests.exceptions.InvalidURL:
    return destination
  except requests.exceptions.MissingSchema:
    return destination
  
  soup = bs(r.content, features="html.parser")
  title = " ".join(soup.title.get_text().split())
  
  for filename in os.listdir("./templates/policies"):
    if filename.endswith(".html"):
      source = filename.split(seperator)[0]
      if source == title:
        destination = filename
  
  return destination

def processor(url):
  preprocessor.parse(url)
  os.system(f"node ./headless.js {url}")
  
if __name__ == "__main__":
  app.run()