from flask import Flask, render_template, request
from requests.exceptions import HTTPError, InvalidURL, InvalidSchema, MissingSchema
from bs4 import BeautifulSoup as bs
import asyncio
import requests
import os

app = Flask(__name__)
destination = None

policies = "./templates/policies/"
seperator = " -- "

async def producer(queue, item):
  print("Producer: Running")
  await queue.put(item)
  await queue.put(None)
  print("Producer: Done")

async def consumer(queue):
  print("Consumer: Running")
  while True:
    try:
      item = queue.get_nowait()
    except asyncio.QueueEmpty:
      await asyncio.sleep(0.5)
      continue
    if item is None:
      break
    retrieve(item)
  print("Consumer: Done")

async def routine(item):
  queue = asyncio.Queue()
  await asyncio.gather(producer(queue, item), consumer(queue))

def run_puppeteer(policy):
  os.system(f"node ./headless.js {policy}")

def retrieve(item):
  global destination
  
  try:
    response = requests.get(item)
    response.raise_for_status()
  except HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
    destination = None
  except InvalidURL:
    print(f"{item} is considered an invalid url")
    destination = None
  except InvalidSchema:
    print(f"{item} is considered an invalid schema")
    destination = None
  except MissingSchema:
    print(f"{item} is missing a schema")
    destination = None
  except Exception as err:
    print(f"Some other error occured: {err}")
    destination = None
  else:
    print(f"The call to requests.get({item}) was successful")
    soup = bs(response.content, features="html.parser")
    title = " ".join(soup.title.get_text().split())
    for policy in os.listdir(policies):
      if policy.endswith(".html"):
        filename = policy.split(seperator)[0]
        if filename == title:
          destination = policy
          break
    else:
      print("Calling Puppeteer")
      run_puppeteer(policy)
    
@app.route("/", methods=["GET", "POST"])
def homepage():
  if request.method == "POST":
    item = request.form["q"]
    asyncio.run(routine(item))
    if destination is not None:
      return render_template("./policies/" + destination)
    else:
      return render_template("./static/loading.html")

  return render_template("./static/homepage.html")