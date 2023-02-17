from flask import Flask, request, render_template
from bs4 import BeautifulSoup as bs

import asyncio
import requests
import os

app = Flask(__name__)
seperator = " -- "

destination = None

@app.route("/", methods=['GET', 'POST'])
def home():
  if request.method == "POST":
    item = request.form.get("url")
    asyncio.run(retrieve(item))
    if destination is not None:
      return render_template("./policies/" + destination)
      
  return render_template("./default/home.html")

def walk(url):
  r = requests.get(url)
  soup = bs(r.content, features="html.parser")
  title = " ".join(soup.title.get_text().split())
  
  global destination
  for filename in os.listdir("./templates/policies"):
    if filename.endswith(".html"):
      source = filename.split(seperator)[0]
      if source == title:
        destination = filename
        
  return destination

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

if __name__ == "__main__":
  app.run()