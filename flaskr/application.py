from flask import Flask, request, render_template
import asyncio
from random import random

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
  if request.method == "POST":
    url = request.form.get("url")
    asyncio.run(retrieve(url))
    
  return render_template("./audit/home.html")

async def producer(item, queue):
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
  
    print(f'> got item: {item}')
  
  print("Consumer: Done")

async def retrieve(url):
  queue = asyncio.Queue()
  await asyncio.gather(producer(url, queue), consumer(queue))

if __name__ == "__main__":
  app.run()