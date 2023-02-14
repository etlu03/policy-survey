from flask import Flask, request, render_template
import asyncio

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
  '''
  if request.method == "POST":
    item = request.form.get("url")
    asyncio.run(retrieve(item))
  '''

  return render_template("./default/waiting.html")

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

async def retrieve(item):
  queue = asyncio.Queue()
  await asyncio.gather(producer(item, queue), consumer(queue))

if __name__ == "__main__":
  app.run()